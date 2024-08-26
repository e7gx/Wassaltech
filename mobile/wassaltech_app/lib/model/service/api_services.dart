import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:wassaltech_app/model/offer_model.dart';
import 'package:wassaltech_app/model/reviews_model.dart';

Future<List<Offer>> fetchOffers() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/offers/'));

  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    print('API Response Data: $data');
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

Future<double> fetchDepositedAmount() async {
  final response =
      await http.get(Uri.parse('http://127.0.0.1:8000/api/amount/'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    // Convert the string to double
    return double.parse(data['total_amount'] as String);
  } else {
    throw Exception('Failed to load deposited amount');
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

Future<double> fetchReviewsCount() async {
  final response = await http
      .get(Uri.parse('http://127.0.0.1:8000/api/reviews/rating_avg/'));

  if (response.statusCode == 200) {
    final Map<String, dynamic> data = json.decode(response.body);
    print('Received data: $data');
    final ratingAvg = data['rating_avg'];
    print('Type of rating_avg: ${ratingAvg.runtimeType}');
    if (ratingAvg is num) {
      return ratingAvg.toDouble();
    } else if (ratingAvg is String) {
      return double.parse(ratingAvg);
    } else {
      throw Exception('Unexpected type for rating_avg');
    }
  } else {
    throw Exception('Failed to load reviews count');
  }
}

Future<double> fetchReviewsAverage() async {
  try {
    final response = await http
        .get(Uri.parse('http://127.0.0.1:8000/api/reviews/rating_avg/'));

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      print('API Response Data: $data');
      return (data['rating_avg'] as num).toDouble();
    } else {
      throw Exception('Failed to load reviews average');
    }
  } catch (e) {
    print('Error: $e');
    return 0.0;
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

class ReviewService {
  static const String baseUrl = 'http://127.0.0.1:8000/api';

  Future<List<Review>> fetchAllReviews() async {
    final response = await http.get(Uri.parse('$baseUrl/reviews/all/'));

    if (response.statusCode == 200) {
      final List<dynamic> reviewsJson = json.decode(response.body)['reviews'];
      return reviewsJson.map((json) => Review.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load reviews');
    }
  }
}
