"""
Logs Screen

Real-time log viewing with filtering, search capabilities,
and log level management.
"""

from textual.widgets import Static, Input, Button, Select, Log, Checkbox
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.validation import Length
import time
from datetime import datetime


class LogsScreen(Container):
    """Real-time logs viewing screen."""
    
    CSS = """
    .logs-section {
        border: round $primary;
        margin: 1;
        padding: 1;
    }
    
    .logs-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .filter-controls {
        background: $surface;
        border: round $accent;
        padding: 1;
        margin-bottom: 1;
    }
    
    .log-viewer {
        height: 25;
        border: round $accent;
    }
    
    .filter-input {
        width: 30;
        margin: 0 1;
    }
    
    .filter-select {
        width: 20;
        margin: 0 1;
    }
    
    .log-info {
        color: cyan;
    }
    
    .log-warning {
        color: yellow;
    }
    
    .log-error {
        color: red;
        text-style: bold;
    }
    
    .log-debug {
        color: $text-muted;
    }
    
    .log-success {
        color: green;
    }
    """
    
    # Reactive attributes for filtering
    filter_text = reactive("")
    log_level = reactive("ALL")
    auto_scroll = reactive(True)
    
    def compose(self):
        """Create logs layout."""
        with Vertical():
            # Filter Controls
            with Container(classes="logs-section"):
                yield Static("🔍 Log Filters", classes="logs-title")
                
                with Container(classes="filter-controls"):
                    with Horizontal():
                        yield Static("Search:")
                        yield Input(
                            placeholder="Filter logs by text...",
                            id="log-search",
                            classes="filter-input"
                        )
                        
                        yield Static("Level:")
                        yield Select(
                            options=[
                                ("ALL", "All Levels"),
                                ("DEBUG", "Debug"),
                                ("INFO", "Info"),
                                ("WARNING", "Warning"),
                                ("ERROR", "Error"),
                            ],
                            value="ALL",
                            id="log-level-filter",
                            classes="filter-select"
                        )
                        
                        yield Static("Simulation:")
                        yield Select(
                            options=[
                                ("ALL", "All Simulations"),
                                ("sim_001", "Petstore API"),
                                ("sim_002", "User Database"),
                                ("sim_003", "Orders API"),
                            ],
                            value="ALL",
                            id="simulation-filter",
                            classes="filter-select"
                        )
                    
                    with Horizontal():
                        yield Checkbox("Auto-scroll", value=True, id="auto-scroll-checkbox")
                        yield Button("📋 Clear Logs", id="clear-logs")
                        yield Button("💾 Export Logs", id="export-logs")
                        yield Button("⏸️ Pause/Resume", id="pause-logs")
            
            # Log Viewer
            with Container(classes="logs-section"):
                yield Static("📝 Live Logs", classes="logs-title")
                yield Log(
                    id="log-viewer",
                    classes="log-viewer",
                    auto_scroll=True,
                    markup=True
                )
    
    def on_mount(self) -> None:
        """Initialize logs screen."""
        self.setup_log_viewer()
        
        # Start generating sample logs
        self.set_interval(1.0, self.add_sample_log)
    
    def setup_log_viewer(self) -> None:
        """Set up the log viewer with initial content."""
        log_viewer = self.query_one("#log-viewer")
        
        # Add some initial log entries
        initial_logs = [
            ("[cyan]INFO[/cyan]", "System", "Fake Sphere CLI started successfully"),
            ("[green]SUCCESS[/green]", "sim_001", "API simulation initialized"),
            ("[cyan]INFO[/cyan]", "sim_001", "Loaded Swagger specification from petstore.swagger.io"),
            ("[yellow]WARNING[/yellow]", "sim_002", "Database connection pool at 80% capacity"),
            ("[cyan]INFO[/cyan]", "sim_001", "Authentication: Bearer token acquired"),
            ("[green]SUCCESS[/green]", "sim_001", "Request completed: GET /api/pets - 200 OK"),
        ]
        
        for level, simulation, message in initial_logs:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_entry = f"[dim]{timestamp}[/dim] {level} [{simulation}] {message}"
            log_viewer.write_line(log_entry)
    
    def add_sample_log(self) -> None:
        """Add sample log entries to simulate real-time logging."""
        import random
        
        log_viewer = self.query_one("#log-viewer")
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Sample log entries
        sample_logs = [
            ("[cyan]INFO[/cyan]", "sim_001", "Request completed: GET /api/pets/123 - 200 OK (245ms)"),
            ("[cyan]INFO[/cyan]", "sim_002", "Inserted 50 records into users table"),
            ("[green]SUCCESS[/green]", "sim_001", "Authentication token refreshed"),
            ("[yellow]WARNING[/yellow]", "sim_003", "Response time exceeding threshold: 1.2s"),
            ("[cyan]INFO[/cyan]", "sim_001", "Request completed: POST /api/pets - 201 Created (189ms)"),
            ("[dim white]DEBUG[/dim white]", "System", "Memory usage: 2.1GB / Thread pool: 5/10 active"),
            ("[red]ERROR[/red]", "sim_003", "Request failed: GET /api/orders/456 - 404 Not Found"),
            ("[cyan]INFO[/cyan]", "sim_002", "Processing table: product_categories (500/1000 records)"),
            ("[green]SUCCESS[/green]", "sim_001", "Simulation milestone: 1000 requests completed"),
            ("[yellow]WARNING[/yellow]", "sim_001", "Rate limit approaching: 95/100 requests per minute"),
        ]
        
        # Randomly select and add a log entry
        level, simulation, message = random.choice(sample_logs)
        log_entry = f"[dim]{timestamp}[/dim] {level} [{simulation}] {message}"
        
        # Apply filters
        if self.should_show_log(log_entry, level, simulation):
            log_viewer.write_line(log_entry)
    
    def should_show_log(self, log_entry: str, level: str, simulation: str) -> bool:
        """Check if log entry should be shown based on current filters."""
        # Level filter
        level_filter = self.query_one("#log-level-filter").value
        if level_filter != "ALL":
            if level_filter not in log_entry:
                return False
        
        # Simulation filter
        sim_filter = self.query_one("#simulation-filter").value
        if sim_filter != "ALL":
            if sim_filter not in log_entry:
                return False
        
        # Text filter
        search_text = self.query_one("#log-search").value
        if search_text and search_text.lower() not in log_entry.lower():
            return False
        
        return True
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        if event.input.id == "log-search":
            self.filter_text = event.value
            self.refresh_logs()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle filter select changes."""
        if event.select.id == "log-level-filter":
            self.log_level = event.value
            self.refresh_logs()
        elif event.select.id == "simulation-filter":
            self.refresh_logs()
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes."""
        if event.checkbox.id == "auto-scroll-checkbox":
            self.auto_scroll = event.value
            log_viewer = self.query_one("#log-viewer")
            log_viewer.auto_scroll = self.auto_scroll
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "clear-logs":
            self.clear_logs()
        elif button_id == "export-logs":
            self.export_logs()
        elif button_id == "pause-logs":
            self.toggle_log_updates()
    
    def refresh_logs(self) -> None:
        """Refresh log display based on current filters."""
        # In a real implementation, this would re-filter the log history
        # For now, just clear and restart with filtered view
        pass
    
    def clear_logs(self) -> None:
        """Clear the log viewer."""
        log_viewer = self.query_one("#log-viewer")
        log_viewer.clear()
        
        # Add a cleared notification
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_viewer.write_line(f"[dim]{timestamp}[/dim] [yellow]SYSTEM[/yellow] [System] Log viewer cleared by user")
    
    def export_logs(self) -> None:
        """Export logs to file."""
        # TODO: Implement log export functionality
        log_viewer = self.query_one("#log-viewer")
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_viewer.write_line(f"[dim]{timestamp}[/dim] [green]SUCCESS[/green] [System] Logs exported to logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    def toggle_log_updates(self) -> None:
        """Pause or resume log updates."""
        # TODO: Implement pause/resume functionality
        pass