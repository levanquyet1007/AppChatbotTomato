import 'package:flutter/material.dart';
import 'package:chatbottomato/providers/chat_provider.dart';
import 'package:chatbottomato/screens/home_screen.dart';
import 'package:provider/provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await ChatProvider.initHive();

  runApp(MultiProvider(
    providers: [
      ChangeNotifierProvider(create: (context) => ChatProvider()),
    ],
    child: const MyApp(),
  ));
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Chatbot take care of Tomato',
      home: HomeScreen(),
    );
  }
}
