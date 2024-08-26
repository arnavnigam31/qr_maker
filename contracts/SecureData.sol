// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SecureData {
    bytes32 public storedHash;

    function storeHash(bytes32 hash) public {
        storedHash = hash;
    }

    function verifyHash(bytes32 hash) public view returns (bool) {
        return storedHash == hash;
    }
}
