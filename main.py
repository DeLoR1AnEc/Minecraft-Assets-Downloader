import os
from zipfile import ZipFile
import requests
from pathlib import Path
import json
import sys
import time

if os.name == 'nt':
	import msvcrt
else:
	import tty
	import termios

_RESET = "\033[0m"
_HIGHLIGHT = "\033[30;103m"

DEFAULT_CONFIG = {
	"manifest_url": "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
	"hashes_base_url": "https://resources.download.minecraft.net/",
	"window_size": 15,
	"output_dir": "versions"
}

def get_config(key):
	config = Path("config.json")
	if config.exists():
		with open(Path("config.json"), "r") as f:
			return json.load(f).get(key)
	else:
		return DEFAULT_CONFIG.get(key)

WINDOW_SIZE = get_config("window_size")

def fetch_piston_meta(url):
	response = requests.get(url)
	response.raise_for_status()
	return response.json()

manifest = fetch_piston_meta(get_config("manifest_url"))

versions = [v["id"] for v in manifest["versions"]]

search_mode = False
search_query = ""
filtered_versions = versions[:]
selected_index = 0

def get_key():
	if os.name == 'nt':
		key = msvcrt.getch()
		if key in {b'\xe0', b'\x00'}:
			key = msvcrt.getch()
		return key.decode('utf-8', errors='ignore')
	else:
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try: 
			tty.setraw(fd)
			key = sys.stdin.read(1)
			if key == '\x1b':
				next1 = sys.stdin.read(1)
				if next1 == '[':
					next2 = sys.stdin.read(1)
					return f'\x1b[{next2}]'
				return key
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def ask(msg):
	print(f"{msg} Y(yes) / N(no)\n")
	while True:
		key = get_key()
		match key.lower():
			case 'n':
				return False
			case 'y':
				return True
			case _:
				continue

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
			print(f"    {_HIGHLIGHT}{filtered_versions[i]}{_RESET}")
		else:
			print(f"    {filtered_versions[i]}")

	print("+-----------------+")

def update_filter():
	global filtered_versions, selected_index
	filtered_versions = [v for v in versions if search_query in v]
	selected_index = 0 if filtered_versions else -1

def download_url(url, download_path):
	response = requests.get(url, stream=True)
	if response.status_code == 429:
		reset_time = int(response.headers.get('X-RateLimit-Reset', time.time()))
		wait_time = reset_time - int(time.time())
		print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
		time.sleep(wait_time)
		download_url(url)
	response.raise_for_status()
	download_path.parent.mkdir(exist_ok=True, parents=True)
	with open(download_path, "wb") as f:
		for chunk in response.iter_content(chunk_size=8192):
			f.write(chunk)

def extract_folders(jar_path, extract_dir):
	with ZipFile(jar_path, "r") as jar:
		files = [f for f in jar.namelist() if f.startswith("assets/") or f.startswith("data/")]
		for file in files:
			jar.extract(file, extract_dir)

def copy_assets(url, dir):
	hashes = fetch_piston_meta(url)

	for asset, data in hashes["objects"].items():
		download_url(f"{get_config("hashes_base_url")}/{data["hash"][:2]}/{data["hash"]}", dir / "assets" / asset)

def download(id):
	hashed_selected = ask("Do you want to download hashed resources?")

	output_dir = Path(get_config("output_dir"))
	output_dir.mkdir(exist_ok=True)
	
	version_info = next((v for v in manifest["versions"] if v["id"] == id), None)
	if not version_info:
		print("Snapshot not found in versions list.")
		return
	
	version_data = fetch_piston_meta(version_info["url"])
	jar_url = version_data["downloads"]["client"]["url"]

	version_dir = output_dir / id
	version_dir.mkdir(exist_ok=True)

	jar_path = version_dir / f"{id}.jar"

	time_start = time.time()

	print(f"Downloading {id}...")
	download_url(jar_url, jar_path)

	print("Extracting assets and data...")
	extract_folders(jar_path, version_dir)
	os.remove(jar_path)

	if hashed_selected:
		print("Copying hashed assets...")
		copy_assets(version_data["assetIndex"]["url"], version_dir)

	print("Done!")

	time_end = time.time()
	print(f"Elapsed time: {(time_end - time_start):.2f} seconds.")

def main(argv):
	global selected_index, search_mode, search_query

	if len(argv) > 1:
		download(argv[1])
		return
	
	draw()

	while True:
		key = get_key()
		
		if selected_index > 0 and key in {'\x1b[A', 'H'}:
			selected_index -= 1
		if selected_index < len(filtered_versions) - 1 and key in {'\x1b[B', 'P'}:
			selected_index += 1
		
		if search_mode:
			if key == '\x1b':
				search_mode = False
				search_query = ""
				update_filter()
			if key in {'\b', '\x7f'}:
				search_query = search_query[:-1]
			if key.isprintable() and not (key in {'P', 'H', '\x1b[A', '\x1b[B'}):
				search_query += key
				update_filter()
			
		else:
			if key.lower() == 'f':
				search_mode = True
			if key == '\x1b':
				print("Exiting...")
				break
				
		if key in {'\r', '\n'}:
			download(filtered_versions[selected_index])
			break
		
		draw()

if __name__ == "__main__":
	main(sys.argv)
