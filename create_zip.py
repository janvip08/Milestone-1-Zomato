import os
import zipfile

def create_portfolio_zip():
    root_dir = r"c:\Users\Abhishek kapoor\Milestone 1"
    zip_path = os.path.join(root_dir, "Milestone1_Portfolio.zip")
    
    exclusions = ['.venv', '__pycache__', '.git', 'node_modules']
    exclude_files = ['.streamlit\\secrets.toml', '.streamlit/secrets.toml']

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Modifying dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclusions]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                # Skip excluded files
                if any(rel_path.endswith(ex) or rel_path.startswith(ex) for ex in exclude_files):
                    continue
                    
                # Skip the zip file itself and temporary scripts
                if file in ["Milestone1_Portfolio.zip", "create_zip.py", "download_images.py"]:
                    continue
                    
                zipf.write(file_path, rel_path)

if __name__ == "__main__":
    create_portfolio_zip()
    print(f"Zip created successfully at: c:\\Users\\Abhishek kapoor\\Milestone 1\\Milestone1_Portfolio.zip")
