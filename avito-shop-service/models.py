from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IntIdPkMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)

class User(IntIdPkMixin, Base):
    __tablename__ = "users"
    username = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    coins = Column(Integer, default=1000, nullable=False)
    purchases = relationship("Purchase", back_populates="user", passive_deletes=True)
    sent_transactions = relationship(
        "Transaction", 
        foreign_keys="Transaction.from_user_id",
        passive_deletes=True
    )
    received_transactions = relationship(
        "Transaction", 
        foreign_keys="Transaction.to_user_id",
        passive_deletes=True
    )
    
    __table_args__ = (
        CheckConstraint('coins >= 0', name='coins_non_negative'),
    )

class MerchItem(Base):
    __tablename__ = "merch_items"
    name = Column(String(255), primary_key=True)
    price = Column(Integer, nullable=False)

class Purchase(Base):
    __tablename__ = "purchases"
    user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'), 
        primary_key=True
    )
    item_name = Column(
        String(255), 
        ForeignKey('merch_items.name'), 
        primary_key=True
    )
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="purchases")

class Transaction(IntIdPkMixin, Base):
    __tablename__ = "transactions"
    from_user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE')
    )
    to_user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE')
    )
    amount = Column(Integer, CheckConstraint('amount > 0'))
    timestamp = Column(DateTime, server_default=func.now())

    from_user = relationship(
        "User", 
        foreign_keys=[from_user_id], 
        back_populates="sent_transactions"
    )
    to_user = relationship(
        "User", 
        foreign_keys=[to_user_id], 
        back_populates="received_transactions"
    )