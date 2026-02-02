from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    url = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="store")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=True)
    subcategory = Column(String, nullable=True)
    price = Column(Float)
    discounted_price = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    standardized_weight = Column(Float, nullable=True) # in g or ml
    url = Column(String)
    image_url = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    store_id = Column(Integer, ForeignKey("stores.id"))
    store = relationship("Store", back_populates="products")
