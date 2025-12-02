"""
Unit tests for Text Utils module

Tests text normalization, sanitization, special character removal,
and slug generation functionality.
"""

import pytest
from src.utils.text_utils import TextUtils


class TestTextUtils:
    """Test suite for TextUtils class"""
    
    def test_normalize_basic(self):
        """Test basic text normalization"""
        text = "café"
        result = TextUtils.normalize(text)
        assert result == "café"
        assert isinstance(result, str)
    
    def test_normalize_vietnamese(self):
        """Test Vietnamese text normalization"""
        text = "Hà Nội"
        result = TextUtils.normalize(text)
        assert result == "Hà Nội"
    
    def test_normalize_empty(self):
        """Test normalization with empty string"""
        assert TextUtils.normalize("") == ""
    
    def test_sanitize_basic(self):
        """Test basic text sanitization"""
        text = "Hello@World!"
        result = TextUtils.sanitize(text, allow_spaces=False)
        assert result == "HelloWorld"
    
    def test_sanitize_with_spaces(self):
        """Test sanitization keeping spaces"""
        text = "Hello World 123"
        result = TextUtils.sanitize(text, allow_spaces=True, allow_numbers=True)
        assert result == "Hello World 123"
    
    def test_sanitize_without_numbers(self):
        """Test sanitization removing numbers"""
        text = "Test 123"
        result = TextUtils.sanitize(text, allow_numbers=False)
        assert "123" not in result
        assert "Test" in result
    
    def test_sanitize_vietnamese(self):
        """Test sanitization with Vietnamese characters"""
        text = "Hà Nội 2024"
        result = TextUtils.sanitize(text)
        assert "Hà Nội" in result
        assert "2024" in result
    
    def test_sanitize_multiple_spaces(self):
        """Test sanitization normalizes multiple spaces"""
        text = "Hello    World"
        result = TextUtils.sanitize(text)
        assert result == "Hello World"
    
    def test_sanitize_empty(self):
        """Test sanitization with empty string"""
        assert TextUtils.sanitize("") == ""
    
    def test_remove_special_chars_basic(self):
        """Test removing special characters"""
        text = "Hello@World!"
        result = TextUtils.remove_special_chars(text)
        assert result == "HelloWorld"
    
    def test_remove_special_chars_keep_some(self):
        """Test removing special chars but keeping specified ones"""
        text = "test-file_name.txt"
        result = TextUtils.remove_special_chars(text, keep_chars=".-_")
        assert result == "test-file_name.txt"
    
    def test_remove_special_chars_vietnamese(self):
        """Test special char removal preserves Vietnamese"""
        text = "Hà Nội@2024!"
        result = TextUtils.remove_special_chars(text)
        assert "Hà Nội" in result
        assert "2024" in result
        assert "@" not in result
        assert "!" not in result
    
    def test_remove_special_chars_empty(self):
        """Test special char removal with empty string"""
        assert TextUtils.remove_special_chars("") == ""
    
    def test_slugify_basic(self):
        """Test basic slug generation"""
        text = "Hello World"
        result = TextUtils.slugify(text)
        assert result == "hello-world"
    
    def test_slugify_vietnamese(self):
        """Test slug generation with Vietnamese"""
        text = "Hà Nội"
        result = TextUtils.slugify(text)
        assert result == "ha-noi"
    
    def test_slugify_complex_vietnamese(self):
        """Test slug with complex Vietnamese text"""
        text = "Hệ Thống Quản Lý"
        result = TextUtils.slugify(text)
        assert result == "he-thong-quan-ly"
    
    def test_slugify_with_numbers(self):
        """Test slug generation preserves numbers"""
        text = "Test 123 ABC"
        result = TextUtils.slugify(text)
        assert result == "test-123-abc"
    
    def test_slugify_custom_separator(self):
        """Test slug with custom separator"""
        text = "Hello World"
        result = TextUtils.slugify(text, separator="_")
        assert result == "hello_world"
    
    def test_slugify_uppercase(self):
        """Test slug without lowercase conversion"""
        text = "Hello World"
        result = TextUtils.slugify(text, lowercase=False)
        assert result == "Hello-World"
    
    def test_slugify_special_chars(self):
        """Test slug removes special characters"""
        text = "Hello@World!"
        result = TextUtils.slugify(text)
        assert result == "helloworld"
    
    def test_slugify_empty(self):
        """Test slug generation with empty string"""
        assert TextUtils.slugify("") == ""
    
    def test_truncate_basic(self):
        """Test basic text truncation"""
        text = "This is a long text"
        result = TextUtils.truncate(text, 10)
        assert len(result) == 10
        assert result.endswith("...")
    
    def test_truncate_no_truncation_needed(self):
        """Test truncation when text is short enough"""
        text = "Short"
        result = TextUtils.truncate(text, 10)
        assert result == "Short"
    
    def test_truncate_custom_suffix(self):
        """Test truncation with custom suffix"""
        text = "This is a long text"
        result = TextUtils.truncate(text, 10, suffix=">>")
        assert result.endswith(">>")
        assert len(result) == 10
    
    def test_truncate_empty(self):
        """Test truncation with empty string"""
        assert TextUtils.truncate("", 10) == ""
    
    def test_capitalize_words_basic(self):
        """Test word capitalization"""
        text = "hello world"
        result = TextUtils.capitalize_words(text)
        assert result == "Hello World"
    
    def test_capitalize_words_vietnamese(self):
        """Test capitalization with Vietnamese"""
        text = "hà nội"
        result = TextUtils.capitalize_words(text)
        assert result == "Hà Nội"
    
    def test_capitalize_words_empty(self):
        """Test capitalization with empty string"""
        assert TextUtils.capitalize_words("") == ""
    
    def test_remove_extra_whitespace_basic(self):
        """Test removing extra whitespace"""
        text = "Hello    World"
        result = TextUtils.remove_extra_whitespace(text)
        assert result == "Hello World"
    
    def test_remove_extra_whitespace_newlines(self):
        """Test removing newlines"""
        text = "Line1\n\n\nLine2"
        result = TextUtils.remove_extra_whitespace(text)
        assert result == "Line1 Line2"
    
    def test_remove_extra_whitespace_tabs(self):
        """Test removing tabs"""
        text = "Hello\t\tWorld"
        result = TextUtils.remove_extra_whitespace(text)
        assert result == "Hello World"
    
    def test_remove_extra_whitespace_empty(self):
        """Test whitespace removal with empty string"""
        assert TextUtils.remove_extra_whitespace("") == ""
    
    def test_strip_html_tags_basic(self):
        """Test HTML tag removal"""
        text = "<p>Hello <b>World</b></p>"
        result = TextUtils.strip_html_tags(text)
        assert result == "Hello World"
        assert "<" not in result
        assert ">" not in result
    
    def test_strip_html_tags_complex(self):
        """Test complex HTML removal"""
        text = '<div class="test"><span>Text</span></div>'
        result = TextUtils.strip_html_tags(text)
        assert result == "Text"
    
    def test_strip_html_tags_empty(self):
        """Test HTML removal with empty string"""
        assert TextUtils.strip_html_tags("") == ""
    
    def test_is_empty_or_whitespace_empty(self):
        """Test empty string detection"""
        assert TextUtils.is_empty_or_whitespace("") is True
    
    def test_is_empty_or_whitespace_spaces(self):
        """Test whitespace-only string detection"""
        assert TextUtils.is_empty_or_whitespace("   ") is True
    
    def test_is_empty_or_whitespace_none(self):
        """Test None detection"""
        assert TextUtils.is_empty_or_whitespace(None) is True
    
    def test_is_empty_or_whitespace_with_text(self):
        """Test non-empty string"""
        assert TextUtils.is_empty_or_whitespace("Hello") is False
    
    def test_extract_numbers_basic(self):
        """Test number extraction"""
        text = "Price: $123.45"
        result = TextUtils.extract_numbers(text)
        assert result == "12345"
    
    def test_extract_numbers_phone(self):
        """Test extracting phone numbers"""
        text = "Phone: 0123-456-789"
        result = TextUtils.extract_numbers(text)
        assert result == "0123456789"
    
    def test_extract_numbers_no_numbers(self):
        """Test extraction when no numbers present"""
        text = "Hello World"
        result = TextUtils.extract_numbers(text)
        assert result == ""
    
    def test_extract_numbers_empty(self):
        """Test number extraction with empty string"""
        assert TextUtils.extract_numbers("") == ""
    
    def test_pad_left_basic(self):
        """Test left padding"""
        text = "123"
        result = TextUtils.pad_left(text, 5, '0')
        assert result == "00123"
        assert len(result) == 5
    
    def test_pad_left_no_padding_needed(self):
        """Test left padding when already long enough"""
        text = "12345"
        result = TextUtils.pad_left(text, 3, '0')
        assert result == "12345"
    
    def test_pad_left_empty(self):
        """Test left padding with empty string"""
        result = TextUtils.pad_left("", 5, '0')
        assert result == "00000"
    
    def test_pad_right_basic(self):
        """Test right padding"""
        text = "123"
        result = TextUtils.pad_right(text, 5, '0')
        assert result == "12300"
        assert len(result) == 5
    
    def test_pad_right_no_padding_needed(self):
        """Test right padding when already long enough"""
        text = "12345"
        result = TextUtils.pad_right(text, 3, '0')
        assert result == "12345"
    
    def test_pad_right_empty(self):
        """Test right padding with empty string"""
        result = TextUtils.pad_right("", 5, '0')
        assert result == "00000"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_convenience_normalize(self):
        """Test normalize convenience function"""
        from src.utils.text_utils import normalize
        result = normalize("café")
        assert result == "café"
    
    def test_convenience_sanitize(self):
        """Test sanitize convenience function"""
        from src.utils.text_utils import sanitize
        result = sanitize("Hello@World!")
        assert "Hello" in result
        assert "World" in result
    
    def test_convenience_slugify(self):
        """Test slugify convenience function"""
        from src.utils.text_utils import slugify
        result = slugify("Hello World")
        assert result == "hello-world"
    
    def test_convenience_truncate(self):
        """Test truncate convenience function"""
        from src.utils.text_utils import truncate
        result = truncate("Long text", 5)
        assert len(result) == 5
