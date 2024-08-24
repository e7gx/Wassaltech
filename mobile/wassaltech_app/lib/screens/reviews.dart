import 'package:flutter/material.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'package:intl/intl.dart';
import 'package:wassaltech_app/screens/review_detail_page.dart';
import 'package:wassaltech_app/widgets/components.dart';

class ReviewsPage extends StatefulWidget {
  const ReviewsPage({super.key});

  @override
  _ReviewsPageState createState() => _ReviewsPageState();
}

class _ReviewsPageState extends State<ReviewsPage> {
  late Future<List<Review>> _futureReviews;

  @override
  void initState() {
    super.initState();
    _futureReviews = ReviewService().fetchAllReviews();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Reviews',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontFamily: 'Cairo',
            fontWeight: FontWeight.bold,
            fontSize: 24,
            color: Colors.white,
          ),
        ),
        backgroundColor: Colors.orange,
      ),
      body: Stack(
        children: [
          stackBacground(),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: FutureBuilder<List<Review>>(
              future: _futureReviews,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return Center(
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.orange),
                    ),
                  );
                } else if (snapshot.hasError) {
                  return Center(
                    child: Text(
                      'Error: ${snapshot.error}',
                      style: TextStyle(color: Colors.redAccent),
                    ),
                  );
                } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return Center(
                    child: Text(
                      'No reviews available',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  );
                } else {
                  final reviews = snapshot.data!;
                  final DateFormat dateFormat =
                      DateFormat('yyyy-MM-dd – kk:mm');

                  return ListView.builder(
                    padding: const EdgeInsets.all(8.0),
                    itemCount: reviews.length,
                    itemBuilder: (context, index) {
                      final review = reviews[index];
                      final String formattedDate =
                          dateFormat.format(review.createdAt);

                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 8.0),
                        elevation: 3,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12.0),
                        ),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16.0),
                          leading: CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.orange,
                            child: Icon(
                              Icons.star,
                              color: Colors.white,
                              size: 24,
                            ),
                          ),
                          title: Text(
                            '${review.rating} Stars',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                              color: Colors.orange.shade700,
                            ),
                          ),
                          subtitle: Text(
                            formattedDate,
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[800],
                            ),
                          ),
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) =>
                                    ReviewDetailPage(review: review),
                              ),
                            );
                          },
                        ),
                      );
                    },
                  );
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}
