"""
Text Utilities Module

Provides comprehensive text handling utilities including:
- Text normalization
- Sanitization functions
- Special character removal
- Slug generation

Requirements: 18.3
"""

import re
import unicodedata
from typing import Optional


class TextUtils:
    """Utility class for text operations"""
    
    # Vietnamese character mappings for slug generation
    VIETNAMESE_MAP = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd',
        'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        'Đ': 'D',
    }
    
    @staticmethod
    def normalize(text: str, form: str = 'NFC') -> str:
        """Normalize text using Unicode normalization."""
        if not text:
            return ""
        return unicodedata.normalize(form, text)
    
    @staticmethod
    def sanitize(text: str, allow_spaces: bool = True, allow_numbers: bool = True) -> str:
        """Sanitize text by removing or replacing unwanted characters."""
        if not text:
            return ""
        
        pattern_parts = [r'a-zA-Z']
        if allow_numbers:
            pattern_parts.append(r'0-9')
        if allow_spaces:
            pattern_parts.append(r'\s')
        
        pattern_parts.append(r'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
        pattern_parts.append(r'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ')
        
        pattern = f"[{''.join(pattern_parts)}]"
        sanitized = ''.join(re.findall(pattern, text))
        
        if allow_spaces:
            sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def remove_special_chars(text: str, keep_chars: str = "") -> str:
        """Remove special characters from text."""
        if not text:
            return ""
        
        escaped_keep = re.escape(keep_chars)
        pattern = f"[^a-zA-Z0-9\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ{escaped_keep}]"
        
        return re.sub(pattern, '', text)
    
    @staticmethod
    def slugify(text: str, separator: str = '-', lowercase: bool = True) -> str:
        """Generate a URL-friendly slug from text."""
        if not text:
            return ""
        
        result = text
        for viet_char, latin_char in TextUtils.VIETNAMESE_MAP.items():
            result = result.replace(viet_char, latin_char)
        
        if lowercase:
            result = result.lower()
        
        result = unicodedata.normalize('NFKD', result)
        result = result.encode('ascii', 'ignore').decode('ascii')
        result = re.sub(r'[^\w\s-]', '', result)
        result = re.sub(r'[-\s]+', separator, result)
        result = result.strip(separator)
        
        return result
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text to specified length."""
        if not text or len(text) <= max_length:
            return text
        
        if max_length <= len(suffix):
            return text[:max_length]
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def capitalize_words(text: str) -> str:
        """Capitalize the first letter of each word."""
        if not text:
            return ""
        
        return ' '.join(word.capitalize() for word in text.split())
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace from text."""
        if not text:
            return ""
        
        result = re.sub(r'\s+', ' ', text)
        return result.strip()
    
    @staticmethod
    def strip_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        
        clean = re.sub(r'<[^>]+>', '', text)
        return TextUtils.remove_extra_whitespace(clean)
    
    @staticmethod
    def is_empty_or_whitespace(text: Optional[str]) -> bool:
        """Check if text is None, empty, or contains only whitespace."""
        return not text or not text.strip()
    
    @staticmethod
    def extract_numbers(text: str) -> str:
        """Extract only numbers from text."""
        if not text:
            return ""
        
        return ''.join(re.findall(r'\d', text))
    
    @staticmethod
    def pad_left(text: str, length: int, pad_char: str = ' ') -> str:
        """Pad text on the left to reach specified length."""
        if not text:
            text = ""
        
        return text.rjust(length, pad_char)
    
    @staticmethod
    def pad_right(text: str, length: int, pad_char: str = ' ') -> str:
        """Pad text on the right to reach specified length."""
        if not text:
            text = ""
        
        return text.ljust(length, pad_char)


# Convenience functions
def normalize(text: str, form: str = 'NFC') -> str:
    return TextUtils.normalize(text, form)

def sanitize(text: str, allow_spaces: bool = True, allow_numbers: bool = True) -> str:
    return TextUtils.sanitize(text, allow_spaces, allow_numbers)

def remove_special_chars(text: str, keep_chars: str = "") -> str:
    return TextUtils.remove_special_chars(text, keep_chars)

def slugify(text: str, separator: str = '-', lowercase: bool = True) -> str:
    return TextUtils.slugify(text, separator, lowercase)

def truncate(text: str, max_length: int, suffix: str = '...') -> str:
    return TextUtils.truncate(text, max_length, suffix)

def capitalize_words(text: str) -> str:
    return TextUtils.capitalize_words(text)

def remove_extra_whitespace(text: str) -> str:
    return TextUtils.remove_extra_whitespace(text)

def strip_html_tags(text: str) -> str:
    return TextUtils.strip_html_tags(text)

def is_empty_or_whitespace(text: Optional[str]) -> bool:
    return TextUtils.is_empty_or_whitespace(text)

def extract_numbers(text: str) -> str:
    return TextUtils.extract_numbers(text)

def pad_left(text: str, length: int, pad_char: str = ' ') -> str:
    return TextUtils.pad_left(text, length, pad_char)

def pad_right(text: str, length: int, pad_char: str = ' ') -> str:
    return TextUtils.pad_right(text, length, pad_char)
