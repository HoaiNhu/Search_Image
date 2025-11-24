"""
Product model representing the MongoDB product schema.
"""
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class Product(BaseModel):
    """Product model matching MongoDB schema."""
    id: Optional[str] = Field(None, alias="_id")
    productName: str
    productPrice: float
    productImage: str
    productCategory: Optional[Union[str, Dict[str, Any], ObjectId]] = None
    productSize: Optional[float] = None
    productDescription: Optional[str] = None
    averageRating: Optional[float] = None
    totalRatings: Optional[int] = None
    createdAt: Optional[Union[datetime, Dict[str, Any]]] = None
    updatedAt: Optional[Union[datetime, Dict[str, Any]]] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        """Convert ObjectId to string for id field."""
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    @field_validator('productCategory', mode='before')
    @classmethod
    def convert_category(cls, v):
        """Convert ObjectId or dict to string for category."""
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, dict) and '$oid' in v:
            return v['$oid']
        return v
    
    @field_validator('createdAt', 'updatedAt', mode='before')
    @classmethod
    def convert_datetime(cls, v):
        """Convert datetime or dict to datetime object."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, dict) and '$date' in v:
            return datetime.fromisoformat(v['$date'].replace('Z', '+00:00'))
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            ObjectId: lambda v: str(v)
        }


class SearchResult(BaseModel):
    """Search result model with similarity score."""
    product: Product
    similarity_score: float
    rank: int
    
    class Config:
        populate_by_name = True
