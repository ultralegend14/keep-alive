import requests
from flask import Flask

app = Flask(__name__)

# GitHub API Credentials (Replace with your own)
GITHUB_USERNAME = "ultralegend14"
GITHUB_PAT = "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"  # ⚠️ SECURITY RISK: Use Railway ENV variables instead!
CODESPACE_NAME = "refactored-meme-5g4wr7p95jr6cv5r4"

HEADERS = {
    "Authorization": f"token {GITHUB_PAT}",
    "Accept": "application/vnd.github+json"
}

# Function to get Codespace info
def get_codespace():
    url = "https://api.github.com/user/codespaces"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        codespaces = response.json().get("codespaces", [])
        for cs in codespaces:
            if cs["name"] == CODESPACE_NAME:
                return cs  # Return full Codespace object
    return None

# Function to restart Codespace if needed
def ensure_codespace_running():
    codespace = get_codespace()
    
    if not codespace:
        return "Error: Codespace not found. Make sure it's created."

    status = codespace.get("state", "Unknown")
    codespace_id = codespace["id"]

    if status == "Available":
        return "✅ Codespace is already running."

    elif status in ["Shutting down", "Starting"]:
        return f"⏳ Codespace is currently {status}. Please wait."

    elif status in ["Stopped", "Unknown"]:
        print("🔄 Restarting Codespace...")
        restart_url = f"https://api.github.com/user/codespaces/{codespace_id}/start"
        response = requests.post(restart_url, headers=HEADERS)

        if response.status_code == 204:
            return "✅ Codespace restarted successfully!"
        else:
            return f"❌ Failed to restart Codespace: {response.text}"

    return "⚠️ Unhandled Codespace state."

@app.route("/")
def monitor():
    message = ensure_codespace_running()
    return message

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
