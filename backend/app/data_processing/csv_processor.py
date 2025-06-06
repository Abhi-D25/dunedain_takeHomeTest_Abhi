from typing import List, Dict
import pandas as pd
from difflib import SequenceMatcher
from ..config import settings

class CSVProcessor:
    def __init__(self):
        self.df = None
        self.search_index = {}

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file into pandas DataFrame."""
        self.df = pd.read_csv(file_path)
        return self.df

    def create_search_index(self, df: pd.DataFrame) -> Dict:
        """Create searchable index from DataFrame."""
        self.search_index = {}
        for _, row in df.iterrows():
            key = f"{row['template_name']}|{row['field_label']}"
            self.search_index[key] = {
                "template_name": row["template_name"],
                "field_label": row["field_label"],
                "instructions": row["instructions"]
            }
        return self.search_index

    def search_exact(self, query: str) -> List[Dict]:
        """Perform exact match search."""
        results = []
        for key, value in self.search_index.items():
            if query.lower() in key.lower():
                results.append(value)
        return results

    def search_fuzzy(self, query: str, threshold: float = 0.6) -> List[Dict]:
        """Perform fuzzy search using difflib."""
        results = []
        for key, value in self.search_index.items():
            similarity = SequenceMatcher(None, query.lower(), key.lower()).ratio()
            if similarity >= threshold:
                results.append({
                    **value,
                    "similarity_score": similarity
                })
        return sorted(results, key=lambda x: x["similarity_score"], reverse=True)

    def process_csv(self) -> Dict:
        """Load and process CSV file."""
        self.df = self.load_csv(settings.csv_path)
        return self.create_search_index(self.df) 