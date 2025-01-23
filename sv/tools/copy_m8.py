import os
import zipfile

M8Path, ZipPath = "/Volumes/M8", "tmp/zip"

if __name__ == "__main__":
    if not os.path.exists(M8Path):
        print(f"Directory {M8Path} does not exist. Exiting.")
        exit()
    stems_path = os.path.join(M8Path, "Stems", "sv")
    os.makedirs(stems_path, exist_ok=True)
    for entry in os.listdir(ZipPath):
        if entry.endswith(".zip"):
            zip_file_path = os.path.join(ZipPath, entry)
            file_name = os.path.splitext(entry)[0]
            target_dir = os.path.join(stems_path, file_name)            
            os.makedirs(target_dir, exist_ok=True)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                for src in zip_ref.namelist():
                    if src.endswith(".wav"):
                        dest_path = os.path.join(target_dir, os.path.basename(src))
                        print(f"Extracting {src} to {dest_path}")
                        with zip_ref.open(src) as src_file, open(dest_path, 'wb') as dest_file:
                            dest_file.write(src_file.read())
