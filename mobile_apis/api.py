from ninja import NinjaAPI
from typing import Dict, List
from accounts.models import Account, Freelancer
from orders.models import Order, Offer
from .schemas import OfferSchema

api = NinjaAPI()

# @api.get("/orders/", response=List[OrderSchema])
# def list_orders(request):
#     return Order.objects.all()

# @api.get("/orders/{order_id}", response=OrderSchema)
# def get_order(request, order_id: int):
#     return Order.objects.get(id=order_id)

@api.get("/offers/", response=List[OfferSchema])
def list_offers(request):
    return Offer.objects.all()

@api.get("/offers/{offer_id}", response=OfferSchema)
def get_offer(request, offer_id: int):
    return Offer.objects.get(id=offer_id)


@api.get("/users/count", response=Dict[str, int])
def get_user_count(request):
    user_count = Account.objects.count()
    return {"user_count": user_count}

@api.get("/freelancers/count", response=Dict[str, int])
def get_freelancer_count(request):
    freelancer_count = Freelancer.objects.count()
    return {"freelancer_count": freelancer_count}
