class Offer {
  final int id;
  final int orderId;
  final int freelancerId;
  final String price;
  final bool completeOnTime;
  final String description;
  final DateTime proposedServiceDate;
  final DateTime appointment;
  final String stage;
  final DateTime updatedAt;
  final DateTime createdAt;

  Offer({
    required this.id,
    required this.orderId,
    required this.freelancerId,
    required this.price,
    required this.completeOnTime,
    required this.description,
    required this.proposedServiceDate,
    required this.appointment,
    required this.stage,
    required this.updatedAt,
    required this.createdAt,
  });

  factory Offer.fromJson(Map<String, dynamic> json) {
    return Offer(
      id: json['id'],
      orderId: json['order_id'],
      freelancerId: json['freelancer_id'],
      price: json['price'], 
      completeOnTime: json['complete_on_time'],
      description: json['description'],
      proposedServiceDate: DateTime.parse(json['proposed_service_date']),
      appointment: DateTime.parse(json['appointment']),
      stage: json['stage'],
      updatedAt: DateTime.parse(json['updated_at']),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
