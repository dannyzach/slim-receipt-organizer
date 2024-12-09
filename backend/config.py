import os
from pathlib import Path

class Config:
    """Application configuration"""
    def __init__(self):
        # Get backend directory path
        self.base_dir = os.path.join(os.path.dirname(__file__), 'Receipts')
        
        # Ensure directories exist
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, 'uploads'), exist_ok=True)
        
        # Set paths
        self.db_path = os.path.join(self.base_dir, 'receipts.db')
        self.upload_folder = os.path.join(self.base_dir, 'uploads')

config = Config()
  