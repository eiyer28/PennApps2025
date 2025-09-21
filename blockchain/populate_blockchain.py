import requests
import time
from web3 import Web3
import os
from eth_utils import to_wei, from_wei
from dotenv import load_dotenv
import json
from typing import List, Dict

# Load environment variables and setup
load_dotenv("test_accounts.env")
API_URL = "http://127.0.0.1:9000"


# Test initiatives with their details
INITIATIVES = [
    {
        "name": "Rainforest Conservation Brazil",
        "tonnes": 10.0,
        "price_per_tonne": 0.5,
        "metadata": "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX/brazil.json"
    },
    {
        "name": "Solar Farm Indonesia",
        "tonnes": 7.0,
        "price_per_tonne": 0.7,
        "metadata": "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX/indonesia.json"
    },
    {
        "name": "Wind Energy Project India",
        "tonnes": 15.0,
        "price_per_tonne": 0.4,
        "metadata": "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX/india.json"
    },
    {
        "name": "Mangrove Restoration Thailand",
        "tonnes": 5.0,
        "price_per_tonne": 0.6,
        "metadata": "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX/thailand.json"
    }
]

# Account configurations for different roles
ACCOUNTS = {
    "proposers": ["ACCOUNT_0", "ACCOUNT_4", "ACCOUNT_5"],
    "beneficiaries": ["ACCOUNT_1", "ACCOUNT_6", "ACCOUNT_7"],
    "verifier": "ACCOUNT_2",  # Centralized verifier
    "funders": ["ACCOUNT_3", "ACCOUNT_8", "ACCOUNT_9", "ACCOUNT_10"]
}

class BlockchainPopulator:
    def __init__(self):
        """Initialize the blockchain populator"""
        self.api_url = API_URL
        self.projects = []

    def create_project(self, initiative: Dict, proposer_id: str, beneficiary_id: str) -> str:
        """Create a new carbon project"""
        total_eth = initiative["tonnes"] * initiative["price_per_tonne"]

        payload = {
            "proposer_id": proposer_id,
            "beneficiary_id": beneficiary_id,
            "verifier_id": ACCOUNTS["verifier"],
            "initiative": initiative["name"],
            "metadata_uri": initiative["metadata"],
            "goal": total_eth
        }

        try:
            print(f"\nCreating project for {initiative['name']}")
            print(f"Tonnes: {initiative['tonnes']}, Price/Tonne: {initiative['price_per_tonne']} ETH")
            print(f"Total goal: {total_eth} ETH")

            response = requests.post(f"{self.api_url}/propose", json=payload)
            response.raise_for_status()

            # Get the newly created project address
            projects_response = requests.get(f"{self.api_url}/projects")
            projects = projects_response.json()["projects"]
            project_address = projects[-1]
            self.projects.append(project_address)

            print(f"Project created at address: {project_address}")
            return project_address

        except requests.exceptions.RequestException as e:
            print(f"Error creating project: {str(e)}")
            return None

    def fund_project(self, project_address: str, funder_id: str, amount_eth: float) -> bool:
        """Fund a project with specified amount"""
        payload = {
            "user_id": funder_id,
            "project_address": project_address,
            "amount": str(amount_eth)
        }

        try:
            print(f"Funding project {project_address[-6:]} with {amount_eth} ETH from {funder_id}")
            response = requests.post(f"{self.api_url}/fund", json=payload)
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error funding project: {str(e)}")
            return False

    def verify_project(self, project_address: str) -> bool:
        """Verify the project using centralized verifier"""
        payload = {
            "verifier_id": ACCOUNTS["verifier"],
            "project_address": project_address
        }

        try:
            print(f"Verifying project {project_address[-6:]}")
            response = requests.post(f"{self.api_url}/verify", json=payload)
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error verifying project: {str(e)}")
            return False

    def populate_blockchain(self):
        """Create and fund multiple projects"""
        print("=== Starting Blockchain Population ===")
        
        for idx, initiative in enumerate(INITIATIVES):
            # Select proposer and beneficiary for this project
            proposer = ACCOUNTS["proposers"][idx % len(ACCOUNTS["proposers"])]
            beneficiary = ACCOUNTS["beneficiaries"][idx % len(ACCOUNTS["beneficiaries"])]
            
            # Create project
            project_address = self.create_project(initiative, proposer, beneficiary)
            if not project_address:
                continue
                
            # Calculate total funding needed
            total_eth = initiative["tonnes"] * initiative["price_per_tonne"]
            
            # Distribute funding among 2-3 random funders
            num_funders = min(len(ACCOUNTS["funders"]), 2 + idx % 2)
            base_amount = total_eth / num_funders
            
            # Fund the project
            funded_amount = 0
            for i in range(num_funders):
                funder = ACCOUNTS["funders"][i % len(ACCOUNTS["funders"])]
                # Vary the funding amount slightly for each funder
                amount = base_amount * (0.9 + (i * 0.2))
                if i == num_funders - 1:  # Last funder completes the goal
                    amount = total_eth - funded_amount
                
                if self.fund_project(project_address, funder, amount):
                    funded_amount += amount
            
            # Verify the project
            if funded_amount >= total_eth:
                self.verify_project(project_address)
            
            # Add small delay between projects
            time.sleep(1)

        print("\n=== Blockchain Population Complete ===")
        print(f"Created {len(self.projects)} projects")
        return self.projects

def main():
    populator = BlockchainPopulator()
    populator.populate_blockchain()
    
    print("\nNow you can run visualize_projects.py to see the funding network!")

if __name__ == "__main__":
    main()
