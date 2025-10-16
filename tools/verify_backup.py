import zipfile, os

def verify_backup(file):
    """
    Verify a backup archive contains required files.
    
    Args:
        file (str): Path to the backup zip file
        
    Returns:
        str: "OK" if backup is valid, error message if not
    """
    try:
        with zipfile.ZipFile(file, 'r') as z:
            names = z.namelist()
            required = ["README.md", "requirements.txt", "app/"]
            missing = [r for r in required if not any(r in n for n in names)]
            return "OK" if not missing else f"Missing: {missing}"
    except Exception as e:
        return f"Error verifying backup: {e}"