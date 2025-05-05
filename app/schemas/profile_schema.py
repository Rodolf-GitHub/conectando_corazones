from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class ProfileBase(BaseModel):
    name: str
    cover_image: Optional[str] = None
    image_1: Optional[str] = None
    image_2: Optional[str] = None
    image_3: Optional[str] = None
    description: Optional[str] = None
    whatsapp_link: Optional[str] = None
    facebook_link: Optional[str] = None

class AllProfilesResponse(BaseModel):
    id: str
    name: str
    cover_image: Optional[str] = None
    

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    name: Optional[str] = None

class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 