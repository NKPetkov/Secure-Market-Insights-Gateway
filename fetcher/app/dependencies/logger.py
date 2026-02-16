import logging
from app.config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(name)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)