# Log
# TODO: Implement this module

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class StructuredLogger:
    """Provides structured logging capabilities for ShipVox."""
    
    def __init__(self, name: str = "shipvox", log_file: Optional[str] = None):
        """
        Initialize the structured logger.
        
        Args:
            name (str): Logger name
            log_file (Optional[str]): Path to log file. If None, logs to console only.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if log file is specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a log message with extra data.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
            
        Returns:
            str: Formatted log message
        """
        if not extra:
            return message
            
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            **extra
        }
        return json.dumps(log_data)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
        """
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
        """
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error message.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
        """
        self.logger.error(self._format_message(message, extra))
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
        """
        self.logger.debug(self._format_message(message, extra))
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an exception message.
        
        Args:
            message (str): The log message
            extra (Optional[Dict[str, Any]]): Additional data to log
        """
        self.logger.exception(self._format_message(message, extra))

# Create a default logger instance
logger = StructuredLogger()
