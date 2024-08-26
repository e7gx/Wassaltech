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