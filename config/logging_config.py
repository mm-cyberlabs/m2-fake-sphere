import logging
import logging.config

class LoggerConfig:
    # Setup logging configuration using a dictionary (best practice)
    @staticmethod
    def setup_logging():
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    # Define log message format
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': 'INFO',
                    'stream': 'ext://sys.stdout',  # Output to console
                },
                # Optional: file handler configuration
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'standard',
                    'level': 'INFO',
                    'filename': 'app.log',  # Log file name
                    'encoding': 'utf8'
                },
            },
            'root': {
                # Attach handlers to the root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
        }
        logging.config.dictConfig(logging_config)  # Apply configuration
