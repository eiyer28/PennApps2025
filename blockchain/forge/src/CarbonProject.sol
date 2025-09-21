// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CarbonProject {
    enum State {
        Proposed,
        Verified,
        Rejected,
        Canceled
    }

    struct Contribution {
        uint256 amount;
        bool refunded;
    }

    address public immutable immutable_proposer;
    address public immutable immutable_beneficiary;
    address public immutable immutable_verifier;
    string public immutable_metadata_uri;
    uint256 public immutable immutable_deadline;


    State public state;
    uint256 public total_contributed;
    mapping(address => Contribution) public contributors;
    address[] private contributor_list;

    event Funded(address contributor, uint256 amount, uint256 new_total);
    event Verified(address verifier, uint256 released_amount, address beneficiary);
    event Rejected(address verifier);
    event Canceled(address caller, string reason);
    event Refunded(address contributor, uint256 amount);

    constructor() {} // Empty constructor for proxy

    function __init__(
        address _proposer,
        address _beneficiary,
        address _verifier,
        string memory _metadata_uri,
        uint256 _deadline
    ) external {
        require(immutable_proposer == address(0), "Already initialized"); // Prevent double initialization
        require(_beneficiary != address(0) && _verifier != address(0), "InvalidAddress");

        // Initialize storage slots directly using assembly since we can't use constructor for proxies
        assembly {
            sstore(immutable_proposer.slot, _proposer)
            sstore(immutable_beneficiary.slot, _beneficiary)
            sstore(immutable_verifier.slot, _verifier)
            sstore(immutable_metadata_uri.slot, _metadata_uri)
            sstore(immutable_deadline.slot, _deadline)
        }
        state = State.Proposed;
    }

    function fund() external payable {
        require(msg.value > 0, "NotPositiveValue");
        require(state == State.Proposed, "NotAcceptingFunds");

        if (contributors[msg.sender].amount == 0) {
            contributor_list.push(msg.sender);
        }
        contributors[msg.sender].amount += msg.value;
        total_contributed += msg.value;

        emit Funded(msg.sender, msg.value, total_contributed);
    }

    function verify_and_release() external {
        require(state == State.Proposed, "AlreadyFinalized");
        require(msg.sender == immutable_verifier, "OnlyVerifier");

        uint256 amount = total_contributed;
        state = State.Verified;
        total_contributed = 0;

        emit Verified(msg.sender, amount, immutable_beneficiary);

        if (amount > 0) {
            (bool success,) = immutable_beneficiary.call{value: amount}("");
            require(success, "Transfer failed");
        }
    }

    function reject() external {
        require(state == State.Proposed, "AlreadyFinalized");
        require(msg.sender == immutable_verifier, "OnlyVerifier");

        state = State.Rejected;
        emit Rejected(msg.sender);
    }

    function cancel(string calldata reason) external {
        require(state == State.Proposed, "AlreadyFinalized");
        require(msg.sender == immutable_proposer, "OnlyProposer");

        state = State.Canceled;
        emit Canceled(msg.sender, reason);
    }

    function claim_refund() external {
        require(state == State.Rejected || state == State.Canceled, "RefundsUnavailable");
        require(contributors[msg.sender].amount > 0, "NoContribution");
        require(!contributors[msg.sender].refunded, "AlreadyRefunded");

        uint256 amount = contributors[msg.sender].amount;
        contributors[msg.sender].refunded = true;
        total_contributed -= amount;

        (bool success,) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        emit Refunded(msg.sender, amount);
    }

    function get_contributors() external view returns (address[] memory) {
        return contributor_list;
    }
}