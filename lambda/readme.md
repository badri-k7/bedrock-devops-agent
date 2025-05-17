# Lambda Functions for DevOps Utility Agent

This folder contains the Lambda functions used by the Bedrock Agent's **DevOpsUtility** action group.

## 📂 Structure

- `devops_utility_action_group_handler.py`: Main Lambda handler file to route Bedrock Agent action group invocations.
- `devops_git_operations.py`: Helper module that performs GitHub operations like:
  - Fetching recent commit messages
  - Listing files changed in the last N commits
  - Pushing release notes to `CHANGELOG.md`

## ⚙️ Prerequisites

### Python Runtime
Ensure the Lambda functions are created using **Python 3.11** runtime.

### GitHub Token (GITHUB_PAT)
You need a GitHub Personal Access Token with `repo` scope to interact with GitHub APIs. This is set as an environment variable.

**Environment Variable:**

```env
GITHUB_PAT=<your-personal-access-token>
```

## 🚀 Lambda Setup Instructions

### 1. Create Lambda Functions

You need to create **two Lambda functions**:

---

#### 🔹 Lambda 1: DevOps Utility Action Group Handler

- **Name:** `DevOpsUtilityHandler`
- **Runtime:** Python 3.11
- **Handler:** `devops_utility_action_group_handler.lambda_handler`
- **Memory:** 256 MB
- **Timeout:** 30 seconds
- **Environment Variables:**
  - `GITHUB_PAT`

> Paste the contents of `devops_utility_action_group_handler.py`into the inline editor via the AWS Lambda Console.

---

#### 🔹 Lambda 2: GitHub Proxy Lambda for API Gateway

- **Name:** `APIGatewayProxyHandler`
- **Runtime:** Python 3.11
- **Handler:** `devops_git_operations.lambda_handler`
- **Memory:** 256 MB
- **Timeout:** 30 seconds
- **Environment Variables:**
  - `GITHUB_PAT`

> Paste the contents of `devops_git_operations.py` into the inline editor via the AWS Lambda Console.

---

### 2. Add Lambda Layer for `requests` Module

Since the `requests` library is not built-in, create a Lambda layer for it:

1. Create the layer package:

```bash
mkdir -p python
pip install requests -t python/
zip -r requests-layer.zip python
```

2. In the AWS Console:
   - Go to **Lambda > Layers** and create a new layer.
   - Upload `requests-layer.zip`
   - Set compatible runtime to **Python 3.11**
   - Once created, attach this layer to both Lambda functions under **Configuration > Layers**

---

### 3. Set Environment Variables

In the Lambda Console, go to each function’s **Configuration > Environment Variables** and set:

| Key         | Value                 |
|-------------|-----------------------|
| `GITHUB_PAT`| Your GitHub PAT Token |

---

### 4. Grant Invoke Permissions to Bedrock Agent

To allow Bedrock to invoke the Lambda function:

1. In AWS Console:
   - Navigate to your Lambda function (e.g., `DevOpsUtilityHandler`)
   - Go to **Permissions > Resource-based policy**
   - Click **Add permissions** → **OTHER**
   - Specify Bedrock as the principal: `bedrock.amazonaws.com`
   - Specify BedrockAgentArn under the ARN reference: `arn:aws:bedrock:<REGION>:<ACCOUNT_NUMBER>:agent/<RANDOM_AGENT_ID>`
   - Choose `InvokeFunction` action
   - Save

---

## 🔌 Supported Endpoints via API Gateway

These routes are defined in the OpenAPI schema and proxied by API Gateway:

| Endpoint           | Method | Description                            |
|--------------------|--------|----------------------------------------|
| `/commits`         | GET    | Retrieve latest commits                |
| `/files-changed`   | GET    | List changed files in last N commits   |
| `/push-changelog`  | POST   | Commit generated release notes         |
