import 'package:flutter/material.dart';
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:intl/intl.dart';

class OfferDetailsPage extends StatelessWidget {
  final Offer offer;

  const OfferDetailsPage({super.key, required this.offer});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
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
              height: 325.0,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15.0),
                image: const DecorationImage(
                  image: AssetImage('assets/images/user2.png'),
                  fit: BoxFit.fill,
                ),
              ),
            ),
            const SizedBox(height: 16.0), 
            _buildDetailCard(
                Icons.insert_drive_file, 'Offer ID', offer.id.toString()),
            _buildDetailCard(
                Icons.card_travel, 'Order ID', offer.orderId.toString()),
            _buildDetailCard(
                Icons.person, 'Freelancer ID', offer.freelancerId.toString()),
            _buildDetailCard(Icons.attach_money, 'Price', '\$${offer.price}'),
            _buildDetailCard(Icons.check, 'Complete On Time',
                offer.completeOnTime ? 'Yes' : 'No'),
            _buildDetailCard(
                Icons.description, 'Description', offer.description),
            _buildDetailCard(Icons.calendar_today, 'Proposed Service Date',
                _formatDate(offer.proposedServiceDate)),
            _buildDetailCard(Icons.calendar_today, 'Appointment',
                _formatDate(offer.appointment)),
            _buildDetailCard(Icons.flag, 'Stage', offer.stage),
            _buildDetailCard(
                Icons.access_time, 'Created At', _formatDate(offer.createdAt)),
            _buildDetailCard(
                Icons.access_time, 'Updated At', _formatDate(offer.updatedAt)),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailCard(IconData icon, String title, String value) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12.0),
      ),
      elevation: 4.0,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16.0),
        leading: Icon(
          icon,
          color: Colors.orange[800],
        ),
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
          style: const TextStyle(
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
