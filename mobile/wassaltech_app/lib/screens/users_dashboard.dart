import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:wassaltech_app/model/service/api_services.dart';

class UsersPage extends StatefulWidget {
  const UsersPage({super.key});

  @override
  State<UsersPage> createState() => _UsersPageState();
}

class _UsersPageState extends State<UsersPage> {
  late Future<int> _userCountFuture;
  late Future<int> _freelancerCountFuture;

  @override
  void initState() {
    super.initState();
    _userCountFuture = fetchUserCount();
    _freelancerCountFuture = fetchFreelancerCount();
    _startPolling();
  }

  void _startPolling() {
    Timer.periodic(const Duration(seconds: 900), (Timer timer) {
      setState(() {
        _userCountFuture = fetchUserCount();
        _freelancerCountFuture = fetchFreelancerCount();
      });
    });
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
        child: FutureBuilder<List<int>>(
          future: Future.wait([
            _userCountFuture,
            _freelancerCountFuture,
          ]),
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              final userCount = snapshot.data![0];
              final freelancerCount = snapshot.data![1];
              final totalCount = userCount + freelancerCount;

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
                            color: const Color(0xFFFFA500),
                            value: userCount.toDouble(),
                            title:
                                '$userCount (${(userCount / totalCount * 100).toStringAsFixed(0)}%)',
                            radius: radius,
                            titleStyle: TextStyle(
                              fontSize: fontSize,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          PieChartSectionData(
                            color: const Color(0xFF5E4F24),
                            value: freelancerCount.toDouble(),
                            title:
                                '$freelancerCount (${(freelancerCount / totalCount * 100).toStringAsFixed(0)}%)',
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
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.person,
                            color: Color(0xFFFFA500),
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Total Customers: ',
                            style: TextStyle(
                              color: Color(0xFFFFA500),
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          ),
                          Text(
                            '$userCount',
                            style: const TextStyle(
                              color: Color(0xFFFFA500),
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 18.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.work,
                            color: Color(0xFF5E4F24),
                          ), // Gold color
                          const SizedBox(width: 8),
                          const Text(
                            'Total Freelancers: ',
                            style: TextStyle(
                              color: Color(0xFF5E4F24),
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          ),
                          Text(
                            '$freelancerCount',
                            style: const TextStyle(
                              color: Color(0xFF5E4F24),
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          ),
                        ],
                      ),
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
