class Review {
  final int id;
  final double rating;
  final String comment;
  final DateTime createdAt;

  Review({
    required this.id,
    required this.rating,
    required this.comment,
    required this.createdAt,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'],
      rating: json['rating'].toDouble(),
      comment: json['comment'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
