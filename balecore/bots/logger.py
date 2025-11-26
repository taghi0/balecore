import logging
import logging.config
import sys
from pathlib import Path

def setup_logger(name=__name__):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,

        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%H:%M:%S'
            },
            'json': {
                'format': '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "file": "%(filename)s", "line": %(lineno)d, "message": "%(message)s"}',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': sys.stdout
            },
            'file_debug': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': log_dir / 'debug.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': log_dir / 'error.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },

        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            }
        }
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)