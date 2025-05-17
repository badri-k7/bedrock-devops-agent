import os
import base64
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def push_changelog(repo, content, changelog_path="CHANGELOG.md"):
    github_token = os.environ['GITHUB_PAT']
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f"https://api.github.com/repos/{repo}/contents/{changelog_path}"
    logger.info(f"[GitHub] Fetching current changelog content from: {url}")

    response = requests.get(url, headers=headers)
    logger.info(f"[GitHub] GET response code: {response.status_code}")
    logger.info(f"[GitHub] GET response body: {response.text}")
    response.raise_for_status()

    data = response.json()
    sha = data['sha']
    current_content = base64.b64decode(data['content']).decode('utf-8')

    logger.info("[GitHub] Current SHA: %s", sha)
    logger.info("[GitHub] Existing CHANGELOG.md content (truncated):\n%s", current_content[:200])

    updated_content = content + "\n\n" + current_content
    b64_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

    commit_data = {
        "message": "chore: update CHANGELOG.md with latest release notes",
        "content": b64_content,
        "sha": sha
    }

    logger.info("[GitHub] Commit payload:\n%s", json.dumps(commit_data, indent=2))

    commit_response = requests.put(url, headers=headers, json=commit_data)
    logger.info(f"[GitHub] PUT response code: {commit_response.status_code}")
    logger.info(f"[GitHub] PUT response body: {commit_response.text}")
    commit_response.raise_for_status()

    return commit_response.json()

def lambda_handler(event, context):
    print("## Start of function ##")
    print(event)

    github_token = os.environ['GITHUB_PAT']
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    resource = event.get('resource')
    method = event.get('httpMethod')

    if resource == '/commits' and method == 'GET':
        params = event.get('queryStringParameters') or {}
        repo = params.get('repo')
        branch = params.get('branch', 'main')

        if not repo:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required query parameter: repo'})
            }

        url = f'https://api.github.com/repos/{repo}/commits?sha={branch}&per_page=10'

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commits = [commit['commit']['message'] for commit in response.json()]
            return {
                'statusCode': 200,
                'body': json.dumps(commits)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

    elif resource == '/push-changelog' and method == 'POST':
        try:
            logger.info("[API] Received POST /push-changelog request")
            body = json.loads(event['body'])
            repo = body.get('repo')
            content = body.get('content')
            changelog_path = body.get('path', 'CHANGELOG.md')

            logger.info("[API] Extracted repo: %s", repo)
            logger.info("[API] Extracted content (truncated): %s", content[:200])
            logger.info("[API] Target changelog path: %s", changelog_path)

            if not repo or not content:
                logger.warning("[API] Missing required fields in payload")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing repo or content in payload'})
                }

            logger.info("[API] Calling push_changelog()...")
            result = push_changelog(repo, content, changelog_path)
            logger.info("[API] push_changelog() completed successfully")

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        except Exception as e:
            logger.error("[API] Error during push_changelog(): %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    elif resource == '/files-changed' and method == 'GET':
        try:
            params = event.get('queryStringParameters') or {}
            repo = params.get('repo')
            branch = params.get('branch', 'main')
            count = int(params.get('count', 5))

            if not repo:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing required query parameter: repo'})
                }

            commits_url = f'https://api.github.com/repos/{repo}/commits?sha={branch}&per_page={count}'
            response = requests.get(commits_url, headers=headers)
            response.raise_for_status()
            commits = response.json()

            file_set = set()
            for commit in commits:
                sha = commit['sha']
                details_url = f'https://api.github.com/repos/{repo}/commits/{sha}'
                detail_resp = requests.get(details_url, headers=headers)
                detail_resp.raise_for_status()
                files = detail_resp.json().get('files', [])
                for f in files:
                    file_set.add(f['filename'])

            return {
                'statusCode': 200,
                'body': json.dumps(sorted(file_set))
            }
 
        except Exception as e:
            logger.error("[API] Error during /files-changed: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Unsupported path or method'})
        }