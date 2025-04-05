#!/usr/bin/env python3
import os
import sys
import requests
from tqdm import tqdm
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model information
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf"
MODEL_PATH = "models/mistral-7b-v0.1.gguf"
EXPECTED_SHA256 = "..."  # Add the correct SHA256 hash here

def download_file(url: str, destination: str, chunk_size: int = 8192):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    with open(destination, 'wb') as f, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=chunk_size):
            size = f.write(data)
            pbar.update(size)

def verify_checksum(file_path: str, expected_hash: str) -> bool:
    """Verify the SHA256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash

def main():
    """Download and verify the model"""
    try:
        # Check if model already exists
        if os.path.exists(MODEL_PATH):
            logger.info(f"Model already exists at {MODEL_PATH}")
            if verify_checksum(MODEL_PATH, EXPECTED_SHA256):
                logger.info("Model checksum verified successfully")
                return
            else:
                logger.warning("Existing model checksum verification failed. Downloading again...")
        
        # Download the model
        logger.info(f"Downloading model from {MODEL_URL}")
        download_file(MODEL_URL, MODEL_PATH)
        
        # Verify checksum
        if verify_checksum(MODEL_PATH, EXPECTED_SHA256):
            logger.info("Model downloaded and verified successfully")
        else:
            logger.error("Model checksum verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 