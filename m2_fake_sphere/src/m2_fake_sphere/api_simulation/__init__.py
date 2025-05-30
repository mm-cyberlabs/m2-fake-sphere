"""
API Traffic Simulation Module

This module provides comprehensive API simulation capabilities including:
- Swagger/OpenAPI specification parsing
- Synthetic request generation using Faker
- Real-time metrics collection
- Multi-threaded simulation execution
- Authentication handling
"""

from .swagger_parser import SwaggerParser
from .request_generator import RequestGenerator
from .metrics_collector import MetricsCollector
from .simulation_engine import SimulationEngine

__all__ = [
    "SwaggerParser",
    "RequestGenerator", 
    "MetricsCollector",
    "SimulationEngine"
]