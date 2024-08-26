const SecureData = artifacts.require("SecureData");

module.exports = function (deployer) {
    deployer.deploy(SecureData);
};
