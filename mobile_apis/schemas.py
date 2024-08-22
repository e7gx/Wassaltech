from ninja import Schema
from datetime import datetime
from decimal import Decimal

# class OrderSchema(Schema):
#     id: int
#     customer_id: int
#     assigned_to_id: int = None
#     category: str
#     issue_description: str
#     created_at: datetime
#     updated_at: datetime
#     freelancer_completed: bool
#     customer_completed: bool
#     status: str

class OfferSchema(Schema):
    id: int
    order_id: int
    freelancer_id: int
    price: Decimal
    refund: Decimal
    complete_on_time: bool
    description: str
    proposed_service_date: datetime
    appointment: datetime
    stage: str
    updated_at: datetime
    created_at: datetime

class LoginSchema(Schema):
    username: str
    password: str
    
class AuthResponseSchema(Schema):
    message: str
    username: str
