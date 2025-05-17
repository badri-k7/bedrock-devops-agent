import logging 
from typing import Dict, Any
from http import HTTPStatus
import requests
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

API_GATEWAY_BASE_URL = "https://apalws54r5.execute-api.us-west-2.amazonaws.com/prod"

def extract_parameters(param_list):
    return {item['name']: item['value'] for item in param_list if 'name' in item and 'value' in item}

def format_bedrock_response(action_group, api_path, http_method, status_code, payload, message_version=1):
    return {
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": payload
                }
            }
        },
        "messageVersion": message_version
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("## Start of Lambda Function ##")
    logger.info("Event: %s", json.dumps(event, indent=2))

    action_group = event.get("actionGroup", "unknown")
    api_path = event.get("apiPath", "unknown")
    http_method = event.get("httpMethod", "unknown")
    message_version = event.get("messageVersion", 1)

    try:
        parameters = extract_parameters(event.get("parameters", []))

        if api_path == "/commits" and http_method.upper() == "GET":
            repo = parameters.get("repo")
            branch = parameters.get("branch", "main")
            if not repo:
                raise ValueError("Missing required parameter: 'repo'")

            query_params = {"repo": repo, "branch": branch}
            url = f"{API_GATEWAY_BASE_URL}{api_path}"
            resp = requests.get(url, params=query_params)
            resp.raise_for_status()
            return format_bedrock_response(action_group, api_path, http_method, 200, resp.json(), message_version)

        elif api_path == "/files-changed" and http_method.upper() == "GET":
            repo = parameters.get("repo")
            branch = parameters.get("branch", "main")
            count = parameters.get("count", "5")  # default to 5 commits if not specified
            if not repo:
                raise ValueError("Missing required parameter: 'repo'")

            query_params = {"repo": repo, "branch": branch, "count": count}
            url = f"{API_GATEWAY_BASE_URL}{api_path}"
            resp = requests.get(url, params=query_params)
            resp.raise_for_status()
            return format_bedrock_response(action_group, api_path, http_method, 200, resp.json(), message_version)

        elif api_path == "/push-changelog" and http_method.upper() == "POST":
            try:
                props = event["requestBody"]["content"]["application/json"]["properties"]
                values = {item["name"]: item["value"] for item in props}
                repo = values.get("repo")
                content = values.get("content")
                if not repo or not content:
                    raise ValueError("Missing 'repo' or 'content' in request body")

                url = f"{API_GATEWAY_BASE_URL}{api_path}"
                payload = {"repo": repo, "content": content}
                resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
                resp.raise_for_status()
                return format_bedrock_response(action_group, api_path, http_method, 200, resp.json(), message_version)

            except KeyError:
                raise ValueError("Malformed requestBody from Bedrock Agent.")

        else:
            raise ValueError(f"Unsupported apiPath or httpMethod: {api_path} {http_method}")

    except ValueError as ve:
        logger.error("Input error: %s", str(ve))
        return format_bedrock_response(action_group, api_path, http_method, 400, {"error": str(ve)}, message_version)

    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return format_bedrock_response(action_group, api_path, http_method, 500, {"error": "Internal server error"}, message_version)
