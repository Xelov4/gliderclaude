"""Enhanced error logging system for Poker AI MVP."""
import sys
import traceback
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import psutil
import threading
from loguru import logger


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "CRITICAL"    # System crashes, data corruption
    HIGH = "HIGH"           # Features broken, major functionality lost
    MEDIUM = "MEDIUM"       # Minor features affected, workarounds exist
    LOW = "LOW"             # Cosmetic issues, logging noise
    INFO = "INFO"           # Informational, not really an error


class ErrorCategory(Enum):
    """Error categories for classification."""
    VISION = "VISION"               # Computer vision, detection errors
    CAPTURE = "CAPTURE"             # Screen capture issues
    DATABASE = "DATABASE"           # Database operations
    GUI = "GUI"                     # User interface errors  
    NETWORK = "NETWORK"             # Network-related issues
    FILE_SYSTEM = "FILE_SYSTEM"     # File I/O operations
    CONFIGURATION = "CONFIGURATION" # Settings, config errors
    PERFORMANCE = "PERFORMANCE"     # Performance-related issues
    UNKNOWN = "UNKNOWN"             # Uncategorized errors


@dataclass
class ErrorContext:
    """Additional context for error logging."""
    session_id: Optional[int] = None
    thread_name: str = ""
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_processes: int = 0
    frame_number: Optional[int] = None
    processing_time_ms: Optional[int] = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}


@dataclass
class ErrorRecord:
    """Comprehensive error record."""
    id: Optional[int] = None
    timestamp: datetime = None
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.UNKNOWN
    component: str = ""         # Which module/class
    function: str = ""          # Which function
    message: str = ""           # Error message
    exception_type: str = ""    # Exception class name
    stack_trace: str = ""       # Full stack trace
    context: ErrorContext = None
    resolution_status: str = "OPEN"  # OPEN, IN_PROGRESS, RESOLVED, IGNORED
    resolution_notes: str = ""
    occurrence_count: int = 1
    first_seen: datetime = None
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.first_seen is None:
            self.first_seen = self.timestamp
        if self.last_seen is None:
            self.last_seen = self.timestamp
        if self.context is None:
            self.context = ErrorContext()


