"""Tests for app.utils.security."""

from app.utils.security import clean_text, is_valid_language_code


class TestCleanText:
    def test_none_returns_empty_string(self):
        assert clean_text(None) == ""

    def test_plain_text_unchanged(self):
        assert clean_text("Hello world") == "Hello world"

    def test_strips_script_tags(self):
        result = clean_text("<script>alert('xss')</script>Hello")
        assert "<script>" not in result

    def test_strips_html_tags(self):
        result = clean_text("<b>Bold</b> text")
        assert "<b>" not in result

    def test_truncates_to_max_length(self):
        result = clean_text("a" * 100, max_length=10)
        assert len(result) == 10

    def test_strips_leading_trailing_whitespace(self):
        assert clean_text("   padded   ") == "padded"

    def test_removes_event_handler_attributes(self):
        result = clean_text('<img src="x" onerror="alert(1)">')
        assert "onerror" not in result


class TestIsValidLanguageCode:
    def test_supported_code_returns_true(self):
        assert is_valid_language_code("hi", ["en", "hi", "ar"]) is True

    def test_unsupported_code_returns_false(self):
        assert is_valid_language_code("zz", ["en", "hi", "ar"]) is False

    def test_empty_code_returns_false(self):
        assert is_valid_language_code("", ["en", "hi", "ar"]) is False

    def test_empty_supported_list_returns_false(self):
        assert is_valid_language_code("en", []) is False
