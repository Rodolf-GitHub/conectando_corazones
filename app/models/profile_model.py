from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel

class Profile(BaseModel):
    __tablename__ = "profiles"
    
    # Campos obligatorios
    name = Column(String(100), nullable=False)
    
    # Campos opcionales
    cover_image = Column(String(255), nullable=True)
    image_1 = Column(String(255), nullable=True)
    image_2 = Column(String(255), nullable=True)
    image_3 = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    whatsapp_link = Column(String(255), nullable=True)
    facebook_link = Column(String(255), nullable=True)
    
    # Relación con el usuario
    user_id = Column(String(32), ForeignKey('users.id'), unique=True)
    user = relationship("User", back_populates="profile") 