"""Test the backup utility"""
import sys
import os

# Test if we can import
try:
    from backup_restore_utility import BackupRestoreUtility
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test if we can create instance
try:
    utility = BackupRestoreUtility()
    print(f"✅ Instance created")
    print(f"   DB Path: {utility.db_path}")
    print(f"   Backup Dir: {utility.backup_dir}")
except Exception as e:
    print(f"❌ Instance creation failed: {e}")
    sys.exit(1)

# Test list backups
try:
    print("\n📋 Testing list_backups()...")
    backups = utility.list_backups()
    print(f"✅ List backups successful: {len(backups)} backups found")
except Exception as e:
    print(f"❌ List backups failed: {e}")
    sys.exit(1)

# Test backup creation
try:
    print("\n📦 Testing backup()...")
    backup_path, metadata_path = utility.backup()
    if backup_path:
        print(f"✅ Backup successful!")
        print(f"   Backup: {backup_path}")
        print(f"   Metadata: {metadata_path}")
    else:
        print(f"⚠️  Backup returned None (database may not exist yet)")
except Exception as e:
    print(f"❌ Backup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
