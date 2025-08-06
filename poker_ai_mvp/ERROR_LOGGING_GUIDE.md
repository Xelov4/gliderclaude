# 🚨 Error Logging System - Comprehensive Guide

## Overview

The Poker AI MVP now includes a sophisticated error logging and analysis system designed to help developers identify, track, and resolve issues quickly and efficiently.

## 🏗️ Architecture

### Core Components

1. **EnhancedErrorLogger** - Central logging system with SQLite storage
2. **Error Categorization** - Systematic classification of error types
3. **Severity Levels** - Priority-based error ranking
4. **Dashboard Integration** - Real-time error monitoring in GUI
5. **Command-Line Tools** - Advanced analysis and reporting
6. **Export Capabilities** - Data export for external analysis

### Error Classification

#### Severity Levels
- **🔴 CRITICAL** - System crashes, data corruption, complete feature failure
- **🟠 HIGH** - Major functionality broken, user-impacting issues
- **🟡 MEDIUM** - Minor features affected, workarounds available
- **🟢 LOW** - Cosmetic issues, performance warnings, logging noise
- **ℹ️ INFO** - Informational messages, not actual errors

#### Categories
- **👁️ VISION** - Computer vision, detection, OCR errors
- **📷 CAPTURE** - Screen capture, MSS, frame processing issues
- **💾 DATABASE** - SQLite operations, data storage problems
- **🖥️ GUI** - User interface, tkinter, dashboard errors
- **🌐 NETWORK** - Network connectivity, HTTP requests
- **📁 FILE_SYSTEM** - File I/O, path resolution, permissions
- **⚙️ CONFIGURATION** - Settings, config file issues
- **⚡ PERFORMANCE** - Slow processing, memory leaks, CPU usage
- **❓ UNKNOWN** - Uncategorized errors

## 📊 Features

### Automatic Error Detection
- **Exception Tracking** - Automatic capture of Python exceptions
- **Performance Monitoring** - Detection of slow operations
- **Resource Monitoring** - Memory and CPU usage tracking
- **Context Capture** - System state at time of error
- **Stack Trace Logging** - Complete error trace information

### Error Deduplication
- **Smart Grouping** - Similar errors are grouped together
- **Occurrence Counting** - Track how many times each error occurs
- **Time Tracking** - First seen and last seen timestamps
- **Pattern Recognition** - Identify recurring issues

### Real-time Monitoring
- **Dashboard Widget** - Live error statistics in main GUI
- **Severity Breakdown** - Visual representation of error types
- **Category Analysis** - Breakdown by error category
- **Live Updates** - Real-time error notifications

## 🔧 Usage

### In Code

#### Basic Error Logging
```python
from src.data.error_logger import log_vision_error, ErrorSeverity

# Simple error logging
log_vision_error("Card detection failed", severity=ErrorSeverity.MEDIUM)

# With exception
try:
    risky_operation()
except Exception as e:
    log_vision_error("Operation failed", exception=e, severity=ErrorSeverity.HIGH)
```

#### Advanced Error Logging
```python
from src.data.error_logger import get_error_logger, ErrorSeverity, ErrorCategory

error_logger = get_error_logger()

error_logger.log_error(
    severity=ErrorSeverity.HIGH,
    category=ErrorCategory.VISION,
    message="YOLO detection timeout",
    component="vision.detection",
    function="detect_cards",
    exception=timeout_exception,
    session_id=current_session_id,
    additional_data={
        "timeout_duration": 5000,
        "image_size": "1920x1080",
        "model_path": "/models/yolo_cards.pt"
    }
)
```

#### Convenience Functions
```python
# Category-specific logging functions
log_capture_error("Screen capture failed", exception=e)
log_database_error("Connection timeout", severity=ErrorSeverity.HIGH)
log_gui_error("Widget creation failed", exception=e)
log_performance_issue("Slow processing", processing_time_ms=250)
```

### Dashboard Integration

The error monitoring widget is automatically integrated into the main dashboard and provides:

- **📊 Real-time Statistics** - Current error counts by severity
- **📂 Category Breakdown** - Errors grouped by type
- **🔍 Detailed View** - Clickable detailed error browser
- **📤 Export Options** - One-click data export
- **🧹 Cleanup Tools** - Automated old error removal

### Command-Line Analysis

#### Error Summary
```bash
# Show 24-hour error summary
python analyze_errors.py summary

# Custom time range
python analyze_errors.py summary --hours 6
```

#### Detailed Error View
```bash
# Show all errors
python analyze_errors.py details

# Filter by severity
python analyze_errors.py details --severity CRITICAL

# Filter by category and time
python analyze_errors.py details --category VISION --hours 12

# Limit results
python analyze_errors.py details --limit 25
```

#### Error Export
```bash
# Export to JSON
python analyze_errors.py export --format json

# Export filtered data
python analyze_errors.py export --format csv --severity HIGH --hours 24
```

#### Live Monitoring
```bash
# Real-time error monitoring
python analyze_errors.py monitor
```

#### Maintenance
```bash
# Clean up old resolved errors
python analyze_errors.py cleanup --days 30

# Dry run (see what would be cleaned)
python analyze_errors.py cleanup --dry-run
```

## 📈 Analytics & Reporting

### Error Summary Reports
- Total error counts (unique vs occurrences)
- Severity distribution
- Category breakdown with rates per hour
- Top error-generating components
- Recent critical errors

