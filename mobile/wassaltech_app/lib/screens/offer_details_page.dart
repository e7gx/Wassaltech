import 'package:flutter/material.dart';
import 'package:wassaltech_app/model/service/api_services.dart';
import 'package:intl/intl.dart';

class OfferDetailsPage extends StatelessWidget {
  final Offer offer;

  const OfferDetailsPage({Key? key, required this.offer}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Offer Details',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            fontFamily: 'Cairo',
          ),
        ),
        backgroundColor: Colors.orange,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Container(
              width: double.infinity,
              height: 200.0,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15.0),
                image: DecorationImage(
                  image: AssetImage('assets/images/user2.png'),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(height: 16.0), // Add spacing
            _buildDetailCard('Offer ID', offer.id.toString()),
            _buildDetailCard('Order ID', offer.orderId.toString()),
            _buildDetailCard('Freelancer ID', offer.freelancerId.toString()),
            _buildDetailCard('Price', '\$${offer.price.toStringAsFixed(2)}'),
            _buildDetailCard('Refund', '\$${offer.refund.toStringAsFixed(2)}'),
            _buildDetailCard(
                'Complete On Time', offer.completeOnTime ? 'Yes' : 'No'),
            _buildDetailCard('Description', offer.description),
            _buildDetailCard('Proposed Service Date',
                _formatDate(offer.proposedServiceDate)),
            _buildDetailCard('Appointment', _formatDate(offer.appointment)),
            _buildDetailCard('Stage', offer.stage),
            _buildDetailCard('Created At', _formatDate(offer.createdAt)),
            _buildDetailCard('Updated At', _formatDate(offer.updatedAt)),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailCard(String title, String value) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.0),
      ),
      elevation: 4.0,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16.0),
        title: Text(
          title,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.orange[800],
            fontFamily: 'Cairo',
          ),
        ),
        subtitle: Text(
          value,
          style: TextStyle(
            fontSize: 16,
            color: Colors.black87,
            fontFamily: 'Cairo',
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dateTime) {
    final formatter = DateFormat('MMM dd, yyyy');
    return formatter.format(dateTime.toLocal());
  }
}
