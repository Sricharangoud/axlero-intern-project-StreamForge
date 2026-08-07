import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text, Boolean, Integer, Numeric, DateTime, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

class User(Base):
    """
    Represents a registered user on StreamForge.
    Can be both a streamer (has 1 Channel) and a viewer (has follows, subs, chat messages).
    """
    __tablename__ = "users"

    # UUID Primary Key is safer and more secure than sequential integers (1, 2, 3...)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        index=True, 
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    # Timestamps track record creation and modification times
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships (SQLAlchemy ORM constructs for navigating tables)
    # uselist=False creates a 1-to-1 relationship.
    # cascade="all, delete-orphan" means if the User is deleted, their Channel is also deleted.
    channel: Mapped["Channel"] = relationship(
        back_populates="owner", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    follows: Mapped[List["Follow"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    donations: Mapped[List["Donation"]] = relationship(
        back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r} email={self.email!r}>"


class Channel(Base):
    """
    Represents a streamer's channel.
    Owned by a User (1-to-1 relationship).
    """
    __tablename__ = "channels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    # Foreign key link to users table. ondelete="CASCADE" automatically deletes
    # the channel if the user is deleted.
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    # Stream key is a unique string used by streaming software (e.g. OBS) to broadcast
    stream_key: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        default=lambda: f"live_{uuid.uuid4().hex}"
    )
    is_live: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )
    follower_count: Mapped[int] = mapped_column(
        Integer, 
        default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        back_populates="channel"
    )
    streams: Mapped[List["Stream"]] = relationship(
        back_populates="channel", 
        cascade="all, delete-orphan"
    )
    follows: Mapped[List["Follow"]] = relationship(
        back_populates="channel", 
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="channel", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Channel name={self.name!r} owner_id={self.owner_id!r}>"


class Category(Base):
    """
    Represents a game or content category (e.g. "Just Chatting", "Valorant").
    Allows streaming channels to categorize their streams.
    """
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False
    )
    # Slugs are URL-friendly representations of names (e.g., "just-chatting")
    slug: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )

    # Relationships
    streams: Mapped[List["Stream"]] = relationship(
        back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<Category name={self.name!r}>"


class Stream(Base):
    """
    Represents a live broadcast session of a Channel.
    """
    __tablename__ = "streams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), 
        nullable=False
    )
    # ondelete="SET NULL" means if a category is deleted, streams in it are NOT deleted;
    # their category_id is just set to NULL.
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), 
        nullable=True
    )
    title: Mapped[str] = mapped_column(
        String(150), 
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    viewer_count: Mapped[int] = mapped_column(
        Integer, 
        default=0
    )
    is_live: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Relationships
    channel: Mapped["Channel"] = relationship(
        back_populates="streams"
    )
    category: Mapped[Optional["Category"]] = relationship(
        back_populates="streams"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="stream", 
        cascade="all, delete-orphan"
    )
    donations: Mapped[List["Donation"]] = relationship(
        back_populates="stream", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Stream title={self.title!r} is_live={self.is_live}>"


class Follow(Base):
    """
    Junction table for the many-to-many relationship between Users and Channels.
    Tracks who follows which channel.
    """
    __tablename__ = "follows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    # Enforce uniqueness so a user can't follow a channel multiple times
    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_user_channel_follow"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="follows"
    )
    channel: Mapped["Channel"] = relationship(
        back_populates="follows"
    )

    def __repr__(self) -> str:
        return f"<Follow user_id={self.user_id} channel_id={self.channel_id}>"


class Subscription(Base):
    """
    Junction table for the many-to-many relationship between Users and Channels.
    Tracks paid subscriptions to channels (Tiers 1, 2, or 3).
    """
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), 
        nullable=False
    )
    tier: Mapped[int] = mapped_column(
        Integer, 
        default=1  # 1 = Tier 1 ($4.99), 2 = Tier 2 ($9.99), 3 = Tier 3 ($24.99)
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # A user can only have one subscription record per channel at a time
    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_user_channel_sub"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="subscriptions"
    )
    channel: Mapped["Channel"] = relationship(
        back_populates="subscriptions"
    )

    def __repr__(self) -> str:
        return f"<Subscription user_id={self.user_id} channel_id={self.channel_id} tier={self.tier}>"


class ChatMessage(Base):
    """
    Represents messages sent in a Stream's chat room.
    """
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    stream_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("streams.id", ondelete="CASCADE"), 
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        String(500), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="chat_messages"
    )
    stream: Mapped["Stream"] = relationship(
        back_populates="chat_messages"
    )

    def __repr__(self) -> str:
        return f"<ChatMessage user_id={self.user_id} content={self.content[:20]!r}>"


class Donation(Base):
    """
    Represents monetary tips/donations sent by viewers to streamers during a live stream.
    """
    __tablename__ = "donations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    # user_id is optional to allow anonymous donations
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    stream_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("streams.id", ondelete="CASCADE"), 
        nullable=False
    )
    # Numeric handles financial data precisely without floating point rounding issues
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        back_populates="donations"
    )
    stream: Mapped["Stream"] = relationship(
        back_populates="donations"
    )

    def __repr__(self) -> str:
        return f"<Donation amount={self.amount} message={self.message[:20]!r}>"
