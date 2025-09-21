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

    // Changed from immutable to regular state variables
    address public proposer;
    address public beneficiary;
    address public verifier;
    string public metadata_uri;
    uint256 public deadline;

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
        require(proposer == address(0), "Already initialized");
        require(_beneficiary != address(0) && _verifier != address(0), "InvalidAddress");

        proposer = _proposer;
        beneficiary = _beneficiary;
        verifier = _verifier;
        metadata_uri = _metadata_uri;
        deadline = _deadline;
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
        require(msg.sender == verifier, "OnlyVerifier");

        uint256 amount = total_contributed;
        state = State.Verified;
        total_contributed = 0;

        emit Verified(msg.sender, amount, beneficiary);

        if (amount > 0) {
            (bool success,) = beneficiary.call{value: amount}("");
            require(success, "Transfer failed");
        }
    }

    function reject() external {
        require(state == State.Proposed, "AlreadyFinalized");
        require(msg.sender == verifier, "OnlyVerifier");

        state = State.Rejected;
        emit Rejected(msg.sender);
    }

    function cancel(string calldata reason) external {
        require(state == State.Proposed, "AlreadyFinalized");
        require(msg.sender == proposer, "OnlyProposer");

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