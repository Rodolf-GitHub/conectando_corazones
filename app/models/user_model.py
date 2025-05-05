from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(100))
    is_superuser = Column(Boolean, default=False)
    
    # Nueva relación con el perfil
    profile = relationship("Profile", back_populates="user", uselist=False)
    
    
   
   