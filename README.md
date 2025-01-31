A simple tool that lets you download assets and data of a selected Minecraft version.

## Running the script

> [!NOTE]
> An executable is available for Windows, in the releases section.

> [!WARNING]
> Ensure you have Python and pip installed.

<details>
<summary>Option A: Using a Virtual Environment (recommended)</summary>
<br>

1. Create a virtual environment to isolate project dependencies:
    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```bash
        venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
3. Install the dependencies (only required to do once):
    ```bash
    pip install -r requirements.txt
    ```

4. Running the script:
    ```bash
    python main.py
    ```

5. Afterwards, if you would like to exit the Virtual Environment, run:
    ```bash
    deactivate
    ```
    You can always activate it again for the next time you run the script (step 2).

</details>

<details>
<summary>Option B: Global Installation</summary>
<br>

1. Install the dependencies (only required to do once):
    - On Windows:
        ```bash
        pip install -r requirements.txt
        ```
    - On macOS and Linux:
        ```bash
        pip install -r requirements.txt
        ```
   
2. Install the dependencies (only required to do once):
    ```bash
    pip install -r requirements.txt
    ```

3. Running the script:
    ```bash
    python main.py
    ```
</details>

## Usage
> [!NOTE]
> If you want to download sounds, fonts or icons select Y when prompted to download hashed assets.

When you run the script, you can use up and down arrow keys for navigation, to search press F and to exit search Esc (also Esc if you want to stop script because Ctrl+C doesn't work).

Or, to avoid navigating through the scary ASCII interface, you can run:
```bash
python main.py <version>
```
Where `<version>` is the version you want to download (e.g., `25w05a`, `1.21.2-pre1`, etc.)
