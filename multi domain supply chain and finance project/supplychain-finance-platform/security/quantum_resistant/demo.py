"""
Demo script for Quantum-Resistant Cryptography System
"""

import sys
import os
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from security.quantum_resistant.pq_crypto import QuantumResistantCryptoSuite

def main():
    """Main demo function"""
    print("=== Quantum-Resistant Cryptography Demo ===\n")
    
    # Initialize quantum-resistant crypto suite
    print("1. Initializing Quantum-Resistant Crypto Suite...")
    pq_crypto = QuantumResistantCryptoSuite(security_level=2)
    
    # Demonstrate CRYSTALS-Dilithium digital signatures
    print("\n2. Demonstrating CRYSTALS-Dilithium Digital Signatures...")
    _demo_dilithium(pq_crypto)
    
    # Demonstrate CRYSTALS-Kyber key encapsulation
    print("\n3. Demonstrating CRYSTALS-Kyber Key Encapsulation...")
    _demo_kyber(pq_crypto)
    
    # Demonstrate SPHINCS+ digital signatures
    print("\n4. Demonstrating SPHINCS+ Digital Signatures...")
    _demo_sphincs(pq_crypto)
    
    # Demonstrate NTRUEncrypt encryption
    print("\n5. Demonstrating NTRUEncrypt Encryption...")
    _demo_ntru(pq_crypto)
    
    # Performance comparison
    print("\n6. Performance Comparison...")
    _performance_comparison(pq_crypto)
    
    print("\n=== Demo Complete ===")

def _demo_dilithium(pq_crypto):
    """Demonstrate CRYSTALS-Dilithium"""
    start_time = time.time()
    
    # Generate key pair
    private_key, public_key = pq_crypto.generate_keypair('dilithium')
    keygen_time = time.time() - start_time
    
    # Sign a message
    message = b"Quantum-resistant message for Dilithium signature"
    start_time = time.time()
    signature = pq_crypto.sign(message, private_key, 'dilithium')
    sign_time = time.time() - start_time
    
    # Verify signature
    start_time = time.time()
    is_valid = pq_crypto.verify(message, signature, public_key, 'dilithium')
    verify_time = time.time() - start_time
    
    print(f"   Key Generation Time: {keygen_time*1000:.2f} ms")
    print(f"   Signing Time: {sign_time*1000:.2f} ms")
    print(f"   Verification Time: {verify_time*1000:.2f} ms")
    print(f"   Signature Size: {len(signature)} bytes")
    print(f"   Signature Valid: {is_valid}")

def _demo_kyber(pq_crypto):
    """Demonstrate CRYSTALS-Kyber"""
    start_time = time.time()
    
    # Generate key pair
    private_key, public_key = pq_crypto.generate_keypair('kyber')
    keygen_time = time.time() - start_time
    
    # Encapsulate key
    start_time = time.time()
    ciphertext, shared_secret = pq_crypto.encapsulate(public_key, 'kyber')
    encaps_time = time.time() - start_time
    
    # Decapsulate key
    start_time = time.time()
    recovered_secret = pq_crypto.decapsulate(ciphertext, private_key, 'kyber')
    decaps_time = time.time() - start_time
    
    print(f"   Key Generation Time: {keygen_time*1000:.2f} ms")
    print(f"   Encapsulation Time: {encaps_time*1000:.2f} ms")
    print(f"   Decapsulation Time: {decaps_time*1000:.2f} ms")
    print(f"   Ciphertext Size: {len(ciphertext)} bytes")
    print(f"   Shared Secret Recovery: {shared_secret == recovered_secret}")

