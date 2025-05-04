import os
import shutil
import stat

# Define ANSI color codes for colored output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def rollback_changes(directory):
    """
    Recursively rollback changes by restoring files from their corresponding .bak backups.
    Deletes the .bak files after restoration and preserves the original file's access permissions.
    Also deletes unnecessary files from ./organizations/cryptogen/ and removes unwanted folders 
    in ./organizations/fabric-ca/ (keeping only ordererOrg, org1, and org2).

    Args:
        directory (str): The path to the directory containing the files and backups.
    """
    if not os.path.isdir(directory):
        print(f"{RED}Error: {directory} is not a valid directory.{RESET}")
        return

    # Walk through all subdirectories and files
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".bak"):
                original_file = filename[:-4]  # Remove .bak extension
                backup_file = os.path.join(root, filename)
                original_file_path = os.path.join(root, original_file)

                # Restore the original file
                if os.path.exists(original_file_path):
                    original_permissions = os.stat(original_file_path).st_mode
                    shutil.copy2(backup_file, original_file_path)
                    os.chmod(original_file_path, original_permissions)  # Restore permissions
                    print(f"{GREEN}Restored: {original_file} from {filename}{RESET}")
                else:
                    shutil.copy2(backup_file, original_file_path)
                    print(f"{GREEN}Restored missing file: {original_file} from {filename}{RESET}")

                # Delete the backup file
                try:
                    os.remove(backup_file)
                    print(f"{RED}Deleted backup: {backup_file}{RESET}")
                except Exception as e:
                    print(f"{RED}Error deleting backup {backup_file}: {e}{RESET}")

    # Cleanup files in organizations/cryptogen/
    cryptogen_path = os.path.join(directory, "organizations/cryptogen/")
    if os.path.isdir(cryptogen_path):
        for filename in os.listdir(cryptogen_path):
            if filename not in ("crypto-config-org1.yaml", "crypto-config-org2.yaml", "crypto-config-orderer.yaml"):
                file_path = os.path.join(cryptogen_path, filename)
                try:
                    os.remove(file_path)
                    print(f"{RED}Deleted: {file_path}{RESET}")
                except Exception as e:
                    print(f"{RED}Error deleting {file_path}: {e}{RESET}")
    else:
        print(f"{RED}Warning: {cryptogen_path} directory does not exist.{RESET}")

    # Cleanup unwanted folders in organizations/fabric-ca/
    fabric_ca_path = os.path.join(directory, "organizations/fabric-ca/")
    if os.path.isdir(fabric_ca_path):
        allowed_folders = {"ordererOrg", "org1", "org2"}
        for folder in os.listdir(fabric_ca_path):
            folder_path = os.path.join(fabric_ca_path, folder)
            if os.path.isdir(folder_path) and folder not in allowed_folders:
                try:
                    shutil.rmtree(folder_path)
                    print(f"{RED}Deleted folder: {folder_path}{RESET}")
                except Exception as e:
                    print(f"{RED}Error deleting folder {folder_path}: {e}{RESET}")
    else:
        print(f"{RED}Warning: {fabric_ca_path} directory does not exist.{RESET}")

    print(f"{GREEN}Rollback completed.{RESET}")

# Specify the directory where the files and .bak backups are located
directory_path = "./"  # Change this to the correct path if needed
rollback_changes(directory_path)
