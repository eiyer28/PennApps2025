# @version ^0.3.10

interface Project:
    def __init__(proposer: address, beneficiary: address, verifier: address, metadata_uri: String[256], deadline: uint256): nonpayable
    def immutable_proposer() -> address: view
    def immutable_beneficiary() -> address: view
    def immutable_verifier() -> address: view
    def immutable_metadata_uri() -> String[256]: view
    def immutable_deadline() -> uint256: view
    def state() -> uint256: view
    def total_contributed() -> uint256: view

event ProjectCreated:
    project_address: address
    proposer: address
    beneficiary: address
    verifier: address
    metadata_uri: String[256]
    deadline: uint256

projects: public(DynArray[address, 1000])  # Store up to 1000 project addresses
implementation: public(immutable(address))

@external
def __init__(project_implementation: address):
    """Initialize with the Project implementation contract address"""
    assert project_implementation != empty(address), "Invalid implementation"
    implementation = project_implementation

@external
def propose_project(
    beneficiary: address,
    verifier: address,
    metadata_uri: String[256],
    deadline: uint256
) -> address:
    """Deploy a new project contract

    Returns: Address of the deployed project contract
    """
    # Deploy new project using minimal proxy
    project: address = create_minimal_proxy_to(implementation)

    # Initialize the project
    Project(project).__init__(
        msg.sender,  # proposer
        beneficiary,
        verifier,
        metadata_uri,
        deadline
    )

    self.projects.append(project)

    log ProjectCreated(
        project,
        msg.sender,
        beneficiary,
        verifier,
        metadata_uri,
        deadline
    )

    return project

@view
@external
def get_all_projects() -> DynArray[address, 1000]:
    """Get addresses of all deployed projects"""
    return self.projects
