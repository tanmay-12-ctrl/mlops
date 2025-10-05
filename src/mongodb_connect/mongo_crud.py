import json
from typing import Union, Any
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.database import Database, Collection


class MongoOperation:
    """
    A class to handle common MongoDB operations like inserting records
    and performing bulk inserts from CSV or Excel files.
    """

    def __init__(self, client_url: str, database_name: str):
        """
        Initializes the MongoOperation object, creates a client, and connects to the database.

        Args:
            client_url (str): The connection URL for the MongoDB client.
            database_name (str): The name of the database to connect to.
        """
        self.client_url = client_url
        self.database_name = database_name
        self.client: MongoClient = MongoClient(self.client_url)
        self.db: Database = self.client[self.database_name]

    def _get_collection(self, collection_name: str) -> Collection:
        """A helper method to get a collection object from the database."""
        return self.db[collection_name]

    def insert_record(
        self, record: Union[dict[str, Any], list[dict[str, Any]]], collection_name: str
    ) -> None:
        """
        Inserts a single record (dict) or multiple records (list of dicts)
        into the specified collection.

        Args:
            record (Union[dict[str, Any], list[dict[str, Any]]]): The data to insert.
            collection_name (str): The name of the collection to insert into.

        Raises:
            TypeError: If record is not a dict or list of dicts.
        """
        collection = self._get_collection(collection_name)

        if isinstance(record, list):
            if not all(isinstance(data, dict) for data in record):
                raise TypeError("All items in the list must be dictionaries.")
            collection.insert_many(record)
        elif isinstance(record, dict):
            collection.insert_one(record)
        else:
            raise TypeError("Record must be a dict or a list of dicts.")

    def bulk_insert(self, datafile_path: str, collection_name: str) -> None:
        """
        Performs a bulk insert into a collection from a CSV or Excel file.

        Args:
            datafile_path (str): The file path for the CSV or Excel data.
            collection_name (str): The name of the collection for the bulk insert.

        Raises:
            ValueError: If file format is not CSV or Excel.
            TypeError: If parsed data is not a list of dictionaries.
        """
        if datafile_path.endswith(".csv"):
            dataframe = pd.read_csv(datafile_path, encoding="utf-8")
        elif datafile_path.endswith(".xlsx"):
            dataframe = pd.read_excel(datafile_path)
        else:
            raise ValueError("Unsupported file format. Use .csv or .xlsx files.")

        # Convert dataframe to a list of dictionaries (JSON records)
        data_json: list[dict[str, Any]] = json.loads(dataframe.to_json(orient="records"))

        if not all(isinstance(row, dict) for row in data_json):
            raise TypeError("All rows in the data file must be dictionaries.")

        collection = self._get_collection(collection_name)
        collection.insert_many(data_json)