class EnhancedErrorLogger:
    """Advanced error logging system with analytics and reporting."""
    
    def __init__(self, db_path: str = "data/error_logs.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self._error_cache: Dict[str, ErrorRecord] = {}
        self._lock = threading.Lock()
        
        # Performance monitoring
        self.process = psutil.Process()
        
        logger.info(f"Enhanced error logger initialized: {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize error logging database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    component TEXT NOT NULL,
                    function TEXT NOT NULL,
                    message TEXT NOT NULL,
                    exception_type TEXT,
                    stack_trace TEXT,
                    context_json TEXT,
                    resolution_status TEXT DEFAULT 'OPEN',
                    resolution_notes TEXT,
                    occurrence_count INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_timestamp 
                ON error_logs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_severity_category 
                ON error_logs(severity, category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_component 
                ON error_logs(component, function)
            """)
    
    def _get_system_context(self, session_id: Optional[int] = None, 
                           additional_data: Dict[str, Any] = None) -> ErrorContext:
        """Gather system context for error logging."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            cpu_percent = self.process.cpu_percent()
            
            return ErrorContext(
                session_id=session_id,
                thread_name=threading.current_thread().name,
                memory_usage_mb=round(memory_mb, 2),
                cpu_usage_percent=round(cpu_percent, 2),
                active_processes=len(psutil.pids()),
                additional_data=additional_data or {}
            )
        except Exception as e:
            # Fallback context if system monitoring fails
            return ErrorContext(
                session_id=session_id,
                thread_name=threading.current_thread().name,
                additional_data=additional_data or {}
            )
    
    def _generate_error_hash(self, error_record: ErrorRecord) -> str:
        """Generate unique hash for error deduplication."""
        key_data = f"{error_record.component}:{error_record.function}:{error_record.exception_type}:{error_record.message[:100]}"
        return str(hash(key_data))
    
    def log_error(self, 
                  severity: ErrorSeverity,
                  category: ErrorCategory, 
                  message: str,
                  component: str = "",
                  function: str = "",
                  exception: Optional[Exception] = None,
                  session_id: Optional[int] = None,
                  additional_data: Dict[str, Any] = None) -> int:
        """Log an error with full context and deduplication."""
        
        # Get current frame info if not provided
        if not component or not function:
            frame = sys._getframe(1)
            if not component:
                component = frame.f_globals.get('__name__', 'unknown')
            if not function:
                function = frame.f_code.co_name
        
        # Get stack trace
        stack_trace = ""
        exception_type = ""
        if exception:
            exception_type = type(exception).__name__
            stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        else:
            stack_trace = ''.join(traceback.format_stack())
        
        # Create error record
        error_record = ErrorRecord(
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            component=component,
            function=function,
            message=message,
            exception_type=exception_type,
            stack_trace=stack_trace,
            context=self._get_system_context(session_id, additional_data)
        )
        
        # Handle deduplication
        error_hash = self._generate_error_hash(error_record)
        
        with self._lock:
            if error_hash in self._error_cache:
                # Update existing error
                existing = self._error_cache[error_hash]
                existing.occurrence_count += 1
                existing.last_seen = datetime.now()
                error_record = existing
            else:
                # New error
                self._error_cache[error_hash] = error_record
        
        # Save to database
        error_id = self._save_error_to_db(error_record)
        error_record.id = error_id
        
        # Log to standard logger based on severity
        log_message = f"[{category.value}] {component}.{function}: {message}"
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        return error_id
    
    def _save_error_to_db(self, error_record: ErrorRecord) -> int:
        """Save error record to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if error already exists (for deduplication)
            cursor = conn.execute("""
                SELECT id, occurrence_count FROM error_logs 
                WHERE component = ? AND function = ? AND exception_type = ? AND message = ?
                ORDER BY last_seen DESC LIMIT 1
            """, (error_record.component, error_record.function, 
                  error_record.exception_type, error_record.message))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                error_id, old_count = existing
                conn.execute("""
                    UPDATE error_logs SET 
                        occurrence_count = ?,
                        last_seen = ?,
                        context_json = ?
                    WHERE id = ?
                """, (error_record.occurrence_count, 
                      error_record.last_seen.isoformat(),
                      json.dumps(asdict(error_record.context)),
                      error_id))
                return error_id
            else:
                # Insert new record
                cursor = conn.execute("""
                    INSERT INTO error_logs (
                        timestamp, severity, category, component, function,
                        message, exception_type, stack_trace, context_json,
                        occurrence_count, first_seen, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    error_record.timestamp.isoformat(),
                    error_record.severity.value,
                    error_record.category.value,
                    error_record.component,
                    error_record.function,
                    error_record.message,
                    error_record.exception_type,
                    error_record.stack_trace,
                    json.dumps(asdict(error_record.context)),
                    error_record.occurrence_count,
                    error_record.first_seen.isoformat(),
                    error_record.last_seen.isoformat()
                ))
                return cursor.lastrowid
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            # Total errors by severity
            cursor = conn.execute("""
                SELECT severity, COUNT(*) as count, SUM(occurrence_count) as total_occurrences
                FROM error_logs 
                WHERE timestamp >= ?
                GROUP BY severity
                ORDER BY count DESC
            """, (since.isoformat(),))
            
            severity_stats = {row[0]: {"unique": row[1], "total": row[2]} 
                            for row in cursor.fetchall()}
            
            # Errors by category
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count, SUM(occurrence_count) as total_occurrences
                FROM error_logs 
                WHERE timestamp >= ?
                GROUP BY category
                ORDER BY count DESC
            """, (since.isoformat(),))
            
            category_stats = {row[0]: {"unique": row[1], "total": row[2]} 
                            for row in cursor.fetchall()}
            
            # Top error components
            cursor = conn.execute("""
                SELECT component, function, COUNT(*) as count, SUM(occurrence_count) as total
                FROM error_logs 
                WHERE timestamp >= ?
                GROUP BY component, function
                ORDER BY total DESC
                LIMIT 10
            """, (since.isoformat(),))
            
            top_components = [{"component": row[0], "function": row[1], 
                             "unique": row[2], "total": row[3]} 
                            for row in cursor.fetchall()]
            
            # Recent critical errors
            cursor = conn.execute("""
                SELECT timestamp, component, function, message, occurrence_count
                FROM error_logs 
                WHERE severity = 'CRITICAL' AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (since.isoformat(),))
            
            critical_errors = [{"timestamp": row[0], "component": row[1], 
                              "function": row[2], "message": row[3], 
                              "count": row[4]} 
                             for row in cursor.fetchall()]
        
        return {
            "time_range_hours": hours,
            "generated_at": datetime.now().isoformat(),
            "severity_breakdown": severity_stats,
            "category_breakdown": category_stats,
            "top_error_sources": top_components,
            "recent_critical_errors": critical_errors,
            "total_unique_errors": sum(stats["unique"] for stats in severity_stats.values()),
            "total_error_occurrences": sum(stats["total"] for stats in severity_stats.values())
        }
    
    def get_errors(self, severity: Optional[ErrorSeverity] = None,
                   category: Optional[ErrorCategory] = None,
                   component: Optional[str] = None,
                   hours: Optional[int] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Get filtered error records."""
        query = "SELECT * FROM error_logs WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if component:
            query += " AND component LIKE ?"
            params.append(f"%{component}%")
        
        if hours:
            since = datetime.now() - timedelta(hours=hours)
            query += " AND timestamp >= ?"
            params.append(since.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            errors = []
            for row in cursor.fetchall():
                error_dict = dict(row)
                # Parse context JSON
                if error_dict['context_json']:
                    try:
                        error_dict['context'] = json.loads(error_dict['context_json'])
                    except:
                        error_dict['context'] = {}
                del error_dict['context_json']
                errors.append(error_dict)
            
            return errors
    
    def mark_error_resolved(self, error_id: int, resolution_notes: str = "") -> bool:
        """Mark an error as resolved."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE error_logs 
                SET resolution_status = 'RESOLVED', resolution_notes = ?
                WHERE id = ?
            """, (resolution_notes, error_id))
            
            return cursor.rowcount > 0
    
    def export_errors(self, format: str = "json", **filters) -> str:
        """Export errors to file."""
        errors = self.get_errors(**filters)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            filename = f"error_export_{timestamp}.json"
            filepath = Path("logs") / filename
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump({
                    "export_info": {
                        "timestamp": datetime.now().isoformat(),
                        "total_errors": len(errors),
                        "filters_applied": filters
                    },
                    "errors": errors
                }, f, indent=2, default=str)
        
        elif format.lower() == "csv":
            import csv
            filename = f"error_export_{timestamp}.csv"
            filepath = Path("logs") / filename
            filepath.parent.mkdir(exist_ok=True)
            
            if errors:
                with open(filepath, 'w', newline='') as f:
                    # Flatten the data for CSV
                    flattened_errors = []
                    for error in errors:
                        flat_error = {k: v for k, v in error.items() if k != 'context'}
                        if 'context' in error and error['context']:
                            for ck, cv in error['context'].items():
                                flat_error[f'context_{ck}'] = cv
                        flattened_errors.append(flat_error)
                    
                    writer = csv.DictWriter(f, fieldnames=flattened_errors[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_errors)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Exported {len(errors)} errors to {filepath}")
        return str(filepath)
    
    def cleanup_old_errors(self, days: int = 30) -> int:
        """Clean up old error records."""
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM error_logs 
                WHERE timestamp < ? AND resolution_status = 'RESOLVED'
            """, (cutoff.isoformat(),))
            
            deleted_count = cursor.rowcount
            logger.info(f"Cleaned up {deleted_count} old error records")
            return deleted_count


# Global error logger instance
_error_logger = None

def get_error_logger() -> EnhancedErrorLogger:
    """Get global error logger instance."""
    global _error_logger
    if _error_logger is None:
        _error_logger = EnhancedErrorLogger()
    return _error_logger


# Convenience functions for common error logging
def log_vision_error(message: str, exception: Optional[Exception] = None, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM, **kwargs) -> int:
    """Log a vision-related error."""
    return get_error_logger().log_error(
        severity=severity,
        category=ErrorCategory.VISION,
        message=message,
        exception=exception,
        **kwargs
    )

def log_capture_error(message: str, exception: Optional[Exception] = None,
                     severity: ErrorSeverity = ErrorSeverity.HIGH, **kwargs) -> int:
    """Log a screen capture error."""
    return get_error_logger().log_error(
        severity=severity,
        category=ErrorCategory.CAPTURE,
        message=message,
        exception=exception,
        **kwargs
    )

def log_database_error(message: str, exception: Optional[Exception] = None,
                      severity: ErrorSeverity = ErrorSeverity.HIGH, **kwargs) -> int:
    """Log a database error."""
    return get_error_logger().log_error(
        severity=severity,
        category=ErrorCategory.DATABASE,
        message=message,
        exception=exception,
        **kwargs
    )

def log_gui_error(message: str, exception: Optional[Exception] = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, **kwargs) -> int:
    """Log a GUI error."""
    return get_error_logger().log_error(
        severity=severity,
        category=ErrorCategory.GUI,
        message=message,
        exception=exception,
        **kwargs
    )

def log_performance_issue(message: str, processing_time_ms: Optional[int] = None,
                         severity: ErrorSeverity = ErrorSeverity.LOW, **kwargs) -> int:
    """Log a performance issue."""
    additional_data = kwargs.get('additional_data', {})
    if processing_time_ms:
        additional_data['processing_time_ms'] = processing_time_ms
    kwargs['additional_data'] = additional_data
    
    return get_error_logger().log_error(
        severity=severity,
        category=ErrorCategory.PERFORMANCE,
        message=message,
        **kwargs
    )