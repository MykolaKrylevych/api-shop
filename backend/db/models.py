from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey, Float
from db.base_class import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, select
from db.session import async_session
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase


# TODO: change Column to mapped_column


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(160), unique=True, nullable=False)
    email = Column(String(40), unique=True, nullable=False)
    balance = Column(Numeric(precision=65, scale=8), default=0)

    ratings = relationship("ProductsRating", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, user_email):
        self.username = username
        self.user_email = user_email

    def __repr__(self):
        return f"<User(balance={self.balance})>"


class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    description = Column(String(160), nullable=False)
    price = Column(Float, nullable=False)
    ratings = relationship("ProductsRating", back_populates="product", cascade="all, delete-orphan")
    images = relationship("Images", back_populates="product", cascade="all, delete-orphan")

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price

    def __repr__(self):
        return f"<Product(name={self.name})>"

    @property
    def average_rating(self):
        avg_rating = (
            select(func.avg(ProductsRating.rating)).where(ProductsRating.product_id == self.id))
        session = async_session()
        data = session.execute(avg_rating).scalar()
        return data if data is not None else 0

    @property
    def list_of_img(self):
        return [files.path for files in self.images]


class ProductsRating(Base):
    # TODO: allow set rating only once for one user
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 0 AND rating <= 5'))

    user = relationship("User", back_populates="ratings")
    product = relationship("Product", back_populates="ratings")


class Images(Base):
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False, unique=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product", back_populates="images")
