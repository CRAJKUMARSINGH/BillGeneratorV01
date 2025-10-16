#!/usr/bin/env python3
"""
Test script to verify that the import error is resolved
"""

print("Testing imports...")

try:
    from enhanced_document_generator_fixed import DocumentGenerator
    print("✅ Successfully imported DocumentGenerator")
except ImportError as e:
    print(f"❌ Failed to import DocumentGenerator: {e}")

try:
    import app
    print("✅ Successfully imported app module")
except ImportError as e:
    print(f"❌ Failed to import app module: {e}")

print("Import test completed.")