### Trend Analysis
- Error patterns over time
- Seasonal/daily patterns
- Component reliability metrics
- Performance degradation detection

### Export Formats
- **JSON** - Complete structured data with metadata
- **CSV** - Tabular format for spreadsheet analysis
- **Custom** - Extensible format system

## 🛠️ Configuration

### Database Settings
The error logging system uses SQLite by default:
- **Location**: `data/error_logs.db`
- **Retention**: Configurable cleanup of old errors
- **Backup**: Regular automated backups recommended

### Performance Settings
- **Batch Processing** - Errors are batched for performance
- **Memory Management** - Automatic cleanup of old cache entries
- **Index Optimization** - Database indexes for fast queries

## 🚀 Advanced Features

### Error Context Capture
Every error automatically captures:
```python
{
    "session_id": 123,
    "thread_name": "MainThread",
    "memory_usage_mb": 245.7,
    "cpu_usage_percent": 15.3,
    "active_processes": 87,
    "frame_number": 1247,
    "processing_time_ms": 156,
    "additional_data": {
        "custom_field": "custom_value"
    }
}
```

### Smart Error Resolution
- **Status Tracking** - OPEN, IN_PROGRESS, RESOLVED, IGNORED
- **Resolution Notes** - Documentation of fixes applied
- **Automatic Cleanup** - Old resolved errors are automatically cleaned

### Integration Points
- **Main Application** - Integrated into PokerAIApplication
- **Screen Capture** - Performance and error monitoring
- **Vision Pipeline** - Detection failure tracking
- **Database Operations** - Transaction error logging
- **GUI Components** - User interface error handling

## 📋 Best Practices

### When to Log Errors
- **Always** - Exceptions that affect functionality
- **Performance Issues** - Operations taking >100ms
- **Resource Problems** - High memory/CPU usage
- **User-Impacting** - Issues affecting user experience
- **Data Integrity** - Database/file corruption issues

### Error Message Guidelines
- **Be Specific** - Include relevant details and context
- **Be Actionable** - Provide information for debugging
- **Be Consistent** - Use standard formatting and terminology
- **Include Values** - Log relevant variable values

### Severity Guidelines
- **CRITICAL** - Application crash, data loss, security breach
- **HIGH** - Core feature broken, significant user impact
- **MEDIUM** - Minor feature issues, degraded performance
- **LOW** - Cosmetic issues, minor performance hits
- **INFO** - Status updates, configuration changes

## 🔍 Troubleshooting

### Common Issues

#### High Error Rates
1. Check error summary for patterns
2. Identify top error sources
3. Look for performance bottlenecks
4. Review recent changes/deployments

#### Performance Impact
1. Monitor error logging overhead
2. Adjust batch sizes if needed
3. Clean up old errors regularly
4. Consider log rotation settings

#### Storage Issues
1. Monitor database size growth
2. Implement regular cleanup
3. Archive old error data
4. Consider external storage for long-term retention

## 📚 API Reference

### Core Classes

#### EnhancedErrorLogger
```python
class EnhancedErrorLogger:
    def log_error(severity, category, message, **kwargs) -> int
    def get_error_summary(hours=24) -> Dict[str, Any]
    def get_errors(**filters) -> List[Dict[str, Any]]
    def mark_error_resolved(error_id, notes="") -> bool
    def export_errors(format="json", **filters) -> str
    def cleanup_old_errors(days=30) -> int
```

#### Error Models
```python
@dataclass
class ErrorRecord:
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    function: str
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    occurrence_count: int
    # ... additional fields

@dataclass
class ErrorContext:
    session_id: Optional[int]
    thread_name: str
    memory_usage_mb: float
    cpu_usage_percent: float
    additional_data: Dict[str, Any]
    # ... additional fields
```

### Convenience Functions
```python
# Category-specific logging
log_vision_error(message, exception=None, severity=MEDIUM, **kwargs)
log_capture_error(message, exception=None, severity=HIGH, **kwargs)
log_database_error(message, exception=None, severity=HIGH, **kwargs)
log_gui_error(message, exception=None, severity=MEDIUM, **kwargs)
log_performance_issue(message, processing_time_ms=None, severity=LOW, **kwargs)
```

## 🔮 Future Enhancements

### Planned Features
- **Machine Learning** - Automatic error pattern recognition
- **Alerting System** - Email/SMS notifications for critical errors
- **Integration APIs** - External monitoring system integration
- **Advanced Analytics** - Predictive error analysis
- **Cloud Storage** - Remote error log storage and analysis

### Extensibility
- **Custom Categories** - Add domain-specific error categories
- **Plugin System** - External error processors and analyzers
- **Custom Exporters** - Additional export format support
- **Webhook Integration** - Real-time error notifications

---

## ✅ Summary

The error logging system provides comprehensive error tracking, analysis, and debugging capabilities for the Poker AI MVP. It enables:

- **Proactive Problem Detection** - Catch issues before they impact users
- **Rapid Debugging** - Rich context and detailed error information
- **Performance Monitoring** - Track system performance over time
- **Data-Driven Improvements** - Make informed decisions based on error patterns
- **Operational Excellence** - Maintain high system reliability and uptime

Use this system to build a more robust, reliable, and maintainable poker AI application.