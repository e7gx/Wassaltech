import 'package:flutter/material.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'offer_details_page.dart'; 

class Wallet extends StatefulWidget {
  final Future<List<Offer>> _offersFuture;
  final int _offerCount;
  final double _totalPrice;

  Wallet({
    super.key,
    required Future<List<Offer>> offersFuture,
    required int offerCount,
    required double totalPrice,
  })  : _offersFuture = offersFuture,
        _offerCount = offerCount,
        _totalPrice = totalPrice;

  @override
  _WalletState createState() => _WalletState();
}

class _WalletState extends State<Wallet> {
  late Future<int> _ordersCountFuture;

  @override
  void initState() {
    super.initState();
    _ordersCountFuture = fetchOrdersCount();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            FutureBuilder<int>(
              future: _ordersCountFuture,
              builder: (context, snapshot) {
                if (snapshot.hasData) {
                  final ordersCount = snapshot.data!;
                  return _buildSummaryCard(ordersCount);
                } else if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                } else {
                  return const Center(
                    child:
                        CircularProgressIndicator(color: Colors.orangeAccent),
                  );
                }
              },
            ),
            const SizedBox(height: 16.0),
            _buildOffersRow(context),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard(int ordersCount) {
    return Card(
      elevation: 4.0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16.0),
      ),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSummaryTile('Wassaltech Wallet',
                '\$ SAR: ${widget._totalPrice.toStringAsFixed(2)}'),
            const SizedBox(height: 8.0),
            _buildSummaryTile('Total Offers', 'Count: ${widget._offerCount}'),
            const SizedBox(height: 8.0),
            _buildSummaryTile('Total Orders', 'Count: $ordersCount'),
          ],
        ),
      ),
    );
  }

  Widget _buildOffersRow(BuildContext context) {
    return FutureBuilder<List<Offer>>(
      future: widget._offersFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          final offers = snapshot.data!;
          return Container(
            height: 200, // Adjust height as needed
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: offers.length,
              itemBuilder: (context, index) {
                final offer = offers[index];
                return GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => OfferDetailsPage(offer: offer),
                      ),
                    );
                  },
                  child: _buildOfferCard(offer),
                );
              },
            ),
          );
        } else if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else {
          return const Center(
              child: CircularProgressIndicator(color: Colors.orangeAccent));
        }
      },
    );
  }

  Widget _buildOfferCard(Offer offer) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Container(
        width: 280, // Adjust width as needed
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(15.0),
          gradient: LinearGradient(
            colors: [
              Colors.orange,
              Colors.deepOrangeAccent,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Stack(
          children: [
            Center(
              child: Opacity(
                opacity: 0.4,
                child: Image.asset(
                  'assets/images/user2.png',
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Icon(
              Icons.attach_money,
              size: 60.0,
              color: Colors.white,
            ),
            Positioned(
              bottom: 20.0,
              left: 16.0,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Offer ID: ${offer.id}',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'Cairo',
                    ),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    'Price: \$${offer.price.toStringAsFixed(2)}',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'Cairo',
                    ),
                  ),
                  const SizedBox(height: 20.0),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryTile(String title, String subtitle) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            spreadRadius: 2,
            blurRadius: 8,
            offset: Offset(0, 2), 
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.deepOrangeAccent[700],
                ),
              ),
              const SizedBox(height: 4.0),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.teal.shade800,
                ),
              ),
            ],
          ),
          Icon(
            Icons.monetization_on,
            color: Colors.orange[800],
            size: 24.0,
          ),
        ],
      ),
    );
  }
}
