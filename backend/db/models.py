import sqlalchemy
from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey, Float, DateTime, Enum
from db.base_class import Base
from sqlalchemy.orm import relationship

from fastapi_users.db import SQLAlchemyBaseUserTable
# enums model for db
from .enums import Status, TransactionStatus


# TODO: change Column to mapped_column


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(160), nullable=False)
    balance = Column(Numeric(precision=65, scale=8), default=0)
    iban = Column(String, nullable=False)
    # email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    # hashed_password: str
    # is_active: bool
    # is_superuser: bool
    # is_verified: bool

    ratings = relationship("ProductsRating", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    transaction = relationship("Transaction", back_populates="user")
    order = relationship("Order", back_populates="user")

    def __init__(self, username, email, hashed_password, iban):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.iban = iban

    def __repr__(self):
        return f"<User(balance={self.balance})>"


class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    description = Column(String(160), nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    status = Column(Enum(Status), server_default=Status.available.name)

    ratings = relationship("ProductsRating", back_populates="product", cascade="all, delete-orphan")
    images = relationship("Images", back_populates="product", cascade="all, delete-orphan")
    category = relationship("ProductCategory", back_populates="product", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    transaction = relationship("Transaction", back_populates="product")
    order = relationship("Order", back_populates="product")

    def __init__(self, name, description, price, amount):
        self.name = name
        self.description = description
        self.price = price
        self.amount = amount

    def __repr__(self):
        return f"<Product(name={self.name})>"


class ProductsRating(Base):
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


# TODO upgrade tables
class Category(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Category(name={self.name})>"


class ProductCategory(Base):
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    product = relationship("Product", back_populates="category")

    def __init__(self, product_id: int, category_id: int):
        self.product_id = product_id
        self.category_id = category_id


class Cart(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), index=True)
    amount = Column(Integer, nullable=False)

    user = relationship("User", back_populates="cart", lazy='select')
    product = relationship("Product", back_populates="cart")

    def __init__(self, product_id, user_id, amount):
        self.product_id = product_id
        self.user_id = user_id
        self.amount = amount


class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    iban = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=sqlalchemy.func.now())
    money_amount = Column(Float, CheckConstraint('money_amount > 0 '), nullable=False)
    status = Column(Enum(TransactionStatus), server_default=TransactionStatus.pending.name)
    provider_transaction_id = Column(Integer, nullable=False)
    # product.price
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="transaction")
    product_id = Column(Integer, ForeignKey("product.id"))
    product = relationship("Product", back_populates="transaction")


class Order(Base):
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    amount = Column(Integer, CheckConstraint('amount > 0 '))
    price = Column(Float, CheckConstraint('amount > 0 '))
    user_id = Column(Integer, ForeignKey("user.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

    product = relationship("Product", back_populates="order")
    user = relationship("User", back_populates="order")
