"""
Logging configuration
"""
import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None):
    """Configure application logging"""
    
    log_level = level or "INFO"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers = [
        "app",
        "uvicorn",
        "fastapi",
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level.upper()))
    
    return root_logger


def get_logger(name: str):
    """Get logger instance"""
    return logging.getLogger(name)