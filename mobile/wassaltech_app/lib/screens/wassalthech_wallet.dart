import 'package:flutter/material.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'offer_details_page.dart';

class Wallet extends StatefulWidget {
  final Future<List<Offer>> offersFuture;
  final int offerCount;
  final double totalPrice;

  Wallet({
    super.key,
    required this.offersFuture,
    required this.offerCount,
    required this.totalPrice,
  });

  @override
  _WalletState createState() => _WalletState();
}

class _WalletState extends State<Wallet> {
  late Future<int> _ordersCountFuture;
  late Future<int> _reviewsCountFuture;

  @override
  void initState() {
    super.initState();
    _ordersCountFuture = fetchOrdersCount();
    _reviewsCountFuture = fetchReviewsCount();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 16.0),
            Text(
              'Orders & Offers',
              style: TextStyle(
                fontFamily: 'Cairo',
                fontWeight: FontWeight.bold,
                color: Colors.orange[800],
                fontSize: 28.0,
              ),
            ),
            _buildOffersRow(context),
            FutureBuilder<int>(
              future: _ordersCountFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(
                    child:
                        CircularProgressIndicator(color: Colors.orangeAccent),
                  );
                } else if (snapshot.hasError) {
                  return Center(child: Text('Error: ${snapshot.error}'));
                } else {
                  final ordersCount = snapshot.data!;
                  return FutureBuilder<int>(
                    future: _reviewsCountFuture,
                    builder: (context, reviewsSnapshot) {
                      if (reviewsSnapshot.connectionState ==
                          ConnectionState.waiting) {
                        return const Center(
                          child: CircularProgressIndicator(
                              color: Colors.orangeAccent),
                        );
                      } else if (reviewsSnapshot.hasError) {
                        return Center(
                            child: Text('Error: ${reviewsSnapshot.error}'));
                      } else {
                        final reviewsCount = reviewsSnapshot.data!;
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 16.0),
                            Text(
                              'Summary',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.bold,
                                color: Colors.orange[800],
                              ),
                            ),
                            const SizedBox(height: 16.0),
                            _buildSummaryCard(ordersCount, reviewsCount)
                          ],
                        );
                      }
                    },
                  );
                }
              },
            ),
            const SizedBox(height: 16.0),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard(int ordersCount, int reviewsCount) {
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
            const SizedBox(height: 16.0),
            _buildSummaryTile(
              'Wassaltech Wallet',
              '\SAR: ${widget.totalPrice.toStringAsFixed(2)}',
              Icon(
                Icons.account_balance_wallet,
                color: Colors.orange[800],
                size: 24.0,
              ),
            ),
            const SizedBox(height: 8.0),
            _buildSummaryTile(
              'Total Offers',
              'Count: ${widget.offerCount}',
              Icon(
                Icons.local_offer,
                color: Colors.orange[800],
                size: 24.0,
              ),
            ),
            const SizedBox(height: 8.0),
            _buildSummaryTile(
              'Total Orders',
              'Count: $ordersCount',
              Icon(
                Icons.shopping_cart,
                color: Colors.orange[800],
                size: 24.0,
              ),
            ),
            const SizedBox(height: 8.0),
            _buildSummaryTile(
              'Average Reviews',
              'Rating: ${reviewsCount.toStringAsFixed(1)}',
              Icon(
                Icons.star,
                color: Colors.orange[800],
                size: 24.0,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOffersRow(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: FutureBuilder<List<Offer>>(
        future: widget.offersFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(
                color: Colors.orangeAccent,
              ),
            );
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else {
            final offers = snapshot.data!;
            return SizedBox(
              height: 200,
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
          }
        },
      ),
    );
  }

  Widget _buildOfferCard(Offer offer) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Container(
        width: 338,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(15.0),
          gradient: const LinearGradient(
            colors: [Colors.orange, Colors.orangeAccent],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Stack(
          children: [
            Center(
              child: Opacity(
                opacity: 0.5,
                child: Image.asset(
                  'assets/images/user2.png',
                  fit: BoxFit.fill,
                  width: double.infinity,
                  height: double.infinity,
                ),
              ),
            ),
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15.0),
                color: Colors.orange.withOpacity(0.3),
              ),
            ),
            // Icon at the Top
            Positioned(
              top: 8.0,
              left: 8.0,
              child: Container(
                child: Image.asset(
                  'assets/images/hhh.png',
                  width: 100,
                  height: 100,
                  fit: BoxFit.contain,
                ),
              ),
            ),
            Positioned(
              bottom: 0.0,
              left: 16.0,
              right: 16.0,
              child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Order ID: ${offer.orderId}',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'Cairo',
                          ),
                        ),
                        Text(
                          'Price: \$${offer.price.toStringAsFixed(2)}',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'Cairo',
                          ),
                        ),
                      ],
                    ),
                    ElevatedButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) =>
                                OfferDetailsPage(offer: offer),
                          ),
                        );
                      },
                      iconAlignment: IconAlignment.end,
                      child: Text(
                        'View Details',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[800],
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(
                          vertical: 9.0,
                          horizontal: 26.0,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8.0),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryTile(String title, String subtitle, Icon icon) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12.0),
        boxShadow: [
          BoxShadow(
            color: Colors.orange.withOpacity(0.99),
            spreadRadius: 2,
            blurRadius: 8,
            offset: const Offset(0, 2),
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
            icon.icon,
            color: Colors.orange[800],
            size: 24.0,
          ),
        ],
      ),
    );
  }
}
