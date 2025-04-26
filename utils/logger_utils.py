import json
import logging
import sys
import warnings
from datetime import datetime, timezone

import ecs_logging
from loguru import logger

# Import app_config after patching loguru
# This is to avoid circular imports
# We'll import it later in the configure_logger function


# Create a class to intercept standard library logs
class InterceptHandler(logging.Handler):
    """Intercepts standard library logs and redirects them to loguru."""

    def emit(self, record):
        # Get the corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class ECSLogSink:
    """Custom sink for loguru that formats logs in ECS format."""

    def __init__(self, sink=sys.stdout):
        self.sink = sink
        self.ecs_formatter = ecs_logging.StdlibFormatter()

    def __call__(self, message):
        # Extract record data from the message
        record = message.record

        # Create a standard LogRecord for ECS formatting
        log_record = logging.LogRecord(
            name=record["name"],
            level=record["level"].no,
            pathname=record["file"].path,
            lineno=record["line"],
            msg=record["message"],
            args=(),
            exc_info=record["exception"],
            func=record["function"],
        )

        # Add extra fields from the loguru record to the log record
        for key, value in record["extra"].items():
            setattr(log_record, key, value)

        # Format using ECS formatter
        ecs_dict = self.ecs_formatter.format_to_ecs(log_record)

        # Add additional fields that might be missing
        # Use UTC time and format with exactly 3 digits for milliseconds
        ecs_dict["@timestamp"] = (
            datetime.fromtimestamp(
                record["time"].timestamp(), tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            + "Z"
        )

        # Convert to JSON and write to sink
        json_line = json.dumps(ecs_dict) + "\n"
        self.sink.write(json_line)
        self.sink.flush()


def configure_logger():
    """Configure loguru logger with ECS format."""
    # Import app_config here to avoid circular imports
    from config import app_config

    # Remove default handler
    logger.remove()

    # Set the log level based on app_config
    log_level = app_config.log_level

    # Add handler with ECS sink
    logger.add(
        ECSLogSink(),
        level=log_level,
        format="{message}",  # This is needed but will be ignored by our sink
        backtrace=True,
        diagnose=True,
        catch=True,
    )

    # Configure the root logger to use our InterceptHandler
    # This ensures all standard library loggers are intercepted
    root_logger = logging.getLogger()
    root_logger.handlers = [InterceptHandler()]
    root_logger.setLevel(logging.getLevelName(log_level))
    root_logger.propagate = False

    # Explicitly configure loggers used by Uvicorn, FastAPI, and SQLAlchemy
    for logger_name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "urllib3",
    ]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False
        lib_logger.level = logging.getLevelName(log_level)

    # Configure warnings to be redirected to the logging system
    # This ensures warnings are also formatted in ECS format
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.handlers = [InterceptHandler()]

    # Optionally, you can also use a custom showwarning function
    original_showwarning = warnings.showwarning

    def showwarning_to_logger(
        message, category, filename, lineno, file=None, line=None
    ):
        logger.warning(f"{category.__name__}: {message}")

    warnings.showwarning = showwarning_to_logger

    return logger


# Patch the standard library's logging module to use our InterceptHandler
# This ensures that all logs, including those from third-party libraries,
# are processed through our loguru logger with ECS formatting
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Configure logger on module import
configure_logger()


def get_shared_logger():
    """Return the configured loguru logger."""
    return logger
