"""
Request Generator with Faker Integration

This module generates synthetic API requests based on Swagger specifications
using Faker library for realistic test data generation.
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from faker import Faker
from datetime import datetime, date
import random
import uuid


class RequestGenerator:
    """Generates synthetic API requests using Faker for data generation."""
    
    def __init__(self, locale: str = 'en_US'):
        self.faker = Faker(locale)
        self.field_mappings = self._initialize_field_mappings()
        
    def _initialize_field_mappings(self) -> Dict[str, str]:
        """Initialize fuzzy matching patterns for field names to Faker methods."""
        return {
            # Personal Information
            r'(first_?name|fname|given_?name)': 'first_name',
            r'(last_?name|lname|surname|family_?name)': 'last_name',
            r'(full_?name|name|display_?name)': 'name',
            r'(email|e_?mail|email_?address)': 'email',
            r'(phone|telephone|mobile|cell)': 'phone_number',
            r'(age|years_?old)': 'random_int(18, 80)',
            
            # Address Information
            r'(address|addr|street)': 'street_address',
            r'(city|town)': 'city',
            r'(state|province|region)': 'state',
            r'(zip|postal_?code|zipcode)': 'zipcode',
            r'(country|nation)': 'country',
            
            # Business Information
            r'(company|organization|org|business)': 'company',
            r'(job_?title|position|role)': 'job',
            r'(department|dept)': 'random_element(["Engineering", "Sales", "Marketing", "HR", "Finance"])',
            
            # Internet/Tech
            r'(username|user_?name|login)': 'user_name',
            r'(password|pwd|pass)': 'password',
            r'(url|website|link)': 'url',
            r'(domain|hostname)': 'domain_name',
            r'(ip_?address|ip)': 'ipv4',
            r'(mac_?address|mac)': 'mac_address',
            
            # Identifiers
            r'(id|identifier|uuid|guid)': 'uuid4',
            r'(ssn|social_?security)': 'ssn',
            r'(license|licence)': 'license_plate',
            r'(vin|vehicle_?id)': 'vin',
            
            # Financial
            r'(credit_?card|cc_?number)': 'credit_card_number',
            r'(bank_?account|account_?number)': 'bban',
            r'(price|cost|amount)': 'random_int(10, 1000)',
            r'(currency|money)': 'currency_code',
            r'(iban)': 'iban',
            
            # Dates and Times
            r'(date|created_?at|updated_?at)': 'date',
            r'(time|timestamp)': 'time',
            r'(datetime|created_?on|modified_?on)': 'date_time',
            r'(birth_?date|dob|birthday)': 'date_of_birth',
            
            # Text Content
            r'(description|desc|summary)': 'text(max_nb_chars=200)',
            r'(comment|note|remarks)': 'sentence',
            r'(title|subject|heading)': 'sentence(nb_words=4)',
            r'(content|body|message)': 'paragraph',
            
            # Numeric
            r'(score|rating|rank)': 'random_int(1, 10)',
            r'(quantity|qty|count)': 'random_int(1, 100)',
            r'(weight|mass)': 'random_int(1, 500)',
            r'(height|length)': 'random_int(50, 200)',
            
            # Boolean
            r'(active|enabled|visible|public)': 'boolean',
            r'(deleted|disabled|hidden|private)': 'boolean',
            
            # Technical
            r'(version|ver)': 'random_element(["1.0.0", "1.1.0", "2.0.0", "2.1.0"])',
            r'(status|state)': 'random_element(["active", "inactive", "pending", "completed"])',
            r'(type|kind|category)': 'random_element(["A", "B", "C", "premium", "standard", "basic"])',
        }
    
    def generate_value_for_field(self, field_name: str, field_schema: Dict[str, Any]) -> Any:
        """
        Generate a value for a specific field based on its name and schema.
        
        Args:
            field_name: Name of the field
            field_schema: Schema definition for the field
            
        Returns:
            Generated value appropriate for the field
        """
        field_type = self._get_field_type(field_schema)
        
        # Check for enum values first
        if 'enum' in field_schema:
            return random.choice(field_schema['enum'])
        
        # Check for example values
        if 'example' in field_schema:
            return field_schema['example']
        
        # Try fuzzy matching on field name
        faker_method = self._match_field_name(field_name.lower())
        if faker_method:
            return self._execute_faker_method(faker_method)
        
        # Fall back to type-based generation
        return self._generate_by_type(field_type, field_schema)
    
    def _get_field_type(self, schema: Dict[str, Any]) -> str:
        """Extract field type from schema."""
        if isinstance(schema, str):
            return schema
        if isinstance(schema, dict):
            return schema.get('type', 'string')
        return 'string'
    
    def _match_field_name(self, field_name: str) -> Optional[str]:
        """Match field name to Faker method using fuzzy patterns."""
        for pattern, faker_method in self.field_mappings.items():
            if re.search(pattern, field_name, re.IGNORECASE):
                return faker_method
        return None
    
    def _execute_faker_method(self, method_spec: str) -> Any:
        """Execute Faker method specification."""
        try:
            # Handle methods with parameters
            if '(' in method_spec:
                # Extract method name and parameters
                method_name = method_spec.split('(')[0]
                params_str = method_spec.split('(')[1].rstrip(')')
                
                # Evaluate parameters safely
                if params_str:
                    # Simple parameter parsing for common cases
                    if method_name == 'random_int':
                        min_val, max_val = map(int, params_str.split(', '))
                        return self.faker.random_int(min_val, max_val)
                    elif method_name == 'text':
                        return self.faker.text(max_nb_chars=int(params_str.split('=')[1]))
                    elif method_name == 'sentence':
                        if 'nb_words' in params_str:
                            nb_words = int(params_str.split('=')[1])
                            return self.faker.sentence(nb_words=nb_words)
                        return self.faker.sentence()
                    elif method_name == 'random_element':
                        # Parse list of options
                        elements_str = params_str.strip('[]"')
                        elements = [elem.strip(' "') for elem in elements_str.split('", "')]
                        return random.choice(elements)
                
                # Fallback to method without parameters
                return getattr(self.faker, method_name)()
            else:
                # Simple method call
                return getattr(self.faker, method_spec)()
        except AttributeError:
            # Fallback if Faker method doesn't exist
            return self.faker.word()
        except Exception:
            # Fallback for any other errors
            return "generated_value"
    
    def _generate_by_type(self, field_type: str, schema: Dict[str, Any]) -> Any:
        """Generate value based on field type."""
        if field_type == 'string':
            max_length = schema.get('maxLength', 50)
            min_length = schema.get('minLength', 1)
            if max_length <= 10:
                return self.faker.word()
            elif max_length <= 50:
                return self.faker.sentence()
            else:
                return self.faker.text(max_nb_chars=max_length)
        
        elif field_type == 'integer':
            minimum = schema.get('minimum', 0)
            maximum = schema.get('maximum', 1000)
            return self.faker.random_int(minimum, maximum)
        
        elif field_type == 'number':
            minimum = schema.get('minimum', 0.0)
            maximum = schema.get('maximum', 1000.0)
            return round(random.uniform(minimum, maximum), 2)
        
        elif field_type == 'boolean':
            return self.faker.boolean()
        
        elif field_type == 'array':
            items_schema = schema.get('items', {'type': 'string'})
            min_items = schema.get('minItems', 1)
            max_items = schema.get('maxItems', 5)
            array_length = random.randint(min_items, max_items)
            return [self._generate_by_type(self._get_field_type(items_schema), items_schema) 
                   for _ in range(array_length)]
        
        elif field_type == 'object':
            return self._generate_object_from_schema(schema)
        
        else:
            return self.faker.word()
    
    def _generate_object_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object from schema properties."""
        obj = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        for prop_name, prop_schema in properties.items():
            # Include required fields and randomly include optional fields
            if prop_name in required or random.choice([True, False]):
                obj[prop_name] = self.generate_value_for_field(prop_name, prop_schema)
        
        return obj
    
    def generate_request_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete request data for an endpoint.
        
        Args:
            endpoint: Endpoint definition from Swagger parser
            
        Returns:
            Dictionary containing generated request data
        """
        request_data = {
            'path_params': {},
            'query_params': {},
            'headers': {},
            'body': None
        }
        
        # Generate path parameters
        for param in endpoint.get('parameters', []):
            if param.get('in') == 'path':
                request_data['path_params'][param['name']] = self.generate_value_for_field(
                    param['name'], param.get('schema', {})
                )
        
        # Generate query parameters
        for param in endpoint.get('parameters', []):
            if param.get('in') == 'query':
                # Include required parameters and randomly include optional ones
                if param.get('required', False) or random.choice([True, False]):
                    request_data['query_params'][param['name']] = self.generate_value_for_field(
                        param['name'], param.get('schema', {})
                    )
        
        # Generate headers
        for param in endpoint.get('parameters', []):
            if param.get('in') == 'header':
                request_data['headers'][param['name']] = self.generate_value_for_field(
                    param['name'], param.get('schema', {})
                )
        
        # Generate request body
        request_body = endpoint.get('request_body')
        if request_body and endpoint['method'] in ['POST', 'PUT', 'PATCH']:
            schema = request_body.get('schema', {})
            request_data['body'] = self._generate_object_from_schema(schema)
        
        return request_data
    
    def create_confidence_mapping(self, endpoint: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Create confidence mapping for field generation choices.
        
        Args:
            endpoint: Endpoint definition
            
        Returns:
            Dictionary with confidence scores for each field mapping
        """
        mapping = {}
        
        # Analyze all parameters
        for param in endpoint.get('parameters', []):
            field_name = param['name']
            faker_method = self._match_field_name(field_name.lower())
            
            confidence = 'high' if faker_method else 'low'
            if not faker_method:
                faker_method = 'random_word'  # Default fallback
            
            mapping[field_name] = {
                'faker_method': faker_method,
                'confidence': confidence,
                'field_type': self._get_field_type(param.get('schema', {})),
                'required': param.get('required', False),
                'location': param.get('in', 'unknown')
            }
        
        # Analyze request body fields
        request_body = endpoint.get('request_body')
        if request_body:
            schema = request_body.get('schema', {})
            properties = schema.get('properties', {})
            
            for prop_name, prop_schema in properties.items():
                faker_method = self._match_field_name(prop_name.lower())
                confidence = 'high' if faker_method else 'low'
                if not faker_method:
                    faker_method = 'random_word'
                
                mapping[prop_name] = {
                    'faker_method': faker_method,
                    'confidence': confidence,
                    'field_type': self._get_field_type(prop_schema),
                    'required': prop_name in schema.get('required', []),
                    'location': 'body'
                }
        
        return mapping