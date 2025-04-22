import tarfile

def extract_file_from_tar(tar_path: str, suffix: str):
    """
    Extracts a file that ends with the given suffix from a tar archive.

    Args:
        tar_path (str): Path to the tar.xz archive.
        suffix (str): The filename suffix to look for (e.g., 'proc/loadavg').

    Returns:
        str or None: Decoded file contents if found and readable, otherwise None.
    """
    with tarfile.open(tar_path, "r:*") as tar:
        match = next((m for m in tar.getnames() if m.endswith(suffix)), None)
        if not match:
            return None
        try:
            f = tar.extractfile(match)
            return f.read().decode() if f else None
        except Exception:
            return None
