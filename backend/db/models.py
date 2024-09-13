import sqlalchemy
from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey, Float, DateTime, Enum
from db.base_class import Base
from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func, select
from fastapi_users.db import SQLAlchemyBaseUserTable
# enums model for db
from .enums import Status

# TODO: change Column to mapped_column


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(160), nullable=False)
    balance = Column(Numeric(precision=65, scale=8), default=0)
    # email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    # hashed_password: str
    # is_active: bool
    # is_superuser: bool
    # is_verified: bool

    ratings = relationship("ProductsRating", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, username, email, hashed_password):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password

    def __repr__(self):
        return f"<User(balance={self.balance})>"


class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    description = Column(String(160), nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    status = Column(Enum(Status), server_default=Status.available.name)
    ratings = relationship("ProductsRating", back_populates="product", cascade="all, delete-orphan")
    images = relationship("Images", back_populates="product", cascade="all, delete-orphan")

    def __init__(self, name, description, price, amount):
        self.name = name
        self.description = description
        self.price = price
        self.amount = amount

    def __repr__(self):
        return f"<Product(name={self.name})>"

    # @property
    # def average_rating(self):
    #     avg_rating = (
    #         select(func.avg(ProductsRating.rating)).where(ProductsRating.product_id == self.id))
    #     session = async_session()
    #     data = session.execute(avg_rating).scalar()
    #     return data if data is not None else 0

    # @property
    # def all_images(self):
    #     return [files.photo_url for files in self.images]


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
    photo_url = Column(String, nullable=False, unique=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product", back_populates="images")

    def __init__(self, photo_url, product_id):
        self.photo_url = photo_url
        self.product_id = product_id

    def __repr__(self):
        return f"<Image(url={self.photo_url})>"
