"""
Monitoring Screen

Real-time monitoring of active simulations with live updates,
progress tracking, and control capabilities.
"""

from textual.widgets import Static, DataTable, ProgressBar, Button
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
import time
import random


class MonitoringScreen(Container):
    """Real-time monitoring screen for active simulations."""
    
    CSS = """
    .monitor-section {
        border: round $primary;
        margin: 1;
        padding: 1;
    }
    
    .monitor-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .progress-container {
        margin: 1 0;
    }
    
    .metric-display {
        text-align: center;
        padding: 1;
        border: round $accent;
        margin: 0 1;
    }
    
    .metric-value {
        text-style: bold;
        color: $accent;
        text-size: 2;
    }
    
    .metric-label {
        color: $text-muted;
    }
    
    .control-button {
        margin: 0 1;
    }
    
    .status-running {
        color: green;
        text-style: bold;
    }
    
    .status-paused {
        color: yellow;
        text-style: bold;
    }
    
    .status-failed {
        color: red;
        text-style: bold;
    }
    """
    
    def compose(self):
        """Create monitoring layout."""
        with Vertical():
            # Active Simulations Overview
            with Container(classes="monitor-section"):
                yield Static("🔄 Active Simulations", classes="monitor-title")
                yield DataTable(id="monitoring-table")
                
                # Control buttons
                with Horizontal():
                    yield Button("⏸️ Pause Selected", id="pause-simulation", classes="control-button")
                    yield Button("▶️ Resume Selected", id="resume-simulation", classes="control-button")
                    yield Button("⏹️ Stop Selected", id="stop-simulation", classes="control-button", variant="error")
                    yield Button("🔄 Refresh", id="refresh-monitoring", classes="control-button")
            
            # Detailed View for Selected Simulation
            with Container(classes="monitor-section"):
                yield Static("📊 Simulation Details", classes="monitor-title")
                
                # Metrics row
                with Horizontal():
                    with Container(classes="metric-display"):
                        yield Static("0", id="current-requests", classes="metric-value")
                        yield Static("Current Requests", classes="metric-label")
                    
                    with Container(classes="metric-display"):
                        yield Static("0.0", id="requests-per-sec", classes="metric-value")
                        yield Static("Requests/sec", classes="metric-label")
                    
                    with Container(classes="metric-display"):
                        yield Static("0ms", id="avg-response-time", classes="metric-value")
                        yield Static("Avg Response", classes="metric-label")
                    
                    with Container(classes="metric-display"):
                        yield Static("0%", id="error-rate", classes="metric-value")
                        yield Static("Error Rate", classes="metric-label")
                
                # Progress bar
                with Container(classes="progress-container"):
                    yield Static("Progress:", id="progress-label")
                    yield ProgressBar(total=100, id="simulation-progress")
                
                # Real-time chart (ASCII version)
                yield Static(id="realtime-chart", classes="metric-display")
            
            # Live Activity Feed
            with Container(classes="monitor-section"):
                yield Static("📡 Live Activity Feed", classes="monitor-title")
                yield DataTable(id="activity-feed")
    
    def on_mount(self) -> None:
        """Initialize monitoring screen."""
        self.setup_tables()
        self.update_monitoring_data()
        
        # Set up real-time updates
        self.set_interval(2.0, self.update_monitoring_data)
        self.set_interval(1.0, self.update_live_metrics)
    
    def setup_tables(self) -> None:
        """Set up monitoring tables."""
        # Main monitoring table
        monitoring_table = self.query_one("#monitoring-table")
        monitoring_table.add_columns(
            "ID", "Name", "Type", "Status", "Progress", "RPS", "Errors", "Runtime", "Actions"
        )
        
        # Activity feed table
        activity_table = self.query_one("#activity-feed")
        activity_table.add_columns("Time", "Simulation", "Event", "Details")
    
    def update_monitoring_data(self) -> None:
        """Update monitoring table with current simulations."""
        monitoring_table = self.query_one("#monitoring-table")
        monitoring_table.clear()
        
        # Sample active simulations
        simulations = [
            ("sim_001", "Petstore API", "API", "Running", "75%", "45.2", "2", "00:14:32", "⏸️ ⏹️"),
            ("sim_002", "User DB", "Database", "Running", "32%", "12.8", "0", "00:05:15", "⏸️ ⏹️"),
            ("sim_003", "Orders API", "API", "Paused", "60%", "0.0", "5", "00:22:45", "▶️ ⏹️"),
        ]
        
        for sim in simulations:
            monitoring_table.add_row(*sim)
        
        # Update activity feed
        activity_table = self.query_one("#activity-feed")
        
        # Add new activity (simulate real-time updates)
        current_time = time.strftime("%H:%M:%S")
        activities = [
            (current_time, "sim_001", "Request completed", "200 OK - /api/pets/123"),
            (current_time, "sim_002", "Data inserted", "users table - 100 records"),
            (current_time, "sim_001", "Authentication", "Bearer token refreshed"),
        ]
        
        for activity in activities:
            activity_table.add_row(*activity)
        
        # Keep only last 10 activities
        if activity_table.row_count > 10:
            while activity_table.row_count > 10:
                activity_table.remove_row(0)
    
    def update_live_metrics(self) -> None:
        """Update live metrics for selected simulation."""
        # Simulate real-time metrics
        current_requests = random.randint(1500, 2000)
        rps = round(random.uniform(40, 50), 1)
        response_time = random.randint(150, 300)
        error_rate = round(random.uniform(0, 5), 1)
        progress = min(100, random.randint(70, 85))
        
        # Update metric displays
        self.query_one("#current-requests").update(str(current_requests))
        self.query_one("#requests-per-sec").update(str(rps))
        self.query_one("#avg-response-time").update(f"{response_time}ms")
        self.query_one("#error-rate").update(f"{error_rate}%")
        
        # Update progress bar
        progress_bar = self.query_one("#simulation-progress")
        progress_bar.progress = progress
        
        # Update progress label
        self.query_one("#progress-label").update(f"Progress: {progress}% ({current_requests}/2000)")
        
        # Update chart with ASCII visualization
        chart = self.query_one("#realtime-chart")
        
        # Generate sample data for the chart
        data_points = 20  # Show 20 data points
        y_data = [random.uniform(35, 55) for _ in range(data_points)]  # RPS data
        
        # Create a simple ASCII chart
        max_value = max(y_data)
        min_value = min(y_data)
        range_value = max(max_value - min_value, 1)  # Avoid division by zero
        
        chart_height = 10
        ascii_chart = []
        
        # Add title
        ascii_chart.append("Real-time Request Rate")
        ascii_chart.append(f"Max: {max_value:.1f} RPS | Min: {min_value:.1f} RPS")
        ascii_chart.append("-" * 50)
        
        # Generate chart rows
        for i in range(chart_height, 0, -1):
            row = []
            threshold = min_value + (range_value * i / chart_height)
            
            for value in y_data:
                if value >= threshold:
                    row.append("█")
                else:
                    row.append(" ")
            
            # Add y-axis label every few rows
            if i == chart_height or i == 1 or i == chart_height // 2:
                y_label = f"{threshold:4.1f} |"
            else:
                y_label = "     |"
                
            ascii_chart.append(f"{y_label} {''.join(row)}")
        
        # Add x-axis
        ascii_chart.append("     " + "-" * data_points)
        ascii_chart.append("     " + "Time (seconds ago)")
        
        # Update the chart widget with ASCII visualization
        chart.update("\n".join(ascii_chart))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle monitoring control buttons."""
        button_id = event.button.id
        
        if button_id == "pause-simulation":
            self.pause_selected_simulation()
        elif button_id == "resume-simulation":
            self.resume_selected_simulation()
        elif button_id == "stop-simulation":
            self.stop_selected_simulation()
        elif button_id == "refresh-monitoring":
            self.update_monitoring_data()
    
    def pause_selected_simulation(self) -> None:
        """Pause the currently selected simulation."""
        # TODO: Implement pause functionality
        pass
    
    def resume_selected_simulation(self) -> None:
        """Resume the currently selected simulation."""
        # TODO: Implement resume functionality
        pass
    
    def stop_selected_simulation(self) -> None:
        """Stop the currently selected simulation."""
        # TODO: Implement stop functionality
        pass