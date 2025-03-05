# s1mc1ty/data_generator.py
# pip install faker pandas sqlalchemy spacy
# python -m spacy download en_core_web_sm

from faker import Faker
import random
import datetime
from typing import Dict, Optional
import pandas as pd
import spacy

class DataGenerator:
    def __init__(self, db_connector, schema_analyzer, context: str):
        self.engine = db_connector.get_engine()
        self.tables_info = schema_analyzer.get_tables_info()
        self.foreign_keys = schema_analyzer.get_foreign_keys()
        self.context = context.lower()
        self.faker = Faker()
        self.nlp = spacy.load("en_core_web_sm")

    def _match_faker_attribute(self, column_name: str, comment: Optional[str]) -> any:
        """Dynamically match column description to a Faker attribute using NLP."""
        if not comment:
            return None
            
        comment = comment.lower()
        doc = self.nlp(comment)
        col_name = column_name.lower()

        # Dynamic mapping based on keywords in description or column name
        for token in doc:
            word = token.text
            # Person-related
            if word in ["name", "person", "customer", "user"] or "name" in col_name:
                return self.faker.name()
            elif word in ["first", "given"] and "name" in comment:
                return self.faker.first_name()
            elif word in ["last", "family", "surname"] and "name" in comment:
                return self.faker.last_name()
            elif word in ["prefix", "title"] and "name" in comment:
                return self.faker.prefix()
            elif word in ["suffix"] and "name" in comment:
                return self.faker.suffix()

            # Address-related
            elif word in ["address", "location", "street"] or "address" in col_name:
                return self.faker.address()
            elif word in ["street"] and "address" in comment:
                return self.faker.street_address()
            elif word in ["city", "town"] or "city" in col_name:
                return self.faker.city()
            elif word in ["state", "province"] or "state" in col_name:
                return self.faker.state()
            elif word in ["country", "nation"] or "country" in col_name:
                return self.faker.country()
            elif word in ["zip", "postal", "postcode"] or "zip" in col_name:
                return self.faker.postcode()

            # Internet-related
            elif word in ["email", "mail"] or "email" in col_name:
                return self.faker.email()
            elif word in ["url", "website"] or "url" in col_name:
                return self.faker.url()
            elif word in ["domain"] or "domain" in col_name:
                return self.faker.domain_name()
            elif word in ["ip", "ipv4"] or "ip" in col_name:
                return self.faker.ipv4()
            elif word in ["username", "login"] or "username" in col_name:
                return self.faker.user_name()

            # Phone-related
            elif word in ["phone", "telephone", "mobile"] or "phone" in col_name:
                return self.faker.phone_number()

            # Date and Time
            elif word in ["birth", "born"] and "date" in comment:
                return self.faker.date_of_birth()
            elif word in ["date", "day", "time"] or "date" in col_name:
                return self.faker.date_this_decade()
            elif word in ["time"] and "date" not in comment:
                return self.faker.time()
            elif word in ["year"] or "year" in col_name:
                return self.faker.year()

            # Company and Business
            elif word in ["company", "business", "organization"] or "company" in col_name:
                return self.faker.company()
            elif word in ["job", "position", "role"] or "job" in col_name:
                return self.faker.job()
            elif word in ["bs", "buzzword"] or "bs" in col_name:
                return self.faker.bs()

            # Financial
            elif word in ["price", "cost", "amount", "value"] or "price" in col_name:
                return round(random.uniform(1.0, 1000.0), 2)
            elif word in ["credit", "card"] and "number" in comment:
                return self.faker.credit_card_number()
            elif word in ["currency"] or "currency" in col_name:
                return self.faker.currency_code()
            elif word in ["iban"] or "iban" in col_name:
                return self.faker.iban()

            # Text
            elif word in ["description", "text", "note", "comment"] or "desc" in col_name:
                return self.faker.text(max_nb_chars=50)
            elif word in ["sentence"] or "sentence" in col_name:
                return self.faker.sentence()
            elif word in ["paragraph"] or "paragraph" in col_name:
                return self.faker.paragraph()

            # Product
            elif word in ["product", "item"] or "product" in col_name:
                return self.faker.word() + " " + random.choice(["Pro", "Plus", "Lite"])

            # Miscellaneous
            elif word in ["ssn", "social", "security"] or "ssn" in col_name:
                return self.faker.ssn()
            elif word in ["uuid", "id"] and "unique" in comment:
                return self.faker.uuid4()
            elif word in ["color"] or "color" in col_name:
                return self.faker.color_name()
            elif word in ["file", "filename"] or "file" in col_name:
                return self.faker.file_name()

        return None

    def _generate_field_data(self, column_name: str, column_info: Dict, fk_ref: Optional[Dict] = None) -> any:
        """Generate simulated data based on column type and description."""
        column_type = column_info['type']
        comment = column_info['comment']
        
        if fk_ref:
            ref_table = fk_ref['referred_table']
            with self.engine.connect() as conn:
                result = conn.execute(f"SELECT {fk_ref['referred_columns'][0]} FROM {ref_table}")
                values = [row[0] for row in result]
            return random.choice(values) if values else None

        # Try matching with description using NLP
        comment_match = self._match_faker_attribute(column_name, comment)
        if comment_match is not None:
            return comment_match

        # Fallback to type-based generation
        col_name = column_name.lower()
        
        if 'int' in str(column_type).lower():
            if 'id' in col_name:
                return None  # Auto-incremented by DB
            return random.randint(1, 1000)
        elif 'varchar' in str(column_type).lower() or 'text' in str(column_type).lower():
            if 'product' in col_name:
                return self.faker.word() + " " + random.choice(['Pro', 'Plus', 'Premium'])
            return self.faker.text(max_nb_chars=50)
        elif 'date' in str(column_type).lower():
            return self.faker.date_this_decade()
        elif 'float' in str(column_type).lower() or 'decimal' in str(column_type).lower():
            return round(random.uniform(0.0, 100.0), 2)
        elif 'bool' in str(column_type).lower():
            return random.choice([True, False])
        return None

    def generate_simulated_data(self, num_records: int = 100) -> Dict[str, pd.DataFrame]:
        """Generate simulated data for all tables."""
        simulated_data = {}
        tables_to_process = list(self.tables_info.keys())
        processed_tables = set()
        
        while tables_to_process:
            for table in tables_to_process[:]:
                can_process = True
                table_fks = self.foreign_keys.get(table, [])
                
                for fk in table_fks:
                    ref_table = fk['referred_table']
                    if ref_table not in processed_tables and ref_table != table:
                        can_process = False
                        break
                
                if can_process:
                    data = []
                    for _ in range(num_records):
                        row = {}
                        for col_name, col_info in self.tables_info[table]['columns'].items():
                            fk_ref = next((fk for fk in table_fks 
                                        if col_name in fk['constrained_columns']), None)
                            row[col_name] = self._generate_field_data(col_name, col_info, fk_ref)
                        data.append(row)
                    
                    simulated_data[table] = pd.DataFrame(data)
                    processed_tables.add(table)
                    tables_to_process.remove(table)
        
        return simulated_data