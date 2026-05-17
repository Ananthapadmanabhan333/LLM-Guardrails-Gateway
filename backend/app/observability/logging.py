import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any
from app.config import settings


class JSONLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "extra"):
            log_entry.update(record.extra)

        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id

        return json.dumps(log_entry)


def setup_logging():
    logger = logging.getLogger("llm_guardrails")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    formatter = JSONLogFormatter() if settings.log_format == "json" else logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)

    return logger


logger = setup_logging()
