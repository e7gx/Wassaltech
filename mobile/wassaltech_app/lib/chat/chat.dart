import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:lottie/lottie.dart';
import 'package:typewritertext/typewritertext.dart';
import 'package:flutter/services.dart';
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'package:wassaltech_app/model/service/shared_preferences_service.dart';

class AiChatPage extends StatefulWidget {
  const AiChatPage({super.key});

  @override
  State<AiChatPage> createState() => _MainPageState();
}

class _MainPageState extends State<AiChatPage> {
  final List<Message> _messages = [];
  String _firstName = 'Admin';
  int _userCount = 0;
  int _freelancerCount = 0;
  int _offerCount = 0;
  int _orderCount = 0;
  double _totalPrice = 0.0;
  double _reviewsAverage = 0.0;
  double _depositedAmount = 0.0;

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _fetchAllCounts();
  }

  Future<List<Offer>> fetchAllOffers() async {
    final response =
        await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/all/'));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Offer.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load offers');
    }
  }

  Future<double> fetchDepositedAmount() async {
    final response =
        await http.get(Uri.parse('http://127.0.0.1:8000/api/amount/'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      return double.parse(data['total_amount'] as String);
    } else {
      throw Exception('Failed to load deposited amount');
    }
  }

  Future<void> _fetchAllCounts() async {
    try {
      _userCount = await fetchUserCount();
      _freelancerCount = await fetchFreelancerCount();
      List<Offer> offers = await fetchAllOffers();
      _orderCount = await fetchOrdersCount();
      _reviewsAverage = await fetchReviewsAverage();
      _depositedAmount = await fetchDepositedAmount();

      setState(() {
        _userCount = _userCount;
        _freelancerCount = _freelancerCount;
        _offerCount = offers.length;
        _orderCount = _orderCount;
        _totalPrice = _totalPrice;
        _reviewsAverage = _reviewsAverage;
        _depositedAmount = _depositedAmount;
      });
    } catch (e) {
      // print("Error fetching counts: $e");
    }
  }

  Future<void> _saveChatHistory() async {
    List<String> messages = _messages
        .map((message) => json.encode({
              'text': message.text,
              'isMe': message.isMe,
            }))
        .toList();

    await SharedPreferencesService.saveChatHistory(messages);
  }

  Future<void> _loadUserData() async {
    final firstName = await SharedPreferencesService.getFirstName();
    final chatHistory = await SharedPreferencesService.getChatHistory();

    setState(() {
      _firstName = firstName;
      if (chatHistory.isNotEmpty) {
        _messages.addAll(chatHistory.map((message) {
          final parsed = json.decode(message);
          return Message(text: parsed['text'], isMe: parsed['isMe']);
        }).toList());
      }
    });
  }

  final TextEditingController _textEditingController = TextEditingController();

  bool _userSentMessage = false;

  void onSendMessage() {
    String trimmedText = _textEditingController.text.trim();
    if (trimmedText.isEmpty) {
      return;
    }

    setState(() {
      _userSentMessage = true;
      Message message = Message(text: trimmedText, isMe: true);
      _messages.insert(0, message);
      _textEditingController.clear();
    });

    _saveChatHistory();

    sendMessageToChatGpt(trimmedText).then((response) {
      Message chatGptMessage = Message(text: response, isMe: false);
      setState(() {
        _messages.insert(0, chatGptMessage);
      });
      _saveChatHistory();
    }).catchError((error) {});
  }

  Future<String> sendMessageToChatGpt(String message) async {
    try {
      String prompt = """
    You are an helpful assistant in a  Wassaltech | وَصّلْتِك app. 

    the username that you are helping is $_firstName.
    
    You are helping the system admin to manage the system like the count of orders and offers and users.


      1- Current user count: $_userCount
      2- Current freelancer count: $_freelancerCount
      3- Current offer count: $_offerCount
      4- Current order count: $_orderCount
      5- Current Financial Amount : $_depositedAmount
      6- Current company's profits : The company's profits are 10% of this amount. I want you to display it with the list $_depositedAmount let's call it company profits. EXAMPLE OF THE RESPONSE : DEPOSITED_AMOUNT = 10000, COMPANY PROFIT : 2000 Just like that. DO NOT EVER MENTION THE 20% JUST WRITE THE NUMBER TO THE USER

      7- Reviews Average: $_reviewsAverage

    only this data is available for now. do not ask for any other data.

    Based on the user's input,answer within the context of System Management and Risk management.

    If the user asks for help, provide a list of commands they can use.

    If the user asks for his Reports clean and helpful Report based on the data that you have.

    make the user feel comfortable and provide the best experience for him.

    make sure to provide the best answer for the user's question.

    Make sure that your respond is well structured and readable.

    Do not respond in markdown format

    your answers must be interactive with the user, use some techniques, like mentioning the user first name in the responses

    also provide good additional data based on given data that could benefits the user

    be creative and your answers must be in simple English language, do not include hard sentences or something that is not understandable by non-native english human.

    """;

      String promptMessage = "$prompt\nUser's Message: $message";

      Uri uri = Uri.parse("https://api.openai.com/v1/chat/completions");
      Map<String, dynamic> body = {
        "model": "gpt-3.5-turbo",
        "messages": [
          {"role": "user", "content": promptMessage}
        ],
        "max_tokens": 500,
      };

      final response = await http.post(
        uri,
        headers: {
          "Content-Type": "application/json; charset=UTF-8",
          "Authorization": "Bearer ${APIKey.apikey}",
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200) {
        Map<String, dynamic> parsedResponse =
            json.decode(utf8.decode(response.bodyBytes));
        if (parsedResponse.containsKey('choices') &&
            parsedResponse['choices'].isNotEmpty &&
            parsedResponse['choices'][0].containsKey('message')) {
          String content = parsedResponse['choices'][0]['message']['content'] ??
              "No reply found.";
          return content;
        } else {
          return "Error: Invalid response format.";
        }
      } else {
        return "Error: ${response.statusCode} - ${response.reasonPhrase}";
      }
    } catch (e) {
      return "Error: Exception during API call.";
    }
  }

  Widget _buildMessage(Message message, bool isLatestMessage) {
    String imagePath =
        message.isMe ? 'assets/images/test.png' : 'assets/images/ai.png';

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
      child: Row(
        mainAxisAlignment:
            message.isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!message.isMe)
            CircleAvatar(
              backgroundImage: AssetImage(imagePath),
            ),
          const SizedBox(width: 10),
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: Colors.orange.withOpacity(0.3),
                    spreadRadius: 2,
                    blurRadius: 5,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              padding: const EdgeInsets.all(15),
              child: message.isMe
                  ? SelectableText(
                      message.text,
                      style: const TextStyle(
                        color: Colors.black,
                        fontSize: 15,
                        fontFamily: 'Cairo',
                        fontWeight: FontWeight.normal,
                      ),
                    )
                  : isLatestMessage
                      ? TypeWriter(
                          controller: TypeWriterController(
                            text: message.text,
                            duration: const Duration(milliseconds: 5),
                          ),
                          builder: (context, value) {
                            return Text(
                              value.text,
                              style: const TextStyle(
                                color: Colors.black,
                                fontSize: 14,
                                fontFamily: 'Cairo',
                                fontWeight: FontWeight.normal,
                              ),
                            );
                          },
                        )
                      : Text(
                          message.text,
                          style: const TextStyle(
                            color: Colors.black,
                            fontSize: 15,
                            fontFamily: 'Cairo',
                            fontWeight: FontWeight.normal,
                          ),
                        ),
            ),
          ),
          if (message.isMe) const SizedBox(width: 6),
          if (message.isMe)
            CircleAvatar(
              backgroundImage: AssetImage(imagePath),
            ),
        ],
      ),
    );
  }

