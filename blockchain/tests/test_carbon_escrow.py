import pytest

@pytest.fixture
def accounts_list(accounts):
    # Return a predictable set of accounts
    # deployer, proposer, beneficiary, verifier, buyer1, buyer2, rando
    return accounts[0], accounts[1], accounts[2], accounts[3], accounts[4], accounts[5], accounts[6]


@pytest.fixture
def escrow(project, accounts_list):
    deployer, *_ = accounts_list
    return project.CarbonEscrow.deploy(sender=deployer)


def propose(escrow, proposer, beneficiary, verifier, metadata="ipfs://meta", deadline=0):
    return escrow.propose_project(beneficiary, verifier, metadata, deadline, sender=proposer)


def test_propose_project_and_getters(escrow, accounts_list, chain):
    _, proposer, beneficiary, verifier, *_ = accounts_list
    deadline = chain.blocks[-1].timestamp + 3600
    tx = propose(escrow, proposer, beneficiary, verifier, "ipfs://x", deadline)
    print(tx)
    pid = tx.return_value

    (p_proposer, p_beneficiary, p_verifier, p_meta, p_state, p_total, p_deadline) = escrow.get_project(pid)
    assert p_proposer == proposer
    assert p_beneficiary == beneficiary
    assert p_verifier == verifier
    assert p_meta == "ipfs://x"
    assert p_state == 0  # Proposed
    assert p_total == 0
    assert p_deadline == deadline

    # Invalid project should revert
    with pytest.raises(Exception) as e:
        escrow.get_project(pid + 1)
    assert "ProjectDoesNotExist" in str(e.value)


def test_fund_and_contributions(escrow, accounts_list):
    _, proposer, beneficiary, verifier, buyer1, buyer2, _ = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier).return_value

    with pytest.raises(Exception) as e:
        escrow.fund_project(pid, sender=buyer1, value=0)
    assert "NotPositiveValue" in str(e.value)

    tx1 = escrow.fund_project(pid, sender=buyer1, value="1 ether")
    assert tx1 is not None
    tx2 = escrow.fund_project(pid, sender=buyer2, value="2 ether")
    assert tx2 is not None

    (_, _, _, _, _, total, _) = escrow.get_project(pid)
    assert total == int(3e18)

    c1 = escrow.get_contribution(pid, buyer1)
    c2 = escrow.get_contribution(pid, buyer2)
    assert c1 == int(1e18)
    assert c2 == int(2e18)

    # Contract balance equals total contributed
    assert escrow.balance == int(3e18)


def test_only_verifier_can_verify_and_release(escrow, accounts_list):
    _, proposer, beneficiary, verifier, buyer1, _, rando = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier).return_value
    escrow.fund_project(pid, sender=buyer1, value=int(1.5e18))

    # Non-verifier cannot verify
    with pytest.raises(Exception) as e:
        escrow.verify_and_release(pid, sender=rando)
    assert "OnlyVerifier" in str(e.value)

    before = beneficiary.balance
    tx = escrow.verify_and_release(pid, sender=verifier)
    assert tx is not None
    after = beneficiary.balance
    assert after - before == int(1.5e18)

    # State updated, totals cleared
    (_, _, _, _, state, total, _) = escrow.get_project(pid)
    assert state == 1  # Verified
    assert total == 0

    # Can't fund or verify/reject/cancel again
    with pytest.raises(Exception) as e:
        escrow.fund_project(pid, sender=buyer1, value=1)
    assert "AlreadyFinalized" in str(e.value)

    with pytest.raises(Exception) as e:
        escrow.verify_and_release(pid, sender=verifier)
    assert "AlreadyFinalized" in str(e.value)

    with pytest.raises(Exception) as e:
        escrow.reject_project(pid, sender=verifier)
    assert "AlreadyFinalized" in str(e.value)

    with pytest.raises(Exception) as e:
        escrow.cancel_project(pid, "nope", sender=proposer)
    assert "AlreadyFinalized" in str(e.value)

    # Refunds unavailable on Verified
    with pytest.raises(Exception) as e:
        escrow.claim_refund(pid, sender=buyer1)
    assert "RefundsUnavailable" in str(e.value)


def test_verify_with_zero_contributions(escrow, accounts_list):
    _, proposer, beneficiary, verifier, *_ = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier).return_value

    before = beneficiary.balance
    escrow.verify_and_release(pid, sender=verifier)
    after = beneficiary.balance
    # No ETH moved, but state should be Verified
    assert after == before
    (_, _, _, _, state, total, _) = escrow.get_project(pid)
    assert state == 1  # Verified
    assert total == 0


