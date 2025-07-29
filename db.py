from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    targets = relationship("Target", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username='{self.username}')>"

class Target(Base):
    __tablename__ = 'targets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    target_telegram_id = Column(Integer, nullable=False)
    target_username = Column(String(50), nullable=True)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(200), nullable=True)
    group_username = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Individual filters for each target
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    language = Column(String(5), nullable=True)  # Language code (e.g., 'en', 'fa')
    media_types = Column(String(100), nullable=True)  # Comma-separated media types
    
    # Relationships
    user = relationship("User", back_populates="targets")
    messages = relationship("TrackedMessage", back_populates="target", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Target(target_username='{self.target_username}', group_name='{self.group_name}')>"

class TrackedMessage(Base):
    __tablename__ = 'tracked_messages'
    
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'), nullable=False)
    message_id = Column(Integer, nullable=False)
    message_text = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    forwarded_at = Column(DateTime, default=datetime.utcnow)
    original_date = Column(DateTime, nullable=True)
    
    # Relationships
    target = relationship("Target", back_populates="messages")
    
    def __repr__(self):
        return f"<TrackedMessage(target_id={self.target_id}, message_id={self.message_id})>"

# Database engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller handle it

def create_user(telegram_id, username=None, first_name=None):
    """Create a new user or return existing one"""
    db = get_db()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            return user
        
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ User created: {user}")
        return user
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        raise
    finally:
        db.close()

def get_user(telegram_id):
    """Get user by telegram_id"""
    db = get_db()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        return user
    finally:
        db.close()

def add_target(user_id, target_telegram_id, target_username, group_id, group_name, group_username=None):
    """Add a new target for monitoring"""
    db = get_db()
    try:
        # Check if target already exists
        existing_target = db.query(Target).filter(
            Target.user_id == user_id,
            Target.target_telegram_id == target_telegram_id,
            Target.group_id == group_id
        ).first()
        
        if existing_target:
            existing_target.is_active = True
            db.commit()
            print(f"✅ Reactivated existing target: {existing_target}")
            return existing_target
        
        # Create new target
        target = Target(
            user_id=user_id,
            target_telegram_id=target_telegram_id,
            target_username=target_username,
            group_id=group_id,
            group_name=group_name,
            group_username=group_username
        )
        db.add(target)
        db.commit()
        db.refresh(target)
        print(f"✅ Target added: {target}")
        return target
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding target: {e}")
        raise
    finally:
        db.close()

def get_user_targets(user_id):
    """Get all active targets for a user"""
    db = get_db()
    try:
        targets = db.query(Target).filter(
            Target.user_id == user_id,
            Target.is_active == True
        ).all()
        return targets
    finally:
        db.close()

def get_target_by_username(user_id, target_username):
    """Get a specific target by username for a user"""
    db = get_db()
    try:
        target = db.query(Target).filter(
            Target.user_id == user_id,
            Target.target_username == target_username,
            Target.is_active == True
        ).first()
        return target
    finally:
        db.close()

def remove_target(user_id, target_username):
    """Remove a target by setting is_active to False"""
    db = get_db()
    try:
        target = db.query(Target).filter(
            Target.user_id == user_id,
            Target.target_username == target_username,
            Target.is_active == True
        ).first()
        
        if target:
            target.is_active = False
            db.commit()
            print(f"✅ Target removed: {target}")
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ Error removing target: {e}")
        raise
    finally:
        db.close()

def get_all_active_targets():
    """Get all active targets across all users"""
    db = get_db()
    try:
        targets = db.query(Target).options(joinedload(Target.user)).filter(Target.is_active == True).all()
        return targets
    finally:
        db.close()

def save_tracked_message(target_id, message_id, message_text, media_type, original_date):
    """Save a tracked message to the database"""
    db = get_db()
    try:
        tracked_message = TrackedMessage(
            target_id=target_id,
            message_id=message_id,
            message_text=message_text,
            media_type=media_type,
            original_date=original_date
        )
        db.add(tracked_message)
        db.commit()
        return tracked_message
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving message: {e}")
        raise
    finally:
        db.close()

def set_target_filter(user_id, target_username, keywords=None, language=None, media_types=None):
    """Set or update filters for a specific target"""
    db = get_db()
    try:
        target = db.query(Target).filter(
            Target.user_id == user_id,
            Target.target_username == target_username,
            Target.is_active == True
        ).first()
        
        if not target:
            return None
        
        # Update target filters
        target.keywords = keywords
        target.language = language
        target.media_types = media_types
        
        db.commit()
        print(f"✅ Filter set for target {target_username}")
        return target
    except Exception as e:
        db.rollback()
        print(f"❌ Error setting target filter: {e}")
        raise
    finally:
        db.close()

def get_target_filter(target_id):
    """Get filter for a specific target"""
    db = get_db()
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        return target
    finally:
        db.close()

def clear_target_filter(user_id, target_username):
    """Clear all filters for a specific target"""
    db = get_db()
    try:
        target = db.query(Target).filter(
            Target.user_id == user_id,
            Target.target_username == target_username,
            Target.is_active == True
        ).first()
        
        if not target:
            return False
        
        target.keywords = None
        target.language = None
        target.media_types = None
        
        db.commit()
        print(f"✅ Filters cleared for target {target_username}")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing target filter: {e}")
        raise
    finally:
        db.close()

def get_user_messages(user_id):
    """Get all tracked messages for a user"""
    db = get_db()
    try:
        messages = db.query(TrackedMessage).join(Target).filter(
            Target.user_id == user_id,
            Target.is_active == True
        ).all()
        return messages
    finally:
        db.close()