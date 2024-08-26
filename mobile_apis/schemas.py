from ninja import Schema
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional



class OfferSchema(Schema):
    id: int
    order_id: int
    freelancer_id: int
    price: Decimal
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

class ReviewSchema(Schema):
    id: int
    rating: float
    comment: str
    created_at: datetime
    

# class FreelancerSchema(Schema):
#     id: int
#     username: str
#     first_name: str
#     last_name: str
#     email: str
#     phone_number: str
#     address: str
#     certificate_id: str
#     certificate_expiration: Optional[datetime]
#     internal_rating: float
#     is_verified: bool
#     created_at: datetime
# class VerifyFreelancerSchema(Schema):
#     is_verified: bool

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