from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cnic: str = Field(pattern=r"^\d{13}$", description="13-digit CNIC")
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, description="Email is optional")
    phone: str = Field(min_length=10, max_length=15)
    age: int = Field(ge=1, le=125)
    father_name: str = Field(min_length=3, max_length=50, alias="fatherName")
    address: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=2, max_length=50)
    initial_balance: float = Field(ge=0, alias="initialBal")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")


class Account(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    account_num: int = Field(ge=1, alias="accountNum")
    user_id: int = Field(ge=1, alias="userId")
    account_type: str = Field(default="savings", alias="accountType")
    balance: float = Field(default=0, ge=0)
    currency: str = Field(default="PKR", min_length=3, max_length=3)
    is_active: bool = Field(default=True, alias="isActive")
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
