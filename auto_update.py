"""
Auto-Update Mechanism for Transport Management System
Checks for updates and provides download/installation functionality

This is an optional feature that can be integrated into the main application.

Usage:
    python auto_update.py check
    python auto_update.py download <version>
    python auto_update.py install <installer_path>

Integration:
    from auto_update import UpdateChecker
    
    checker = UpdateChecker()
    if checker.check_for_updates():
        print(f"New version available: {checker.latest_version}")
"""

import os
import sys
import json
import urllib.request
import urllib.error
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

# Current version
CURRENT_VERSION = "1.0.0"

# Update server configuration
UPDATE_SERVER_URL = "https://api.github.com/repos/yourusername/transport-management/releases/latest"
# Alternative: Use your own server
# UPDATE_SERVER_URL = "https://yourserver.com/api/updates/latest"

# Local cache for update info
UPDATE_CACHE_FILE = "update_cache.json"
UPDATE_CHECK_INTERVAL = 86400  # 24 hours in seconds


class UpdateChecker:
    """Check for application updates"""
    
    def __init__(self, current_version=CURRENT_VERSION):
        self.current_version = current_version
        self.latest_version = None
        self.update_info = None
        self.cache_file = UPDATE_CACHE_FILE
    
    def _parse_version(self, version_string):
        """Parse version string to tuple for comparison"""
        try:
            # Remove 'v' prefix if present
            version_string = version_string.lstrip('v')
            return tuple(map(int, version_string.split('.')))
        except:
            return (0, 0, 0)
    
    def _load_cache(self):
        """Load cached update information"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None
    
    def _save_cache(self, data):
        """Save update information to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def _should_check_updates(self):
        """Determine if we should check for updates based on cache"""
        cache = self._load_cache()
        if not cache:
            return True
        
        last_check = cache.get('last_check')
        if not last_check:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            elapsed = (datetime.now() - last_check_time).total_seconds()
            return elapsed > UPDATE_CHECK_INTERVAL
        except:
            return True
    
    def check_for_updates(self, force=False):
        """
        Check if updates are available
        
        Args:
            force: Force check even if cache is recent
            
        Returns:
            bool: True if update available, False otherwise
        """
        try:
            # Check cache first
            if not force and not self._should_check_updates():
                cache = self._load_cache()
                if cache:
                    self.latest_version = cache.get('latest_version')
                    self.update_info = cache.get('update_info')
                    
                    current = self._parse_version(self.current_version)
                    latest = self._parse_version(self.latest_version)
                    return latest > current
            
            # Fetch latest release info from server
            print("🔍 Checking for updates...")
            
            req = urllib.request.Request(
                UPDATE_SERVER_URL,
                headers={'User-Agent': 'TransportManagementSystem'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Parse GitHub release format
            self.latest_version = data.get('tag_name', '').lstrip('v')
            self.update_info = {
                'version': self.latest_version,
                'release_date': data.get('published_at'),
                'release_notes': data.get('body'),
                'download_url': None,
                'checksum': None
            }
            
            # Find installer asset
            for asset in data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    self.update_info['download_url'] = asset['browser_download_url']
                    self.update_info['size'] = asset['size']
                    break
            
            # Save to cache
            cache_data = {
                'last_check': datetime.now().isoformat(),
                'latest_version': self.latest_version,
                'update_info': self.update_info
            }
            self._save_cache(cache_data)
            
            # Compare versions
            current = self._parse_version(self.current_version)
            latest = self._parse_version(self.latest_version)
            
            if latest > current:
                print(f"✅ New version available: {self.latest_version}")
                print(f"   Current version: {self.current_version}")
                return True
            else:
                print(f"✅ You have the latest version: {self.current_version}")
                return False
            
        except urllib.error.URLError as e:
            print(f"⚠️  Unable to check for updates: Network error")
            return False
        except Exception as e:
            print(f"⚠️  Unable to check for updates: {str(e)}")
            return False
    
    def get_update_info(self):
        """Get information about available update"""
        if not self.update_info:
            self.check_for_updates()
        return self.update_info
    
    def download_update(self, output_dir="."):
        """
        Download the latest update
        
        Args:
            output_dir: Directory to save the installer
            
        Returns:
            str: Path to downloaded file, or None on failure
        """
        try:
            if not self.update_info or not self.update_info.get('download_url'):
                print("❌ No update information available")
                return None
            
            download_url = self.update_info['download_url']
            filename = os.path.basename(download_url)
            output_path = os.path.join(output_dir, filename)
            
            print(f"📥 Downloading update...")
            print(f"   Version: {self.latest_version}")
            print(f"   URL: {download_url}")
            print(f"   Destination: {output_path}")
            
            # Download with progress
            def reporthook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 / total_size)
                print(f"\r   Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)", end='')
            
            urllib.request.urlretrieve(download_url, output_path, reporthook)
            print()  # New line after progress
            
            # Verify download
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✅ Download complete!")
                print(f"   Size: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
                print(f"   Path: {output_path}")
                return output_path
            else:
                print(f"❌ Download failed: File not found")
                return None
            
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return None
    
    def install_update(self, installer_path):
        """
        Install the downloaded update
        
        Args:
            installer_path: Path to installer file
            
        Returns:
            bool: True if installation started, False otherwise
        """
        try:
            if not os.path.exists(installer_path):
                print(f"❌ Installer not found: {installer_path}")
                return False
            
            print(f"🚀 Starting installer...")
            print(f"   Path: {installer_path}")
            print(f"\n⚠️  The application will close after starting the installer.")
            print(f"   The installer will guide you through the update process.")
            
            # Confirm installation
            response = input("\nProceed with installation? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Installation cancelled")
                return False
            
            # Start installer
            if sys.platform == 'win32':
                # Windows: Start installer and exit
                subprocess.Popen([installer_path])
                print(f"✅ Installer started. Exiting application...")
                return True
            else:
                print(f"❌ Auto-installation not supported on this platform")
                print(f"   Please run the installer manually: {installer_path}")
                return False
            
        except Exception as e:
            print(f"❌ Installation failed: {str(e)}")
            return False


class UpdateNotifier:
    """Notify users about available updates"""
    
    def __init__(self):
        self.checker = UpdateChecker()
    
    def check_and_notify(self):
        """Check for updates and show notification if available"""
        try:
            if self.checker.check_for_updates():
                info = self.checker.get_update_info()
                
                print(f"\n{'='*60}")
                print(f"🎉 NEW VERSION AVAILABLE!")
                print(f"{'='*60}")
                print(f"Current Version: {self.checker.current_version}")
                print(f"Latest Version:  {self.checker.latest_version}")
                print(f"Release Date:    {info.get('release_date', 'N/A')}")
                print(f"\nRelease Notes:")
                print(f"{'-'*60}")
                print(info.get('release_notes', 'No release notes available'))
                print(f"{'='*60}\n")
                
                return True
            return False
        except Exception as e:
            print(f"⚠️  Update check failed: {str(e)}")
            return False
    
    def prompt_download(self):
        """Prompt user to download update"""
        response = input("Would you like to download the update? (yes/no): ")
        if response.lower() == 'yes':
            installer_path = self.checker.download_update()
            if installer_path:
                return self.prompt_install(installer_path)
        return False
    
    def prompt_install(self, installer_path):
        """Prompt user to install update"""
        return self.checker.install_update(installer_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Auto-Update Utility for Transport Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check
  %(prog)s check --force
  %(prog)s download
  %(prog)s install path/to/installer.exe
  %(prog)s interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check for updates')
    check_parser.add_argument('--force', action='store_true', help='Force check, ignore cache')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download latest update')
    download_parser.add_argument('--output-dir', default='.', help='Output directory')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install downloaded update')
    install_parser.add_argument('installer_path', help='Path to installer file')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Interactive update process')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'check':
        checker = UpdateChecker()
        has_update = checker.check_for_updates(force=args.force)
        
        if has_update:
            info = checker.get_update_info()
            print(f"\nUpdate Information:")
            print(f"  Version: {info.get('version')}")
            print(f"  Release Date: {info.get('release_date')}")
            print(f"  Download URL: {info.get('download_url')}")
        
        return 0 if has_update else 1
    
    elif args.command == 'download':
        checker = UpdateChecker()
        if checker.check_for_updates():
            installer_path = checker.download_update(args.output_dir)
            return 0 if installer_path else 1
        else:
            print("No updates available")
            return 1
    
    elif args.command == 'install':
        checker = UpdateChecker()
        success = checker.install_update(args.installer_path)
        return 0 if success else 1
    
    elif args.command == 'interactive':
        notifier = UpdateNotifier()
        if notifier.check_and_notify():
            notifier.prompt_download()
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
