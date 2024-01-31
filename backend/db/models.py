from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey, Float
from db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, select
from db.session import SessionLocal
# TODO: change Column to mapped_column


class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(160), unique=True, nullable=False)
    user_email = Column(String(40), unique=True, nullable=False)
    password = Column(String(250), nullable=False)
    balance = Column(Numeric(precision=65, scale=8), default=0)

    ratings = relationship("ProductsRating", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, password, user_email):
        self.username = username
        self.password = password
        self.user_email = user_email

    def __repr__(self):
        return f"<User(balance={self.balance})>"


class Product(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    descriptions = Column(String(160), nullable=False)
    price = Column(Float, nullable=False)
    # TODO: add file path
    ratings = relationship("ProductsRating", back_populates="product", cascade="all, delete-orphan")

    def __init__(self, name, descriptions, price):
        self.name = name
        self.descriptions = descriptions
        self.price = price

    def __repr__(self):
        return f"<Product(name={self.name})>"

    @property
    def average_rating(self):
        avg_rating = (
            select(func.avg(ProductsRating.rating)).where(ProductsRating.product_id == self.id))
        session = SessionLocal()
        data = session.execute(avg_rating).scalar()
        return data if data is not None else 0


class ProductsRating(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 0 AND rating <= 5'))

    user = relationship("User", back_populates="ratings")
    product = relationship("Product", back_populates="ratings")
