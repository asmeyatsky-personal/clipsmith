from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, UTC
import uuid


class TransactionDB(SQLModel, table=True):
    __tablename__ = "transactions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    amount: float
    currency: str = Field(default="USD")
    transaction_type: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    description: Optional[str] = None
    reference_id: Optional[str] = Field(index=True)
    extra_metadata: Optional[str] = Field(
        default=None, sa_column_kwargs={"name": "extra_metadata"}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    user: "UserDB" = Relationship(back_populates="transactions")


class CreatorWalletDB(SQLModel, table=True):
    __tablename__ = "creator_wallets"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", unique=True, index=True)
    balance: float = Field(default=0.0)
    pending_balance: float = Field(default=0.0)
    total_earned: float = Field(default=0.0)
    total_withdrawn: float = Field(default=0.0)
    currency: str = Field(default="USD")
    status: str = Field(default="active")
    stripe_account_id: Optional[str] = Field(index=True)
    payout_schedule: str = Field(default="monthly")
    minimum_payout: float = Field(default=10.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    last_payout_at: Optional[datetime] = None

    user: "UserDB" = Relationship(back_populates="wallet")
    payouts: List["PayoutDB"] = Relationship(back_populates="wallet")


class PayoutDB(SQLModel, table=True):
    __tablename__ = "payouts"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wallet_id: str = Field(foreign_key="creator_wallets.id")
    user_id: str = Field(foreign_key="users.id", index=True)
    amount: float
    currency: str = Field(default="USD")
    status: str = Field(default="pending", index=True)
    stripe_payout_id: Optional[str] = Field(index=True)
    bank_account_id: Optional[str] = None
    fee_amount: float = Field(default=0.0)
    net_amount: float
    description: Optional[str] = None
    extra_metadata: Optional[str] = Field(
        default=None, sa_column_kwargs={"name": "extra_metadata"}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_reason: Optional[str] = None

    wallet: "CreatorWalletDB" = Relationship(back_populates="payouts")


class SubscriptionDB(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    creator_id: str = Field(foreign_key="users.id", index=True)
    stripe_subscription_id: str = Field(unique=True, index=True)
    status: str = Field(index=True)
    amount: float
    currency: str = Field(default="USD")
    interval: str
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    subscriber: "UserDB" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubscriptionDB.user_id]"}
    )
    creator: "UserDB" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[SubscriptionDB.creator_id]"}
    )


class PremiumContentDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    video_id: str = Field(index=True)
    price: float
    currency: str = Field(default="USD")
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    purchase_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class PremiumPurchaseDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    premium_content_id: str = Field(index=True)
    amount: float
    currency: str = Field(default="USD")
    stripe_payment_id: Optional[str] = Field(index=True)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BrandCampaignDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    brand_id: str = Field(index=True)
    creator_id: str = Field(index=True)
    title: str
    description: Optional[str] = None
    budget: float
    requirements: Optional[str] = None
    deliverables: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str = Field(default="pending")
    payment_status: str = Field(default="unpaid")
    stripe_payment_id: Optional[str] = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class BrandProfileDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True)
    company_name: str
    industry: str
    website: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None


class SubscriptionTierDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    creator_id: str = Field(index=True)
    name: str
    price: float
    currency: str = Field(default="USD")
    interval: str
    description: Optional[str] = None
    benefits: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CreatorFundEligibilityDB(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(unique=True, index=True)
    follower_count: int = Field(default=0)
    monthly_views: int = Field(default=0)
    is_eligible: bool = Field(default=False)
    applied_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    status: str = Field(default="pending", index=True)
