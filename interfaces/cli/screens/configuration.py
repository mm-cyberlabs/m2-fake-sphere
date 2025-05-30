"""
Configuration Screen

Interactive configuration screen for setting up new API simulations
and database data ingestions.
"""

from textual.widgets import (
    Static, Input, Button, Select, TextArea, Checkbox, 
    RadioSet, RadioButton, TabbedContent, TabPane
)
from textual.containers import Container, Horizontal, Vertical
from textual.validation import Number
from textual.screen import Screen


class ConfigurationScreen(Container):
    """Configuration screen for setting up simulations."""
    
    CSS = """
    .config-section {
        border: round $primary;
        margin: 1;
        padding: 1;
        height: auto;
    }
    
    .config-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .input-group {
        margin: 1 0;
    }
    
    .input-label {
        width: 20;
        text-align: right;
        padding-right: 2;
    }
    
    .input-field {
        flex: 1;
    }
    
    .button-group {
        margin-top: 2;
        text-align: center;
    }
    
    .preview-section {
        background: $surface;
        border: round $accent;
        margin: 1;
        padding: 1;
        height: 10;
    }
    """
    
    def compose(self):
        """Create configuration layout."""
        with TabbedContent():
            with TabPane("🌐 API Simulation", id="api-tab"):
                with Vertical():
                    # Basic Configuration
                    with Container(classes="config-section"):
                        yield Static("📝 Basic Configuration", classes="config-title")
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Simulation Name:", classes="input-label")
                            yield Input(
                                placeholder="e.g., Petstore API Test",
                                id="api-sim-name",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("API Source:", classes="input-label")
                            yield Input(
                                placeholder="Swagger URL or file path",
                                id="api-source",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Environment:", classes="input-label")
                            yield Select(
                                options=[
                                    ("dev", "Development"),
                                    ("staging", "Staging"),
                                    ("production", "Production"),
                                ],
                                id="api-environment",
                                classes="input-field"
                            )
                    
                    # Load Configuration
                    with Container(classes="config-section"):
                        yield Static("⚡ Load Configuration", classes="config-title")
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Total Requests:", classes="input-label")
                            yield Input(
                                placeholder="1000",
                                validators=[Number(minimum=1, maximum=1000000)],
                                id="api-total-requests",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Concurrent Threads:", classes="input-label")
                            yield Input(
                                placeholder="5",
                                validators=[Number(minimum=1, maximum=50)],
                                id="api-threads",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Request Delay (ms):", classes="input-label")
                            yield Input(
                                placeholder="0",
                                validators=[Number(minimum=0, maximum=10000)],
                                id="api-delay",
                                classes="input-field"
                            )
                    
                    # Authentication Configuration
                    with Container(classes="config-section"):
                        yield Static("🔐 Authentication", classes="config-title")
                        
                        with RadioSet(id="auth-type"):
                            yield RadioButton("None", value=True, id="auth-none")
                            yield RadioButton("Bearer Token", id="auth-bearer")
                            yield RadioButton("API Key", id="auth-apikey")
                            yield RadioButton("Basic Auth", id="auth-basic")
                        
                        # Auth details will be shown based on selection
                        with Container(id="auth-details"):
                            pass
                    
                    # Preview and Actions
                    with Container(classes="config-section"):
                        yield Static("👁️ Configuration Preview", classes="config-title")
                        yield TextArea(
                            text="# Configuration will be shown here\n# after you fill in the form above",
                            read_only=True,
                            id="api-config-preview",
                            classes="preview-section"
                        )
                        
                        with Horizontal(classes="button-group"):
                            yield Button("💾 Save Template", id="save-api-template")
                            yield Button("🔍 Validate Config", id="validate-api-config")
                            yield Button("🚀 Start Simulation", id="start-api-simulation", variant="primary")
            
            with TabPane("🗄️ Database Ingestion", id="db-tab"):
                with Vertical():
                    # Database Connection
                    with Container(classes="config-section"):
                        yield Static("🗄️ Database Connection", classes="config-title")
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Simulation Name:", classes="input-label")
                            yield Input(
                                placeholder="e.g., User Database Ingestion",
                                id="db-sim-name",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Database Type:", classes="input-label")
                            yield Select(
                                options=[
                                    ("postgresql", "PostgreSQL"),
                                    ("mysql", "MySQL"),
                                    ("sqlite", "SQLite"),
                                    ("mssql", "SQL Server"),
                                ],
                                id="db-type",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Host:", classes="input-label")
                            yield Input(
                                placeholder="localhost",
                                id="db-host",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Port:", classes="input-label")
                            yield Input(
                                placeholder="5432",
                                validators=[Number(minimum=1, maximum=65535)],
                                id="db-port",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Database Name:", classes="input-label")
                            yield Input(
                                placeholder="myapp_db",
                                id="db-name",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Username:", classes="input-label")
                            yield Input(
                                placeholder="username",
                                id="db-username",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Password:", classes="input-label")
                            yield Input(
                                placeholder="password",
                                password=True,
                                id="db-password",
                                classes="input-field"
                            )
                    
                    # Data Generation Settings
                    with Container(classes="config-section"):
                        yield Static("📊 Data Generation", classes="config-title")
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Records per Table:", classes="input-label")
                            yield Input(
                                placeholder="1000",
                                validators=[Number(minimum=1, maximum=1000000)],
                                id="db-records",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Static("Target Schema:", classes="input-label")
                            yield Input(
                                placeholder="public (leave empty for all schemas)",
                                id="db-schema",
                                classes="input-field"
                            )
                        
                        with Horizontal(classes="input-group"):
                            yield Checkbox("Preserve existing data", id="db-preserve-data")
                        
                        with Horizontal(classes="input-group"):
                            yield Checkbox("Generate foreign key relationships", id="db-fk-relationships", value=True)
                    
                    # Preview and Actions
                    with Container(classes="config-section"):
                        yield Static("👁️ Configuration Preview", classes="config-title")
                        yield TextArea(
                            text="# Database configuration will be shown here\n# after you fill in the form above",
                            read_only=True,
                            id="db-config-preview",
                            classes="preview-section"
                        )
                        
                        with Horizontal(classes="button-group"):
                            yield Button("🔗 Test Connection", id="test-db-connection")
                            yield Button("💾 Save Template", id="save-db-template")
                            yield Button("🗄️ Start Ingestion", id="start-db-ingestion", variant="primary")
            
            with TabPane("📋 Templates", id="templates-tab"):
                with Vertical():
                    with Container(classes="config-section"):
                        yield Static("📋 Saved Templates", classes="config-title")
                        yield Static("Manage your saved configuration templates")
                        
                        # TODO: Add template management UI
                        yield Static("🚧 Template management coming soon...")
    # The helper methods are removed as their content is now directly in the compose method
    
    def on_mount(self) -> None:
        """Initialize configuration screen."""
        # Set up form validation and preview updates
        self.setup_form_validation()
    
    def setup_form_validation(self) -> None:
        """Set up form validation and live preview updates."""
        # TODO: Implement form validation and preview updates
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses in configuration forms."""
        button_id = event.button.id
        
        if button_id == "start-api-simulation":
            self.start_api_simulation()
        elif button_id == "start-db-ingestion":
            self.start_db_ingestion()
        elif button_id == "test-db-connection":
            self.test_database_connection()
        elif button_id == "validate-api-config":
            self.validate_api_configuration()
    
    def start_api_simulation(self) -> None:
        """Start API simulation with current configuration."""
        # TODO: Collect form data and start simulation
        pass
    
    def start_db_ingestion(self) -> None:
        """Start database ingestion with current configuration."""
        # TODO: Collect form data and start ingestion
        pass
    
    def test_database_connection(self) -> None:
        """Test database connection."""
        # TODO: Test database connection with provided credentials
        pass
    
    def validate_api_configuration(self) -> None:
        """Validate API configuration."""
        # TODO: Validate API configuration and Swagger spec
        pass