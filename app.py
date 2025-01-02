from flask import Flask, request, render_template
import requests
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Fetch Groq API key and GitHub token from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Initialize Groq client with API key
client = Groq(api_key=GROQ_API_KEY)

# HTML form template
template = """
<!doctype html>
<html>
    <body>
        <h1>GitHub Commit Summarizer</h1>
        <form method="post">
            <label for="repo_url">GitHub Repo URL:</label>
            <input type="text" name="repo_url" required>
            <button type="submit">Generate Summary</button>
        </form>
        {% if summary %}
            <h2>Commit Summary:</h2>
            <p>{{ summary }}</p>
        {% endif %}
    </body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        owner, repo = parse_repo_url(repo_url)
        commits = fetch_commits(owner, repo)
        summary = summarize_commits(commits)
    return render_template('index.html', summary=summary)

def parse_repo_url(url):
    parts = url.rstrip('/').split('/')
    return parts[-2], parts[-1]

def fetch_commits(owner, repo):
    # Define headers with the access token for authentication
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    # GitHub API for fetching commits
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    print(f"Fetching commits from: {api_url}")  # Debug message: shows the API URL being accessed

    response = requests.get(api_url, headers=headers)
    
    # Debugging the status code and response
    print(f"Status Code: {response.status_code}")  # Debug: Status code of the response
    if response.status_code == 200:
        print("Successfully fetched commits.")  # Debug: Success message
        commits = response.json()
        if commits:
            print(f"Found {len(commits)} commits.")  # Debug: Number of commits found
        else:
            print("No commits found in the response.")  # Debug: No commits found in the response
        return [commit['commit']['message'] for commit in commits[:5]]  # Fetch last 5 commits
    elif response.status_code == 403:
        print("Rate limit exceeded or token is invalid.")  # Debug: If rate limit exceeded or token is invalid
        return []
    else:
        print(f"Failed to fetch commits: {response.status_code}")  # Debug: Failure message with status code
        return []

def summarize_commits(commits):
    if not commits:
        return "No commits found."

    # Groq API call to summarize the commits
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarize the following commit messages:\n" + "\n".join(commits)}
        ],
        model="llama-3.3-70b-versatile",  # Adjust model as needed
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    # Return the summary
    return chat_completion.choices[0].message.content.strip()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
