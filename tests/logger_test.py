# SPDX-License-Identifier: MIT
"""Tests for loguru-compatible message formatting on Logger."""

from loguru import logger as loguru_logger

from fastlib.config._log_config import LogConfig
from fastlib.logging.handlers import Logger


class TestLoggerLoguruFormatting:
    """Logger should format messages the same way as loguru."""

    def setup_method(self):
        Logger.reset()
        self._records: list[dict] = []
        self._handler_id: int | None = None

    def teardown_method(self):
        if self._handler_id is not None:
            loguru_logger.remove(self._handler_id)
        Logger.reset()

    def _create_logger(self, tmp_path) -> Logger:
        Logger._config = LogConfig(
            log_dir=str(tmp_path),
            app_name="fastlib-test",
            log_level="TRACE",
            enable_console_log=False,
            enable_async=False,
        )
        instance = Logger.initialize()
        self._handler_id = loguru_logger.add(
            lambda message: self._records.append(message.record),
            level="TRACE",
        )
        return instance

    def test_positional_brace_formatting(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.info("User {} logged in", "alice")

        assert self._records[-1]["message"] == "User alice logged in"

    def test_named_brace_formatting(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.info("User {name} logged in", name="bob")

        assert self._records[-1]["message"] == "User bob logged in"

    def test_mixed_args_and_kwargs_match_loguru_docs(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.info(
            "If you're using Python {}, prefer {feature} of course!",
            3.6,
            feature="f-strings",
        )

        assert (
            self._records[-1]["message"]
            == "If you're using Python 3.6, prefer f-strings of course!"
        )

    def test_f_string_still_works(self, tmp_path):
        app_logger = self._create_logger(tmp_path)
        user = "carol"

        app_logger.info(f"User {user} logged in")

        assert self._records[-1]["message"] == "User carol logged in"

    def test_kwargs_are_captured_in_extra(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.info("order {order_id} paid", order_id=42)

        record = self._records[-1]
        assert record["message"] == "order 42 paid"
        assert record["extra"]["order_id"] == 42

    def test_bind_adds_extra_without_formatting_message(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.bind(request_id="req-1").info("done")

        record = self._records[-1]
        assert record["message"] == "done"
        assert record["extra"]["request_id"] == "req-1"

    def test_record_points_to_caller_not_wrapper(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.warning("caller check")

        record = self._records[-1]
        assert record["function"] == "test_record_points_to_caller_not_wrapper"
        assert record["file"].name == "logger_test.py"

    def test_success_and_trace_levels(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.trace("trace {}", "a")
        app_logger.success("success {name}", name="b")

        assert self._records[-2]["level"].name == "TRACE"
        assert self._records[-2]["message"] == "trace a"
        assert self._records[-1]["level"].name == "SUCCESS"
        assert self._records[-1]["message"] == "success b"

    def test_log_with_explicit_level(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        app_logger.log("ERROR", "failed: {}", "timeout")

        record = self._records[-1]
        assert record["level"].name == "ERROR"
        assert record["message"] == "failed: timeout"

    def test_exception_includes_traceback(self, tmp_path):
        app_logger = self._create_logger(tmp_path)

        try:
            raise ValueError("boom")
        except ValueError:
            app_logger.exception("caught {}", "error")

        record = self._records[-1]
        assert record["message"] == "caught error"
        assert record["exception"] is not None
        assert record["exception"].type is ValueError

    def test_package_logger_supports_brace_formatting(self, tmp_path):
        self._create_logger(tmp_path)
        from fastlib.logging import logger as package_logger

        package_logger.debug("exported {}", "ok")

        assert self._records[-1]["message"] == "exported ok"