//! KEYBOARD STYLE HERE //!
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [
                Color(0xFFFFC061),
                Color(0xFFFFFFFF),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Column(
            children: <Widget>[
              if (!_userSentMessage) _buildWelcomeMessage(),
              Expanded(
                child: ListView.builder(
                  reverse: true,
                  itemCount: _messages.length,
                  itemBuilder: (BuildContext context, int index) {
                    bool isLatestMessage = index == 0;
                    return _buildMessage(_messages[index], isLatestMessage);
                  },
                ),
              ),
              Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.white,
                      Colors.orange,
                    ],
                    begin: Alignment.topRight,
                    end: Alignment.bottomCenter,
                  ),
                ),
                child: const Divider(height: 4.0),
              ),
              Container(
                decoration: BoxDecoration(color: Theme.of(context).cardColor),
                child: Row(
                  children: <Widget>[
                    Expanded(
                      child: TextField(
                        style: const TextStyle(
                          color: Colors.deepOrange,
                          fontSize: 16,
                        ),
                        controller: _textEditingController,
                        decoration: InputDecoration(
                          contentPadding: const EdgeInsets.all(20.0),
                          hintText: "Say Hi $_firstName ...",
                          border: InputBorder.none,
                        ),
                        inputFormatters: [
                          TextInputFormatter.withFunction((oldValue, newValue) {
                            if (newValue.text.isEmpty ||
                                newValue.text[0] != ' ') {
                              return newValue;
                            }
                            return oldValue;
                          }),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: onSendMessage,
                      icon: Icon(
                        Icons.rocket_launch,
                        color: Colors.orange[700],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeMessage() {
    if (!_userSentMessage && _textEditingController.text.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(5),
        decoration: BoxDecoration(
          color: Colors.orange[100],
          border: Border.all(color: Colors.orange[300]!),
        ),
        child: Row(
          children: [
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                "Hello $_firstName, I'm here to help you. You can ask me anything about وَصّلْتِك.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.orange[900],
                  fontSize: 16,
                  fontFamily: 'Cario',
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            Lottie.asset(
              'assets/animation/like1.json',
              fit: BoxFit.fitWidth,
              height: 50,
            ),
          ],
        ),
      );
    } else {
      return const SizedBox();
    }
  }
}

class Message {
  final String text;
  final bool isMe;
  Message({required this.text, required this.isMe});
}

class APIKey {
  static final apikey = dotenv.env['OPENAI_API_KEY'];
}
