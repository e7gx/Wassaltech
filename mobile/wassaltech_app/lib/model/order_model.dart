// class Order {
//   final int id;
//   final int customerId;
//   final int? assignedToId;
//   final String category;
//   final String issueDescription;
//   final DateTime createdAt;
//   final DateTime updatedAt;
//   final bool freelancerCompleted;
//   final bool customerCompleted;
//   final String status;

//   Order({
//     required this.id,
//     required this.customerId,
//     this.assignedToId,
//     required this.category,
//     required this.issueDescription,
//     required this.createdAt,
//     required this.updatedAt,
//     required this.freelancerCompleted,
//     required this.customerCompleted,
//     required this.status,
//   });

//   factory Order.fromJson(Map<String, dynamic> json) {
//     return Order(
//       id: json['id'],
//       customerId: json['customer_id'],
//       assignedToId: json['assigned_to_id'],
//       category: json['category'],
//       issueDescription: json['issue_description'],
//       createdAt: DateTime.parse(json['created_at']),
//       updatedAt: DateTime.parse(json['updated_at']),
//       freelancerCompleted: json['freelancer_completed'],
//       customerCompleted: json['customer_completed'],
//       status: json['status'],
//     );
//   }
// }