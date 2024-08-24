from django.http import JsonResponse
from ninja import NinjaAPI
from typing import Dict, List
from accounts.models import Account, Freelancer
from orders.models import Order, Offer
from reviews.models import Review
from django.db.models import Avg
from .schemas import AuthResponseSchema, OfferSchema,LoginSchema, ReviewSchema
from django.contrib.auth import authenticate

api = NinjaAPI()

@api.post("/login/", response=AuthResponseSchema)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    
    if user is None:
        return JsonResponse({"message": "Invalid credentials"}, status=401)

    try:
        account = Account.objects.get(user=user)
    except Account.DoesNotExist:
        return JsonResponse({"message": "Account does not exist"}, status=404)

    if account.user_type != 'Admin' or not user.is_superuser:
        return JsonResponse({"message": "Unauthorized access"}, status=403)
    
    return JsonResponse({"message": "Login successful", "username": user.username})


@api.get("/offers/", response=List[OfferSchema])
def list_offers(request):
    return Offer.objects.filter(stage="Accepted", order__status="Completed").all()


@api.get("/users/count", response=Dict[str, int])
def get_user_count(request):
    user_count = Account.objects.count()
    return {"user_count": user_count}

@api.get("/freelancers/count", response=Dict[str, int])
def get_freelancer_count(request):
    freelancer_count = Freelancer.objects.count()
    return {"freelancer_count": freelancer_count}


@api.get("/offers/count/", response=Dict[str, int])
def get_offer_count(request):
    offer_count = Offer.objects.count()
    return {"offer_count": offer_count}

@api.get("/orders/count/", response=Dict[str, int])
def get_order_count(request):
    order_count = Order.objects.count()
    return {"order_count": order_count}


@api.get("/reviews/rating_avg/", response=Dict[str, int])
def get_reviews_count(request):
    rating_avg = Review.objects.aggregate(Avg('rating'))['rating__avg']
    return {"rating_avg": rating_avg}


@api.get("/reviews/all/", response=Dict[str, List[ReviewSchema]])
def get_reviews_all(request):
    reviews = Review.objects.order_by('-id')[:25]
    reviews_data = [ReviewSchema.from_orm(review) for review in reviews]
    return {"reviews": reviews_data}


# @api.put("/freelancers/{freelancer_id}/verify/", response=FreelancerSchema)
# def verify_freelancer(request, freelancer_id: int, data: VerifyFreelancerSchema):
#     freelancer = get_object_or_404(Freelancer, id=freelancer_id)
#     freelancer.is_verified = data.is_verified
#     freelancer.save()
    
#     account = Account.objects.get(user=freelancer.user)
    
#     return FreelancerSchema(
#         id=freelancer.id,
#         username=freelancer.user.username,
#         first_name=freelancer.user.first_name,
#         last_name=freelancer.user.last_name,
#         email=freelancer.user.email,
#         phone_number=account.phone_number,
#         address=account.address,
#         certificate_id=freelancer.certificate_id,
#         certificate_expiration=freelancer.certificate_expiration,
#         internal_rating=freelancer.internal_rating,
#         is_verified=freelancer.is_verified,
#         created_at=account.created_at
#     )
