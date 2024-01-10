import hashlib

sha256 = hashlib.sha256()

def create_sha_file(local_path, shafile_path):
    try:
        with open(local_path, "rb") as file:
            # Read the file in chunks for efficiency
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256.update(byte_block)
        # Save the SHA-256 hash to a file
        with open(shafile_path, 'w') as sha_file:
            sha_file.write(sha256.hexdigest())
    except FileNotFoundError:
        print(f"File not found: {local_path}")
    except Exception as e:
        print(f"Error creating SHA file: {e}")

