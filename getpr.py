import requests
import json
from datetime import datetime
from langchain_core.tools import tool
from urllib.parse import urlparse


# from config import USERNAME,ACCESS_TOKEN,REPO_OWNER,REPO_SLUG,PULL_REQUEST_ID

@tool
def get_pr(pr_url, acc_tok):
    """
      The particular function returns a pull_request_json file which contains the details of file and Pull request.
      The tool returns a pull_request_json file which contains the details of file and Pull request.
      The file contains the changes which happened due to the pull request. The changes include the added lines and
      removed lines with their line number. There is files section which have all these changes explicitly mentioned
      with the filename.Use this tool to analyze the changes made in a pull request and provide code review
    """
    with open('config.json', 'r') as file:
        config = json.load(file)

    GITHUB_TOKEN = config['github']['token']
    GITHUB_USERNAME = config['github']['username']
    
    # Parse GitHub PR URL: https://github.com/owner/repo/pull/123
    parsed_url = urlparse(pr_url)
    path_components = parsed_url.path.split('/')
    
    REPO_OWNER = path_components[1]
    REPO_NAME = path_components[2]
    PULL_REQUEST_ID = int(path_components[4])

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    pull_request_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PULL_REQUEST_ID}"
    pull_request_response = requests.get(pull_request_url, headers=headers)
    pull_request_response.raise_for_status()
    pull_request = pull_request_response.json()

    created_at_datetime = pull_request['created_at']

    pull_request_details = {
        "title": pull_request['title'],
        "author": pull_request['user']['login'],
        "state": pull_request['state'],
        "created_at": created_at_datetime,
        "body": pull_request.get('body', ''),
        "files": []
    }

    changes_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PULL_REQUEST_ID}/files"
    changes_response = requests.get(changes_url, headers=headers)
    changes_response.raise_for_status()
    changes = changes_response.json()

    for change in changes:
        file_details = {
            "filename": change['filename'],
            "status": change['status'],
            "additions": change['additions'],
            "deletions": change['deletions'],
            "changes": change['changes'],
            "added_lines": [],
            "removed_lines": []
        }

        diff_content = change['patch']
        
        added_lines = []
        removed_lines = []
        
        if diff_content:
            lines = diff_content.split('\n')
            line_number = 0
            
            for line in lines:
                if line.startswith('@@'):
                    # Parse the @@ line to get line numbers
                    import re
                    match = re.search(r'@@ -(\d+),?\d* \+(\d+),?\d* @@', line)
                    if match:
                        line_number = int(match.group(2))
                elif line.startswith('+') and not line.startswith('+++'):
                    added_lines.append((line_number, line[1:]))
                    line_number += 1
                elif line.startswith('-') and not line.startswith('---'):
                    removed_lines.append((line_number, line[1:]))
                elif line.startswith(' '):
                    line_number += 1

        file_details["added_lines"] = added_lines
        file_details["removed_lines"] = removed_lines
        pull_request_details["files"].append(file_details)

    pull_request_json = json.dumps(pull_request_details, indent=4)
    print(pull_request_json)
    return pull_request_json


# print(get_pr())
# get_pr()
