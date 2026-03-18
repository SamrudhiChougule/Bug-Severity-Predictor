"""Test script to verify OPTIONS are loaded correctly from the dataset."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import OPTIONS

print("✅ Options loaded successfully!")
print(f"📊 Products: {len(OPTIONS['product_name'])} items")
print(f"📊 Components: {len(OPTIONS['component_name'])} items")
print(f"📊 Resolutions: {OPTIONS['resolution_category']}")
print(f"📊 Statuses: {OPTIONS['status_category']}")
print(f"\nSample products (first 5): {OPTIONS['product_name'][:5]}")
print(f"Sample components (first 5): {OPTIONS['component_name'][:5]}")

