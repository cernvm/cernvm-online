import hashlib
from Crypto.Cipher import AES
from Crypto import Random

class DecryptionError(Exception):
    pass

def encrypt(plaintext, secret, mode=AES.MODE_CFB):
    """Encrypt plaintext with the specified secret
    plaintext   - The content to encrypt
    secret      - The secret to encrypt plaintext
    mode        - The chaining mode to use for encryption (Optional)
    This function returns the encrypted ciphertext in a format compatible with OpenSSL symmetric encryption algorithms.
    To decrypt using OpenSSL use: echo '<ciphertext>' | openssl enc -d -aes-256-cfb8 -k '<secret>'
    """
    # Generate salt
    salt = Random.new().read(8)
    
    # Salt the password
    passTheSalt = str(secret) + salt
    
    # Generate hashes that will produce the KEY and the IV
    hashes = [hashlib.md5(passTheSalt).digest()]
    for i in range(1, 3):
       hashes.append(hashlib.md5(hashes[i - 1] + passTheSalt).digest())

    # Extract Key and IV
    key = hashes[0] + hashes[1]
    iv = hashes[2]

    # Encrypt
    cipher = AES.new(key, mode, iv)
    data = cipher.encrypt(plaintext)
    
    # Return an openssl-compatible string
    return 'Salted__' + salt + data

def decrypt(ciphertext, secret, mode=AES.MODE_CFB):
    """Decrypt ciphertext with secret
    ciphertext  - The encrypted content to decrypt
    secret      - The secret to decrypt ciphertext
    mode        - The chaining mode to use for decryption (Optional)
    This function returns the decrypted plaintext.
    To encrypt plaintext using OpenSSL use: echo '<plaintext>' | openssl enc -e -aes-256-cfb8 -k '<secret>'
    """
    
    # Validate magic header
    if ciphertext[:8] != 'Salted__':
        raise DecryptionError("Magic mismatch")
    
    # Extract salt
    salt = ciphertext[8:16]
    
    # Salt the password
    passTheSalt = str(secret) + salt

    # Generate hashes that will produce the KEY and the IV
    hashes = [hashlib.md5(passTheSalt).digest()]
    for i in range(1, 3):
       hashes.append(hashlib.md5(hashes[i - 1] + passTheSalt).digest())
    
    # Extract Key and IV
    key = hashes[0] + hashes[1]
    iv = hashes[2]
    
    # Decrypt
    cipher = AES.new(key, mode, iv)
    return cipher.decrypt(ciphertext[16:])
