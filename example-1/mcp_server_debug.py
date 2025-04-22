
import tarfile
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("samba_debug")

ERROR_KEYWORDS = ["error", "nt_status", "not supported", "denied", "refused"]

def contains_error(line):
    return any(term in line.lower() for term in ERROR_KEYWORDS)

def inspect_samba_logs(tar_path):
    if not tarfile.is_tarfile(tar_path):
        logger.error(f"Not a valid tar file: {tar_path}")
        return

    with tarfile.open(tar_path, "r:*") as tar:
        members = [m for m in tar.getnames() if "samba" in m.lower()]
        members = [m for m in members if "old" not in m.lower()]

        if not members:
            logger.warning("No samba-related files found.")
            return

        logger.info(f"Scanning {len(members)} samba-related files for relevant errors...")
        for member in members:
            try:
                f = tar.extractfile(member)
                if not f:
                    continue
                lines = f.read().decode(errors="replace").splitlines()
                error_lines = [line for line in lines if contains_error(line)]

                if not error_lines:
                    continue  # skip this file if it has no relevant errors

                logger.info(f"🗂️ {member} — {len(error_lines)} relevant lines")
                for preview_line in error_lines[:5]:
                    logger.info(f"   {preview_line.strip()}")
                logger.info("...")

            except Exception as e:
                logger.warning(f"⚠️ Failed to process {member}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug.py <sosreport.tar.xz>")
        sys.exit(1)

    inspect_samba_logs(sys.argv[1])