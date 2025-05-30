"""
Dashboard Screen

Main dashboard showing overview of all simulations, system status,
and quick access to key metrics.
"""

from textual.widgets import Static, DataTable, ProgressBar
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.reactive import reactive
import time
from datetime import datetime


class DashboardScreen(Container):
    """Dashboard screen showing simulation overview."""
    
    CSS = """
    .dashboard-section {
        border: round $primary;
        margin: 1;
        padding: 1;
    }
    
    .dashboard-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .status-active {
        color: green;
        text-style: bold;
    }
    
    .status-failed {
        color: red;
        text-style: bold;
    }
    
    .status-completed {
        color: blue;
        text-style: bold;
    }
    
    .metric-value {
        text-style: bold;
        color: $accent;
    }
    """
    
    def compose(self):
        """Create dashboard layout."""
        with Vertical():
            # System Status Section
            with Container(classes="dashboard-section"):
                yield Static("📊 System Status", classes="dashboard-title")
                with Horizontal():
                    with Vertical():
                        yield Static("🔄 Active Simulations: ", id="active-simulations")
                        yield Static("✅ Completed Today: ", id="completed-today")
                        yield Static("❌ Failed Today: ", id="failed-today")
                        yield Static("📈 Total Requests: ", id="total-requests")
                    with Vertical():
                        yield Static("🖥️ System Load: ", id="system-load")
                        yield Static("💾 Memory Usage: ", id="memory-usage")
                        yield Static("🌐 Network Status: ", id="network-status")
                        yield Static("⏱️ Uptime: ", id="uptime")
            
            # Active Simulations Section
            with Container(classes="dashboard-section"):
                yield Static("🚀 Active Simulations", classes="dashboard-title")
                yield DataTable(id="active-simulations-table")
            
            # Recent Activity Section
            with Container(classes="dashboard-section"):
                yield Static("📝 Recent Activity", classes="dashboard-title")
                yield DataTable(id="recent-activity-table")
    
    def on_mount(self) -> None:
        """Initialize dashboard when mounted."""
        self.setup_tables()
        self.update_dashboard_data()
        
        # Set up periodic updates
        self.set_interval(5.0, self.update_dashboard_data)
    
    def setup_tables(self) -> None:
        """Set up data tables."""
        # Active simulations table
        active_table = self.query_one("#active-simulations-table")
        active_table.add_columns("ID", "Type", "Status", "Progress", "RPS", "Started")
        
        # Recent activity table
        recent_table = self.query_one("#recent-activity-table")
        recent_table.add_columns("Time", "Type", "Action", "Status", "Details")
    
    def update_dashboard_data(self) -> None:
        """Update dashboard with current data."""
        # Update system status
        self.query_one("#active-simulations").update("🔄 Active Simulations: 2")
        self.query_one("#completed-today").update("✅ Completed Today: 15")
        self.query_one("#failed-today").update("❌ Failed Today: 1")
        self.query_one("#total-requests").update("📈 Total Requests: 45,230")
        self.query_one("#system-load").update("🖥️ System Load: 65%")
        self.query_one("#memory-usage").update("💾 Memory Usage: 2.1GB")
        self.query_one("#network-status").update("🌐 Network Status: Online")
        self.query_one("#uptime").update("⏱️ Uptime: 2d 14h 32m")
        
        # Update active simulations table
        active_table = self.query_one("#active-simulations-table")
        active_table.clear()
        
        # Sample active simulations
        active_simulations = [
            ("sim_001", "API", "Running", "75%", "45.2", "14:30:15"),
            ("sim_002", "Database", "Running", "32%", "12.8", "15:45:30"),
        ]
        
        for sim in active_simulations:
            active_table.add_row(*sim)
        
        # Update recent activity table
        recent_table = self.query_one("#recent-activity-table")
        recent_table.clear()
        
        # Sample recent activities
        recent_activities = [
            ("16:23:45", "API", "Started", "Success", "Petstore simulation"),
            ("16:20:12", "API", "Completed", "Success", "User API test - 1000 requests"),
            ("16:15:30", "Database", "Started", "Running", "PostgreSQL ingestion"),
            ("16:10:08", "API", "Failed", "Error", "Auth token expired"),
            ("16:05:22", "System", "Started", "Success", "Fake Sphere CLI"),
        ]
        
        for activity in recent_activities:
            recent_table.add_row(*activity)