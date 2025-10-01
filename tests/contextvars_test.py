import os
import sys
from contextvars import Token
from unittest.mock import patch

import pytest

# Add module path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlib.contextvars import (
    _current_user_id,
    clear_current_user,
    get_current_user,
    set_current_user,
)


class TestCurrentUserContext:
    """Test current user context functionality"""

    def setup_method(self):
        """Reset context before each test method"""
        # Save original context value
        self.original_value = _current_user_id.get()
        # Reset to default value
        if _current_user_id.get() is not None:
            token = _current_user_id.set(None)
            _current_user_id.reset(token)

    def teardown_method(self):
        """Clean up context after each test method"""
        # Restore original context value
        if self.original_value is not None:
            _current_user_id.set(None)

    def test_set_current_user_valid(self):
        """Test setting a valid user ID"""
        # Prepare
        user_id = 123

        # Execute
        token = set_current_user(user_id)

        # Assert
        assert isinstance(token, Token)
        assert get_current_user() == user_id
        assert _current_user_id.get() == user_id

    def test_set_current_user_invalid_type(self):
        """Test setting a non-integer user ID"""
        # Prepare
        invalid_user_id = "123"

        # Execute & Assert
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(invalid_user_id)

    def test_set_current_user_negative(self):
        """Test setting a negative user ID"""
        # Prepare
        negative_user_id = -1

        # Execute & Assert
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(negative_user_id)

    def test_set_current_user_zero(self):
        """Test setting 0 as user ID"""
        # Prepare
        zero_user_id = 0

        # Execute & Assert
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(zero_user_id)

    def test_set_current_user_float(self):
        """Test setting a float user ID"""
        # Prepare
        float_user_id = 123.45

        # Execute & Assert
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(float_user_id)

    def test_get_current_user_when_set(self):
        """Test getting a set user ID"""
        # Prepare
        user_id = 456
        set_current_user(user_id)

        # Execute
        result = get_current_user()

        # Assert
        assert result == user_id

    def test_context_isolation(self):
        """Test context isolation"""
        # Prepare
        user_id_1 = 111
        user_id_2 = 222

        # Execute
        context1_value = get_current_user()

        token2 = set_current_user(user_id_2)
        context2_value = get_current_user()

        clear_current_user(token2)
        after_clear_value = get_current_user()

        # Assert
        assert context1_value == user_id_1
        assert context2_value == user_id_2
        assert after_clear_value == user_id_1

    @patch("fastlib.contextvars.logger")
    def test_set_current_user_logging(self, mock_logger):
        """Test logging when setting user ID"""
        # Prepare
        user_id = 123

        # Execute
        set_current_user(user_id)

        # Assert
        mock_logger.debug.assert_called_once_with(
            "Setting current user context: user_id=%s", user_id
        )

    @patch("fastlib.contextvars.logger")
    def test_clear_current_user_logging(self, mock_logger):
        """Test logging when clearing user context"""
        # Prepare
        user_id = 123
        token = set_current_user(user_id)

        # Execute
        clear_current_user(token)

        # Assert
        mock_logger.debug.assert_called_with("Cleared current user context")

    def test_multiple_operations_sequence(self):
        """Test sequential execution of multiple operations"""
        # Prepare
        user_ids = [101, 102, 103]
        tokens = []

        # Execute - sequentially set multiple users
        for uid in user_ids:
            token = set_current_user(uid)
            tokens.append(token)
            assert get_current_user() == uid

        # Execute - clear in reverse order
        for token in reversed(tokens):
            clear_current_user(token)

        # Assert - should return to initial state
        assert get_current_user() is None

    def test_context_var_default_value(self):
        """Test ContextVar default value"""
        # Ensure ContextVar is correctly initialized
        assert _current_user_id.get() is None
        assert _current_user_id.name == "current_user_id"
