#!/usr/bin/env python3
"""
Script to clean up all previously created COCOA and SASA files.
"""

import os
from pathlib import Path

def cleanup_files():
    """Clean up all COCOA and SASA files."""
    base_dir = Path(__file__).parent
    print(f"Working in directory: {base_dir}")
    
    # Find all COCOA and SASA files
    cocoa_files = list(base_dir.rglob("COCOA_*_VO.*"))
    sasa_files = list(base_dir.rglob("SASA_*_VO.*"))
    
    all_files = cocoa_files + sasa_files
    print(f"Found {len(all_files)} files to delete")
    
    deleted_count = 0
    error_count = 0
    
    for file_path in all_files:
        try:
            # Change permissions to allow deletion
            os.chmod(file_path, 0o644)
            file_path.unlink()
            print(f"  ✓ Deleted: {file_path}")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ Error deleting {file_path}: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Successfully deleted: {deleted_count} files")
    print(f"  Errors: {error_count} files")
    
    if error_count == 0:
        print(f"\nAll files have been successfully deleted!")
    else:
        print(f"\nThere were {error_count} errors. Please check the output above.")

if __name__ == "__main__":
    cleanup_files()
