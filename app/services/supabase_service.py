"""
SupabaseService - Fetch and store subsets of data from Supabase
"""
from flask import current_app
from ..models import db, Species, OceanographicData, EdnaSample, Dataset

class SupabaseService:
    def __init__(self):
        # Use the Supabase client initialized in create_app()
        self.supabase = current_app.supabase

    def fetch_table(self, table_name: str, select: str = '*', filters: dict = None, limit: int = None):
        """
        Generic fetch from a Supabase table.
        :param table_name: Name of the Supabase table
        :param select: Columns to select (SQL-like syntax)
        :param filters: Dict of column:value pairs to filter by
        :param limit: Number of records to retrieve
        :return: List of records (dict)
        """
        query = self.supabase.table(table_name).select(select)
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        if limit:
            query = query.limit(limit)
        response = query.execute()
        if response.error:
            current_app.logger.error(f"Supabase fetch error: {response.error.message}")
            return []
        return response.data

    def store_species_subset(self, filters: dict = None, limit: int = None):
        """
        Fetch a subset of species from Supabase and store in local DB.
        Returns the list of created Species objects.
        """
        data = self.fetch_table('species', select='*', filters=filters, limit=limit)
        created = []
        for item in data:
            try:
                species = Species(
                    dataset_id=None,  # assign your own dataset record if needed
                    scientific_name=item.get('scientific_name'),
                    common_name=item.get('common_name'),
                    family=item.get('family'),
                    genus=item.get('genus'),
                    order=item.get('order'),
                    class_name=item.get('class_name'),
                    phylum=item.get('phylum'),
                    kingdom=item.get('kingdom'),
                    habitat=item.get('habitat'),
                    conservation_status=item.get('conservation_status'),
                )
                db.session.add(species)
                created.append(species)
            except Exception as e:
                current_app.logger.error(f"Error storing species {item}: {e}")
                continue
        db.session.commit()
        return created

    # Similar methods can be added for OceanographicData and EdnaSample
