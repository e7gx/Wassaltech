import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:google_nav_bar/google_nav_bar.dart';
// import 'package:lottie/lottie.dart';
import 'package:wassaltech_app/auth/login.dart';
import 'package:wassaltech_app/chat/chat.dart';
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'package:wassaltech_app/model/service/shared_preferences_service.dart';
import 'package:wassaltech_app/screens/order_offers_chart.dart';
import 'package:wassaltech_app/screens/reviews.dart';
import 'package:wassaltech_app/screens/users_dashboard.dart';
// import 'package:wassaltech_app/screens/verify_freelancer_screen.dart';
import 'package:wassaltech_app/screens/wassalthech_wallet.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  double _totalPrice = 0.0;
  int _selectedIndex = 0;
  String _firstName = '';

  Future<void> _loadUserData() async {
    final firstName = await SharedPreferencesService.getFirstName();
    setState(() {
      _firstName = firstName;
    });
  }

  @override
  void initState() {
    super.initState();
    _startPolling();
    _loadUserData();
  }

  void _startPolling() {
    Timer.periodic(const Duration(seconds: 1000), (Timer timer) {
      setState(() {});
    });
  }

  Future<List<Offer>> fetchOffers() async {
    final response =
        await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/'));
    if (response.statusCode == 200) {
      final List<dynamic> offersList = json.decode(response.body);
      final List<Offer> offers =
          offersList.map((json) => Offer.fromJson(json)).toList();
      _calculateTotals(offers);
      return offers;
    } else {
      throw Exception('Failed to load offers');
    }
  }

  void _calculateTotals(List<Offer> offers) {
    setState(() {
      _totalPrice = offers.fold(0.0, (sum, offer) {
        double offerPrice = double.tryParse(offer.price) ?? 0.0;
        return sum + offerPrice;
      });
    });
  }

  void _onTabChange(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> pages = [
      Wallet(
        offers: [],
        offersFuture: fetchAllOffers(),
        totalPrice: _totalPrice,
      ),
      const OffersOrdersPage(),
      const UsersPage(),
      const AiChatPage(),
    ];

    return Scaffold(
      endDrawer: _buildDrawer(),
      appBar: _buildAppBar(),
      body: pages[_selectedIndex],
      bottomNavigationBar: _buildBottomNavigationBar(),
    );
  }

  AppBar _buildAppBar() {
    return AppBar(
      backgroundColor: Colors.transparent,
      elevation: 0,
      title: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          CircleAvatar(
            backgroundImage: AssetImage('assets/images/test.png'),
            radius: 22,
            backgroundColor: Colors.transparent,
          ),
          const SizedBox(width: 8),
          Text(
            'Welcome $_firstName 👋',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontFamily: 'Cairo',
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade800,
              fontSize: 20.0,
            ),
          ),
        ],
      ),
      iconTheme: IconThemeData(
        color: Colors.black,
      ),
    );
  }

  Drawer _buildDrawer() {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          DrawerHeader(
            decoration: BoxDecoration(
              color: Colors.orange,
            ),
            child: Column(
              children: [
                Image.asset(
                  'assets/images/Wassaltech.png',
                  height: 80,
                ),
                SizedBox(height: 8),
                Text(
                  'WassalTech | وَصّلْتِك',
                  style: TextStyle(
                    fontFamily: 'Cairo',
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontSize: 27,
                  ),
                ),
              ],
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
          _buildDrawerItem(
            'Offers',
            0,
            Icon(
              Icons.date_range_sharp,
              color: Colors.orange,
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
          _buildDrawerItem(
            'Orders',
            1,
            Icon(
              Icons.shopping_cart,
              color: Colors.orange,
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
          ListTile(
            title: Text(
              'Reviews',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                fontSize: 24,
                color: Colors.orange,
              ),
            ),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ReviewsPage(),
                ),
              );
            },
            leading: Icon(
              Icons.rate_review_sharp,
              color: Colors.orange,
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
          _buildDrawerItem(
            'Chat',
            3,
            Icon(
              Icons.memory,
              color: Colors.orange,
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
          ListTile(
            onTap: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(
                  builder: (context) => const LoginPage(),
                ),
              );
            },
            leading: Icon(
              Icons.logout,
              color: Colors.red,
            ),
            title: Text(
              'Logout',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                fontSize: 24,
                color: Colors.orange,
              ),
            ),
          ),
          Divider(
            color: Colors.grey.shade100,
            thickness: 12,
          ),
        ],
      ),
    );
  }

  ListTile _buildDrawerItem(String title, int index, Icon icon) {
    return ListTile(
      title: Text(
        title,
        textAlign: TextAlign.center,
        style: TextStyle(
          fontFamily: 'Cairo',
          fontWeight: FontWeight.bold,
          fontSize: 24,
          color: Colors.orange,
        ),
      ),
      leading: icon,
      onTap: () {
        if (index == -1) {
        } else {
          setState(() {
            _selectedIndex = index;
          });
          Navigator.pop(context);
        }
      },
    );
  }

  Container _buildBottomNavigationBar() {
    return Container(
      color: Colors.orange.shade500,
      child: Padding(
        padding:
            const EdgeInsets.only(bottom: 40, left: 30, right: 30, top: 16),
        child: GNav(
          backgroundColor: Colors.transparent,
          tabBackgroundColor: Colors.white,
          tabBorderRadius: 50,
          padding: const EdgeInsets.all(10),
          gap: 8,
          selectedIndex: _selectedIndex,
          onTabChange: _onTabChange,
          tabs: const [
            GButton(
              icon: Icons.insert_chart_rounded,
              text: 'Offers',
              iconColor: Colors.white,
              iconActiveColor: Colors.orangeAccent,
              textStyle: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            GButton(
              icon: Icons.shopping_cart,
              text: 'Orders',
              iconColor: Colors.white,
              iconActiveColor: Colors.orangeAccent,
              textStyle: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            GButton(
              icon: Icons.people,
              text: 'Users',
              iconColor: Colors.white,
              iconActiveColor: Colors.orangeAccent,
              textStyle: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
            GButton(
              icon: Icons.memory,
              text: 'Chat',
              iconColor: Colors.white,
              iconActiveColor: Colors.orangeAccent,
              textStyle: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                color: Colors.brown,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
