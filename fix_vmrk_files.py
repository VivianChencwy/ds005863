#!/usr/bin/env python3
"""
Script to fix vmrk and eeg file naming issues in ds005863 dataset.
The program expects files like 'COCOA_014_VO.vmrk' and 'COCOA_014_VO.eeg' but the actual files are named
like 'sub-001_task-visualoddball_eeg.vmrk' and 'sub-001_task-visualoddball_eeg.eeg'.

This script will copy and rename both vmrk and eeg files to match the expected naming convention.
"""

import os
import shutil
import glob
from pathlib import Path

def get_expected_filename(subject_dir, file_type):
    """
    Determine the expected filename based on the subject directory name.
    Based on the vhdr file content, the pattern seems to be:
    - COCOA_XXX_VO.vmrk/.eeg for subjects 001-096
    - SASA_XXX_VO.vmrk/.eeg for subjects 111-127
    
    From vhdr file content: DataFile=COCOA_070_VO.eeg, MarkerFile=COCOA_070_VO.vmrk
    This suggests the formula is: subject_num + 13 for COCOA series
    """
    subject_num = int(subject_dir.name.split('-')[1])
    
    if 1 <= subject_num <= 96:
        # COCOA series - based on vhdr file content:
        # sub-001 -> COCOA_014_VO, sub-002 -> COCOA_015_VO, etc.
        # This suggests the formula is: subject_num + 13
        return f"COCOA_{subject_num+13:03d}_VO.{file_type}"
    elif 111 <= subject_num <= 127:
        # SASA series - based on error messages, the pattern seems to be:
        # sub-111 -> SASA_115_VO, sub-112 -> SASA_116_VO, etc.
        # This suggests the formula is: subject_num - 96
        return f"SASA_{subject_num-96:03d}_VO.{file_type}"
    else:
        # For subjects 97-110, 128+, use a generic pattern
        return f"SUBJECT_{subject_num:03d}_VO.{file_type}"

def fix_vmrk_files():
    """Main function to fix all vmrk and eeg files."""
    base_dir = Path(__file__).parent
    print(f"Working in directory: {base_dir}")
    
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
            target_vmrk_path = eeg_dir / expected_vmrk_name
            shutil.copy2(existing_vmrk, target_vmrk_path)
            print(f"  ✓ Copied vmrk: {existing_vmrk.name} -> {expected_vmrk_name}")
            fixed_vmrk_count += 1
            
            # Copy eeg file with new name
            expected_eeg_name = get_expected_filename(subject_dir, 'eeg')
            target_eeg_path = eeg_dir / expected_eeg_name
            shutil.copy2(existing_eeg, target_eeg_path)
            print(f"  ✓ Copied eeg: {existing_eeg.name} -> {expected_eeg_name}")
            fixed_eeg_count += 1
            
        except Exception as e:
            print(f"  ✗ Error copying files: {e}")
            error_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Successfully fixed vmrk files: {fixed_vmrk_count}")
    print(f"  Successfully fixed eeg files: {fixed_eeg_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total subjects processed: {len(subject_dirs)}")
    
    if error_count == 0:
        print(f"\nAll vmrk and eeg files have been successfully renamed!")
    else:
        print(f"\nThere were {error_count} errors. Please check the output above.")

if __name__ == "__main__":
    fix_vmrk_files()
