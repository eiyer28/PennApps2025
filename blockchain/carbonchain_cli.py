import requests
import time
from web3 import Web3
import os
from eth_utils import to_wei, from_wei

API_URL = "http://127.0.0.1:8000"
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
assert w3.is_connected()

PROPOSER_ACCNAME = "ACCOUNT_0"
BENEFICIARY_ACCNAME = "ACCOUNT_1"
VERIFIER_ACCNAME = "ACCOUNT_2"
FUNDER_ACCNAME = "ACCOUNT_3"

def create_proposal(goal_eth: float = 1.0) -> str:
    """Create a new project contract with specified goal

    Args:
        goal_eth: Goal amount in ETH (default 1.0 ETH)

    Returns:
        str: Address of the deployed project contract
    """
    payload = {
        "proposer_id": PROPOSER_ACCNAME,
        "beneficiary_id": BENEFICIARY_ACCNAME,
        "verifier_id": VERIFIER_ACCNAME,
        "initiative": "Test Initiative",
        "metadata_uri": "ipfs://QmT5NvUtoM5nWFfrQdVrFtvGfKFmG7AHE8P34isapyhCxX",
        "goal": goal_eth
    }

    print(f"\nCreating new project proposal with goal {goal_eth} ETH...")
    resp = requests.post(f"{API_URL}/propose", json=payload)
    print("Response:", resp.json()["status"])

    # Get the project address from the /projects endpoint
    resp = requests.get(f"{API_URL}/projects")
    print("All projects:", resp.json())
    projects = resp.json()["projects"]
    project_address = projects[-1] if projects else None  # Get latest project
    print("Deployed project address:", project_address)

    return project_address


def fund_project(project_address: str, amount_eth: float):
    """Fund an existing project with ETH

    Args:
        project_address: Address of the project contract
        amount_eth: Amount to contribute in ETH
    """
    payload = {
        "user_id": FUNDER_ACCNAME,
        "project_address": project_address,
        "amount": str(amount_eth)  # API expects string for proper decimal handling
    }

    print(f"\nFunding project {project_address} with {amount_eth} ETH...")
    resp = requests.post(f"{API_URL}/fund", json=payload)
    print("Response:", resp.json()["status"])
    return resp.json()


def verify_project(project_address: str):
    """Verify a project and release funds"""
    payload = {
        "verifier_id": VERIFIER_ACCNAME,
        "project_address": project_address
    }

    print(f"\nVerifying project {project_address}...")
    resp = requests.post(f"{API_URL}/verify", json=payload)
    print("Response:", resp.json()["status"])
    return resp.json()


def get_project_details(project_address: str):
    """Get project details including contributors"""
    print(f"\nGetting details for project {project_address}...")
    resp = requests.get(f"{API_URL}/project/{project_address}")
    print("Response:", resp.json())
    return resp.json()


def list_all_projects():
    """Get all deployed projects"""
    print("\nListing all projects...")
    resp = requests.get(f"{API_URL}/projects")
    print("Response:", resp.json())
    return resp.json()


def run_test_flow():
    """Run through a complete test flow"""
    print("Starting test flow...")

    # 1. Create new project with 2 ETH goal
    project_address = create_proposal(goal_eth=2.0)
    if not project_address:
        print("Failed to create project")
        return

    # 2. Get initial project details
    details = get_project_details(project_address)
    print("Initial project goal:", details["project"]["goal"], "ETH")

    # 3. Try to fund with less than goal
    fund_result = fund_project(project_address, 1.0)

    # 4. Try to verify (should fail as goal not met)
    try:
        verify_project(project_address)
        print("ERROR: Verification should have failed")
    except Exception as e:
        print("Expected verification failure (goal not met):", str(e))

    # 5. Fund to meet goal
    fund_result = fund_project(project_address, 1.0)

    # 6. Verify project (should succeed now)
    verify_result = verify_project(project_address)
    print("Final verification result:", verify_result)

    # 7. Get final project details
    final_details = get_project_details(project_address)
    print("Final project state:", final_details)


if __name__ == "__main__":
    run_test_flow()
