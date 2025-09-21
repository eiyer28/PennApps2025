import requests
import time
from web3 import Web3
import os
from eth_utils import to_wei, from_wei
from dotenv import load_dotenv
import json

# Load environment variables and setup
load_dotenv("test_accounts.env")  # Updated path since we're in blockchain directory
API_URL = "http://127.0.0.1:8000"  # FastAPI server URL

# Test constants
TONNES_OF_CARBON = 5.0
PRICE_PER_TONNE = 0.5  # in ETH
INITIATIVE_NAME = "Rainforest Conservation Project"
METADATA_URI = "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX/carbon_data.json"

# Account names for test
PROPOSER_ACCNAME = "ACCOUNT_0"
BENEFICIARY_ACCNAME = "ACCOUNT_1"
VERIFIER_ACCNAME = "ACCOUNT_2"  # Centralized host key
FUNDER_ACCNAME = "ACCOUNT_3"

class CarbonPurchaseWorkflow:
    def __init__(self):
        """Initialize the workflow handler"""
        self.api_url = API_URL
        self.project_address = None

    def create_project(self, tonnes: float, price_per_tonne: float, initiative: str, metadata_uri: str) -> bool:
        """Create a new carbon project with calculated goal"""
        total_eth = tonnes * price_per_tonne

        payload = {
            "proposer_id": PROPOSER_ACCNAME,
            "beneficiary_id": BENEFICIARY_ACCNAME,
            "verifier_id": VERIFIER_ACCNAME,
            "initiative": initiative,
            "metadata_uri": metadata_uri,
            "goal": total_eth
        }

        print(payload)

        try:
            print(f"\nCreating project with {tonnes} tonnes at {price_per_tonne} ETH per tonne...")
            print(f"Total goal: {total_eth} ETH")

            response = requests.post(f"{self.api_url}/propose", json=payload)
            response.raise_for_status()

            # Get the newly created project address
            projects_response = requests.get(f"{self.api_url}/projects")
            projects = projects_response.json()["projects"]
            self.project_address = projects[-1]  # Get the latest project

            print(f"Project created at address: {self.project_address}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error creating project: {str(e)}")
            return False

    def fund_project(self, amount_eth: float) -> bool:
        """Fund the project with specified amount"""
        if not self.project_address:
            print("No project address available")
            return False

        payload = {
            "user_id": FUNDER_ACCNAME,
            "project_address": self.project_address,
            "amount": str(amount_eth)
        }

        try:
            print(f"\nFunding project with {amount_eth} ETH...")
            response = requests.post(f"{self.api_url}/fund", json=payload)
            response.raise_for_status()
            print("Funding successful")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error funding project: {str(e)}")
            return False

    def verify_project(self) -> bool:
        """Automatically verify the project using centralized host key"""
        if not self.project_address:
            print("No project address available")
            return False

        payload = {
            "verifier_id": VERIFIER_ACCNAME,
            "project_address": self.project_address
        }

        try:
            print("\nAutomatically verifying project...")
            response = requests.post(f"{self.api_url}/verify", json=payload)
            response.raise_for_status()
            print("Verification successful")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error verifying project: {str(e)}")
            return False

    def get_project_status(self) -> dict:
        """Get the current project status"""
        if not self.project_address:
            print("No project address available")
            return None

        try:
            response = requests.get(f"{self.api_url}/project/{self.project_address}")
            response.raise_for_status()
            return response.json()["project"]

        except requests.exceptions.RequestException as e:
            print(f"Error getting project status: {str(e)}")
            return None

def run_purchase_workflow():
    """Execute the complete carbon purchase workflow"""
    workflow = CarbonPurchaseWorkflow()

    print("=== Starting Carbon Purchase Workflow ===")
    print(f"Tonnes of Carbon: {TONNES_OF_CARBON}")
    print(f"Price per Tonne: {PRICE_PER_TONNE} ETH")
    print(f"Initiative: {INITIATIVE_NAME}")

    # Calculate total ETH needed
    total_eth = TONNES_OF_CARBON * PRICE_PER_TONNE

    # 1. Create project
    if not workflow.create_project(TONNES_OF_CARBON, PRICE_PER_TONNE, INITIATIVE_NAME, METADATA_URI):
        print("Failed to create project")
        return

    # 2. Get initial status
    initial_status = workflow.get_project_status()
    if initial_status:
        print("\nInitial Project Status:")
        print(f"Goal: {initial_status['goal']} ETH")
        print(f"State: {initial_status['state']}")

    # 3. Fund the project
    if not workflow.fund_project(total_eth):
        print("Failed to fund project")
        return

    # 4. Automatically verify
    if not workflow.verify_project():
        print("Failed to verify project")
        return

    # 5. Get final status
    final_status = workflow.get_project_status()
    if final_status:
        print("\n=== Final Project Status ===")
        print(f"State: {final_status['state']}")
        print(f"Total Contributed: {final_status['total_contributed']} ETH")
        print(f"Beneficiary: {final_status['beneficiary']}")
        print("Workflow completed successfully")

if __name__ == "__main__":
    run_purchase_workflow()
