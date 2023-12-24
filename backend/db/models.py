from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint, ForeignKey
from backend.db.base_class import Base
from sqlalchemy.orm import relationship


class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(160), unique=True)
    user_email = Column(String(40), unique=True)
    password = Column(String(250))
    balance = Column(Numeric(precision=65, scale=8), default=0)

    ratings = relationship("ProductsRating", back_populates="user")

    def __init__(self, username, password, user_email):
        self.username = username
        self.password = password
        self.user_email = user_email

    def __repr__(self):
        return f"<User(balance={self.balance})>"


class Product(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    descriptions = Column(String(160))

    # TODO: make by default rating 0 if not exist add price
    ratings = relationship("ProductsRating", back_populates="product")

    def __init__(self, name, descriptions):
        self.name = name
        self.descriptions = descriptions

    def __repr__(self):
        return f"<Product(name={self.name})>"


class ProductsRating(Base):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    rating = Column(Integer, CheckConstraint('rating >= 0 AND rating <= 5'), default=0)

    user = relationship("User", back_populates="ratings")
    product = relationship("Product", back_populates="ratings")
