"""
Demo script for Zero Trust Security Architecture
"""

import json
import qrcode
from datetime import datetime
from security.advanced.zero_trust_architecture import (
    ZeroTrustEngine, 
    AccessRequest, 
    UserContext
)

def main():
    """Main demo function"""
    print("=== Zero Trust Security Architecture Demo ===\n")
    
    # Initialize Zero Trust Engine
    print("1. Initializing Zero Trust Engine...")
    zt_engine = ZeroTrustEngine()
    
    # Register a user
    print("2. Registering user...")
    zt_engine.register_user('demo_user', {
        'email': 'demo@example.com',
        'role': 'admin',
        'mfa_enabled': True
    })
    
    # Register a device
    print("3. Registering device...")
    zt_engine.register_device('demo_device', {
        'user_id': 'demo_user',
        'device_type': 'laptop',
        'os': 'Windows 11',
        'antivirus_installed': True,
        'encryption_enabled': True,
        'os_updated': True,
        'screen_lock_enabled': True,
        'expected_locations': [(37.7749, -122.4194)]  # San Francisco
    })
    
    # Generate TOTP QR code
    print("4. Generating TOTP QR code...")
    totp_uri = zt_engine.get_totp_uri('demo_user')
    if totp_uri:
        qr = qrcode.make(totp_uri)
        qr.save("totp_qr_demo.png")
        print("   TOTP QR code saved to totp_qr_demo.png")
        print(f"   TOTP URI: {totp_uri}")
    
    # Simulate user scanning QR code and entering TOTP
    user = zt_engine.user_registry['demo_user']
    totp_code = input("5. Enter the current TOTP code from your authenticator app: ")
    
    # Create access request
    print("6. Creating access request...")
    user_context = UserContext(
        user_id='demo_user',
        device_id='demo_device',
        source_ip='192.168.1.100',
        location=(37.7749, -122.4194),  # San Francisco
        network='corporate_wifi',
        time_of_access=datetime.now(),
        behavior_profile={},
        risk_factors=[],
        trust_score=0.9,
        totp_code=totp_code
    )
    
    access_request = AccessRequest(
        request_id='demo_request',
        user_id='demo_user',
        resource='financial_data',
        action='read',
        context=user_context,
        timestamp=datetime.now(),
        session_id='demo_session'
    )
    
    # Evaluate access request
    print("7. Evaluating access request...")
    result = zt_engine.evaluate_access_request(access_request)
    
    # Display results
    print("\n=== Access Decision Result ===")
    print(json.dumps(result, indent=2, default=str))
    
    # Demonstrate quantum-resistant cryptography
    print("\n=== Quantum-Resistant Cryptography Demo ===")
    qr_crypto = zt_engine.quantum_crypto
    private_key, public_key = qr_crypto.generate_quantum_resistant_keypair('dilithium')
    message = b"Secure message for quantum-resistant signing"
    signature = qr_crypto._dilithium_sign(message, private_key)
    print(f"Message: {message}")
    print(f"Private Key: {private_key.hex()[:32]}...")
    print(f"Public Key: {public_key.hex()[:32]}...")
    print(f"Signature: {signature.hex()[:32]}...")
    
    # Demonstrate homomorphic encryption
    print("\n=== Homomorphic Encryption Demo ===")
    hom_enc = zt_engine.homomorphic_enc
    value1, value2 = 123, 456
    encrypted1 = hom_enc.encrypt(value1)
    encrypted2 = hom_enc.encrypt(value2)
    encrypted_sum = hom_enc.add_encrypted(encrypted1, encrypted2)
    decrypted_sum = hom_enc.decrypt(encrypted_sum)
    print(f"Value 1: {value1}")
    print(f"Value 2: {value2}")
    print(f"Encrypted Sum: {encrypted_sum.hex()[:32]}...")
    print(f"Decrypted Sum: {decrypted_sum}")
    print(f"Verification: {decrypted_sum == value1 + value2}")
    
    # Demonstrate zero-knowledge proof
    print("\n=== Zero-Knowledge Proof Demo ===")
    zk_proof = zt_engine.zk_proof
    secret = "super_secret_password"
    statement = "I know the secret password"
    proof = zk_proof.generate_proof(secret, statement)
    is_valid = zk_proof.verify_proof(proof)
    print(f"Statement: {statement}")
    print(f"Proof generated: {is_valid}")
    print(f"Proof verification: {is_valid}")

if __name__ == "__main__":
    main()