from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    id: int
    email: EmailStr
    name: str

    model_config = {"from_attributes": True}

    @field_validator("id")
    def id_positive(cls, v):
        if v <= 0:
            raise ValueError("1以上の値を入力してください")
        return v

    @field_validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("名前を入力してください")
        return v
