# 🤖 Bedrock DevOps Utility Agent Setup Guide

This guide walks you through the process of setting up a Bedrock Agent that integrates with GitHub to generate and optionally push release notes using a Bedrock Action Group.

---

## ✅ Prerequisites

Ensure you have the following in place:

- An AWS account with Bedrock enabled in **Singapore Region (`ap-southeast-1`)**
- IAM permissions to create Bedrock agents, Lambda functions, API Gateway, and IAM roles
- A GitHub Personal Access Token (PAT) with `repo` scope
- AWS CLI or Console access

---

## 🧠 Step 1: Create a Bedrock Agent

1. Go to **Amazon Bedrock** → **Agents** → **Create Agent**
2. Name the agent, e.g., `DevOpsUtilityAgent`
3. Under **Foundation model**, select:
   - **Claude 3.5 Sonnet**
   - If not already activated, click on **Model access** in the Bedrock sidebar and enable Claude 3.5 Sonnet for your account.
4. Leave the knowledge base empty for now.
5. Save the agent.

---

## ✍️ Step 1.1: Add Agent Instruction

1. Open the agent you just created.
2. Under the **Instruction** section, copy the content from [`prompt.txt`](./prompt.txt) in this repo.
3. Paste it as the **System prompt** for your agent.
4. Save the update.

This instruction file guides the agent to:
- Generate categorized release notes from GitHub commits
- Ask the user for confirmation before committing to `CHANGELOG.md`
- Invoke appropriate functions based on intent (e.g., `getCommits`, `pushChangelog`)

---

## ⚙️ Step 2: Define the Action Group

1. Inside the agent, go to the **Action groups** tab.
2. Click **Create action group**.
3. Name it `DevopsUtility`
4. Upload the **OpenAPI schema** located in `./openapi/github-actions.yaml`
5. For Lambda function, select the one deployed as part of the [`lambda/github-handler.py`](lambda/github-handler.py) implementation.
6. Save the action group.

> 🧠 This Lambda function is responsible for handling GitHub API calls such as fetching commits, listing files changed, and pushing updates to `CHANGELOG.md`.

---

## 🚀 Next Steps

- Add this agent to an application (e.g., Bedrock Playground or an external chatbot)
- Interact using prompts like:
  > “Generate release notes for repo `org/repo-name` from branch `main`”
  > "Generate release notes for the repo "`org/repo-name`" from the `main` branch. Then, tell me which files were changed in the last 10 commits. And yes, go ahead and commit the release notes to the CHANGELOG.md."

---

## 📁 Files to Look At

- `lambda/github-handler.py`: Handles GitHub commit queries and changelog push
- `openapi/github-actions.yaml`: Defines the API interface for Bedrock action group
- `agent-setup.md`: This setup guide

---

## 📌 Region Note

All resources (agent, Lambda, API Gateway) should be created in the `ap-southeast-1` region (Singapore).
