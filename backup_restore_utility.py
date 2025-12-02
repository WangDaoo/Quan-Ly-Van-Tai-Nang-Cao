"""
Backup and Restore Utility for Transport Management System
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime, timedelta
import hashlib
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from config import DATABASE_PATH, BACKUP_DIR


class BackupRestoreUtility:
    def __init__(self):
        self.db_path = str(DATABASE_PATH)
        self.backup_dir = str(BACKUP_DIR)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _generate_backup_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"transport_backup_{timestamp}.db"
    
    def _calculate_checksum(self, filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _save_metadata(self, backup_path, size, checksum):
        metadata = {
            "backup_file": os.path.basename(backup_path),
            "timestamp": datetime.now().isoformat(),
            "size_bytes": size,
            "checksum": checksum
        }
        with open(backup_path + ".meta", 'w') as f:
            json.dump(metadata, f, indent=2)
        return backup_path + ".meta"
    
    def backup(self, output_dir=None):
        try:
            backup_dir = output_dir or self.backup_dir
            os.makedirs(backup_dir, exist_ok=True)
            
            if not os.path.exists(self.db_path):
                print(f"❌ Database not found: {self.db_path}")
                return None, None
            
            backup_filename = self._generate_backup_filename()
            backup_path = os.path.join(backup_dir, backup_filename)
            
            print(f"📦 Creating backup...")
            print(f"   Source: {self.db_path}")
            print(f"   Destination: {backup_path}")
            
            original_size = os.path.getsize(self.db_path)
            
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            with backup_conn:
                source_conn.backup(backup_conn)
            source_conn.close()
            backup_conn.close()
            
            checksum = self._calculate_checksum(backup_path)
            metadata_path = self._save_metadata(backup_path, original_size, checksum)
            
            print(f"✅ Backup created!")
            print(f"   Size: {os.path.getsize(backup_path):,} bytes")
            print(f"   Checksum: {checksum[:16]}...")
            
            return backup_path, metadata_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None, None
    
    def list_backups(self):
        if not os.path.exists(self.backup_dir):
            print("📁 No backups found")
            return []
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db') and filename.startswith('transport_backup_'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        if not backups:
            print(f"📁 No backups in {self.backup_dir}")
            return []
        
        print(f"\n📋 Available Backups ({len(backups)}):")
        print("=" * 80)
        for i, b in enumerate(backups, 1):
            print(f"\n{i}. {b['filename']}")
            print(f"   Path: {b['filepath']}")
            print(f"   Size: {b['size']:,} bytes")
            print(f"   Date: {b['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        return backups
    
    def auto_backup(self, keep_days=7):
        print(f"🔄 Running auto-backup (keep {keep_days} days)...")
        backup_path, _ = self.backup()
        if not backup_path:
            return False
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed = 0
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db') and filename.startswith('transport_backup_'):
                filepath = os.path.join(self.backup_dir, filename)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)
                    meta = filepath + ".meta"
                    if os.path.exists(meta):
                        os.remove(meta)
                    removed += 1
        
        print(f"✅ Removed {removed} old backup(s)")
        return True


def main():
    parser = argparse.ArgumentParser(description='Backup Utility')
    subparsers = parser.add_subparsers(dest='command')
    
    backup_parser = subparsers.add_parser('backup')
    backup_parser.add_argument('--output-dir')
    
    subparsers.add_parser('list')
    
    auto_parser = subparsers.add_parser('auto-backup')
    auto_parser.add_argument('--days', type=int, default=7)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    utility = BackupRestoreUtility()
    
    if args.command == 'backup':
        backup_path, _ = utility.backup(args.output_dir)
        return 0 if backup_path else 1
    elif args.command == 'list':
        utility.list_backups()
        return 0
    elif args.command == 'auto-backup':
        return 0 if utility.auto_backup(args.days) else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
