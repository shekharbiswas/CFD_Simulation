# Utility functions can be added here if needed
# For example, logging setup:
import logging

def setup_logging(level=logging.INFO):
    """Sets up basic logging."""
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    setup_logging()
    logging.info("Logging is set up.")
