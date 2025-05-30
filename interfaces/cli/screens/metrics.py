"""
Metrics Screen

Comprehensive metrics visualization with charts, statistics,
and historical data analysis.
"""

from textual.widgets import Static, DataTable, Button, Select, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
import random
import time
from datetime import datetime, timedelta


class MetricsScreen(Container):
    """Comprehensive metrics visualization screen."""
    
    CSS = """
    .metrics-section {
        border: round $primary;
        margin: 1;
        padding: 1;
    }
    
    .metrics-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .stat-grid {
        height: 8;
    }
    
    .stat-box {
        border: round $accent;
        text-align: center;
        padding: 1;
        margin: 0 1;
        height: 6;
    }
    
    .stat-value {
        text-style: bold;
        color: $accent;
        text-size: 2;
    }
    
    .stat-label {
        color: $text-muted;
    }
    
    .stat-change {
        color: green;
        text-style: bold;
    }
    
    .stat-change-negative {
        color: red;
        text-style: bold;
    }
    
    .chart-container {
        height: 20;
        border: round $accent;
        padding: 1;
    }
    
    .filter-bar {
        background: $surface;
        padding: 1;
        margin-bottom: 1;
        border: round $accent;
    }
    """
    
    def compose(self):
        """Create metrics layout."""
        with TabbedContent():
            with TabPane("📊 Overview", id="overview-tab"):
                yield self.create_overview_tab()
            
            with TabPane("📈 Performance", id="performance-tab"):
                yield self.create_performance_tab()
            
            with TabPane("🔍 Analysis", id="analysis-tab"):
                yield self.create_analysis_tab()
            
            with TabPane("📋 Reports", id="reports-tab"):
                yield self.create_reports_tab()
    
    def create_overview_tab(self) -> Container:
        """Create overview metrics tab."""
        with Vertical():
            # Quick Stats
            with Container(classes="metrics-section"):
                yield Static("📊 Quick Statistics", classes="metrics-title")
                
                with Container(classes="filter-bar"):
                    with Horizontal():
                        yield Static("Time Period:")
                        yield Select(
                            options=[
                                ("1h", "Last Hour"),
                                ("24h", "Last 24 Hours"),
                                ("7d", "Last 7 Days"),
                                ("30d", "Last 30 Days"),
                            ],
                            value="24h",
                            id="time-period-filter"
                        )
                        yield Button("🔄 Refresh", id="refresh-metrics")
                
                with Container(classes="stat-grid"):
                    with Horizontal():
                        with Container(classes="stat-box"):
                            yield Static("2,847", id="total-requests", classes="stat-value")
                            yield Static("Total Requests", classes="stat-label")
                            yield Static("↗ +12.5%", classes="stat-change")
                        
                        with Container(classes="stat-box"):
                            yield Static("42.3", id="avg-rps", classes="stat-value")
                            yield Static("Avg RPS", classes="stat-label")
                            yield Static("↗ +8.2%", classes="stat-change")
                        
                        with Container(classes="stat-box"):
                            yield Static("245ms", id="avg-response-time", classes="stat-value")
                            yield Static("Avg Response", classes="stat-label")
                            yield Static("↘ -5.1%", classes="stat-change")
                        
                        with Container(classes="stat-box"):
                            yield Static("2.4%", id="error-rate", classes="stat-value")
                            yield Static("Error Rate", classes="stat-label")
                            yield Static("↘ -1.2%", classes="stat-change")
            
            # Request Volume Chart
            with Container(classes="metrics-section"):
                yield Static("📈 Request Volume Over Time", classes="metrics-title")
                yield Static(id="volume-chart", classes="chart-container")
            
            # Status Code Distribution
            with Container(classes="metrics-section"):
                yield Static("🎯 Status Code Distribution", classes="metrics-title")
                yield DataTable(id="status-codes-table")
    
    def create_performance_tab(self) -> Container:
        """Create performance metrics tab."""
        with Vertical():
            # Response Time Analysis
            with Container(classes="metrics-section"):
                yield Static("⚡ Response Time Analysis", classes="metrics-title")
                yield Static(id="response-time-chart", classes="chart-container")
            
            # Throughput Analysis
            with Container(classes="metrics-section"):
                yield Static("🚀 Throughput Analysis", classes="metrics-title")
                yield Static(id="throughput-chart", classes="chart-container")
            
            # Performance Summary
            with Container(classes="metrics-section"):
                yield Static("📋 Performance Summary", classes="metrics-title")
                yield DataTable(id="performance-summary-table")
    
    def create_analysis_tab(self) -> Container:
        """Create analysis metrics tab."""
        with Vertical():
            # Endpoint Performance
            with Container(classes="metrics-section"):
                yield Static("🎯 Endpoint Performance", classes="metrics-title")
                yield DataTable(id="endpoint-performance-table")
            
            # Error Analysis
            with Container(classes="metrics-section"):
                yield Static("❌ Error Analysis", classes="metrics-title")
                yield DataTable(id="error-analysis-table")
            
            # Trends and Patterns
            with Container(classes="metrics-section"):
                yield Static("📊 Trends and Patterns", classes="metrics-title")
                yield Static(id="trends-chart", classes="chart-container")
    
    def create_reports_tab(self) -> Container:
        """Create reports tab."""
        with Vertical():
            # Report Generation
            with Container(classes="metrics-section"):
                yield Static("📋 Generate Reports", classes="metrics-title")
                yield Static("🚧 Report generation coming soon...")
                
                with Horizontal():
                    yield Button("📊 Performance Report", id="gen-performance-report")
                    yield Button("❌ Error Report", id="gen-error-report")
                    yield Button("📈 Trend Analysis", id="gen-trend-report")
                    yield Button("📋 Summary Report", id="gen-summary-report")
    
    def on_mount(self) -> None:
        """Initialize metrics screen."""
        self.setup_tables()
        self.setup_charts()
        self.update_metrics()
        
        # Set up periodic updates
        self.set_interval(5.0, self.update_metrics)
        self.set_interval(2.0, self.update_charts)
    
    def setup_tables(self) -> None:
        """Set up metrics tables."""
        # Status codes table
        status_table = self.query_one("#status-codes-table")
        status_table.add_columns("Status Code", "Count", "Percentage", "Description")
        
        # Performance summary table
        try:
            perf_table = self.query_one("#performance-summary-table")
            perf_table.add_columns("Metric", "Value", "Target", "Status")
        except:
            pass  # Table might not exist yet due to tab loading
        
        # Endpoint performance table
        try:
            endpoint_table = self.query_one("#endpoint-performance-table")
            endpoint_table.add_columns("Endpoint", "Requests", "Avg Response", "Error Rate", "Performance")
        except:
            pass
        
        # Error analysis table
        try:
            error_table = self.query_one("#error-analysis-table")
            error_table.add_columns("Error Type", "Count", "Percentage", "First Seen", "Last Seen")
        except:
            pass
    
    def setup_charts(self) -> None:
        """Set up metrics charts."""
        # Initialize all charts with empty content
        volume_chart = self.query_one("#volume-chart")
        volume_chart.update("Loading chart data...")
        
        # Other charts will be initialized when their tabs are accessed
    
    def update_metrics(self) -> None:
        """Update metrics data."""
        # Update quick stats
        self.query_one("#total-requests").update(f"{random.randint(2800, 3000):,}")
        self.query_one("#avg-rps").update(f"{random.uniform(40, 45):.1f}")
        self.query_one("#avg-response-time").update(f"{random.randint(200, 280)}ms")
        self.query_one("#error-rate").update(f"{random.uniform(1.5, 3.0):.1f}%")
        
        # Update status codes table
        status_table = self.query_one("#status-codes-table")
        status_table.clear()
        
        status_data = [
            ("200 OK", "2,654", "93.2%", "Success"),
            ("201 Created", "87", "3.1%", "Created"),
            ("400 Bad Request", "45", "1.6%", "Client Error"),
            ("401 Unauthorized", "23", "0.8%", "Auth Error"),
            ("404 Not Found", "18", "0.6%", "Not Found"),
            ("500 Server Error", "20", "0.7%", "Server Error"),
        ]
        
        for row in status_data:
            status_table.add_row(*row)
        
        # Update performance summary (if tab is active)
        try:
            perf_table = self.query_one("#performance-summary-table")
            perf_table.clear()
            
            perf_data = [
                ("Avg Response Time", "245ms", "< 500ms", "✅ Good"),
                ("95th Percentile", "450ms", "< 1000ms", "✅ Good"),
                ("99th Percentile", "850ms", "< 2000ms", "✅ Good"),
                ("Error Rate", "2.4%", "< 5%", "✅ Good"),
                ("Throughput", "42.3 RPS", "> 30 RPS", "✅ Good"),
                ("Uptime", "99.8%", "> 99%", "✅ Good"),
            ]
            
            for row in perf_data:
                perf_table.add_row(*row)
        except:
            pass
        
        # Update endpoint performance (if tab is active)
        try:
            endpoint_table = self.query_one("#endpoint-performance-table")
            endpoint_table.clear()
            
            endpoint_data = [
                ("GET /api/pets", "1,245", "180ms", "1.2%", "⭐⭐⭐⭐⭐"),
                ("POST /api/pets", "234", "290ms", "2.8%", "⭐⭐⭐⭐"),
                ("GET /api/pets/{id}", "892", "210ms", "1.5%", "⭐⭐⭐⭐⭐"),
                ("PUT /api/pets/{id}", "156", "340ms", "4.2%", "⭐⭐⭐"),
                ("DELETE /api/pets/{id}", "45", "198ms", "0.9%", "⭐⭐⭐⭐⭐"),
            ]
            
            for row in endpoint_data:
                endpoint_table.add_row(*row)
        except:
            pass
        
        # Update error analysis (if tab is active)
        try:
            error_table = self.query_one("#error-analysis-table")
            error_table.clear()
            
            error_data = [
                ("Timeout", "28", "31.5%", "14:23:45", "16:45:12"),
                ("Auth Failed", "23", "25.8%", "14:15:30", "16:40:55"),
                ("Rate Limited", "18", "20.2%", "15:20:15", "16:30:22"),
                ("Not Found", "15", "16.9%", "14:45:20", "16:25:10"),
                ("Server Error", "5", "5.6%", "15:10:45", "15:55:30"),
            ]
            
            for row in error_data:
                error_table.add_row(*row)
        except:
            pass
    
    def create_line_chart(self, title, data_points, max_width=60, max_height=15) -> str:
        """Create an ASCII line chart."""
        if not data_points:
            return "No data available"
            
        # Find min/max values
        max_value = max(data_points)
        min_value = min(data_points)
        range_value = max(max_value - min_value, 1)  # Avoid division by zero
        
        # Scale data points to fit in height
        chart_height = max_height
        chart_width = min(max_width, len(data_points))
        
        # Select evenly distributed points if we have too many
        if len(data_points) > chart_width:
            step = len(data_points) / chart_width
            sample_indices = [int(i * step) for i in range(chart_width)]
            sampled_data = [data_points[i] for i in sample_indices]
        else:
            sampled_data = data_points
            
        # Generate ASCII chart
        ascii_chart = []
        
        # Add title
        ascii_chart.append(title)
        ascii_chart.append(f"Max: {max_value:.1f} | Min: {min_value:.1f}")
        ascii_chart.append("-" * chart_width)
        
        # Generate chart rows
        for i in range(chart_height, 0, -1):
            row = []
            threshold = min_value + (range_value * i / chart_height)
            
            for value in sampled_data:
                if value >= threshold:
                    row.append("█")
                else:
                    row.append(" ")
            
            # Add y-axis label
            if i == chart_height or i == 1 or i == chart_height // 2:
                y_label = f"{threshold:4.1f} |"
            else:
                y_label = "     |"
                
            ascii_chart.append(f"{y_label} {''.join(row)}")
        
        # Add x-axis
        ascii_chart.append("     " + "-" * chart_width)
        
        # Add labels
        if len(sampled_data) <= 24:  # Only add labels for small charts
            # For time-series, use hour labels
            labels = []
            for i in range(len(sampled_data)):
                if i % (max(1, len(sampled_data) // 6)) == 0:  # Show ~6 labels
                    labels.append(f"{i:2d}")
                else:
                    labels.append("  ")
            ascii_chart.append("     " + "".join(labels))
            
        return "\n".join(ascii_chart)
    
    def create_bar_chart(self, title, labels, values, max_width=60, max_height=15) -> str:
        """Create an ASCII bar chart."""
        if not values or not labels:
            return "No data available"
            
        # Find max value for scaling
        max_value = max(values)
        
        # Calculate bar heights
        bar_heights = [min(max_height, int((value / max_value) * max_height)) for value in values]
        
        # Generate ASCII chart
        ascii_chart = []
        
        # Add title
        ascii_chart.append(title)
        ascii_chart.append("-" * max_width)
        
        # Generate chart rows from top to bottom
        for h in range(max_height, 0, -1):
            row = "     |"
            for bar_height in bar_heights:
                if bar_height >= h:
                    row += "█ "
                else:
                    row += "  "
            ascii_chart.append(row)
        
        # Add x-axis
        ascii_chart.append("     +" + "-" * (len(values) * 2 + 1))
        
        # Add labels
        label_row = "      "
        for label in labels:
            label_row += f"{label[:2]} "  # Truncate labels to 2 chars
        ascii_chart.append(label_row)
        
        # Add values
        value_row = "      "
        for value in values:
            value_row += f"{value:2d} "
        ascii_chart.append(value_row)
            
        return "\n".join(ascii_chart)
    
    def update_charts(self) -> None:
        """Update chart data."""
        # Update volume chart (time series line chart)
        volume_chart = self.query_one("#volume-chart")
        
        # Generate sample time series data for last 60 minutes
        y_data = [random.randint(30, 60) for _ in range(60)]  # RPS data
        
        # Create ASCII line chart
        chart_text = self.create_line_chart(
            title="Request Volume - Last Hour",
            data_points=y_data,
            max_width=60,
            max_height=15
        )
        volume_chart.update(chart_text)
        
        # Update response time chart (bar chart)
        try:
            response_chart = self.query_one("#response-time-chart")
            
            # Generate response time data
            percentiles = ["p50", "p75", "p90", "p95", "p99"]
            values = [180, 250, 350, 450, 850]
            
            # Scale values down to make them fit in the chart
            scaled_values = [min(int(v / 100), 15) for v in values]
            
            chart_text = self.create_bar_chart(
                title="Response Time Percentiles (ms)",
                labels=percentiles,
                values=scaled_values,
                max_width=40,
                max_height=10
            )
            response_chart.update(chart_text)
        except:
            pass
        
        # Update throughput chart (time series for 24 hours)
        try:
            throughput_chart = self.query_one("#throughput-chart")
            
            # Generate throughput data
            throughput = [random.uniform(20, 60) for _ in range(24)]
            
            chart_text = self.create_line_chart(
                title="Throughput - Last 24 Hours",
                data_points=throughput,
                max_width=48,
                max_height=10
            )
            throughput_chart.update(chart_text)
        except:
            pass
            
        # Update trends chart if available
        try:
            trends_chart = self.query_one("#trends-chart")
            
            # Generate trend data (30 days)
            trend_data = [random.uniform(30, 50) for _ in range(30)]
            
            chart_text = self.create_line_chart(
                title="30-Day Trend Analysis",
                data_points=trend_data,
                max_width=60,
                max_height=15
            )
            trends_chart.update(chart_text)
        except:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "refresh-metrics":
            self.update_metrics()
            self.update_charts()
        elif button_id.startswith("gen-"):
            self.generate_report(button_id)
    
    def generate_report(self, report_type: str) -> None:
        """Generate the specified report."""
        # TODO: Implement report generation
        pass