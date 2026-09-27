from pydantic import BaseModel, EmailStr, Field
from typing import Any, Literal

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=120)
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]

class BudgetBase(BaseModel):
    total_budget: float = Field(gt=0, le=10_000_000)
    additional_requirements: str | None = Field(default="", max_length=1000)

class HomeBudgetInput(BudgetBase):
    num_lights: int = Field(default=2, ge=0, le=50)
    num_fans: int = Field(default=2, ge=0, le=50)
    num_furniture: int = Field(default=2, ge=0, le=50)
    num_dining_tables: int = Field(default=1, ge=0, le=10)
    has_living_room: bool = True
    has_kitchen: bool = False
    has_bedroom: bool = True

class PartyBudgetInput(BudgetBase):
    guest_count: int = Field(default=10, ge=1, le=1000)
    event_type: str = Field(default="Birthday", min_length=2, max_length=80)
    venue_required: bool = True
    food_required: bool = True
    decoration_required: bool = True
    photography_required: bool = False

class JewelryBudgetInput(BudgetBase):
    occasion: str = Field(default="Casual", min_length=2, max_length=80)
    jewelry_type: str = Field(default="Earrings", min_length=2, max_length=80)
    material_preference: str = Field(default="Fashion jewellery", max_length=80)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

class RecommendationOut(BaseModel):
    id: int
    recommendation_type: str
    title: str
    input_summary: str
    result: dict[str, Any]
    created_at: str
