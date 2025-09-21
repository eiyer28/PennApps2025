import json
from web3 import Web3
from web3.contract import Contract
from typing import Dict, Any, Optional, List

class CarbonProjectContract:
    """Represents an individual project contract"""
    def __init__(self, web3: Web3, address: str, abi: List[Dict]):
        self.web3 = web3
        self.address = web3.to_checksum_address(address)
        self.contract = web3.eth.contract(address=self.address, abi=abi)

    def fund(self, from_address: str, amount: int) -> Dict[str, Any]:
        """Fund the project"""
        return self.contract.functions.fund().build_transaction({
            'from': from_address,
            'value': amount,
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })

    def verify(self, verifier_address: str) -> Dict[str, Any]:
        """Verify and release funds"""
        return self.contract.functions.verify_and_release().build_transaction({
            'from': verifier_address,
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(verifier_address)
        })

    def reject(self, verifier_address: str) -> Dict[str, Any]:
        """Reject the project"""
        return self.contract.functions.reject().build_transaction({
            'from': verifier_address,
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(verifier_address)
        })

    def get_details(self) -> Dict[str, Any]:
        """Get project details"""
        return {
            'proposer': self.contract.functions.proposer().call(),
            'beneficiary': self.contract.functions.beneficiary().call(),
            'verifier': self.contract.functions.verifier().call(),
            'initiative': self.contract.functions.initiative().call(),
            'metadata_uri': self.contract.functions.metadata_uri().call(),
            'state': self.contract.functions.state().call(),
            'total_contributed': self.contract.functions.total_contributed().call(),
            'goal': self.contract.functions.goal().call()
        }

    def get_contributors(self) -> List[str]:
        """Get list of all contributors"""
        return self.contract.functions.get_contributors().call()

    def get_contribution(self, contributor: str) -> tuple[int, bool]:
        """Get contribution amount and refund status for an address"""
        return self.contract.functions.get_contribution(contributor).call()

class CarbonEscrowContract:
    """Factory contract that deploys individual project contracts"""
    def __init__(self, factory_abi_path: str, contract_abi_path: str, web3_provider: str, contract_address: str):
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract_address = self.web3.to_checksum_address(contract_address)
        self.contract = None
        self.project_abi = None
        self.factory_abi = None
        self.load_abis(factory_abi_path, contract_abi_path)

    def load_abis(self, factory_abi_path: str, contract_abi_path: str):
        """Load contract ABIs from file"""
        try:
                # Load both factory and project ABIs
                fabi = open(factory_abi_path)
                cabi = open(contract_abi_path)
                self.factory_abi = json.load(fabi)["abi"]
                self.project_abi = json.load(cabi)["abi"]
                fabi.close()
                cabi.close()
                self.contract = self.web3.eth.contract(
                    address=self.contract_address,
                    abi=self.factory_abi
                )
        except Exception as e:
            raise Exception(f"Failed to load ABI: {str(e)}")

    def propose_project(
        self,
        beneficiary: str,
        verifier: str,
        initiative: str,
        metadata_uri: str,
        goal: int,
        from_address: str
    ) -> Dict[str, Any]:
        """Deploy a new project contract"""
        if not self.contract:
            raise Exception("Contract not initialized")

        transaction = self.contract.functions.propose_project(
            beneficiary,
            verifier,
            initiative,
            metadata_uri,
            goal
        ).build_transaction({
            'from': from_address,
            'gas': 5000000,  # Higher gas limit for contract deployment
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(from_address)
        })

        return transaction

    def get_project(self, project_address: str) -> CarbonProjectContract:
        """Get interface to an existing project contract"""
        if not self.project_abi:
            raise Exception("Project ABI not loaded")
        return CarbonProjectContract(self.web3, project_address, self.project_abi)

    def get_all_projects(self) -> List[str]:
        """Get addresses of all deployed projects"""
        if not self.contract:
            raise Exception("Contract not initialized")
        return self.contract.functions.get_all_projects().call()
