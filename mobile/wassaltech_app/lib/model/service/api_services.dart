import 'dart:convert';
import 'package:http/http.dart' as http;

class Order {
  final int id;
  final int customerId;
  final int? assignedToId;
  final String category;
  final String issueDescription;
  final DateTime createdAt;
  final DateTime updatedAt;
  final bool freelancerCompleted;
  final bool customerCompleted;
  final String status;

  Order({
    required this.id,
    required this.customerId,
    this.assignedToId,
    required this.category,
    required this.issueDescription,
    required this.createdAt,
    required this.updatedAt,
    required this.freelancerCompleted,
    required this.customerCompleted,
    required this.status,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      customerId: json['customer_id'],
      assignedToId: json['assigned_to_id'],
      category: json['category'],
      issueDescription: json['issue_description'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      freelancerCompleted: json['freelancer_completed'],
      customerCompleted: json['customer_completed'],
      status: json['status'],
    );
  }
}

class Offer {
  final int id;
  final int orderId;
  final int freelancerId;
  final double price;
  final double refund;
  final bool completeOnTime;
  final String description;
  final DateTime proposedServiceDate;
  final DateTime appointment;
  final String stage;
  final DateTime createdAt;
  final DateTime updatedAt;

  Offer({
    required this.id,
    required this.orderId,
    required this.freelancerId,
    required this.price,
    required this.refund,
    required this.completeOnTime,
    required this.description,
    required this.proposedServiceDate,
    required this.appointment,
    required this.stage,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Offer.fromJson(Map<String, dynamic> json) {
    return Offer(
      id: json['id'],
      orderId: json['order_id'],
      freelancerId: json['freelancer_id'],
      price: double.tryParse(json['price']) ?? 0.0,
      refund: double.tryParse(json['refund']) ?? 0.0,
      completeOnTime: json['complete_on_time'],
      description: json['description'],
      proposedServiceDate: DateTime.parse(json['proposed_service_date']),
      appointment: DateTime.parse(json['appointment']),
      stage: json['stage'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

Future<List<Offer>> fetchOffers() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/'));

  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Offer.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load offers');
  }
}

Future<int> fetchUserCount() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/users/count'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return data['user_count'] as int;
  } else {
    throw Exception('Failed to load user count');
  }
}

Future<int> fetchFreelancerCount() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/freelancers/count'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return data['freelancer_count'] as int;
  } else {
    throw Exception('Failed to load freelancer count');
  }
}

Future<int> fetchOffersCount() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/count/'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return data['offer_count'] as int;
  } else {
    throw Exception('Failed to load user count');
  }
}

Future<int> fetchOrdersCount() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/orders/count/'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    return data['order_count'] as int;
  } else {
    throw Exception('Failed to load freelancer count');
  }
}

class ApiService {
  final String baseUrl = "http://127.0.0.1:8000/api";

  Future<Map<String, dynamic>?> loginUser(
      String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to login');
    }
  }
}
