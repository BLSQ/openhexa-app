import json
import sys
import traceback
from logging import Handler

# Specific logging module for GCP, use json to serialize output -> work better for GKE
# Can be used for further customization


class GCPHandler(Handler):
    def emit(self, record):
        try:
            message = self.format(record)
            # to in JSON, be friendly with GCP
            print(json.dumps(message), file=sys.stderr)
            sys.stderr.flush()
        except Exception:
            pass  # don't loop

    def format(self, record):
        if record.exc_info is not None:
            type, _, tb = record.exc_info
            message = (
                f"{''.join(traceback.format_tb(tb))} \n{record.getMessage()}\n{type}"
            )
        else:
            message = record.msg % record.args
        return {
            "severity": record.levelname,
            "message": f"{record.name}: {message}",
        }
