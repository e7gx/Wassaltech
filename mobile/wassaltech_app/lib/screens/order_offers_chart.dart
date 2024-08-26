import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'package:wassaltech_app/screens/offer_details_page.dart';

class OffersOrdersPage extends StatefulWidget {
  const OffersOrdersPage({super.key});

  @override
  State<OffersOrdersPage> createState() => _OffersOrdersPageState();
}

class _OffersOrdersPageState extends State<OffersOrdersPage> {
  late Future<int> _offersCountFuture;
  late Future<int> _ordersCountFuture;
  late Future<List<Offer>> _offersFuture;

  @override
  void initState() {
    super.initState();
    _offersCountFuture = fetchOffersCount();
    _ordersCountFuture = fetchOrdersCount();
    _offersFuture = fetchOffers();
    _startPolling();
  }

  void _startPolling() {
    Timer.periodic(const Duration(seconds: 900), (Timer timer) {
      setState(() {
        _offersCountFuture = fetchOffersCount();
        _ordersCountFuture = fetchOrdersCount();
        _offersFuture = fetchOffers();
      });
    });
  }

  Future<int> fetchOffersCount() async {
    final response =
        await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/count/'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      return data['offer_count'] as int;
    } else {
      throw Exception('Failed to load offers count');
    }
  }

  Future<int> fetchOrdersCount() async {
    final response =
        await http.get(Uri.parse('http://127.0.0.1:8000/api/orders/count/'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      return data['order_count'] as int;
    } else {
      throw Exception('Failed to load orders count');
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    final radius = screenWidth * 0.2;
    final fontSize = screenWidth * 0.04;

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: FutureBuilder<List<dynamic>>(
          future: Future.wait([
            _offersCountFuture,
            _ordersCountFuture,
            _offersFuture,
          ]),
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              final offersCount = snapshot.data![0] as int;
              final ordersCount = snapshot.data![1] as int;
              final offers = snapshot.data![2] as List<Offer>;
              final totalCount = offersCount + ordersCount;

              return Column(
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  SizedBox(
                    height: screenHeight * 0.4,
                    width: screenWidth * 0.8,
                    child: PieChart(
                      PieChartData(
                        sections: [
                          PieChartSectionData(
                            color: Colors.orange,
                            value: offersCount.toDouble(),
                            title:
                                '${offersCount} (${(offersCount / totalCount * 100).toStringAsFixed(0)}%)',
                            radius: radius,
                            titleStyle: TextStyle(
                              fontSize: fontSize,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          PieChartSectionData(
                            color: Colors.deepOrangeAccent,
                            value: ordersCount.toDouble(),
                            title:
                                '${ordersCount} (${(ordersCount / totalCount * 100).toStringAsFixed(0)}%)',
                            radius: radius,
                            titleStyle: TextStyle(
                              fontSize: fontSize,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            badgePositionPercentageOffset: .98,
                          ),
                        ],
                        centerSpaceRadius: screenWidth * 0.15,
                        startDegreeOffset: -90,
                        sectionsSpace: 2,
                        borderData: FlBorderData(show: false),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.attach_money,
                        color: Colors.orange,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'Total Offers: ',
                        style: TextStyle(
                          color: Colors.orange,
                          fontWeight: FontWeight.bold,
                          fontSize: 24,
                        ),
                      ),
                      Text(
                        '$offersCount',
                        style: const TextStyle(
                          color: Colors.orange,
                          fontWeight: FontWeight.bold,
                          fontSize: 24,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.work, color: Colors.deepOrangeAccent),
                      const SizedBox(width: 8),
                      const Text(
                        'Total Orders: ',
                        style: TextStyle(
                          color: Colors.deepOrangeAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 24,
                        ),
                      ),
                      Text(
                        '$ordersCount',
                        style: const TextStyle(
                          color: Colors.deepOrangeAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 24,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Expanded(
                    child: ListView.builder(
                      itemCount: offers.length,
                      itemBuilder: (context, index) {
                        final offer = offers[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 8.0),
                          elevation: 4.0,
                          child: ListTile(
                            title: Text('Offer ID: ${offer.id}'),
                            subtitle: Text('Price: \$${offer.price}'),
                            trailing: Text(
                              offer.stage,
                              style: TextStyle(
                                color: offer.stage == 'Accepted'
                                    ? Colors.green
                                    : Colors.yellow,
                                fontWeight: offer.stage == 'Accepted'
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => OfferDetailsPage(
                                    offer: offer,
                                  ),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    ),
                  ),
                ],
              );
            } else if (snapshot.hasError) {
              return Center(
                child: Text('Error: ${snapshot.error}'),
              );
            } else {
              return const Center(
                child: CircularProgressIndicator(
                  color: Colors.black,
                ),
              );
            }
          },
        ),
      ),
    );
  }
}
