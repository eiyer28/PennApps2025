#!/usr/bin/env python3
"""
Simple test to examine Carbonmark prices API response structure
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_prices_api():
    """Test the Carbonmark prices API to see the exact response structure"""
    
    carbonmark_api_key = os.getenv("CARBONMARK_API_KEY")
    if not carbonmark_api_key:
        print("ERROR: Carbonmark API key not configured")
        return
    
    headers = {
        "Authorization": f"Bearer {carbonmark_api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a known project
    project_id = "VCS-773"  # The project from the error log
    
    print(f"Testing Carbonmark prices API for project: {project_id}")
    print("=" * 60)
    
    # Make the API call
    response = requests.get(
        f"https://api.carbonmark.com/prices?project={project_id}",
        headers=headers
    )
    
    print(f"API Response Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"Response type: {type(data)}")
        print(f"Response structure: {json.dumps(data, indent=2)}")
        
        # If it's a list, examine the first item
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            print(f"\nFirst item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
            print(f"First item: {json.dumps(first_item, indent=2)}")
        
    else:
        print(f"API Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error text: {response.text}")

if __name__ == "__main__":
    test_prices_api()