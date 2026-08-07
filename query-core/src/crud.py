import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from src import models

# ==============================================================================
# USER CRUD OPERATIONS
# ==============================================================================

def create_user(
    db: Session, 
    username: str, 
    email: str, 
    password_hash: str, 
    display_name: Optional[str] = None, 
    bio: Optional[str] = None
) -> models.User:
    """Creates a new User in the database."""
    # 1. Instantiate the model class
    new_user = models.User(
        username=username,
        email=email,
        password_hash=password_hash,
        display_name=display_name or username,
        bio=bio
    )
    # 2. Add to transaction session
    db.add(new_user)
    # 3. Flush change to DB to auto-generate UUID (or commit directly)
    db.flush()
    return new_user

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[models.User]:
    """Retrieves a User by their primary key UUID."""
    # db.get() is a shorthand for retrieving by primary key
    return db.get(models.User, user_id)

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Retrieves a User by username (case-sensitive)."""
    # select() builds a SQL query. db.scalars() runs it and extracts the model instances.
    stmt = select(models.User).where(models.User.username == username)
    return db.scalars(stmt).first()

def update_user_bio(db: Session, user_id: uuid.UUID, new_bio: str) -> Optional[models.User]:
    """Updates a User's bio description."""
    user = get_user_id = db.get(models.User, user_id)
    if user:
        user.bio = new_bio  # Just modifying the attribute queues the UPDATE SQL
        db.flush()
    return user

def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    """Deletes a User by ID. Their channel will be deleted due to Cascade rules."""
    user = db.get(models.User, user_id)
    if user:
        db.delete(user)
        db.flush()
        return True
    return False


# ==============================================================================
# CHANNEL CRUD OPERATIONS
# ==============================================================================

def create_channel(
    db: Session, 
    owner_id: uuid.UUID, 
    name: str, 
    description: Optional[str] = None
) -> models.Channel:
    """Creates a streaming Channel for a User."""
    new_channel = models.Channel(
        owner_id=owner_id,
        name=name,
        description=description
    )
    db.add(new_channel)
    db.flush()
    return new_channel

def get_channel_by_id(db: Session, channel_id: uuid.UUID) -> Optional[models.Channel]:
    """Retrieves a Channel by its primary key UUID."""
    return db.get(models.Channel, channel_id)

def get_channel_by_owner(db: Session, owner_id: uuid.UUID) -> Optional[models.Channel]:
    """Retrieves the Channel owned by a specific User."""
    stmt = select(models.Channel).where(models.Channel.owner_id == owner_id)
    return db.scalars(stmt).first()


# ==============================================================================
# CATEGORY CRUD OPERATIONS
# ==============================================================================

def create_category(
    db: Session, 
    name: str, 
    slug: str, 
    description: Optional[str] = None, 
    image_url: Optional[str] = None
) -> models.Category:
    """Creates a content Category."""
    category = models.Category(
        name=name,
        slug=slug,
        description=description,
        image_url=image_url
    )
    db.add(category)
    db.flush()
    return category

def get_categories(db: Session) -> List[models.Category]:
    """Fetches all categories."""
    stmt = select(models.Category).order_by(models.Category.name)
    return list(db.scalars(stmt).all())


# ==============================================================================
# STREAM CRUD OPERATIONS
# ==============================================================================

def start_stream(
    db: Session, 
    channel_id: uuid.UUID, 
    category_id: Optional[uuid.UUID], 
    title: str, 
    description: Optional[str] = None
) -> models.Stream:
    """Starts a live Stream session for a Channel and marks the Channel as live."""
    channel = db.get(models.Channel, channel_id)
    if not channel:
        raise ValueError(f"Channel with ID {channel_id} does not exist.")
    
    # 1. Create stream entry
    stream = models.Stream(
        channel_id=channel_id,
        category_id=category_id,
        title=title,
        description=description,
        is_live=True
    )
    db.add(stream)
    
    # 2. Mark channel as live
    channel.is_live = True
    db.flush()
    return stream

def end_stream(db: Session, stream_id: uuid.UUID) -> Optional[models.Stream]:
    """Ends a live Stream, records end time, and sets Channel status to offline."""
    stream = db.get(models.Stream, stream_id)
    if stream:
        stream.is_live = False
        stream.ended_at = datetime.now(timezone.utc)
        
        # Mark channel offline
        stream.channel.is_live = False
        db.flush()
    return stream

def get_live_streams(db: Session) -> List[models.Stream]:
    """Retrieves all streams currently broadcasting live."""
    stmt = select(models.Stream).where(models.Stream.is_live == True).order_by(models.Stream.viewer_count.desc())
    return list(db.scalars(stmt).all())


# ==============================================================================
# INTERACTION CRUD OPERATIONS (FOLLOWS, SUBSCRIPTIONS, CHAT, DONATIONS)
# ==============================================================================

def follow_channel(db: Session, user_id: uuid.UUID, channel_id: uuid.UUID) -> models.Follow:
    """Follows a channel and updates the channel's follower count."""
    follow = models.Follow(user_id=user_id, channel_id=channel_id)
    db.add(follow)
    
    # Increment follower count
    channel = db.get(models.Channel, channel_id)
    if channel:
        channel.follower_count += 1
        
    db.flush()
    return follow

def unfollow_channel(db: Session, user_id: uuid.UUID, channel_id: uuid.UUID) -> bool:
    """Unfollows a channel and decrements the follower count."""
    stmt = select(models.Follow).where(
        and_(models.Follow.user_id == user_id, models.Follow.channel_id == channel_id)
    )
    follow = db.scalars(stmt).first()
    if follow:
        db.delete(follow)
        
        # Decrement follower count
        channel = db.get(models.Channel, channel_id)
        if channel and channel.follower_count > 0:
            channel.follower_count -= 1
            
        db.flush()
        return True
    return False

def subscribe_to_channel(
    db: Session, 
    user_id: uuid.UUID, 
    channel_id: uuid.UUID, 
    tier: int = 1
) -> models.Subscription:
    """Subscribes a user to a channel at a given tier (1, 2, or 3)."""
    sub = models.Subscription(
        user_id=user_id,
        channel_id=channel_id,
        tier=tier,
        is_active=True
    )
    db.add(sub)
    db.flush()
    return sub

def send_chat_message(
    db: Session, 
    user_id: uuid.UUID, 
    stream_id: uuid.UUID, 
    content: str
) -> models.ChatMessage:
    """Inserts a chat message sent during a stream."""
    message = models.ChatMessage(
        user_id=user_id,
        stream_id=stream_id,
        content=content
    )
    db.add(message)
    db.flush()
    return message

def make_donation(
    db: Session, 
    user_id: Optional[uuid.UUID], 
    stream_id: uuid.UUID, 
    amount: Decimal, 
    message: Optional[str] = None
) -> models.Donation:
    """Records a viewer donation to a stream."""
    donation = models.Donation(
        user_id=user_id,
        stream_id=stream_id,
        amount=amount,
        message=message
    )
    db.add(donation)
    db.flush()
    return donation
