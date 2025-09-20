# @version ^0.3.10

# An ETH escrow for project proposals funded by contributors.
# Funds are released to the beneficiary only if the verifier verifies the project.
# On rejection/cancel/expiration, contributors can claim refunds.

STRING_MAX_LEN: constant(uint256) = 256

enum State:
    Proposed
    Verified
    Rejected
    Canceled

struct Project:
    proposer: address
    beneficiary: address
    verifier: address
    metadata_uri: String[STRING_MAX_LEN]
    state: State
    total_contributed: uint256
    deadline: uint256  # 0 means no deadline

event ProjectProposed:
    project_id: uint256
    proposer: address
    beneficiary: address
    verifier: address
    metadata_hash: bytes32
    deadline: uint256

event Funded:
    project_id: uint256
    contributor: address
    amount: uint256
    new_total: uint256

event Verified:
    project_id: uint256
    verifier: address
    released_amount: uint256
    beneficiary: address

event Rejected:
    project_id: uint256
    verifier: address

event Canceled:
    project_id: uint256
    caller: address
    reason: String[64]

event Refunded:
    project_id: uint256
    contributor: address
    amount: uint256

next_project_id: public(uint256)
projects: HashMap[uint256, Project]
contributions: HashMap[uint256, HashMap[address, uint256]]


@external
@payable
def __default__():
    # Prevent direct ETH payments
    assert False, "Direct payments not allowed"


@external
def propose_project(
    beneficiary: address,
    verifier: address,
    metadata_uri: String[STRING_MAX_LEN],
    deadline: uint256
) -> uint256:
    assert beneficiary != empty(address) and verifier != empty(address), "InvalidAddress"

    # Use zero-based project IDs
    project_id: uint256 = self.next_project_id
    self.next_project_id = project_id + 1

    p: Project = Project({
        proposer: msg.sender,
        beneficiary: beneficiary,
        verifier: verifier,
        metadata_uri: metadata_uri,
        state: State.Proposed,
        total_contributed: 0,
        deadline: deadline
    })
    self.projects[project_id] = p

    log ProjectProposed(
        project_id,
        msg.sender,
        beneficiary,
        verifier,
        keccak256(convert(metadata_uri, Bytes[STRING_MAX_LEN])),
        deadline
    )
    return project_id


@view
@external
def get_project(project_id: uint256) -> (
    address, address, address, String[STRING_MAX_LEN], uint256, uint256, uint256
):
    """
    Returns:
      - proposer
      - beneficiary
      - verifier
      - metadata_uri
      - state (as uint256)
      - total_contributed
      - deadline
    """
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    return (
        p.proposer,
        p.beneficiary,
        p.verifier,
        p.metadata_uri,
        convert(p.state, uint256),
        p.total_contributed,
        p.deadline
    )


@view
@external
def get_contribution(project_id: uint256, contributor: address) -> uint256:
    # Keep consistency with other getters
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    return self.contributions[project_id][contributor]


@payable
@external
def fund_project(project_id: uint256):
    # Order matters for some tests: check positive value before existence.
    assert msg.value > 0, "NotPositiveValue"

    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Proposed, "AlreadyFinalized"

    prev: uint256 = self.contributions[project_id][msg.sender]
    new_contrib: uint256 = prev + msg.value
    self.contributions[project_id][msg.sender] = new_contrib

    new_total: uint256 = p.total_contributed + msg.value
    self.projects[project_id].total_contributed = new_total

    log Funded(project_id, msg.sender, msg.value, new_total)


@external
def verify_and_release(project_id: uint256):
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == p.verifier, "OnlyVerifier"

    amount: uint256 = p.total_contributed

    # Effects
    self.projects[project_id].state = State.Verified
    self.projects[project_id].total_contributed = 0

    log Verified(project_id, msg.sender, amount, p.beneficiary)

    # Interaction
    if amount > 0:
        raw_call(p.beneficiary, b"", value=amount, revert_on_failure=True)


@external
def reject_project(project_id: uint256):
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == p.verifier, "OnlyVerifier"

    self.projects[project_id].state = State.Rejected
    log Rejected(project_id, msg.sender)


@external
def cancel_project(project_id: uint256, reason: String[64]):
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == p.proposer, "OnlyProposer"

    self.projects[project_id].state = State.Canceled
    log Canceled(project_id, msg.sender, reason)


@external
def cancel_if_expired(project_id: uint256):
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Proposed, "AlreadyFinalized"

    if p.deadline != 0 and block.timestamp > p.deadline:
        self.projects[project_id].state = State.Canceled
        log Canceled(project_id, msg.sender, "Expired")
    else:
        assert False, "NotExpired"


@external
def claim_refund(project_id: uint256):
    p: Project = self.projects[project_id]
    assert p.proposer != empty(address), "ProjectDoesNotExist"
    assert p.state == State.Rejected or p.state == State.Canceled, "RefundsUnavailable"

    amount: uint256 = self.contributions[project_id][msg.sender]
    assert amount > 0, "NoContribution"

    # Effects
    self.contributions[project_id][msg.sender] = 0

    # Track reduced total to mirror escrow balance accounting
    total_before: uint256 = p.total_contributed
    if amount <= total_before:
        self.projects[project_id].total_contributed = total_before - amount
    else:
        self.projects[project_id].total_contributed = 0

    # Interaction
    send(msg.sender, amount)
    log Refunded(project_id, msg.sender, amount)