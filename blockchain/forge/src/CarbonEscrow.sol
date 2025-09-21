// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CarbonEscrow {
    address public immutable implementation;
    address[] public projects;

    event ProjectCreated(
        address project_address,
        address proposer,
        address beneficiary,
        address verifier,
        string initiative,
        string metadata_uri,
        uint256 goal
    );

    constructor(address project_implementation) {
        require(project_implementation != address(0), "Invalid implementation");
        implementation = project_implementation;
    }

    function propose_project(
        address beneficiary,
        address verifier,
        string calldata initiative,
        string calldata metadata_uri,
        uint256 goal
    ) external returns (address) {
        require(goal > 0, "Goal must be positive");
        address project = _createClone(implementation);

        (bool success,) = project.call(
            abi.encodeWithSignature(
                "__init__(address,address,address,string,string,uint256)",
                msg.sender,
                beneficiary,
                verifier,
                initiative,
                metadata_uri,
                goal
            )
        );
        require(success, "Project initialization failed");

        projects.push(project);

        emit ProjectCreated(
            project,
            msg.sender,
            beneficiary,
            verifier,
            initiative,
            metadata_uri,
            goal
        );

        return project;
    }

    function get_all_projects() external view returns (address[] memory) {
        return projects;
    }

    function _createClone(address target) internal returns (address result) {
        bytes20 targetBytes = bytes20(target);
        assembly {
            let clone := mload(0x40)
            mstore(clone, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73000000000000000000000000)
            mstore(add(clone, 0x14), targetBytes)
            mstore(add(clone, 0x28), 0x5af43d82803e903d91602b57fd5bf30000000000000000000000000000000000)
            result := create(0, clone, 0x37)
        }
        require(result != address(0), "Create failed");
    }
}