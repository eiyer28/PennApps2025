from ape import accounts, project, networks
from web3 import Web3

def deploy():
    """Deploy contracts to local Foundry chain"""
    # Connect to local Foundry network
    with networks.ethereum.local.use_provider("foundry"):
        print("Connected to local Foundry network")

        # Use first test account
        account = accounts.test_accounts[0]
        print(f"Deploying from address: {account.address}")

        # First deploy Project implementation with dummy values
        # These values don't matter since this is just the implementation
        print("\nDeploying Project implementation...")
        project_impl = account.deploy(
            project.CarbonProject,
            account.address,  # proposer
            account.address,  # beneficiary
            account.address,  # verifier
            "dummy_uri",     # metadata_uri
            0               # deadline
        )
        print(f"Project implementation deployed at: {project_impl.address}")

        # Then deploy CarbonEscrow factory with Project implementation address
        print("\nDeploying CarbonEscrow factory...")
        factory = account.deploy(project.CarbonEscrow, project_impl.address)
        print(f"CarbonEscrow factory deployed at: {factory.address}")

        print("\nDeployment complete! Update these addresses in your bc_api_main.py:")
        print(f"FACTORY_ADDRESS = \"{factory.address}\"")

        return {
            "project_implementation": project_impl.address,
            "factory": factory.address
        }

def main():
    """Main deployment function"""
    return deploy()

if __name__ == "__main__":
    main()
