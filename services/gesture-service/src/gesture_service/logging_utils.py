from __future__ import annotations

import json
import logging
from typing import Any


def configure_logging() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    return logging.getLogger("gesture-service")


def log_json(logger: logging.Logger, message: str, **fields: Any) -> None:
    payload = {"message": message, **fields}
    logger.info(json.dumps(payload, separators=(",", ":")))

