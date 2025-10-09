#!/usr/bin/env python3
"""
ChromaDB Telemetry Disabler

This script comprehensively disables ChromaDB telemetry to prevent capture() errors.
"""

import os
import sys

def disable_chromadb_telemetry():
    """Comprehensively disable ChromaDB telemetry"""
    
    # Set all known environment variables
    telemetry_vars = [
        "ANONYMIZED_TELEMETRY",
        "CHROMA_TELEMETRY", 
        "CHROMA_SERVER_TELEMETRY",
        "CHROMA_DISABLE_TELEMETRY",
        "CHROMA_TELEMETRY_DISABLED"
    ]
    
    for var in telemetry_vars:
        os.environ[var] = "False"
    
    # Additional explicit disabling
    os.environ["CHROMA_TELEMETRY"] = "0"
    os.environ["ANONYMIZED_TELEMETRY"] = "0"
    
    print("✅ ChromaDB telemetry environment variables set")

if __name__ == "__main__":
    disable_chromadb_telemetry()
    print("🔧 ChromaDB telemetry has been disabled")