import 'package:chatbottomato/constants/constants.dart';
import 'package:chatbottomato/hive/chat_history.dart';
import 'package:chatbottomato/hive/user_model.dart';
import 'package:hive/hive.dart';

class Boxes {
  // get the chat history box
  static Box<ChatHistory> getChatHistory() =>
      Hive.box<ChatHistory>(Constants.chatHistoryBox);

  // get user box
  static Box<UserModel> getUser() => Hive.box<UserModel>(Constants.userBox);
}
