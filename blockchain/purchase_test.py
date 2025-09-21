from web3 import Web3
import os
from dotenv import load_dotenv
import sys
import pytest
from eth_utils import to_wei, from_wei

# Add the parent directory to the path so we can import from blockchain directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.carbon_escrow import CarbonEscrowContract

# Load environment variables
load_dotenv("../test_accounts.env")

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

class TestCarbonPurchase:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
        assert self.w3.is_connected(), "Web3 not connected"

        # Initialize contract handler
        self.contract_handler = CarbonEscrowContract(
            factory_abi_path="../blockchain/forge/out/CarbonEscrow.sol/CarbonEscrow.json",
            contract_abi_path="../blockchain/forge/out/CarbonProject.sol/CarbonProject.json",
            web3_provider="http://localhost:8545",
            contract_address=os.getenv("FACTORY_ADDRESS")
        )

        # Get account addresses and keys
        self.proposer_addr = os.getenv(f"{PROPOSER_ACCNAME}")
        self.beneficiary_addr = os.getenv(f"{BENEFICIARY_ACCNAME}")
        self.verifier_addr = os.getenv(f"{VERIFIER_ACCNAME}")
        self.funder_addr = os.getenv(f"{FUNDER_ACCNAME}")
        
        self.proposer_key = os.getenv(f"{PROPOSER_ACCNAME}_PK")
        self.verifier_key = os.getenv(f"{VERIFIER_ACCNAME}_PK")
        self.funder_key = os.getenv(f"{FUNDER_ACCNAME}_PK")

    def test_complete_purchase_workflow(self):
        """Test complete carbon credit purchase workflow"""
        # Calculate total ETH needed
        total_eth = TONNES_OF_CARBON * PRICE_PER_TONNE
        goal_wei = self.w3.to_wei(total_eth, 'ether')

        # 1. Create project
        tx = self.contract_handler.propose_project(
            beneficiary=self.beneficiary_addr,
            verifier=self.verifier_addr,
            initiative=INITIATIVE_NAME,
            metadata_uri=METADATA_URI,
            goal=goal_wei,
            from_address=self.proposer_addr
        )

        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.proposer_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Get project address from event logs
        event = self.contract_handler.contract.events.ProjectCreated().process_receipt(receipt)[0]
        project_address = event['args']['project_address']
        
        # 2. Get project instance
        project = self.contract_handler.get_project(project_address)
        
        # 3. Fund the project
        fund_tx = project.fund(
            from_address=self.funder_addr,
            amount=goal_wei
        )
        
        signed_fund_tx = self.w3.eth.account.sign_transaction(fund_tx, private_key=self.funder_key)
        fund_tx_hash = self.w3.eth.send_raw_transaction(signed_fund_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(fund_tx_hash)
        
        # 4. Automatic verification by centralized host
        verify_tx = project.verify(self.verifier_addr)
        signed_verify_tx = self.w3.eth.account.sign_transaction(verify_tx, private_key=self.verifier_key)
        verify_tx_hash = self.w3.eth.send_raw_transaction(signed_verify_tx.rawTransaction)
        verify_receipt = self.w3.eth.wait_for_transaction_receipt(verify_tx_hash)
        
        # 5. Verify final state
        details = project.get_details()
        assert details['state'] == 1  # Verified state
        assert details['total_contributed'] == 0  # Funds have been released
        assert float(from_wei(details['goal'], 'ether')) == total_eth

        # Print test results
        print(f"\nCarbon Purchase Test Results:")
        print(f"Tonnes of Carbon: {TONNES_OF_CARBON}")
        print(f"Price per Tonne: {PRICE_PER_TONNE} ETH")
        print(f"Total Cost: {total_eth} ETH")
        print(f"Project Address: {project_address}")
        print(f"Status: Verified and Funded")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
