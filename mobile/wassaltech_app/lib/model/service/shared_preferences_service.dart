import 'package:shared_preferences/shared_preferences.dart';

class SharedPreferencesService {
  static Future<String> getFirstName() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('first_name') ?? 'User';
  }

  static Future<void> saveFirstName(String firstName) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('first_name', firstName);
  }

  static const _chatHistoryKey = 'chat_history';

  static Future<void> saveChatHistory(List<String> messages) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_chatHistoryKey, messages);
  }

  static Future<List<String>> getChatHistory() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_chatHistoryKey) ?? [];
  }
}