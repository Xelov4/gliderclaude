#!/usr/bin/env python3
"""
Error Analysis Tool for Poker AI MVP

This command-line tool provides comprehensive error analysis and reporting
capabilities for debugging and improving the poker AI system.

Usage:
    python analyze_errors.py [command] [options]

Commands:
    summary     - Show error summary statistics
    details     - Show detailed error listings
    export      - Export errors to file
    cleanup     - Clean up old resolved errors
    monitor     - Real-time error monitoring
    trends      - Show error trends over time

Examples:
    python analyze_errors.py summary --hours 24
    python analyze_errors.py details --severity CRITICAL
    python analyze_errors.py export --format json --category VISION
    python analyze_errors.py monitor --live
"""

import argparse
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import os

# Fix encoding for Windows console
if sys.platform == "win32":
    os.system("chcp 65001 > nul")  # Set UTF-8 encoding

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data.error_logger import (
    get_error_logger, ErrorSeverity, ErrorCategory
)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_error_summary(hours: int = 24):
    """Print error summary statistics."""
    error_logger = get_error_logger()
    summary = error_logger.get_error_summary(hours=hours)
    
    print_header(f"Error Summary - Last {hours} Hours")
    
    print(f"[STATS] Total Unique Errors: {summary['total_unique_errors']}")
    print(f"[STATS] Total Occurrences: {summary['total_error_occurrences']}")
    print(f"[STATS] Generated: {summary['generated_at']}")
    
    print("\n[SEVERITY] Breakdown:")
    severity_stats = summary.get('severity_breakdown', {})
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if severity in severity_stats:
            stats = severity_stats[severity]
            icon = {'CRITICAL': '[!]', 'HIGH': '[H]', 'MEDIUM': '[M]', 'LOW': '[L]'}[severity]
            print(f"  {icon} {severity:<10}: {stats['unique']:>3} unique, {stats['total']:>4} total")
    
    print("\n[CATEGORY] Breakdown:")
    category_stats = summary.get('category_breakdown', {})
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['total'], reverse=True):
        rate = round(stats['total'] / hours, 1)
        print(f"  [C] {category:<15}: {stats['unique']:>3} unique, {stats['total']:>4} total ({rate}/hr)")
    
    print("\n[TOP] Error Sources:")
    top_components = summary.get('top_error_sources', [])
    for i, comp in enumerate(top_components[:10], 1):
        print(f"  {i:>2}. {comp['component']}.{comp['function']:<20}: {comp['total']:>3} errors")
    
    print("\n[CRITICAL] Recent Errors:")
    critical_errors = summary.get('recent_critical_errors', [])
    if critical_errors:
        for error in critical_errors:
            timestamp = datetime.fromisoformat(error['timestamp']).strftime("%m/%d %H:%M")
            print(f"  [!] [{timestamp}] {error['component']}.{error['function']}: {error['message'][:50]}...")
    else:
        print("  [OK] No critical errors in time range")


def print_error_details(severity=None, category=None, component=None, hours=None, limit=50):
    """Print detailed error listings."""
    error_logger = get_error_logger()
    
    # Build filters
    filters = {"limit": limit}
    if severity:
        filters["severity"] = ErrorSeverity(severity.upper())
    if category:
        filters["category"] = ErrorCategory(category.upper())
    if component:
        filters["component"] = component
    if hours:
        filters["hours"] = hours
    
    errors = error_logger.get_errors(**filters)
    
    filter_desc = []
    if severity:
        filter_desc.append(f"Severity: {severity}")
    if category:
        filter_desc.append(f"Category: {category}")
    if component:
        filter_desc.append(f"Component: {component}")
    if hours:
        filter_desc.append(f"Last {hours}h")
    
    title = f"Error Details ({', '.join(filter_desc) if filter_desc else 'All'})"
    print_header(title)
    
    if not errors:
        print("No errors found matching criteria.")
        return
    
    print(f"Found {len(errors)} errors\n")
    
    for i, error in enumerate(errors, 1):
        timestamp = datetime.fromisoformat(error['timestamp']).strftime("%m/%d %H:%M:%S")
        severity_icon = {'CRITICAL': '[!]', 'HIGH': '[H]', 'MEDIUM': '[M]', 'LOW': '[L]'}.get(error['severity'], '[?]')
        
        print(f"{i:>3}. {severity_icon} [{timestamp}] {error['severity']}/{error['category']}")
        print(f"     [LOC] {error['component']}.{error['function']}")
        print(f"     [MSG] {error['message']}")
        
        if error['occurrence_count'] > 1:
            print(f"     [CNT] Occurred {error['occurrence_count']} times")
        
        # Show context if available
        if error.get('context'):
            context = error['context']
            if context.get('memory_usage_mb'):
                print(f"     [SYS] Memory: {context['memory_usage_mb']:.1f}MB, CPU: {context.get('cpu_usage_percent', 0):.1f}%")
            if context.get('additional_data'):
                for key, value in context['additional_data'].items():
                    if key in ['processing_time_ms', 'callback_time_ms']:
                        print(f"     [TIME] {key}: {value}ms")
        
        print()  # Empty line between errors


