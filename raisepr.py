import requests
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import json
from langchain_core.tools import tool
from repofetch import implementation
from shared import get_unit_test_response, set_unit_test_response
from langchain_core.tools import Tool

now = datetime.now()
formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

def get_github_headers(token):
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

def get_commit_sha(token, owner, repo, branch):
    """Get the SHA of the latest commit on a branch"""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    response = requests.get(url, headers=get_github_headers(token))
    if response.status_code == 200:
        return response.json()['commit']['sha']
    return None

def branch_exists(token, owner, repo, branch_name):
    """Check if a branch exists"""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch_name}"
    response = requests.get(url, headers=get_github_headers(token))
    return response.status_code == 200

def create_branch_github(token, owner, repo, new_branch_name, source_branch_name):
    """Create a new branch on GitHub"""
    source_sha = get_commit_sha(token, owner, repo, source_branch_name)
    if not source_sha:
        print(f"Failed to get SHA for source branch {source_branch_name}")
        return False
    
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    payload = {
        "ref": f"refs/heads/{new_branch_name}",
        "sha": source_sha
    }
    
    response = requests.post(url, json=payload, headers=get_github_headers(token))
    if response.status_code == 201:
        print("Branch created successfully on GitHub.")
        return True
    else:
        print(f"Failed to create branch: {response.status_code}")
        print(response.json())
        return False

def create_file_in_github(token, owner, repo, branch_name, file_path, file_content, commit_message):
    """Create a file in GitHub repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    # Check if file exists
    response = requests.get(url, headers=get_github_headers(token), params={'ref': branch_name})
    
    payload = {
        "message": commit_message,
        "content": file_content.encode('utf-8').decode('latin-1'),  # GitHub expects base64-like encoding
        "branch": branch_name
    }
    
    if response.status_code == 200:
        # File exists, update it
        existing_file = response.json()
        payload["sha"] = existing_file["sha"]
        method = "PUT"
    else:
        # File doesn't exist, create it
        method = "PUT"
    
    response = requests.put(url, json=payload, headers=get_github_headers(token))
    if response.status_code in [200, 201]:
        print(f"File {file_path} created/updated successfully in branch {branch_name}.")
        return True
    else:
        print(f"Failed to create/update file {file_path}: {response.status_code}")
        print(response.json())
        return False

def create_pull_request_github(token, owner, repo, from_branch, to_branch, title, description):
    """Create a pull request on GitHub"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {
        "title": title,
        "body": description,
        "head": from_branch,
        "base": to_branch
    }
    
    response = requests.post(url, json=payload, headers=get_github_headers(token))
    if response.status_code == 201:
        print("Pull request created successfully on GitHub.")
        return response.json()
    else:
        print(f"Failed to create pull request: {response.status_code}")
        print(response.json())
        return None

async def send_pr(*args):
    """
    GitHub implementation for creating unit test files and raising pull requests
    """
    with open('config.json', 'r') as file:
        config = json.load(file)

    token = config['github']['token']
    username = config['github']['username']
    repo_url = config['github']['repo_url'] if 'repo_url' in config['github'] else None

    if repo_url:
        parsed_url = urlparse(repo_url)
        path_components = parsed_url.path.split('/')
        repo_owner = path_components[1]
        repo_name = path_components[2]
    else:
        repo_owner = config['github']['repo_owner']
        repo_name = config['github']['repo_name']

    source_branch_name = "main"  
    new_branch_name = "unit-tests-" + formatted_now.replace(" ", "-").replace(":", "-")
    folder_path = "tests"

    print("Waiting for unit test response...")
    unit_test_response = await get_unit_test_response()
    print(f"Unit test response received: {unit_test_response}")

    file_contents = unit_test_response.split('###')
    
    # Create branch
    branch_created = create_branch_github(token, repo_owner, repo_name, new_branch_name, source_branch_name)
    if not branch_created:
        print("Branch creation failed. Exiting...")
        return

    # Create test files
    for file_content in file_contents:
        if file_content.strip():
            lines = file_content.strip().split('\n')
            file_name = lines[0].strip().replace('###', '').strip()
            content = '\n'.join(lines[1:]).strip().strip('"""').strip("'''").strip()
            
            if content:
                file_path = f"{folder_path}/test_{file_name}"
                commit_message = f"Add unit tests for {file_name}"
                
                print(f"Creating file {file_name} with content:\n{content}")
                create_file_in_github(token, repo_owner, repo_name, new_branch_name, file_path, content, commit_message)

    resp = create_pull_request_github(
        token=token,
        owner=repo_owner,
        repo=repo_name,
        from_branch=new_branch_name,
        to_branch=source_branch_name,
        title=f"Add Unit Tests - {formatted_now}",
        description="This PR adds comprehensive unit tests for the codebase."
    )

    return resp

async def send_pr_wrapper(*args):
    await send_pr()

pr_tool = Tool(
    name="request",
    func=send_pr_wrapper,
    description="The tool will wait until the unit tests are generated and then will scrap the unit test response. after that branch will be created and in that branch unit test files will be pushed"
)



if __name__ == "__main__":
    import asyncio
    asyncio.run(send_pr_wrapper())