def _demo_sphincs(pq_crypto):
    """Demonstrate SPHINCS+"""
    start_time = time.time()
    
    # Generate key pair
    private_key, public_key = pq_crypto.generate_keypair('sphincs')
    keygen_time = time.time() - start_time
    
    # Sign a message
    message = b"Quantum-resistant message for SPHINCS+ signature"
    start_time = time.time()
    signature = pq_crypto.sign(message, private_key, 'sphincs')
    sign_time = time.time() - start_time
    
    # Verify signature
    start_time = time.time()
    is_valid = pq_crypto.verify(message, signature, public_key, 'sphincs')
    verify_time = time.time() - start_time
    
    print(f"   Key Generation Time: {keygen_time*1000:.2f} ms")
    print(f"   Signing Time: {sign_time*1000:.2f} ms")
    print(f"   Verification Time: {verify_time*1000:.2f} ms")
    print(f"   Signature Size: {len(signature)} bytes")
    print(f"   Signature Valid: {is_valid}")

def _demo_ntru(pq_crypto):
    """Demonstrate NTRUEncrypt"""
    start_time = time.time()
    
    # Generate key pair
    private_key, public_key = pq_crypto.generate_keypair('ntru')
    keygen_time = time.time() - start_time
    
    # Encrypt a message
    message = b"Secret quantum-resistant message for NTRUEncrypt"
    start_time = time.time()
    ciphertext = pq_crypto.encrypt(message, public_key, 'ntru')
    encrypt_time = time.time() - start_time
    
    # Decrypt the message
    start_time = time.time()
    decrypted_text = pq_crypto.decrypt(ciphertext, private_key, 'ntru')
    decrypt_time = time.time() - start_time
    
    print(f"   Key Generation Time: {keygen_time*1000:.2f} ms")
    print(f"   Encryption Time: {encrypt_time*1000:.2f} ms")
    print(f"   Decryption Time: {decrypt_time*1000:.2f} ms")
    print(f"   Ciphertext Size: {len(ciphertext)} bytes")
    print(f"   Encryption/Decryption Successful: {message == decrypted_text}")

def _performance_comparison(pq_crypto):
    """Compare performance of different algorithms"""
    message = b"Performance comparison message"
    iterations = 100
    
    print(f"   Performing {iterations} iterations for each algorithm...")
    
    # Dilithium performance
    dilithium_times = []
    private_key, public_key = pq_crypto.generate_keypair('dilithium')
    for _ in range(iterations):
        start_time = time.time()
        signature = pq_crypto.sign(message, private_key, 'dilithium')
        pq_crypto.verify(message, signature, public_key, 'dilithium')
        dilithium_times.append(time.time() - start_time)
    
    avg_dilithium = sum(dilithium_times) / len(dilithium_times)
    
    # Kyber performance
    kyber_times = []
    private_key, public_key = pq_crypto.generate_keypair('kyber')
    for _ in range(iterations):
        start_time = time.time()
        ciphertext, _ = pq_crypto.encapsulate(public_key, 'kyber')
        pq_crypto.decapsulate(ciphertext, private_key, 'kyber')
        kyber_times.append(time.time() - start_time)
    
    avg_kyber = sum(kyber_times) / len(kyber_times)
    
    # SPHINCS+ performance
    sphincs_times = []
    private_key, public_key = pq_crypto.generate_keypair('sphincs')
    for _ in range(iterations):
        start_time = time.time()
        signature = pq_crypto.sign(message, private_key, 'sphincs')
        pq_crypto.verify(message, signature, public_key, 'sphincs')
        sphincs_times.append(time.time() - start_time)
    
    avg_sphincs = sum(sphincs_times) / len(sphincs_times)
    
    # NTRUEncrypt performance
    ntru_times = []
    private_key, public_key = pq_crypto.generate_keypair('ntru')
    for _ in range(iterations):
        start_time = time.time()
        ciphertext = pq_crypto.encrypt(message, public_key, 'ntru')
        pq_crypto.decrypt(ciphertext, private_key, 'ntru')
        ntru_times.append(time.time() - start_time)
    
    avg_ntru = sum(ntru_times) / len(ntru_times)
    
    print(f"   Average Dilithium Time: {avg_dilithium*1000:.2f} ms")
    print(f"   Average Kyber Time: {avg_kyber*1000:.2f} ms")
    print(f"   Average SPHINCS+ Time: {avg_sphincs*1000:.2f} ms")
    print(f"   Average NTRUEncrypt Time: {avg_ntru*1000:.2f} ms")

if __name__ == "__main__":
    main()