"""
Directory Helper Utilities - Windows-Compatible Path Creation
Ensures all directories are created properly before file operations
"""

import os


def ensure_user_directories(base_results_folder: str, user_id: int) -> dict:
    """
    Create all necessary directories for a user session
    
    Args:
        base_results_folder: Base results directory (e.g., 'results')
        user_id: Telegram user ID or chat ID
    
    Returns:
        dict with paths: {
            'user_folder': 'results/123456',
            'zip_folder': 'results/123456/zip',
            'logs_folder': 'results/123456/logs',
            'extracted_folder': 'results/123456/extracted'
        }
    """
    try:
        # Create base results folder first
        os.makedirs(base_results_folder, exist_ok=True)
        
        # Create user-specific folder
        user_folder = os.path.join(base_results_folder, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        
        # Create subfolders
        zip_folder = os.path.join(user_folder, 'zip')
        logs_folder = os.path.join(user_folder, 'logs')
        extracted_folder = os.path.join(user_folder, 'extracted')
        
        os.makedirs(zip_folder, exist_ok=True)
        os.makedirs(logs_folder, exist_ok=True)
        os.makedirs(extracted_folder, exist_ok=True)
        
        return {
            'user_folder': user_folder,
            'zip_folder': zip_folder,
            'logs_folder': logs_folder,
            'extracted_folder': extracted_folder
        }
    
    except Exception as e:
        # If creation fails, return None
        return None


def get_safe_zip_path(base_results_folder: str, user_id: int, filename: str = 'uploaded.zip') -> str:
    """
    Get a safe path for saving uploaded ZIP files
    
    Args:
        base_results_folder: Base results directory
        user_id: Telegram user ID
        filename: ZIP filename (default: 'uploaded.zip')
    
    Returns:
        Full path to save ZIP file: 'results/<user_id>/zip/uploaded.zip'
    """
    # Ensure directories exist
    dirs = ensure_user_directories(base_results_folder, user_id)
    
    if not dirs:
        # Fallback: try to create at least the user folder
        user_folder = os.path.join(base_results_folder, str(user_id))
        zip_folder = os.path.join(user_folder, 'zip')
        try:
            os.makedirs(zip_folder, exist_ok=True)
        except:
            pass
    else:
        zip_folder = dirs['zip_folder']
    
    # Return full path
    return os.path.join(zip_folder, filename)


def verify_write_access(path: str) -> bool:
    """
    Verify if we can write to a directory
    
    Args:
        path: Directory path to check
    
    Returns:
        True if writable, False otherwise
    """
    try:
        # Try to create the directory
        os.makedirs(path, exist_ok=True)
        
        # Try to create a test file
        test_file = os.path.join(path, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Remove test file
        os.remove(test_file)
        
        return True
    except:
        return False


def create_results_structure(base_results_folder: str = 'results') -> bool:
    """
    Create the base results directory structure
    
    Args:
        base_results_folder: Base results directory (default: 'results')
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create base folder
        os.makedirs(base_results_folder, exist_ok=True)
        
        # Create common subfolders
        common_folders = ['logs', 'temp', 'cache']
        for folder in common_folders:
            folder_path = os.path.join(base_results_folder, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        return True
    except:
        return False
