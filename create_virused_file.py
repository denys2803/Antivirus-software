# signature_bytes = b"d9d31cd0e8d1fbc50a7f4ba656de2d577b00372c871054eec1215c110acbe801"

# with open("fake_signature.bin", "wb") as f:
#     f.write(signature_bytes)


import hashlib



# hash_bytes = hashlib.sha256(signature_bytes).digest()  # digest(), а не hexdigest()

# with open("fake_signature.bin", "wb") as f:
#     f.write(hash_bytes)


with open("EICAR.COM", "wb") as f:
    f.write(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")

eicar_bytes = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
eicar_hash = hashlib.sha256(eicar_bytes).hexdigest()
print(eicar_hash)