from pydantic import BaseModel
class BaseConfigModel(BaseModel):
    class Config:
        from_attributes = True