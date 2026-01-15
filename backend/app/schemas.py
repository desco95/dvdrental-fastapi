from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ============ FILMS ============
class Film(BaseModel):
    film_id: int
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    rental_rate: Decimal
    length: Optional[int] = None
    rating: Optional[str] = None
    
    class Config:
        from_attributes = True

# ============ CUSTOMERS ============
class Customer(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    active: int
    
    class Config:
        from_attributes = True

# ============ STAFF ============
class Staff(BaseModel):
    staff_id: int
    first_name: str
    last_name: str
    email: str
    active: bool
    
    class Config:
        from_attributes = True

# ============ RENTALS ============
class RentalCreate(BaseModel):
    customer_id: int = Field(..., gt=0, description="ID del cliente")
    film_id: int = Field(..., gt=0, description="ID de la película")
    staff_id: int = Field(..., gt=0, description="ID del empleado")

class RentalResponse(BaseModel):
    rental_id: int
    rental_date: datetime
    customer_id: int
    film_id: int
    staff_id: int
    return_date: Optional[datetime] = None
    film_title: Optional[str] = None
    customer_name: Optional[str] = None
    staff_name: Optional[str] = None
    rental_duration: Optional[int] = None
    expected_return_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============ REPORTS ============
class UnreturnedDVD(BaseModel):
    rental_id: int
    film_title: str
    customer_name: str
    rental_date: datetime
    expected_return_date: datetime
    days_overdue: int

class MostRentedFilm(BaseModel):
    film_id: int
    title: str
    category: Optional[str] = None
    total_rentals: int
    rental_rate: Decimal
    total_revenue: Decimal

class StaffRevenue(BaseModel):
    staff_id: int
    staff_name: str
    email: str
    total_rentals: int
    total_payments: int
    total_revenue: Decimal
    average_payment: Decimal

class CustomerRental(BaseModel):
    rental_id: int
    film_title: str
    rental_date: datetime
    return_date: Optional[datetime] = None
    payment_amount: Optional[Decimal] = None
    days_rented: Optional[int] = None

# ============ GENERIC RESPONSES ============
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: Optional[str] = None