def export_errors(format_type="json", **filters):
    """Export errors to file."""
    error_logger = get_error_logger()
    
    try:
        exported_file = error_logger.export_errors(format=format_type, **filters)
        print(f"✅ Errors exported to: {exported_file}")
        
        # Show summary of exported data
        errors = error_logger.get_errors(**filters)
        print(f"📊 Exported {len(errors)} error records")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")


def cleanup_old_errors(days=30, dry_run=False):
    """Clean up old resolved errors."""
    error_logger = get_error_logger()
    
    print_header(f"Cleanup Old Errors (>{days} days)")
    
    if dry_run:
        print("🔍 DRY RUN - No changes will be made")
        # Would need to implement dry run in error logger
        print("This would clean up old resolved errors...")
    else:
        try:
            count = error_logger.cleanup_old_errors(days=days)
            print(f"🧹 Cleaned up {count} old error records")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")


def monitor_errors_live():
    """Real-time error monitoring."""
    error_logger = get_error_logger()
    
    print_header("Live Error Monitor")
    print("Monitoring for new errors... (Press Ctrl+C to stop)")
    
    last_check = datetime.now()
    
    try:
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            # Get errors since last check
            now = datetime.now()
            hours_since = (now - last_check).total_seconds() / 3600
            
            if hours_since > 0.001:  # At least a few seconds
                recent_errors = error_logger.get_errors(hours=hours_since, limit=100)
                
                for error in recent_errors:
                    if datetime.fromisoformat(error['timestamp']) > last_check:
                        timestamp = datetime.fromisoformat(error['timestamp']).strftime("%H:%M:%S")
                        severity_icon = {'CRITICAL': '[!]', 'HIGH': '[H]', 'MEDIUM': '[M]', 'LOW': '[L]'}.get(error['severity'], '[?]')
                        
                        print(f"{severity_icon} [{timestamp}] {error['severity']}/{error['category']} - {error['component']}.{error['function']}: {error['message'][:60]}")
                
                last_check = now
    
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")


def show_error_trends(days=7):
    """Show error trends over time."""
    error_logger = get_error_logger()
    
    print_header(f"Error Trends - Last {days} Days")
    
    # Get errors for each day
    trends = {}
    for day_offset in range(days):
        day_start = datetime.now() - timedelta(days=day_offset+1)
        day_end = datetime.now() - timedelta(days=day_offset)
        
        # This would need additional functionality in error_logger
        # For now, approximate with hourly data
        day_errors = error_logger.get_errors(hours=24, limit=1000)
        day_count = len([e for e in day_errors 
                        if day_start <= datetime.fromisoformat(e['timestamp']) < day_end])
        
        trends[day_start.strftime("%m/%d")] = day_count
    
    # Display trend
    print("Daily Error Counts:")
    for date, count in sorted(trends.items()):
        bar = "█" * (count // 5) if count > 0 else ""
        print(f"  {date}: {count:>3} {bar}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Error Analysis Tool for Poker AI MVP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show error summary')
    summary_parser.add_argument('--hours', type=int, default=24, 
                               help='Time range in hours (default: 24)')
    
    # Details command
    details_parser = subparsers.add_parser('details', help='Show detailed errors')
    details_parser.add_argument('--severity', choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
                               help='Filter by severity')
    details_parser.add_argument('--category', 
                               choices=['VISION', 'CAPTURE', 'DATABASE', 'GUI', 'NETWORK', 
                                       'FILE_SYSTEM', 'CONFIGURATION', 'PERFORMANCE', 'UNKNOWN'],
                               help='Filter by category')
    details_parser.add_argument('--component', help='Filter by component name')
    details_parser.add_argument('--hours', type=int, help='Time range in hours')
    details_parser.add_argument('--limit', type=int, default=50, help='Maximum results')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export errors')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Export format')
    export_parser.add_argument('--severity', choices=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    export_parser.add_argument('--category', 
                              choices=['VISION', 'CAPTURE', 'DATABASE', 'GUI', 'NETWORK', 
                                      'FILE_SYSTEM', 'CONFIGURATION', 'PERFORMANCE', 'UNKNOWN'])
    export_parser.add_argument('--hours', type=int, help='Time range in hours')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old errors')
    cleanup_parser.add_argument('--days', type=int, default=30,
                               help='Age threshold in days (default: 30)')
    cleanup_parser.add_argument('--dry-run', action='store_true',
                               help='Show what would be cleaned without doing it')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Live error monitoring')
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Show error trends')
    trends_parser.add_argument('--days', type=int, default=7,
                              help='Number of days to analyze (default: 7)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'summary':
            print_error_summary(hours=args.hours)
        
        elif args.command == 'details':
            print_error_details(
                severity=args.severity,
                category=args.category,
                component=args.component,
                hours=args.hours,
                limit=args.limit
            )
        
        elif args.command == 'export':
            filters = {}
            if args.severity:
                filters['severity'] = ErrorSeverity(args.severity)
            if args.category:
                filters['category'] = ErrorCategory(args.category)
            if args.hours:
                filters['hours'] = args.hours
            
            export_errors(format_type=args.format, **filters)
        
        elif args.command == 'cleanup':
            cleanup_old_errors(days=args.days, dry_run=args.dry_run)
        
        elif args.command == 'monitor':
            monitor_errors_live()
        
        elif args.command == 'trends':
            show_error_trends(days=args.days)
    
    except Exception as e:
        print(f"[ERROR] Command failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())