"""Error monitoring widgets for the dashboard."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from ..data.error_logger import get_error_logger, ErrorSeverity, ErrorCategory


class ErrorSummaryWidget(ttk.Frame):
    """Widget displaying error summary and statistics."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.error_logger = get_error_logger()
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the error summary UI."""
        # Title
        title_label = ttk.Label(self, text="🚨 Error Monitor", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Time range selector
        time_frame = ttk.Frame(self)
        time_frame.pack(fill="x", pady=5)
        
        ttk.Label(time_frame, text="Last:").pack(side="left")
        self.time_var = tk.StringVar(value="24")
        time_combo = ttk.Combobox(time_frame, textvariable=self.time_var, 
                                values=["1", "6", "12", "24", "48", "168"], 
                                width=8, state="readonly")
        time_combo.pack(side="left", padx=(5, 0))
        ttk.Label(time_frame, text="hours").pack(side="left", padx=(5, 0))
        
        refresh_btn = ttk.Button(time_frame, text="🔄", command=self.update_display, width=3)
        refresh_btn.pack(side="right")
        
        # Stats display
        stats_frame = ttk.LabelFrame(self, text="Error Statistics")
        stats_frame.pack(fill="both", expand=True, pady=5)
        
        # Severity breakdown
        severity_frame = ttk.Frame(stats_frame)
        severity_frame.pack(fill="x", pady=5)
        
        self.severity_labels = {}
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            frame = ttk.Frame(severity_frame)
            frame.pack(side="left", padx=10)
            
            color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "yellow", "LOW": "lightgreen"}[severity]
            
            ttk.Label(frame, text=severity, font=("Arial", 8, "bold")).pack()
            label = ttk.Label(frame, text="0", font=("Arial", 12), foreground=color)
            label.pack()
            
            self.severity_labels[severity] = label
        
        # Category breakdown
        category_frame = ttk.LabelFrame(stats_frame, text="Top Error Categories")
        category_frame.pack(fill="both", expand=True, pady=5)
        
        self.category_tree = ttk.Treeview(category_frame, columns=("Count", "Rate"), 
                                        height=6, show="tree headings")
        self.category_tree.heading("#0", text="Category")
        self.category_tree.heading("Count", text="Total")
        self.category_tree.heading("Rate", text="Rate/hr")
        
        self.category_tree.column("#0", width=100)
        self.category_tree.column("Count", width=60)
        self.category_tree.column("Rate", width=60)
        
        category_scroll = ttk.Scrollbar(category_frame, orient="vertical", 
                                      command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=category_scroll.set)
        
        self.category_tree.pack(side="left", fill="both", expand=True)
        category_scroll.pack(side="right", fill="y")
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="📊 View Details", 
                  command=self.show_error_details).pack(side="left", padx=2)
        ttk.Button(button_frame, text="📤 Export", 
                  command=self.export_errors).pack(side="left", padx=2)
        ttk.Button(button_frame, text="🧹 Cleanup", 
                  command=self.cleanup_old_errors).pack(side="left", padx=2)
    
    def update_display(self):
        """Update the error display with latest data."""
        try:
            hours = int(self.time_var.get())
            summary = self.error_logger.get_error_summary(hours=hours)
            
            # Update severity counts
            severity_stats = summary.get("severity_breakdown", {})
            for severity in self.severity_labels:
                count = severity_stats.get(severity, {}).get("total", 0)
                self.severity_labels[severity].config(text=str(count))
            
            # Update category tree
            self.category_tree.delete(*self.category_tree.get_children())
            
            category_stats = summary.get("category_breakdown", {})
            for category, stats in sorted(category_stats.items(), 
                                        key=lambda x: x[1]["total"], reverse=True):
                rate = round(stats["total"] / hours, 1)
                self.category_tree.insert("", "end", text=category, 
                                        values=(stats["total"], f"{rate}/hr"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update error display: {e}")
    
    def show_error_details(self):
        """Show detailed error window."""
        ErrorDetailWindow(self, self.error_logger)
    
    def export_errors(self):
        """Export errors to file."""
        try:
            hours = int(self.time_var.get())
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                format_type = "csv" if filename.endswith(".csv") else "json"
                exported_file = self.error_logger.export_errors(
                    format=format_type, 
                    hours=hours
                )
                messagebox.showinfo("Export Complete", 
                                  f"Errors exported to {exported_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export errors: {e}")
    
    def cleanup_old_errors(self):
        """Cleanup old resolved errors."""
        try:
            result = messagebox.askyesno("Confirm Cleanup", 
                                       "Remove old resolved errors (30+ days)?\n"
                                       "This action cannot be undone.")
            if result:
                count = self.error_logger.cleanup_old_errors(days=30)
                messagebox.showinfo("Cleanup Complete", 
                                  f"Removed {count} old error records")
                self.update_display()
        except Exception as e:
            messagebox.showerror("Cleanup Error", f"Failed to cleanup errors: {e}")


class ErrorDetailWindow:
    """Detailed error viewing window."""
    
    def __init__(self, parent, error_logger):
        self.error_logger = error_logger
        self.window = tk.Toplevel(parent)
        self.window.title("Error Details")
        self.window.geometry("900x600")
        self.setup_ui()
        self.load_errors()
    
    def setup_ui(self):
        """Setup the detailed error UI."""
        # Filters frame
        filter_frame = ttk.Frame(self.window)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Severity filter
        ttk.Label(filter_frame, text="Severity:").pack(side="left")
        self.severity_var = tk.StringVar()
        severity_combo = ttk.Combobox(filter_frame, textvariable=self.severity_var,
                                     values=["All"] + [s.value for s in ErrorSeverity],
                                     state="readonly", width=12)
        severity_combo.set("All")
        severity_combo.pack(side="left", padx=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side="left", padx=(10, 0))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var,
                                     values=["All"] + [c.value for c in ErrorCategory],
                                     state="readonly", width=12)
        category_combo.set("All")
        category_combo.pack(side="left", padx=5)
        
        # Time filter
        ttk.Label(filter_frame, text="Hours:").pack(side="left", padx=(10, 0))
        self.hours_var = tk.StringVar(value="24")
        hours_combo = ttk.Combobox(filter_frame, textvariable=self.hours_var,
                                  values=["6", "12", "24", "48", "168"],
                                  state="readonly", width=8)
        hours_combo.pack(side="left", padx=5)
        
        # Filter button
        ttk.Button(filter_frame, text="Apply Filter", 
                  command=self.load_errors).pack(side="left", padx=10)
        
        # Error list
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Treeview for errors
        columns = ("Time", "Severity", "Category", "Component", "Message", "Count")
        self.error_tree = ttk.Treeview(list_frame, columns=columns, 
                                      height=15, show="headings")
        
        for col in columns:
            self.error_tree.heading(col, text=col)
            width = {"Time": 120, "Severity": 80, "Category": 100, 
                    "Component": 120, "Message": 300, "Count": 60}[col]
            self.error_tree.column(col, width=width)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.error_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient="horizontal", 
                                command=self.error_tree.xview)
        
        self.error_tree.configure(yscrollcommand=v_scroll.set, 
                                 xscrollcommand=h_scroll.set)
        
        self.error_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        
        # Bind double-click to show error details
        self.error_tree.bind("<Double-1>", self.show_error_detail)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.window, text="Error Details")
        details_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.details_text = tk.Text(details_frame, height=8, wrap="word")
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", 
                                     command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")
        
        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_errors).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export Filtered", 
                  command=self.export_filtered).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side="right", padx=5)
    
    def load_errors(self):
        """Load and display errors based on filters."""
        try:
            # Clear existing items
            self.error_tree.delete(*self.error_tree.get_children())
            
            # Build filter parameters
            filters = {}
            
            if self.severity_var.get() != "All":
                filters["severity"] = ErrorSeverity(self.severity_var.get())
            
            if self.category_var.get() != "All":
                filters["category"] = ErrorCategory(self.category_var.get())
            
            if self.hours_var.get():
                filters["hours"] = int(self.hours_var.get())
            
            # Get errors
            errors = self.error_logger.get_errors(**filters, limit=500)
            
            # Populate tree
            for error in errors:
                timestamp = datetime.fromisoformat(error["timestamp"]).strftime("%m/%d %H:%M")
                
                self.error_tree.insert("", "end", values=(
                    timestamp,
                    error["severity"],
                    error["category"],
                    error["component"],
                    error["message"][:50] + "..." if len(error["message"]) > 50 else error["message"],
                    error["occurrence_count"]
                ), tags=(error["id"],))
            
            # Update status
            self.window.title(f"Error Details - {len(errors)} errors")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load errors: {e}")
    
    def show_error_detail(self, event):
        """Show detailed information for selected error."""
        selection = self.error_tree.selection()
        if not selection:
            return
        
        try:
            # Get error ID from tags
            item = self.error_tree.item(selection[0])
            error_id = item["tags"][0] if item["tags"] else None
            
            if error_id:
                # Get full error details
                errors = self.error_logger.get_errors(limit=1000)
                error = next((e for e in errors if e["id"] == int(error_id)), None)
                
                if error:
                    # Format error details
                    details = f"Error ID: {error['id']}\n"
                    details += f"Timestamp: {error['timestamp']}\n"
                    details += f"Severity: {error['severity']}\n"
                    details += f"Category: {error['category']}\n"
                    details += f"Component: {error['component']}\n"
                    details += f"Function: {error['function']}\n"
                    details += f"Message: {error['message']}\n"
                    details += f"Occurrences: {error['occurrence_count']}\n\n"
                    
                    if error.get('context'):
                        details += "Context:\n"
                        for key, value in error['context'].items():
                            details += f"  {key}: {value}\n"
                        details += "\n"
                    
                    if error.get('stack_trace'):
                        details += "Stack Trace:\n"
                        details += error['stack_trace']
                    
                    # Display in text widget
                    self.details_text.delete(1.0, "end")
                    self.details_text.insert(1.0, details)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show error details: {e}")
    
    def export_filtered(self):
        """Export currently filtered errors."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
            )
            
            if filename:
                # Build filters
                filters = {}
                if self.severity_var.get() != "All":
                    filters["severity"] = ErrorSeverity(self.severity_var.get())
                if self.category_var.get() != "All":
                    filters["category"] = ErrorCategory(self.category_var.get())
                if self.hours_var.get():
                    filters["hours"] = int(self.hours_var.get())
                
                format_type = "csv" if filename.endswith(".csv") else "json"
                exported_file = self.error_logger.export_errors(
                    format=format_type, **filters
                )
                messagebox.showinfo("Export Complete", 
                                  f"Filtered errors exported to {exported_file}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export errors: {e}")