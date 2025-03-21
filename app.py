import os
import requests
from flask import Flask

app = Flask(__name__)

# Load credentials securely from environment variables
GITHUB_PAT = os.getenv("GITHUB_PAT")  # GitHub Personal Access Token
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Example: "ultralegend14/deepfake"
CODESPACE_NAME = os.getenv("CODESPACE_NAME")  # Example: "refactored-meme-5g4wr7p95jr6cv5r4"

HEADERS = {
    "Authorization": f"token {GITHUB_PAT}",
    "Accept": "application/vnd.github+json"
}

# Function to fetch Codespace info
def get_codespace():
    url = "https://api.github.com/user/codespaces"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 403:
        return "GitHub API rate limit exceeded. Try again later."
    elif response.status_code != 200:
        return f"GitHub API error: {response.text}"

    codespaces = response.json().get("codespaces", [])
    for cs in codespaces:
        if cs["name"] == CODESPACE_NAME:
            return cs  # Return the full Codespace object
    return None  # No Codespace found

# Function to create a new Codespace if needed
def create_codespace():
    url = "https://api.github.com/user/codespaces"
    payload = {
        "repository": GITHUB_REPO,
        "branch": "main",
        "machine": "standardLinux32gb",  # Adjust machine size if needed
    }
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 201:
        return "New Codespace created successfully!"
    return f"Failed to create Codespace: {response.text}"

# Function to restart an existing Codespace
def restart_codespace():
    codespace = get_codespace()
    
    if not codespace:
        return create_codespace()  # Create a new one if not found

    status = codespace.get("state", "Unknown")
    codespace_id = codespace["id"]

    if status == "Available":
        return "Codespace is already running."
    
    elif status in ["Shutting down", "Starting"]:
        return f"Codespace is currently {status}. Please wait."

    elif status in ["Stopped", "Unknown"]:
        print("Restarting Codespace...")
        restart_url = f"https://api.github.com/user/codespaces/{codespace_id}/start"
        response = requests.post(restart_url, headers=HEADERS)

        if response.status_code == 204:
            return "Codespace restarted successfully!"
        return f"Failed to restart Codespace: {response.text}"

    return "Unhandled Codespace state."

@app.route("/")
def monitor():
    message = restart_codespace()
    return message

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
