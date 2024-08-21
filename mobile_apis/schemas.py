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


# class AccountSchema(Schema):
#     id: int
#     user_id: int
#     user_type: str
#     created_at: datetime
#     updated_at: datetime
#     phone_number: str
#     address: str
#     city: str
#     country: str
#     zip_code: str
