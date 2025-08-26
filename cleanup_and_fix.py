#!/usr/bin/env python3
"""
Script to clean up all incorrect COCOA and SASA files and recreate them with correct names.
"""

import os
import shutil
from pathlib import Path

def cleanup_incorrect_files():
    """Clean up all incorrect COCOA and SASA files."""
    base_dir = Path(__file__).parent
    print(f"Working in directory: {base_dir}")
    
    # Find all COCOA and SASA files
    cocoa_files = list(base_dir.rglob("COCOA_*_VO.*"))
    sasa_files = list(base_dir.rglob("SASA_*_VO.*"))
    
    all_files = cocoa_files + sasa_files
    print(f"Found {len(all_files)} files to delete")
    
    deleted_count = 0
    for file_path in all_files:
        try:
            # Change permissions to allow deletion
            os.chmod(file_path, 0o644)
            file_path.unlink()
            print(f"  ✓ Deleted: {file_path}")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗ Error deleting {file_path}: {e}")
    
    print(f"Deleted {deleted_count} files")
    return deleted_count

def get_expected_filename(subject_dir, file_type):
    """
    Determine the expected filename based on the subject directory name.
    Formula analysis from vhdr files:
    - sub-001 to sub-056: subject_num + 12 (e.g., sub-001 -> COCOA_013_VO)
    - sub-057 to sub-077: subject_num + 13 (e.g., sub-057 -> COCOA_070_VO, sub-077 -> COCOA_090_VO)
    - sub-078 to sub-096: subject_num + 14 (e.g., sub-078 -> COCOA_092_VO)
    - sub-111 to sub-127: subject_num - 96 (e.g., sub-111 -> SASA_015_VO)
    """
    subject_num = int(subject_dir.name.split('-')[1])
    
    if 1 <= subject_num <= 56:
        # COCOA series - first segment: subject_num + 12
        return f"COCOA_{subject_num+12:03d}_VO.{file_type}"
    elif 57 <= subject_num <= 77:
        # COCOA series - second segment: subject_num + 13
        return f"COCOA_{subject_num+13:03d}_VO.{file_type}"
    elif 78 <= subject_num <= 96:
        # COCOA series - third segment: subject_num + 14
        return f"COCOA_{subject_num+14:03d}_VO.{file_type}"
    elif 111 <= subject_num <= 127:
        # SASA series: subject_num - 96
        return f"SASA_{subject_num-96:03d}_VO.{file_type}"
    else:
        # Unknown subject range
        return None

def recreate_correct_files():
    """Recreate all files with correct names."""
    base_dir = Path(__file__).parent
    
    # Find all subject directories
    subject_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('sub-')]
    subject_dirs.sort(key=lambda x: int(x.name.split('-')[1]))
    
    print(f"Found {len(subject_dirs)} subject directories")
    
    fixed_vmrk_count = 0
    fixed_eeg_count = 0
    error_count = 0
    
    for subject_dir in subject_dirs:
        subject_num = subject_dir.name.split('-')[1]
        print(f"\nProcessing {subject_dir.name}...")
        
        # Look for the vmrk and eeg files in the eeg subdirectory
        eeg_dir = subject_dir / 'eeg'
        if not eeg_dir.exists():
            print(f"  Warning: No 'eeg' subdirectory found in {subject_dir.name}")
            continue
            
        # Find the existing vmrk file
        vmrk_files = list(eeg_dir.glob('*_task-visualoddball_eeg.vmrk'))
        if not vmrk_files:
            print(f"  Warning: No vmrk file found in {eeg_dir}")
            continue
            
        # Find the existing eeg file
        eeg_files = list(eeg_dir.glob('*_task-visualoddball_eeg.eeg'))
        if not eeg_files:
            print(f"  Warning: No eeg file found in {eeg_dir}")
            continue
            
        existing_vmrk = vmrk_files[0]
        existing_eeg = eeg_files[0]
        
        try:
            # Copy vmrk file with new name
            expected_vmrk_name = get_expected_filename(subject_dir, 'vmrk')
            if expected_vmrk_name is None:
                print(f"  Warning: Unknown subject range for {subject_dir.name}")
                continue
                
            target_vmrk_path = eeg_dir / expected_vmrk_name
            shutil.copy2(existing_vmrk, target_vmrk_path)
            print(f"  ✓ Created vmrk: {expected_vmrk_name}")
            fixed_vmrk_count += 1
            
            # Copy eeg file with new name
            expected_eeg_name = get_expected_filename(subject_dir, 'eeg')
            target_eeg_path = eeg_dir / expected_eeg_name
            shutil.copy2(existing_eeg, target_eeg_path)
            print(f"  ✓ Created eeg: {expected_eeg_name}")
            fixed_eeg_count += 1
            
        except Exception as e:
            print(f"  ✗ Error creating files: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Successfully created vmrk files: {fixed_vmrk_count}")
    print(f"  Successfully created eeg files: {fixed_eeg_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total subjects processed: {len(subject_dirs)}")
    
    if error_count == 0:
        print(f"\nAll vmrk and eeg files have been successfully created!")
    else:
        print(f"\nThere were {error_count} errors. Please check the output above.")

def main():
    """Main function to clean up and recreate files."""
    print("Step 1: Cleaning up incorrect files...")
    cleanup_incorrect_files()
    
    print("\nStep 2: Recreating files with correct names...")
    recreate_correct_files()

if __name__ == "__main__":
    main()
