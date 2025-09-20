# @version ^0.3.10

enum State:
    Proposed
    Verified
    Rejected
    Canceled

event Funded:
    contributor: address
    amount: uint256
    new_total: uint256

event Verified:
    verifier: address
    released_amount: uint256
    beneficiary: address

event Rejected:
    verifier: address

event Canceled:
    caller: address
    reason: String[64]

event Refunded:
    contributor: address
    amount: uint256

struct Contribution:
    amount: uint256
    refunded: bool

# Project state
immutable_proposer: public(immutable(address))
immutable_beneficiary: public(immutable(address))
immutable_verifier: public(immutable(address))
immutable_metadata_uri: public(immutable(String[256]))
immutable_deadline: public(immutable(uint256))
state: public(State)
total_contributed: public(uint256)

# Track contributors
contributors: HashMap[address, Contribution]
contributor_list: DynArray[address, 100]  # Max 100 contributors per project

@external
def __init__(
    _proposer: address,
    _beneficiary: address,
    _verifier: address,
    _metadata_uri: String[256],
    _deadline: uint256
):
    """Initialize a new project contract"""
    assert _beneficiary != empty(address) and _verifier != empty(address), "InvalidAddress"

    immutable_proposer = _proposer
    immutable_beneficiary = _beneficiary
    immutable_verifier = _verifier
    immutable_metadata_uri = _metadata_uri
    immutable_deadline = _deadline
    self.state = State.Proposed
    self.total_contributed = 0

@external
@payable
def fund():
    """Fund the project"""
    assert msg.value > 0, "NotPositiveValue"
    assert self.state == State.Proposed, "NotAcceptingFunds"

    # Track contribution
    contribution: Contribution = self.contributors[msg.sender]
    if contribution.amount == 0:  # New contributor
        self.contributor_list.append(msg.sender)

    # Update contribution
    self.contributors[msg.sender] = Contribution({
        amount: contribution.amount + msg.value,
        refunded: False
    })

    # Update total
    self.total_contributed += msg.value

    log Funded(msg.sender, msg.value, self.total_contributed)

@external
def verify_and_release():
    """Verify project and release funds to beneficiary"""
    assert self.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == immutable_verifier, "OnlyVerifier"

    amount: uint256 = self.total_contributed
    self.state = State.Verified
    self.total_contributed = 0

    log Verified(msg.sender, amount, immutable_beneficiary)

    if amount > 0:
        raw_call(immutable_beneficiary, b"", value=amount)

@external
def reject():
    """Reject the project, enabling refunds"""
    assert self.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == immutable_verifier, "OnlyVerifier"

    self.state = State.Rejected
    log Rejected(msg.sender)

@external
def cancel(reason: String[64]):
    """Cancel the project"""
    assert self.state == State.Proposed, "AlreadyFinalized"
    assert msg.sender == immutable_proposer, "OnlyProposer"

    self.state = State.Canceled
    log Canceled(msg.sender, reason)

@external
def cancel_if_expired():
    """Cancel if deadline has passed"""
    assert self.state == State.Proposed, "AlreadyFinalized"
    assert immutable_deadline > 0 and block.timestamp > immutable_deadline, "NotExpired"

    self.state = State.Canceled
    log Canceled(msg.sender, "Expired")

@external
def claim_refund():
    """Claim refund if project was rejected/canceled"""
    assert self.state == State.Rejected or self.state == State.Canceled, "RefundsUnavailable"

    contribution: Contribution = self.contributors[msg.sender]
    assert contribution.amount > 0, "NoContribution"
    assert not contribution.refunded, "AlreadyRefunded"

    # Mark as refunded
    self.contributors[msg.sender].refunded = True

    # Update total
    amount: uint256 = contribution.amount
    if amount <= self.total_contributed:
        self.total_contributed -= amount
    else:
        self.total_contributed = 0

    # Send refund
    send(msg.sender, amount)
    log Refunded(msg.sender, amount)

@view
@external
def get_contribution(_contributor: address) -> uint256:
    """Get contribution amount for an address"""
    return self.contributors[_contributor].amount

@view
@external
def get_contributors() -> DynArray[address, 100]:
    """Get list of all contributors"""
    return self.contributor_list
