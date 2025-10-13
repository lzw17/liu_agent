"""Logging configuration for LiuAgent."""
import sys
from pathlib import Path
from loguru import logger
from .config import get_config


def setup_logger():
    """Setup logger configuration."""
    config = get_config()
    
    # Remove default handler
    logger.remove()
    
    # Create logs directory
    log_path = Path(config.logging.file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Console handler
    logger.add(
        sys.stdout,
        level=config.logging.level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler
    logger.add(
        config.logging.file_path,
        level=config.logging.level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=config.logging.max_file_size,
        retention=config.logging.backup_count,
        compression="zip"
    )
    
    return logger


# Initialize logger
setup_logger()
