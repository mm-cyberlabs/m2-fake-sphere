"""
Swagger/OpenAPI Specification Parser

This module parses Swagger/OpenAPI specifications to extract:
- API endpoints and HTTP methods
- Request/response schemas and data types
- Parameter definitions and requirements
- Authentication schemes
"""

import json
import yaml
import requests
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse
import os


class SwaggerParser:
    """Parses Swagger/OpenAPI specifications from URLs or local files."""
    
    def __init__(self):
        self.spec_data: Optional[Dict[str, Any]] = None
        self.base_url: Optional[str] = None
        self.endpoints: List[Dict[str, Any]] = []
        self.schemas: Dict[str, Any] = {}
        self.auth_schemes: Dict[str, Any] = {}
        
    def load_specification(self, source: str) -> bool:
        """
        Load Swagger specification from URL or local file path.
        
        Args:
            source: URL or file path to Swagger/OpenAPI spec
            
        Returns:
            bool: True if successfully loaded, False otherwise
        """
        try:
            if self._is_url(source):
                return self._load_from_url(source)
            else:
                return self._load_from_file(source)
        except Exception as e:
            print(f"Error loading specification: {e}")
            return False
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _load_from_url(self, url: str) -> bool:
        """Load specification from URL."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        if 'json' in content_type:
            self.spec_data = response.json()
        else:
            self.spec_data = yaml.safe_load(response.text)
        
        return self._parse_specification()
    
    def _load_from_file(self, file_path: str) -> bool:
        """Load specification from local file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Specification file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.lower().endswith('.json'):
                self.spec_data = json.load(f)
            else:
                self.spec_data = yaml.safe_load(f)
        
        return self._parse_specification()
    
    def _parse_specification(self) -> bool:
        """Parse the loaded specification data."""
        if not self.spec_data:
            return False
        
        # Extract base URL
        self._extract_base_url()
        
        # Extract schemas/components
        self._extract_schemas()
        
        # Extract authentication schemes
        self._extract_auth_schemes()
        
        # Extract endpoints
        self._extract_endpoints()
        
        return True
    
    def _extract_base_url(self):
        """Extract base URL from specification."""
        # OpenAPI 3.x
        if 'servers' in self.spec_data:
            self.base_url = self.spec_data['servers'][0]['url']
        # Swagger 2.0
        elif 'host' in self.spec_data:
            scheme = self.spec_data.get('schemes', ['https'])[0]
            host = self.spec_data['host']
            base_path = self.spec_data.get('basePath', '')
            self.base_url = f"{scheme}://{host}{base_path}"
        else:
            self.base_url = "http://localhost"
    
    def _extract_schemas(self):
        """Extract data schemas from specification."""
        # OpenAPI 3.x
        if 'components' in self.spec_data and 'schemas' in self.spec_data['components']:
            self.schemas = self.spec_data['components']['schemas']
        # Swagger 2.0
        elif 'definitions' in self.spec_data:
            self.schemas = self.spec_data['definitions']
    
    def _extract_auth_schemes(self):
        """Extract authentication schemes."""
        # OpenAPI 3.x
        if 'components' in self.spec_data and 'securitySchemes' in self.spec_data['components']:
            self.auth_schemes = self.spec_data['components']['securitySchemes']
        # Swagger 2.0
        elif 'securityDefinitions' in self.spec_data:
            self.auth_schemes = self.spec_data['securityDefinitions']
    
    def _extract_endpoints(self):
        """Extract API endpoints and their details."""
        if 'paths' not in self.spec_data:
            return
        
        self.endpoints = []
        
        for path, path_item in self.spec_data['paths'].items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId'),
                        'summary': operation.get('summary'),
                        'description': operation.get('description'),
                        'parameters': self._extract_parameters(operation.get('parameters', [])),
                        'request_body': self._extract_request_body(operation.get('requestBody')),
                        'responses': operation.get('responses', {}),
                        'security': operation.get('security', []),
                        'tags': operation.get('tags', [])
                    }
                    self.endpoints.append(endpoint)
    
    def _extract_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Extract and normalize parameter definitions."""
        extracted = []
        for param in parameters:
            param_info = {
                'name': param.get('name'),
                'in': param.get('in'),  # query, path, header, cookie
                'required': param.get('required', False),
                'description': param.get('description'),
                'schema': param.get('schema', param.get('type')),  # OpenAPI 3.x vs 2.0
                'example': param.get('example')
            }
            extracted.append(param_info)
        return extracted
    
    def _extract_request_body(self, request_body: Optional[Dict]) -> Optional[Dict]:
        """Extract request body schema (OpenAPI 3.x)."""
        if not request_body:
            return None
        
        content = request_body.get('content', {})
        for media_type, media_info in content.items():
            return {
                'media_type': media_type,
                'schema': media_info.get('schema'),
                'required': request_body.get('required', False),
                'description': request_body.get('description')
            }
        return None
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Get all parsed endpoints."""
        return self.endpoints
    
    def get_endpoints_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get endpoints filtered by tag."""
        return [ep for ep in self.endpoints if tag in ep.get('tags', [])]
    
    def get_endpoints_by_method(self, method: str) -> List[Dict[str, Any]]:
        """Get endpoints filtered by HTTP method."""
        return [ep for ep in self.endpoints if ep['method'] == method.upper()]
    
    def get_schemas(self) -> Dict[str, Any]:
        """Get all schemas/definitions."""
        return self.schemas
    
    def get_auth_schemes(self) -> Dict[str, Any]:
        """Get authentication schemes."""
        return self.auth_schemes
    
    def get_base_url(self) -> Optional[str]:
        """Get the base URL for API calls."""
        return self.base_url
    
    def get_specification_info(self) -> Dict[str, Any]:
        """Get general information about the API specification."""
        if not self.spec_data:
            return {}
        
        info = self.spec_data.get('info', {})
        return {
            'title': info.get('title'),
            'version': info.get('version'),
            'description': info.get('description'),
            'contact': info.get('contact'),
            'license': info.get('license'),
            'base_url': self.base_url,
            'total_endpoints': len(self.endpoints),
            'auth_schemes': list(self.auth_schemes.keys()),
            'tags': list(set(tag for ep in self.endpoints for tag in ep.get('tags', [])))
        }