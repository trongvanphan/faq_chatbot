#!/usr/bin/env python3
"""
Debug script for kb_manager get_stats issue
"""

import sys
sys.path.append('.')

from kb_manager import get_kb_stats, kb_manager

print("=== Testing get_kb_stats function ===")

try:
    # Test the internal method first
    print("1. Testing kb_manager.get_knowledge_base_stats()...")
    result = kb_manager.get_knowledge_base_stats()
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    print()
    
    # Test the public function
    print("2. Testing get_kb_stats()...")
    stats = get_kb_stats()
    print(f"Stats type: {type(stats)}")
    print(f"Stats: {stats}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
