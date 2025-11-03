import requests
import json
from urllib.parse import urlparse, parse_qs
from langchain_core.tools import tool

def get_files_list_github(token, owner, repo, branch):
    """Get list of files from GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=true"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch files, Error Code: {response.status_code}")
        return []
    
    files = response.json().get('tree', [])
    return [item['path'] for item in files if item['type'] == 'blob']

def get_repo_content_github(token, owner, repo, file_path, branch):
    """Get file content from GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {file_path}")
        return None
    
    import base64
    content = response.json().get('content', '')
    decoded_content = base64.b64decode(content).decode('utf-8')
    return decoded_content

@tool
def implementation():
    """
    The Particular function returns the json file which contains all the code in the given branch in a
    given repository. Your work is to write the Unit Tests for code and provide the data for the same.
    Also you have to convert the response in proper string such that it will explicitly show unit tests for each file.
    The response should be in MARKDOWN format.
    """
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Use GitHub credentials
    token = config['github']['token']
    owner = config['github']['repo_owner']
    repo = config['github']['repo_name']
    branch = 'main'  # Default branch

    try:
        # Get list of Python files
        all_files = get_files_list_github(token, owner, repo, branch)
        python_files = [f for f in all_files if f.endswith('.py') and not f.startswith('test_')]
        
        print(f"Found {len(python_files)} Python files: {python_files}")
        
        all_content = {}
        
        for file_path in python_files:
            content = get_repo_content_github(token, owner, repo, file_path, branch)
            if content:
                all_content[file_path] = content
                print(f"Fetched content for {file_path}")
        
        return all_content
        
    except Exception as e:
        print(f"Error in implementation: {e}")
        return {"error": str(e)}