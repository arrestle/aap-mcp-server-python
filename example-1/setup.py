import glob
import tarfile
import os

def inspect_sosreports(directory="tar"):
    tarballs = glob.glob(os.path.join(directory, "sosreport-*.tar.xz"))
    if not tarballs:
        print("No .tar.xz files found.")
        return

    for tarball_path in tarballs:
        print(f"\n📦 {tarball_path}")
        try:
            with tarfile.open(tarball_path, "r:*") as tar:
                members = tar.getmembers()

                for member in members:
                    # Skip directories or binary files (e.g., .tar inside .tar.xz)
                    if member.isdir() or member.name.endswith(('.tar', '.xz', '.gz')):
                        continue

                    print(f"  └── {member.name}")
                    try:
                        file_content = tar.extractfile(member).read().decode(errors='replace')
                        preview = "\n".join(file_content.splitlines()[:10])
                        print(f"      --- Contents (first 10 lines) ---\n{preview}\n")
                    except Exception as e:
                        print(f"      ⚠️ Could not read file content: {e}")

        except Exception as e:
            print(f"⚠️ Failed to process {tarball_path}: {e}")

if __name__ == "__main__":
    inspect_sosreports("tar")
