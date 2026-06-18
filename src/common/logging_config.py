"""Logging configuration with JSON and text formatters."""

from __future__ import annotations

import json
import logging
import logging.config
import time
from pathlib import Path
from typing import Any
from typing import ClassVar

_configured = False
_DEFAULT_INI = Path(__file__).resolve().parents[2] / "config" / "logging.ini"


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter with UTC timestamps."""

    converter = time.gmtime
    extra_keys: ClassVar[set[str]] = {"duration_seconds"}

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for k, v in record.__dict__.items():
            if k in self.extra_keys:
                payload[k] = v
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    """Text formatter with UTC timestamps."""

    converter = time.gmtime

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        super().__init__(
            fmt="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )


def configure_logging(config_path: str | Path | None = None) -> None:
    """Load logging configuration from an INI file. Call once at startup."""
    global _configured
    if _configured:
        return
    _configured = True

    path = Path(config_path) if config_path else _DEFAULT_INI
    if not path.exists():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        )
        logging.getLogger(__name__).warning("Logging INI not found at %s — using basicConfig", path)
        return

    logging.config.fileConfig(str(path), disable_existing_loggers=False)
