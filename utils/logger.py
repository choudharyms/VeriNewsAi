import logging
import json
import sys
from datetime import datetime

class StructuredLogger:
    def __init__(self, name="VeriNewsAI"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def _log(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

    def info(self, message, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        self._log("ERROR", message, **kwargs)

    def warning(self, message, **kwargs):
        self._log("WARNING", message, **kwargs)

logger = StructuredLogger()
