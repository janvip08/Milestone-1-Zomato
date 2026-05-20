import os
import requests

images = {
    "indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800&q=80",
    "italian": "https://images.unsplash.com/photo-1498579150354-977475b0ea0b?w=800&q=80",
    "japanese": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=800&q=80",
    "chinese": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80",
    "cafe": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&q=80",
    "fine_dining": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80",
    "default": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80",
}

os.makedirs(r"c:\Users\Abhishek kapoor\Milestone 1\phase4\assets", exist_ok=True)
for name, url in images.items():
    print(f"Downloading {name}...")
    r = requests.get(url)
    if r.status_code == 200:
        with open(rf"c:\Users\Abhishek kapoor\Milestone 1\phase4\assets\{name}.jpg", "wb") as f:
            f.write(r.content)
    else:
        print(f"Failed {name}")
