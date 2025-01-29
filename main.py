import os
from zipfile import ZipFile
import msvcrt
import requests
from pathlib import Path
import json
import sys

_RESET = "\033[0m"
_HIGHLIGHT = "\033[30;103m"

def get_config(path):
	with open(Path("config.json"), "r") as f:
		return json.load(f).get(path)

WINDOW_SIZE = get_config("window_size")

def fetch_version_manifest():
	url = get_config("manifest_url")
	response = requests.get(url)
	response.raise_for_status()
	return response.json()

manifest = fetch_version_manifest()

versions = [v["id"] for v in manifest["versions"]]

search_mode = False
search_query = ""
filtered_versions = versions[:]
selected_index = 0

def get_key():
	key = msvcrt.getch()
	if key in {b'\xe0', b'\x00'}:  # Arrow keys pref
		key = msvcrt.getch()
	return key.decode('utf-8', errors='ignore')

def clear_screen():
	os.system('cls')

def draw():
	clear_screen()

	print("Minecraft Versions (Press 'F' to search, 'Esc' to exit search, 'Enter' to download)\n")

	if search_mode:
		print(f"Search: {search_query}_\n")
	
	print("+-----------------+")
	print("|     Version     |")
	print("+-----------------+")

	start_index = max(0, selected_index - WINDOW_SIZE // 2)
	end_index = min(len(filtered_versions), start_index + WINDOW_SIZE)
	
	for i in range(start_index, end_index):
		if i == selected_index:
			print(f"{_HIGHLIGHT}   {filtered_versions[i]}   {_RESET}")
		else:
			print(f"    {filtered_versions[i]}")

	#for i, version in enumerate(filtered_versions):
	#	if i == selected_index:
	#		print(f"{_HIGHLIGHT}   {version}   {_RESET}")
	#	else:
	#		print(f"    {version}    ")
	
	print("+-----------------+")

def update_filter():
	global filtered_versions, selected_index
	filtered_versions = [v for v in versions if search_query in v]
	selected_index = 0 if filtered_versions else -1

def download_version(version_url, download_dir):
	response = requests.get(version_url, stream=True)
	response.raise_for_status()
	with open(download_dir, "wb") as f:
		for chunk in response.iter_content(chunk_size=8192):
			f.write(chunk)

def extract_folders(jar_path, extract_dir):
  with ZipFile(jar_path, "r") as jar:
    files = [f for f in jar.namelist() if f.startswith("assets/") or f.startswith("data/")]
    for file in files:
    	jar.extract(file, extract_dir)

def download(id):
	output_dir = Path(get_config("output_dir"))
	output_dir.mkdir(exist_ok=True)
	
	version_info = next((v for v in manifest["versions"] if v["id"] == id), None)
	if not version_info:
		print("Snapshot not found in versions list.")
		return
	
	version_data = requests.get(version_info["url"]).json()
	jar_url = version_data["downloads"]["client"]["url"]

	version_folder = output_dir / id
	version_folder.mkdir(exist_ok=True)

	jar_path = version_folder / f"{id}.jar"

	print(f"Downloading {id}...")
	download_version(jar_url, jar_path)

	print("Extracting assets and data...")
	extract_folders(jar_path, version_folder)
	os.remove(jar_path)

	print("Done!")



def main(argv):
	global selected_index, search_mode, search_query

	if len(argv) > 1:
		download(argv[1])
		return
	
	draw()

	while True:
		key = get_key()
		if search_mode:
			if key == '\x1b':
				search_mode = False
				search_query = ""
				update_filter()
			if key == '\b':
				search_query = search_query[:-1]
			if key.isprintable():
				search_query += key
				update_filter()
		
		elif key == 'H' and selected_index > 0:
			selected_index -= 1
		elif key == 'P' and selected_index < len(filtered_versions):
			selected_index += 1
		elif key.lower() == 'f':
			search_mode = True
		elif key in {'\r', '\n'}:
			download(filtered_versions[selected_index])
			break
		elif key == '\x1b':
			print("Exiting...")
			break

		draw()

if __name__ == "__main__":
	main(sys.argv)