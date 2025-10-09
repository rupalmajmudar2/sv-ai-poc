#!/usr/bin/env python3
"""
ChromaDB Wrapper with Telemetry Error Suppression

This module provides a cleaner interface to ChromaDB by suppressing telemetry errors.
"""

import os
import sys
import contextlib
from io import StringIO
from typing import Any

# Set environment variables before importing chromadb
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_TELEMETRY"] = "False"
os.environ["CHROMA_DISABLE_TELEMETRY"] = "True"

import chromadb
from chromadb.config import Settings

@contextlib.contextmanager
def suppress_chromadb_errors():
    """Context manager to suppress ChromaDB telemetry error messages"""
    old_stderr = sys.stderr
    try:
        # Redirect stderr to suppress error messages
        sys.stderr = StringIO()
        yield
    finally:
        # Restore stderr
        sys.stderr = old_stderr

class SilentChromaClient:
    """Wrapper around ChromaDB client that suppresses telemetry errors"""
    
    def __init__(self, **kwargs):
        with suppress_chromadb_errors():
            self.client = chromadb.PersistentClient(**kwargs)
    
    def __getattr__(self, name):
        """Delegate all method calls to the underlying client with error suppression"""
        def wrapper(*args, **kwargs):
            with suppress_chromadb_errors():
                return getattr(self.client, name)(*args, **kwargs)
        return wrapper
    
    def list_collections(self):
        with suppress_chromadb_errors():
            return self.client.list_collections()
    
    def get_collection(self, name):
        with suppress_chromadb_errors():
            return SilentCollection(self.client.get_collection(name))
    
    def get_or_create_collection(self, name, **kwargs):
        with suppress_chromadb_errors():
            return SilentCollection(self.client.get_or_create_collection(name, **kwargs))

class SilentCollection:
    """Wrapper around ChromaDB collection that suppresses telemetry errors"""
    
    def __init__(self, collection):
        self.collection = collection
    
    def __getattr__(self, name):
        """Delegate all method calls to the underlying collection with error suppression"""
        def wrapper(*args, **kwargs):
            with suppress_chromadb_errors():
                return getattr(self.collection, name)(*args, **kwargs)
        return wrapper
    
    def query(self, *args, **kwargs):
        with suppress_chromadb_errors():
            return self.collection.query(*args, **kwargs)
    
    def upsert(self, *args, **kwargs):
        with suppress_chromadb_errors():
            return self.collection.upsert(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        with suppress_chromadb_errors():
            return self.collection.get(*args, **kwargs)
    
    def peek(self, *args, **kwargs):
        with suppress_chromadb_errors():
            return self.collection.peek(*args, **kwargs)
    
    def count(self):
        with suppress_chromadb_errors():
            return self.collection.count()
    
    @property
    def name(self):
        return self.collection.name
    
    @property
    def metadata(self):
        return self.collection.metadata

def create_silent_chroma_client(path: str, settings: Settings = None) -> SilentChromaClient:
    """Create a ChromaDB client that suppresses telemetry errors"""
    if settings is None:
        settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    
    return SilentChromaClient(
        path=path,
        settings=settings
    )