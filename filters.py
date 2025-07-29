from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

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

def should_forward(message, target):
    """
    Determine if a message should be forwarded based on target filters
    
    Args:
        message: Telethon message object
        target: Target object with filters
        
    Returns:
        bool: True if message should be forwarded
    """
    try:
        # If no filters are set, allow all messages
        if not target.keywords and not target.language and not target.media_types:
            return True
        
        # Get message text
        message_text = message.text or ""
        if hasattr(message, 'message'):
            message_text = message.message or ""
        
        # Check keywords
        if target.keywords:
            if not matches_keywords(message_text, target.keywords):
                return False
        
        # Check language
        if target.language:
            if not matches_language(message_text, target.language):
                return False
        
        # Check media type
        if target.media_types:
            if not matches_media_type(message, target.media_types):
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in should_forward: {e}")
        return True  # Default to forwarding if error occurs

def get_target_filter_summary_safe(user_id, target_username):
    """
    Safely get a summary of target's current filters using a fresh database query
    
    Args:
        user_id: User ID
        target_username: Target username
        
    Returns:
        str: Filter summary
    """
    try:
        from db import get_target_by_username
        
        # Get fresh target from database
        target = get_target_by_username(user_id, target_username)
        if not target:
            return "Target not found"
        
        summary = []
        if target.keywords:
            summary.append(f"Keywords: {target.keywords}")
        if target.language:
            summary.append(f"Language: {target.language}")
        if target.media_types:
            summary.append(f"Media types: {target.media_types}")
        
        return "\n".join(summary) if summary else "No filters set"
    
    except Exception as e:
        print(f"❌ Error getting filter summary: {e}")
        return "Error retrieving filters"

def get_target_filter_summary(target):
    """
    DEPRECATED: Use get_target_filter_summary_safe instead
    Get a summary of target's current filters
    """
    try:
        if not target:
            return "Target not found"
        
        # Try to access attributes safely
        summary = []
        
        try:
            if hasattr(target, 'keywords') and target.keywords:
                summary.append(f"Keywords: {target.keywords}")
        except:
            pass
            
        try:
            if hasattr(target, 'language') and target.language:
                summary.append(f"Language: {target.language}")
        except:
            pass
            
        try:
            if hasattr(target, 'media_types') and target.media_types:
                summary.append(f"Media types: {target.media_types}")
        except:
            pass
        
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