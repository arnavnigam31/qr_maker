from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from web3 import Web3
import qrcode

# 1. Generate Data
data = b"Secure information to encode"

# 2. Hash the Data
digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
digest.update(data)
hashed_data = digest.finalize()

# 3. Generate a Private/Public Key Pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
public_key = private_key.public_key()

# 4. Sign the Hash with the Private Key
signature = private_key.sign(
    hashed_data,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# 5. Combine Data and Signature
combined_data = data + signature

# 6. Generate the QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(combined_data)
qr.make(fit=True)

img = qr.make_image(fill='black', back_color='white')
img.save("secure_qr.png")
print("QR Code generated and saved as secure_qr.png")

# 7. Connect to Ethereum Blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Replace with your network
contract_address = '0xD68caA6ec099A7E6031938AC65B3c72C3568B2Ff'  # Replace with your contract address
contract_abi = '''
[
    {
        "constant": false,
        "inputs": [
            {
                "name": "hash",
                "type": "bytes32"
            }
        ],
        "name": "storeHash",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "hash",
                "type": "bytes32"
            }
        ],
        "name": "verifyHash",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "storedHash",
        "outputs": [
            {
                "name": "",
                "type": "bytes32"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
'''  # Replace with your contract ABI

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 8. Store the Hash on Blockchain
tx_hash = contract.functions.storeHash(hashed_data).transact({'from': w3.eth.accounts[0]})
w3.eth.wait_for_transaction_receipt(tx_hash)
print("Hash stored on blockchain.")

# 9. Verification Process
# Assume you extract `extracted_data` and `extracted_signature` from the QR code
extracted_data = data  # For simplicity, use original data
extracted_signature = signature  # For simplicity, use original signature

# Hash the Extracted Data
digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
digest.update(extracted_data)
extracted_hashed_data = digest.finalize()

# Verify the Signature with Public Key
try:
    public_key.verify(
        extracted_signature,
        extracted_hashed_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature is valid.")
except:
    print("Signature is invalid.")

# Verify the Hash on Blockchain
is_valid = contract.functions.verifyHash(extracted_hashed_data).call()
if is_valid:
    print("Hash matches with the blockchain record.")
else:
    print("Hash does not match.")
