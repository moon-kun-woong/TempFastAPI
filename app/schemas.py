from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    title: str = Field(..., description="아이템의 제목")
    description: Optional[str] = Field(None, description="아이템에 대한 상세 설명")
    is_active: Optional[bool] = Field(True, description="아이템 활성화 상태")
    
    model_config = {
        "extra": "forbid",
    }


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, description="업데이트할 아이템의 제목")
    description: Optional[str] = Field(None, description="업데이트할 아이템의 상세 설명")
    is_active: Optional[bool] = Field(None, description="업데이트할 아이템의 활성화 상태")
    
    model_config = {
        "extra": "forbid",
    }


class Item(ItemBase):
    id: int = Field(..., description="아이템의 고유 ID")
    created_at: datetime = Field(..., description="아이템 생성 시간")
    
    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }
