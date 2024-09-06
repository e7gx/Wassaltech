import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'offer_details_page.dart';

class Wallet extends StatefulWidget {
  final Future<List<Offer>> offersFuture;
  final double totalPrice;

  const Wallet({
    super.key,
    required this.offersFuture,
    required this.totalPrice,
    required List<Offer> offers,
  });

  @override
  // ignore: library_private_types_in_public_api
  _WalletState createState() => _WalletState();
}

class _WalletState extends State<Wallet> {
  late Future<int> _ordersCountFuture;
  late Future<double> _depositedAmountFuture;
  late Future<double> _reviewsCountFuture;

  @override
  void initState() {
    super.initState();
    _ordersCountFuture = fetchOrdersCount();
    _reviewsCountFuture = fetchReviewsCount();
    _depositedAmountFuture = fetchDepositedAmount();
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
                  return FutureBuilder<double>(
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
                            child: Column(
                          children: [
                            Center(
                              child: Lottie.asset(
                                'assets/animation/x.json',
                                width: 200,
                                height: 200,
                                fit: BoxFit.cover,
                              ),
                            ),
                            const Padding(
                              padding: EdgeInsets.all(8.0),
                              child: Text('Opss Something went wrong'),
                            ),
                          ],
                        ));
                      } else {
                        final reviewsCount = reviewsSnapshot.data!;
                        return FutureBuilder<double>(
                          future: _depositedAmountFuture,
                          builder: (context, depositedSnapshot) {
                            if (depositedSnapshot.connectionState ==
                                ConnectionState.waiting) {
                              return const Center(
                                child: CircularProgressIndicator(
                                    color: Colors.orangeAccent),
                              );
                            } else if (depositedSnapshot.hasError) {
                              return Center(
                                child: Lottie.asset(
                                  'assets/animation/x.json',
                                  width: 200,
                                  height: 200,
                                  fit: BoxFit.cover,
                                ),
                              );
                            } else {
                              final depositedAmount = depositedSnapshot.data!;
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 16.0),
                                  Text(
                                    'Orders & Reviews',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontFamily: 'Cairo',
                                      fontWeight: FontWeight.bold,
                                      color: Colors.orange[800],
                                      fontSize: 28.0,
                                    ),
                                  ),
                                  const SizedBox(height: 16.0),
                                  _buildSummaryCard(
                                    ordersCount,
                                    reviewsCount,
                                    depositedAmount,
                                  ),
                                ],
                              );
                            }
                          },
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

  Widget _buildSummaryCard(
      int ordersCount, double reviewsCount, double depositedAmount) {
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
              'Cash Flow ',
              'SAR: ${depositedAmount.toStringAsFixed(2)}',
              Icon(
                Icons.account_balance_wallet,
                color: Colors.orange[800],
                size: 24.0,
              ),
            ),
            _buildSummaryTile(
              'Commissions',
              'SAR: ${(depositedAmount * 0.10).toStringAsFixed(2)}',
              Icon(
                Icons.monetization_on_sharp,
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

//! 234567890234567890

  Widget _buildOffersRow(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: FutureBuilder<List<Offer>>(
        future: widget.offersFuture, // Use the passed future
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(color: Colors.orangeAccent),
            );
          } else if (snapshot.hasError) {
            return Column(
              children: [
                Center(
                  child: Lottie.asset(
                    'assets/animation/x.json',
                    width: 200,
                    height: 200,
                    fit: BoxFit.cover,
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text('Opss Something went wrong'),
                ),
              ],
            );
          } else if (snapshot.hasData && snapshot.data!.isEmpty) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Center(
                  child: Lottie.asset(
                    'assets/animation/x.json',
                    width: 200,
                    height: 200,
                    fit: BoxFit.cover,
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text('Opss Something went wrong'),
                ),
              ],
            );
          } else if (snapshot.hasData) {
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
          } else {
            return const Center(child: Text('No offers available'));
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
            Opacity(
              opacity: 0.3,
              child: Image.asset(
                'assets/images/user2.png',
                fit: BoxFit.contain,
                width: double.infinity,
                height: double.infinity,
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
              child: Image.asset(
                'assets/images/hhh.png',
                width: 100,
                height: 100,
                fit: BoxFit.contain,
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
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'Cairo',
                          ),
                        ),
                        Text(
                          'Price: \$${offer.price}',
                          style: const TextStyle(
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
                      style: ElevatedButton.styleFrom(
                        foregroundColor: Colors.orange[800],
                        backgroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          vertical: 4.0,
                          horizontal: 16.0,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8.0),
                        ),
                      ),
                      iconAlignment: IconAlignment.end,
                      child: Text(
                        'View Details',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[800],
                          fontFamily: 'Cairo',
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

  //! ttttt1234567890

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
