import uuid
from decimal import Decimal
from src.database import db_session, Base, engine
from src import crud, models

def seed_database():
    print("[SEED] Starting database seeding...")
    
    # Using the db_session context manager to auto-commit and clean up
    with db_session() as db:
        # 1. Seed Categories
        print("[SEED] Seeding categories...")
        cat_just_chatting = crud.create_category(
            db, 
            name="Just Chatting", 
            slug="just-chatting", 
            description="Talk about anything and everything with the community.",
            image_url="https://images.streamforge.tv/categories/just-chatting.jpg"
        )
        cat_software = crud.create_category(
            db, 
            name="Software Development", 
            slug="software-dev", 
            description="Writing code, building systems, and pair programming.",
            image_url="https://images.streamforge.tv/categories/software-dev.jpg"
        )
        cat_gaming = crud.create_category(
            db, 
            name="Cyberpunk 2077", 
            slug="cyberpunk-2077", 
            description="Welcome to Night City.",
            image_url="https://images.streamforge.tv/categories/cyberpunk-2077.jpg"
        )
        
        # 2. Seed Users
        print("[SEED] Seeding users...")
        alice = crud.create_user(
            db, 
            username="alice_dev", 
            email="alice@streamforge.tv", 
            password_hash="pbkdf2:sha256:password_hash_alice", 
            display_name="Alice Codes", 
            bio="Senior backend engineer streaming system design and database architecture."
        )
        bob = crud.create_user(
            db, 
            username="bob_gaming", 
            email="bob@streamforge.tv", 
            password_hash="pbkdf2:sha256:password_hash_bob", 
            display_name="BobTheGamer", 
            bio="Professional speedrunner and RPG enthusiast."
        )
        charlie = crud.create_user(
            db, 
            username="charlie_viewer", 
            email="charlie@gmail.com", 
            password_hash="pbkdf2:sha256:password_hash_charlie", 
            display_name="Charlie", 
            bio="Casual viewer who loves code streams."
        )
        david = crud.create_user(
            db, 
            username="david_viewer", 
            email="david@gmail.com", 
            password_hash="pbkdf2:sha256:password_hash_david", 
            display_name="David_T", 
            bio="Just here for the gameplay!"
        )
        eve = crud.create_user(
            db, 
            username="eve_anon", 
            email="eve@gmail.com", 
            password_hash="pbkdf2:sha256:password_hash_eve", 
            display_name="Eve", 
            bio="Lurker."
        )

        # 3. Seed Channels
        print("[SEED] Seeding channels...")
        alice_channel = crud.create_channel(
            db, 
            owner_id=alice.id, 
            name="Alice Codes Live", 
            description="Daily streams building scalable software systems using Python, PostgreSQL, and Docker."
        )
        bob_channel = crud.create_channel(
            db, 
            owner_id=bob.id, 
            name="Bob's Gaming Haven", 
            description="Retro and modern RPG speedruns. Current focus: Cyberpunk 2077 100% run."
        )

        # 4. Seed Follows
        print("[SEED] Seeding follows...")
        crud.follow_channel(db, user_id=charlie.id, channel_id=alice_channel.id)
        crud.follow_channel(db, user_id=charlie.id, channel_id=bob_channel.id)
        crud.follow_channel(db, user_id=david.id, channel_id=bob_channel.id)
        crud.follow_channel(db, user_id=eve.id, channel_id=alice_channel.id)

        # 5. Seed Subscriptions
        print("[SEED] Seeding subscriptions...")
        # Charlie subscribes to Alice (Tier 1)
        crud.subscribe_to_channel(db, user_id=charlie.id, channel_id=alice_channel.id, tier=1)
        # David subscribes to Bob (Tier 3)
        crud.subscribe_to_channel(db, user_id=david.id, channel_id=bob_channel.id, tier=3)

        # 6. Seed Stream (Alice's Live Stream)
        print("[SEED] Seeding live stream for Alice...")
        alice_stream = crud.start_stream(
            db, 
            channel_id=alice_channel.id, 
            category_id=cat_software.id, 
            title="Designing a Streaming DB from scratch in Postgres!",
            description="Writing DDL, SQLAlchemy models, and configuring migrations for StreamForge!"
        )
        # Set viewer count
        alice_stream.viewer_count = 42

        # 7. Seed Stream (Bob's Live Stream)
        print("[SEED] Seeding live stream for Bob...")
        bob_stream = crud.start_stream(
            db, 
            channel_id=bob_channel.id, 
            category_id=cat_gaming.id, 
            title="Cyberpunk 2077 Speedrun Any% - World Record Attempt",
            description="Going fast in Night City. Come hang out!"
        )
        bob_stream.viewer_count = 128

        # 8. Seed Chat Messages
        print("[SEED] Seeding chat messages...")
        crud.send_chat_message(
            db, 
            user_id=charlie.id, 
            stream_id=alice_stream.id, 
            content="Is UUIDv4 preferred over INT for database scaling?"
        )
        crud.send_chat_message(
            db, 
            user_id=eve.id, 
            stream_id=alice_stream.id, 
            content="Yes! UUIDs prevent ID guessing and make distributed merges easier."
        )
        crud.send_chat_message(
            db, 
            user_id=david.id, 
            stream_id=bob_stream.id, 
            content="Insane routing in Watson! Keep it up!"
        )

        # 9. Seed Donations
        print("[SEED] Seeding donations...")
        # Charlie donates $25 to Alice
        crud.make_donation(
            db, 
            user_id=charlie.id, 
            stream_id=alice_stream.id, 
            amount=Decimal("25.00"), 
            message="Thanks for explaining foreign key indexing!"
        )
        # Anonymous donation to Alice
        crud.make_donation(
            db, 
            user_id=None, 
            stream_id=alice_stream.id, 
            amount=Decimal("5.00"), 
            message="Love the stream!"
        )
        # David donates $50 to Bob
        crud.make_donation(
            db, 
            user_id=david.id, 
            stream_id=bob_stream.id, 
            amount=Decimal("50.00"), 
            message="Epic run! Get that WR!"
        )

    print("[SEED] Database successfully seeded with sample data!")

if __name__ == "__main__":
    # If this script is run directly, it will drop and recreate all tables (if SQLite)
    # and seed the data. Let's make sure it handles both.
    from src.config import DATABASE_URL
    if DATABASE_URL.startswith("sqlite"):
        # For SQLite, we can easily recreate the database tables automatically
        print("[SEED] SQLite detected: Auto-creating tables before seeding...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
    seed_database()
