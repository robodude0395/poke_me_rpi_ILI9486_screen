import json
import os
from typing import List, Dict, Any, Optional


class JSONDatabase:
    def __init__(self, filepath: str = "", dictionary_override: list[dict] = None):
        """Initialize the JSON database and create the file if it doesn't exist."""
        self._dictionary_override = None

        self.REQUIRED_KEYS = [
            "from",
            "message"
        ]

        if dictionary_override is None:
            self.filepath = filepath
            if filepath is None or not os.path.exists(filepath):
                self._save([])
        else:
            if isinstance(dictionary_override, list) and all([isinstance(d, dict) for d in dictionary_override]):
                self._dictionary_override = dictionary_override
            else:
                raise TypeError("Dictionary override is of wrong type")

    def _load(self) -> List[Dict[str, Any]]:
        """Load and return all data from the JSON file."""
        if self._dictionary_override is not None:
            return self._dictionary_override

        with open(self.filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _save(self, data: List[Dict[str, Any]]) -> None:
        """Save data (list of dicts) to the JSON file."""
        if self._dictionary_override is not None:
            self._dictionary_override = data
            return
        else:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

    def create(self, record: Dict[str, Any]) -> None:
        """Add a new record (dictionary) to the JSON database."""

        if not all([k in record for k in self.REQUIRED_KEYS]):
            raise KeyError("Record is missing details!")

        data = self._load()
        data.append(record.copy())  # ← FIX
        self._save(data)

    def read_all(self) -> List[Dict[str, Any]]:
        """Return all records."""
        return self._load()

    def read(self, key: str, value: Any) -> Optional[Dict[str, Any]]:
        """Find and return the first record where key == value."""
        data = self._load()
        out = next((item for item in data if item.get(key) == value), None)
        if out is None:
            raise Exception("Record does not exist!")
        return out

    def update(self, key: str, value: Any, updates: Dict[str, Any]) -> bool:
        """
        Update the first record where key == value.
        Returns True if updated, False if not found.
        """
        if not isinstance(value, int):
            raise TypeError("Record id is of wrong type")

        data = self._load()
        for item in data:
            if item.get(key) == value:
                item.update(updates)
                self._save(data)
                return updates
        raise TypeError("Record to update not found! id does not exist!")

    def delete(self, key: str, value: int) -> dict:
        """
        Delete the first record where key == value.
        Returns True if deleted, False if not found.
        """
        data = self._load()
        new_data = [item for item in data if item.get(key) != value]
        if len(new_data) == len(data):
            raise LookupError("Record to delete not found!")  # Nothing deleted
        self._save(new_data)
        return True
