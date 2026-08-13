import sys
from decimal import Decimal
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src import models, crud

def run_tests():
    print("[TEST] Starting Database Verification Tests (Using In-Memory SQLite)...")
    
    # 1. Initialize in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)
    Session = sessionmaker(bind=engine)
    
    # 2. Build tables
    print("[TEST] Generating tables from SQLAlchemy models...")
    Base.metadata.create_all(engine)
    print("[TEST] Schema created successfully.")

    # 3. Create session and run assertions
    db = Session()
    try:
        # --- Test 1: User & Channel Creation ---
        print("\n[TEST 1] Creating users and channels...")
        streamer = crud.create_user(
            db, 
            username="test_streamer", 
            email="streamer@test.com", 
            password_hash="hashed_pw"
        )
        viewer = crud.create_user(
            db, 
            username="test_viewer", 
            email="viewer@test.com", 
            password_hash="hashed_pw"
        )
        
        channel = crud.create_channel(
            db, 
            owner_id=streamer.id, 
            name="Test Stream Room", 
            description="A channel for verification tests."
        )
        
        db.commit()
        
        assert streamer.id is not None, "User ID was not generated"
        assert channel.id is not None, "Channel ID was not generated"
        assert channel.owner_id == streamer.id, "Channel owner_id mismatch"
        print("[TEST 1] User and Channel successfully created and linked (1:1).")

        # --- Test 2: Relationships and Follows ---
        print("\n[TEST 2] Following channels...")
        crud.follow_channel(db, user_id=viewer.id, channel_id=channel.id)
        db.commit()
        
        # Verify relationship loads correctly
        db.refresh(channel)
        db.refresh(viewer)
        
        assert channel.follower_count == 1, "Follower count did not increment"
        assert len(viewer.follows) == 1, "User follows relationship not updated"
        assert viewer.follows[0].channel_id == channel.id, "Follow channel_id mismatch"
        print("[TEST 2] Followers successfully linked and counted (M:N follow).")

        # --- Test 3: Starting & Querying Streams ---
        print("\n[TEST 3] Starting live stream...")
        category = crud.create_category(
            db, 
            name="Test Category", 
            slug="test-cat", 
            description="Testing category"
        )
        
        stream = crud.start_stream(
            db, 
            channel_id=channel.id, 
            category_id=category.id, 
            title="Verification Stream!"
        )
        db.commit()
        
        db.refresh(channel)
        assert channel.is_live is True, "Channel is_live was not set to True"
        assert stream.is_live is True, "Stream is_live was not set to True"
        
        # Fetch live streams
        live_streams = crud.get_live_streams(db)
        assert len(live_streams) == 1, "Live stream was not retrieved"
        assert live_streams[0].id == stream.id, "Live stream ID mismatch"
        print("[TEST 3] Streams successfully categorized, started, and queried.")

        # --- Test 4: Subscriptions, Chat, and Donations ---
        print("\n[TEST 4] Creating subscriptions, chat, and donations...")
        # Subscribe
        crud.subscribe_to_channel(db, user_id=viewer.id, channel_id=channel.id, tier=2)
        # Chat
        crud.send_chat_message(db, user_id=viewer.id, stream_id=stream.id, content="Hello World!")
        # Donation
        donation = crud.make_donation(
            db, 
            user_id=viewer.id, 
            stream_id=stream.id, 
            amount=Decimal("15.50"), 
            message="Keep up the good work!"
        )
        db.commit()
        
        # Verify
        db.refresh(stream)
        assert len(stream.chat_messages) == 1, "Chat message not linked to stream"
        assert stream.chat_messages[0].content == "Hello World!", "Chat content mismatch"
        
        assert len(stream.donations) == 1, "Donation not linked to stream"
        assert stream.donations[0].amount == Decimal("15.50"), "Donation amount mismatch"
        print("[TEST 4] Subscriptions, chat messages, and donations successfully registered.")

        # --- Test 5: Cascade Deletion ---
        print("\n[TEST 5] Verifying database CASCADE and SET NULL rules...")
        
        # Scenario A: Delete the viewer who made the donation
        # - The donation must NOT be deleted, but its user_id should be NULL (SET NULL)
        viewer_id = viewer.id
        donation_id = donation.id
        
        crud.delete_user(db, viewer_id)
        db.commit()
        
        # Verify donation user_id is set to null, but donation record remains
        remaining_donation = db.get(models.Donation, donation_id)
        assert remaining_donation is not None, "Donation was deleted when viewer was deleted"
        assert remaining_donation.user_id is None, "Donation user_id was not set to NULL on user deletion"
        
        # Scenario B: Delete the streamer
        # - The channel must be deleted (CASCADE)
        streamer_id = streamer.id
        
        crud.delete_user(db, streamer_id)
        db.commit()
        
        # Verify channel is deleted
        deleted_channel = crud.get_channel_by_id(db, channel.id)
        assert deleted_channel is None, "Channel was not deleted cascade-on-user-delete"
        
        print("[TEST 5] CASCADE and SET NULL referential integrity rules verified successfully.")
        
        print("\n[SUCCESS] ALL TESTS PASSED! SQLAlchemy models and CRUD operations are fully functional.")
        
    except AssertionError as e:
        print(f"\n[ERROR] Verification failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during verification: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
