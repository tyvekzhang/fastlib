import pytest
from contextvars import Token
from unittest.mock import patch
import sys
import os

# 添加模块路径以便导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastlib.contextvars import set_current_user, get_current_user, clear_current_user, _current_user_id


class TestCurrentUserContext:
    """测试当前用户上下文功能"""

    def setup_method(self):
        """每个测试方法前重置上下文"""
        # 保存原始上下文值
        self.original_value = _current_user_id.get()
        # 重置为默认值
        if _current_user_id.get() is not None:
            token = _current_user_id.set(None)
            _current_user_id.reset(token)

    def teardown_method(self):
        """每个测试方法后清理上下文"""
        # 恢复原始上下文值
        if self.original_value is not None:
            _current_user_id.set(None)

    def test_set_current_user_valid(self):
        """测试设置有效的用户ID"""
        # 准备
        user_id = 123
        
        # 执行
        token = set_current_user(user_id)
        
        # 断言
        assert isinstance(token, Token)
        assert get_current_user() == user_id
        assert _current_user_id.get() == user_id

    def test_set_current_user_invalid_type(self):
        """测试设置非整数用户ID"""
        # 准备
        invalid_user_id = "123"
        
        # 执行 & 断言
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(invalid_user_id)

    def test_set_current_user_negative(self):
        """测试设置负数的用户ID"""
        # 准备
        negative_user_id = -1
        
        # 执行 & 断言
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(negative_user_id)

    def test_set_current_user_zero(self):
        """测试设置0作为用户ID"""
        # 准备
        zero_user_id = 0
        
        # 执行 & 断言
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(zero_user_id)

    def test_set_current_user_float(self):
        """测试设置浮点数用户ID"""
        # 准备
        float_user_id = 123.45
        
        # 执行 & 断言
        with pytest.raises(ValueError, match="user_id must be a positive integer"):
            set_current_user(float_user_id)

    def test_get_current_user_when_set(self):
        """测试获取已设置的用户ID"""
        # 准备
        user_id = 456
        set_current_user(user_id)
        
        # 执行
        result = get_current_user()
        
        # 断言
        assert result == user_id

    def test_context_isolation(self):
        """测试上下文隔离性"""
        # 准备
        user_id_1 = 111
        user_id_2 = 222
        
        # 执行
        token1 = set_current_user(user_id_1)
        context1_value = get_current_user()
        
        token2 = set_current_user(user_id_2)
        context2_value = get_current_user()
        
        clear_current_user(token2)
        after_clear_value = get_current_user()
        
        # 断言
        assert context1_value == user_id_1
        assert context2_value == user_id_2
        assert after_clear_value == user_id_1

    @patch('fastlib.contextvars.logger')
    def test_set_current_user_logging(self, mock_logger):
        """测试设置用户ID时的日志记录"""
        # 准备
        user_id = 123
        
        # 执行
        set_current_user(user_id)
        
        # 断言
        mock_logger.debug.assert_called_once_with(
            "Setting current user context: user_id=%s", user_id
        )

    @patch('fastlib.contextvars.logger')
    def test_clear_current_user_logging(self, mock_logger):
        """测试清除用户上下文时的日志记录"""
        # 准备
        user_id = 123
        token = set_current_user(user_id)
        
        # 执行
        clear_current_user(token)
        
        # 断言
        mock_logger.debug.assert_called_with("Cleared current user context")

    def test_multiple_operations_sequence(self):
        """测试多个操作的顺序执行"""
        # 准备
        user_ids = [101, 102, 103]
        tokens = []
        
        # 执行 - 顺序设置多个用户
        for uid in user_ids:
            token = set_current_user(uid)
            tokens.append(token)
            assert get_current_user() == uid
        
        # 执行 - 逆序清除
        for token in reversed(tokens):
            current_before_clear = get_current_user()
            clear_current_user(token)
        
        # 断言 - 最终应该回到初始状态
        assert get_current_user() is None

    def test_context_var_default_value(self):
        """测试ContextVar的默认值"""
        # 确保ContextVar正确初始化
        assert _current_user_id.get() is None
        assert _current_user_id.name == "current_user_id"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])