from ape import accounts, project, networks
from ape_accounts import import_account_from_private_key
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv("test_accounts.env")

def deploy():
    """Deploy contracts to local Foundry chain"""
    # Connect to local Foundry network
    with networks.ethereum.local.use_provider("foundry"):
        account = os.getenv("ACCOUNT_0")
        account_pk = os.getenv("ACCOUNT_0_PK")
        try:
            account = accounts.load("ACCOUNT_0")
        except:
            account = import_account_from_private_key("ACCOUNT_0", "ACCOUNT_0", account_pk)

        # Deploy Project implementation with valid test values
        project_impl = account.deploy(
            project.CarbonProject,
            account.address,      # proposer - use deployer address
            accounts.test_accounts[1].address,  # beneficiary - use different test account
            accounts.test_accounts[2].address,  # verifier - use different test account
            "ipfs://test",       # metadata_uri
            1735689600,          # deadline - set future timestamp
            sender=account
        )

        # Deploy factory with verified implementation
        # factory = account.deploy(project.CarbonEscrow, project_impl.address)
        # print(f"Project implementation deployed at: {project_impl.address}")
        # print(f"CarbonEscrow factory deployed at: {factory.address}")
        # print("\nDeployment complete! Update these addresses in your bc_api_main.py:")
        # print(f"FACTORY_ADDRESS = \"{factory.address}\"")
        return {
            "project_implementation": project_impl.address,
            # "factory": factory.address
        }


def main():
    """Main deployment function"""
    return deploy()

if __name__ == "__main__":
    main()
