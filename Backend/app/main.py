from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import os
import tensorflow as tf
from PIL import Image
import numpy as np
from io import BytesIO
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras.applications import DenseNet121
import requests
# import asyncio
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_pinecone import PineconeEmbeddings
from groq import Groq

app = FastAPI()
def load_model(model_path="D:\DATN\Backend\model\ckpt_epoch_13.weights.h5"):
    conv_base = DenseNet121(
        weights='imagenet',
        include_top = False,
        input_shape=(256,256,3),
        pooling='avg'
    )
    conv_base.trainable = False
    model = Sequential()
    model.add(conv_base)
    model.add(BatchNormalization())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.35))
    model.add(BatchNormalization())
    model.add(Dense(120, activation='relu'))
    model.add(Dense(10, activation='softmax'))
    model.load_weights(model_path)
    return model

def preprocess_image(file: bytes, target_size):
    image = Image.open(BytesIO(file)).convert("RGB")  
    image = image.resize(target_size)  
    image_array = np.array(image) / 255.0  
    return np.expand_dims(image_array, axis=0) 


def read_file_from_folder(file_name, folder_path):
    # Kiểm tra nếu file tồn tại trong thư mục
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        # Nếu file tồn tại, mở và đọc nội dung file
        with open(file_path, 'r', encoding='utf-8') as file:
            return "cách xử lý như sau: "+file.read()
    else:
        # Nếu file không tồn tại, trả về chuỗi rỗng
        return ""
    
# Hàm để dự đoán
def predict(input_data, model):
   
    input_data = preprocess_image(input_data,(256,256))
    # Thực hiện dự đoán
    predictions = model.predict(input_data)
    class_names = ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']
    return class_names[np.argmax(predictions , axis=1)[0]]


model = load_model()
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}



@app.post("/predict/")
async def upload_image(
    text: str = Form(...), 
    file: UploadFile = File(...)  
):
   
    try:
        contents = await file.read()
        predictions = predict(contents, model)
        result_webSearch = await process_search_results(search_web(f"Thông tin và cách chăm sóc cây cà chua"))
        print(result_webSearch)
        infoFromPredictions  = read_file_from_folder(predictions + 'txt',"D:\DATN\Backend\doc")

        infoFromDB = await retrival(f"trình trạng cây {predictions}"+text)

        promt =f"Đóng vai trò là chuyên gia chăm sóc cây trông hãy dựa vào Tình trạng của cây cà chua: '{predictions}' '{infoFromPredictions}' hãy đọc thêm thông tin '{infoFromDB}' và '{result_webSearch}' sau đó trả lời câu hỏi '{text}' bằng tiếng việt đúng trọng tâm nhưng vẫn. Nhớ thật kỹ là bằng tiếng việt"

        result = genAns(promt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Cấu hình Google Custom Search API
API_KEY = "AIzaSyDw7k_WiTmD8LLG9iiqxqys5IFZlSgCloU"
CX = "b0a6735745d474671"

# Hàm gọi Google Custom Search API
def search_web(query: str):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Web search failed")

# Hàm lọc kết quả trả về và lấy nội dung đầu tiên
def process_search_results(results):
    # Kiểm tra nếu có kết quả
    if 'items' not in results or len(results['items']) == 0:
        return {"message": "No results found."}
    
    # Lấy nội dung (snippet) của kết quả đầu tiên
    first_result_snippet = results['items'][0].get("snippet")
    
    return {"snippet": first_result_snippet}




PINECONE_API_KEY = 'fd1814ff-1a2c-4475-9b33-0c34953bc304'
model_name = "multilingual-e5-large"
client = Groq(
    api_key="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",
)

async def retrival(inputtext):
    embeddings = PineconeEmbeddings(
        model=model_name,
        pinecone_api_key=PINECONE_API_KEY
    )

    # Sử dụng embeddings để chuyển câu văn bản thành vector
    query_vector = embeddings.embed_query(inputtext)

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("rag")

    query_result = index.query(
        namespace="wondervector5000",
        vector=query_vector,
        top_k=3,
        include_metadata=True
    )

    info = query_result['matches'][0]['metadata'].get('text', 'No text available') + "\n"
    print(info)
    return info

def genAns(inputtext):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": inputtext,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

