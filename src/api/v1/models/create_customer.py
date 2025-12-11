from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class PhoneCreate(BaseModel):
    number: str = Field(..., min_length=5, max_length=32, strip_whitespace=True)
    model_config = ConfigDict(extra="forbid")


class CustomerCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=255, strip_whitespace=True)
    email: EmailStr
    phones: list[PhoneCreate] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def ensure_unique_phones(self) -> "CustomerCreate":
        numbers = [phone.number for phone in self.phones]
        if len(numbers) != len(set(numbers)):
            raise ValueError("телефоны должны быть уникальны")
        return self


class CustomerCreateResponse(BaseModel):
    success: bool
    id: int
