#!/usr/bin/env python3
"""Sync backend services from frontend/medi-ai implementations"""
import shutil
import os
from pathlib import Path

def sync_services():
    """Copy all service files from frontend to backend"""
    frontend_dir = Path("frontend/medi-ai/services")
    backend_dir = Path("backend/services")
    
    if not frontend_dir.exists():
        print(f"❌ Frontend services not found: {frontend_dir}")
        return False
    
    if not backend_dir.exists():
        backend_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📋 Syncing: {frontend_dir} → {backend_dir}\n")
    
    # Get all Python files from frontend
    frontend_files = sorted(frontend_dir.glob("*.py"))
    
    success_count = 0
    for src_file in frontend_files:
        dst_file = backend_dir / src_file.name
        try:
            shutil.copy2(src_file, dst_file)
            print(f"✅ {src_file.name}")
            success_count += 1
        except Exception as e:
            print(f"❌ {src_file.name}: {str(e)}")
    
    # Remove extra files in backend that don't exist in frontend
    extra_files = ["query_expansion.py", "response_formatter.py"]
    for fname in extra_files:
        fpath = backend_dir / fname
        if fpath.exists():
            try:
                fpath.unlink()
                print(f"🗑️  Removed: {fname} (not needed)")
            except Exception as e:
                print(f"⚠️  Could not remove {fname}: {str(e)}")
    
    print(f"\n✅ Synced {success_count} service files successfully!")
    return True

if __name__ == "__main__":
    sync_services()
