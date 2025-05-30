"""
Main CLI Application Entry Point

This is the main entry point for the Fake Sphere CLI application.
It provides a modern, terminal-native interface for managing simulations.
"""

import sys
import os
from pathlib import Path

# Add the core module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "m2_fake_sphere" / "src"))

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Log
from textual.screen import Screen
from textual import events

from screens.dashboard import DashboardScreen
from screens.configuration import ConfigurationScreen
from screens.monitoring import MonitoringScreen
from screens.logs import LogsScreen
from screens.metrics import MetricsScreen


class FakeSphereApp(App):
    """Main Fake Sphere CLI Application."""
    
    CSS = """
    .title {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }
    
    .sidebar {
        dock: left;
        width: 25;
        background: $surface;
        border-right: wide $primary;
    }
    
    .main-content {
        dock: right;
        width: 100%;
        height: 100%;
        background: $background;
    }
    
    .nav-button {
        width: 100%;
        height: 3;
        margin: 1 0;
        background: $surface;
        border: none;
    }
    
    .nav-button:hover {
        background: $primary 30%;
    }
    
    .nav-button.-active {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    .status-bar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }
    """
    
    BINDINGS = [
        ("d", "show_dashboard", "Dashboard"),
        ("c", "show_config", "Configuration"),
        ("m", "show_monitoring", "Monitoring"),
        ("l", "show_logs", "Logs"),
        ("s", "show_metrics", "Metrics"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_screen_name = "dashboard"
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        with Container():
            # Title bar
            yield Static("🌐 FAKE SPHERE - API Simulation Engine", classes="title")
            
            with Horizontal():
                # Sidebar navigation
                with Vertical(classes="sidebar"):
                    yield Static("Navigation", id="nav-title")
                    yield Button("📊 Dashboard", id="nav-dashboard", classes="nav-button -active")
                    yield Button("⚙️ Configuration", id="nav-config", classes="nav-button")
                    yield Button("👁️ Monitoring", id="nav-monitoring", classes="nav-button")
                    yield Button("📝 Logs", id="nav-logs", classes="nav-button")
                    yield Button("📈 Metrics", id="nav-metrics", classes="nav-button")
                    
                    yield Static("Quick Actions", id="actions-title")
                    yield Button("🚀 New API Simulation", id="new-api-sim", classes="nav-button")
                    yield Button("🗄️ New DB Ingestion", id="new-db-ingestion", classes="nav-button")
                    yield Button("⏹️ Stop All", id="stop-all", classes="nav-button")
                
                # Main content area
                with Container(classes="main-content"):
                    yield DashboardScreen(id="dashboard-content")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "Fake Sphere CLI"
        self.sub_title = "API Simulation & Database Data Generation"
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        # Clear active state from all nav buttons
        for button in self.query(".nav-button"):
            button.remove_class("-active")
        
        if button_id == "nav-dashboard":
            self._switch_to_screen("dashboard", DashboardScreen())
            event.button.add_class("-active")
            
        elif button_id == "nav-config":
            self._switch_to_screen("configuration", ConfigurationScreen())
            event.button.add_class("-active")
            
        elif button_id == "nav-monitoring":
            self._switch_to_screen("monitoring", MonitoringScreen())
            event.button.add_class("-active")
            
        elif button_id == "nav-logs":
            self._switch_to_screen("logs", LogsScreen())
            event.button.add_class("-active")
            
        elif button_id == "nav-metrics":
            self._switch_to_screen("metrics", MetricsScreen())
            event.button.add_class("-active")
            
        elif button_id == "new-api-sim":
            self.action_new_api_simulation()
            
        elif button_id == "new-db-ingestion":
            self.action_new_db_ingestion()
            
        elif button_id == "stop-all":
            self.action_stop_all()
    
    def _switch_to_screen(self, screen_name: str, screen_widget):
        """Switch to a different screen."""
        main_content = self.query_one(".main-content")
        main_content.remove_children()
        main_content.mount(screen_widget)
        self.current_screen_name = screen_name
    
    def action_show_dashboard(self) -> None:
        """Show dashboard screen."""
        self.query_one("#nav-dashboard").press()
    
    def action_show_config(self) -> None:
        """Show configuration screen."""
        self.query_one("#nav-config").press()
    
    def action_show_monitoring(self) -> None:
        """Show monitoring screen."""
        self.query_one("#nav-monitoring").press()
    
    def action_show_logs(self) -> None:
        """Show logs screen."""
        self.query_one("#nav-logs").press()
    
    def action_show_metrics(self) -> None:
        """Show metrics screen."""
        self.query_one("#nav-metrics").press()
    
    def action_new_api_simulation(self) -> None:
        """Create new API simulation."""
        # Switch to configuration screen
        self.action_show_config()
        # TODO: Auto-select API simulation mode
    
    def action_new_db_ingestion(self) -> None:
        """Create new database ingestion."""
        # Switch to configuration screen
        self.action_show_config()
        # TODO: Auto-select DB ingestion mode
    
    def action_stop_all(self) -> None:
        """Stop all running simulations."""
        # TODO: Implement stop all functionality
        pass


def main():
    """Main entry point for the CLI application."""
    app = FakeSphereApp()
    app.run()


if __name__ == "__main__":
    main()