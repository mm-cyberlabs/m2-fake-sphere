# s1mc1ty/data_saver.py
# pip install pandas sqlalchemy

from typing import Dict
import pandas as pd

class DataSaver:
    def __init__(self, db_connector):
        self.engine = db_connector.get_engine()

    def save_to_database(self, simulated_data: Dict[str, pd.DataFrame]):
        """Save simulated data to the database."""
        for table_name, df in simulated_data.items():
            try:
                df.to_sql(table_name, self.engine, if_exists='append', index=False)
                print(f"Successfully saved {len(df)} records to {table_name}")
            except Exception as e:
                print(f"Error saving to {table_name}: {str(e)}")