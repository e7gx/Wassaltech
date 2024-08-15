from django.db import models

class Review(models.Model):  # Corrected the typo here
    class RatingChoices(models.IntegerChoices):
        ONE = 1, '1 Star'
        TWO = 2, '2 Stars'
        THREE = 3, '3 Stars'
        FOUR = 4, '4 Stars'
        FIVE = 5, '5 Stars'
    
    # offer = models.OneToOneField(Order, on_delete=models.CASCADE) 
    rating = models.IntegerField(choices=RatingChoices.choices)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Adjust the __str__ method based on actual fields
        return f"{self.offer} | {self.rating} Stars"