def test_rejection_then_refunds(escrow, accounts_list):
    _, proposer, beneficiary, verifier, buyer1, buyer2, _ = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier).return_value
    escrow.fund_project(pid, sender=buyer1, value="1 ether")
    escrow.fund_project(pid, sender=buyer2, value="2 ether")

    tx = escrow.reject_project(pid, sender=verifier)
    assert tx is not None

    # Buyer1 refund
    b1_before = buyer1.balance
    escrow.claim_refund(pid, sender=buyer1)
    b1_after = buyer1.balance
    assert b1_after > b1_before  # net positive despite gas

    # Can't refund twice
    with pytest.raises(Exception) as e:
        escrow.claim_refund(pid, sender=buyer1)
    assert "NoContribution" in str(e.value)

    # Buyer2 refund
    b2_before = buyer2.balance
    escrow.claim_refund(pid, sender=buyer2)
    b2_after = buyer2.balance
    assert b2_after > b2_before

    assert escrow.balance == 0


def test_proposer_cancel_and_refunds(escrow, accounts_list):
    _, proposer, beneficiary, verifier, buyer1, _, rando = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier).return_value
    escrow.fund_project(pid, sender=buyer1, value="1 ether")

    # Only proposer can cancel
    with pytest.raises(Exception) as e:
        escrow.cancel_project(pid, "nope", sender=rando)
    assert "OnlyProposer" in str(e.value)

    escrow.cancel_project(pid, "no longer needed", sender=proposer)

    # Can't fund after cancel
    with pytest.raises(Exception) as e:
        escrow.fund_project(pid, sender=buyer1, value=1)
    assert "AlreadyFinalized" in str(e.value)

    # Buyer refund
    before = buyer1.balance
    escrow.claim_refund(pid, sender=buyer1)
    after = buyer1.balance
    assert after > before
    assert escrow.balance == 0


def test_anyone_can_cancel_if_expired(escrow, accounts_list, chain):
    _, proposer, beneficiary, verifier, buyer1, _, rando = accounts_list
    now = chain.blocks[-1].timestamp
    pid = propose(escrow, proposer, beneficiary, verifier, "meta", now + 10).return_value
    escrow.fund_project(pid, sender=buyer1, value=int(0.5e18))

    # Not yet expired
    with pytest.raises(Exception) as e:
        escrow.cancel_if_expired(pid, sender=rando)
    assert "NotExpired" in str(e.value)

    # Advance time past deadline
    chain.mine(timestamp=now + 11)
    escrow.cancel_if_expired(pid, sender=rando)

    before = buyer1.balance
    escrow.claim_refund(pid, sender=buyer1)
    after = buyer1.balance
    assert after > before
    assert escrow.balance == 0


def test_deadline_zero_is_never_expired(escrow, accounts_list, chain):
    _, proposer, beneficiary, verifier, buyer1, _, rando = accounts_list
    pid = propose(escrow, proposer, beneficiary, verifier, "meta", 0).return_value
    escrow.fund_project(pid, sender=buyer1, value=int(1e18))

    # Deadline 0 -> cancel_if_expired should revert
    with pytest.raises(Exception) as e:
        escrow.cancel_if_expired(pid, sender=rando)
    assert "NotExpired" in str(e.value)


def test_invalid_addresses_and_direct_payments(escrow, accounts_list):
    _, proposer, verifier, *_ = accounts_list

    with pytest.raises(Exception) as e:
        escrow.propose_project("0x0000000000000000000000000000000000000000", verifier, "m", 0, sender=proposer)
    assert "InvalidAddress" in str(e.value)

    with pytest.raises(Exception) as e:
        escrow.propose_project(proposer, "0x0000000000000000000000000000000000000000", "m", 0, sender=proposer)
    assert "InvalidAddress" in str(e.value)

    # Direct payment should revert
    with pytest.raises(Exception) as e:
        proposer.transfer(escrow.address, 1)
    assert "Direct payments not allowed" in str(e.value)


def test_cannot_reject_after_cancel_or_verify(escrow, accounts_list):
    _, proposer, beneficiary, verifier, buyer1, _, _ = accounts_list


    # Cancel then try reject
    pid1 = propose(escrow, proposer, beneficiary, verifier).return_value
    escrow.fund_project(pid1, sender=buyer1, value=int(1e18))
    escrow.cancel_project(pid1, "c", sender=proposer)
    with pytest.raises(Exception) as e:
        escrow.reject_project(pid1, sender=verifier)
    assert "AlreadyFinalized" in str(e.value)

    # Verify then try reject
    pid2 = propose(escrow, proposer, beneficiary, verifier).return_value
    escrow.fund_project(pid2, sender=buyer1, value=int(1e18))
    escrow.verify_and_release(pid2, sender=verifier)
    with pytest.raises(Exception) as e:
        escrow.reject_project(pid2, sender=verifier)
    assert "AlreadyFinalized" in str(e.value)