import requests
from pathlib import Path

def download_url(url, download_path):
	response = requests.get(url, stream=True)
	response.raise_for_status()
	download_path.parent.mkdir(exist_ok=True)
	with open(download_path, "wb") as f:
		for chunk in response.iter_content(chunk_size=8192):
			f.write(chunk)

hash = "b62ca8ec10d07e6bf5ac8dae0c8c1d2e6a1e3356"

download_url(f"https://resources.download.minecraft.net/{hash[:2]}/{hash}", Path(f"test/{hash[:5]}.png"))