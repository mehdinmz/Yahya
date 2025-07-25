from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from db import get_user_filter

# Set seed for consistent results
DetectorFactory.seed = 0

def detect_language(text):
    """Detect language of text"""
    if not text or len(text.strip()) < 10:
        return None
    
    try:
        return detect(text)
    except LangDetectException:
        return None

def get_media_type(message):
    """Get media type from message"""
    if message.media is None:
        return 'text'
    
    if isinstance(message.media, MessageMediaPhoto):
        return 'photo'
    elif isinstance(message.media, MessageMediaDocument):
        if message.media.document.mime_type.startswith('video/'):
            return 'video'
        elif message.media.document.mime_type.startswith('audio/'):
            return 'audio'
        elif message.media.document.mime_type.startswith('image/'):
            return 'image'
        else:
            return 'document'
    elif isinstance(message.media, MessageMediaVideo):
        return 'video'
    else:
        return 'media'

def matches_keywords(text, keywords):
    """Check if text contains any of the keywords"""
    if not keywords or not text:
        return True
    
    keywords_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    if not keywords_list:
        return True
    
    text_lower = text.lower()
    for keyword in keywords_list:
        if keyword in text_lower:
            return True
    
    return False

def matches_language(text, target_language):
    """Check if text matches target language"""
    if not target_language or not text:
        return True
    
    detected_lang = detect_language(text)
    if detected_lang is None:
        return True  # Allow if can't detect
    
    return detected_lang == target_language.lower()

def matches_media_type(message, target_media_types):
    """Check if message media type matches target types"""
    if not target_media_types:
        return True
    
    media_types_list = [m.strip().lower() for m in target_media_types.split(',') if m.strip()]
    if not media_types_list:
        return True
    
    message_media_type = get_media_type(message)
    return message_media_type in media_types_list

def should_forward(message, user_id):
    """
    Determine if a message should be forwarded based on user filters
    
    Args:
        message: Telethon message object
        user_id: Database user ID
        
    Returns:
        bool: True if message should be forwarded
    """
    try:
        # Get user filter
        user_filter = get_user_filter(user_id)
        
        # If no filter exists, allow all messages
        if not user_filter:
            print(f"🔄 No filter found for user {user_id}, allowing message")
            return True
        
        # Get message text
        message_text = message.text or ""
        if hasattr(message, 'message'):
            message_text = message.message or ""
        
        # Check keywords
        if user_filter.keywords:
            if not matches_keywords(message_text, user_filter.keywords):
                print(f"❌ Message doesn't match keywords: {user_filter.keywords}")
                return False
        
        # Check language
        if user_filter.language:
            if not matches_language(message_text, user_filter.language):
                print(f"❌ Message doesn't match language: {user_filter.language}")
                return False
        
        # Check media type
        if user_filter.media_types:
            if not matches_media_type(message, user_filter.media_types):
                print(f"❌ Message doesn't match media types: {user_filter.media_types}")
                return False
        
        print(f"✅ Message passed all filters for user {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error in should_forward: {e}")
        return True  # Default to forwarding if error occurs

def get_filter_summary(user_id):
    """Get a summary of user's current filters"""
    try:
        user_filter = get_user_filter(user_id)
        if not user_filter:
            return "No filters set"
        
        summary = []
        if user_filter.keywords:
            summary.append(f"Keywords: {user_filter.keywords}")
        if user_filter.language:
            summary.append(f"Language: {user_filter.language}")
        if user_filter.media_types:
            summary.append(f"Media types: {user_filter.media_types}")
        
        return "\n".join(summary) if summary else "No filters set"
    
    except Exception as e:
        print(f"❌ Error getting filter summary: {e}")
        return "Error retrieving filters"

def validate_filter_input(keywords=None, language=None, media_types=None):
    """Validate filter input parameters"""
    errors = []
    
    # Validate language code
    if language:
        valid_languages = ['en', 'fa', 'ar', 'fr', 'de', 'es', 'it', 'ru', 'zh', 'ja', 'ko']
        if language.lower() not in valid_languages:
            errors.append(f"Invalid language code: {language}. Supported: {', '.join(valid_languages)}")
    
    # Validate media types
    if media_types:
        valid_media_types = ['text', 'photo', 'video', 'audio', 'image', 'document', 'media']
        media_list = [m.strip().lower() for m in media_types.split(',') if m.strip()]
        invalid_types = [m for m in media_list if m not in valid_media_types]
        if invalid_types:
            errors.append(f"Invalid media types: {', '.join(invalid_types)}. Supported: {', '.join(valid_media_types)}")
    
    return errors