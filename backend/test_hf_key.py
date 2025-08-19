#!/usr/bin/env python
"""Test Hugging Face API key directly"""

import os
import json
import requests
from pathlib import Path

# Load API key from file
keys_file = Path('.api_keys.json')
if keys_file.exists():
    with open(keys_file, 'r') as f:
        keys = json.load(f)
        api_key = keys.get('HUGGINGFACE_API_KEY')
        
        if api_key:
            print(f"Testing key: {api_key[:7]}...{api_key[-4:]}")
            
            # Test 1: Check whoami endpoint
            print("\n1. Testing whoami endpoint...")
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://huggingface.co/api/whoami",
                headers=headers,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Valid key! User: {data.get('name', 'Unknown')}")
                print(f"   Email: {data.get('email', 'Unknown')}")
            else:
                print(f"   ❌ Invalid: {response.text}")
            
            # Test 2: Try a simple inference
            print("\n2. Testing inference API...")
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "inputs": "The capital of France is",
                "parameters": {
                    "max_new_tokens": 10,
                    "temperature": 0.5
                }
            }
            
            # Try with a small, fast model
            response = requests.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json=payload,
                timeout=30
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Inference API works!")
                result = response.json()
                print(f"   Response: {result}")
            elif response.status_code == 503:
                print(f"   ⏳ Model is loading, this is normal for first request")
            else:
                print(f"   ❌ Error: {response.text}")
                
        else:
            print("No API key found in .api_keys.json")
else:
    print(".api_keys.json file not found")

print("\n" + "="*50)
print("Key Format Requirements:")
print("- Must start with 'hf_'")
print("- Should be 37+ characters long")
print("- Get from: https://huggingface.co/settings/tokens")
print("- Token type: 'Read' is sufficient")
print("="*50)