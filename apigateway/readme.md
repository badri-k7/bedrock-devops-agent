# API Gateway Setup for DevOps Utility Agent

This folder contains the OpenAPI specification and instructions to configure API Gateway as the middleware between the Bedrock Agent and Lambda functions.

---

## 🌐 Overview

The API Gateway acts as a proxy between the Bedrock Agent's **DevOpsUtility** action group and the backend Lambda function. It translates HTTP requests into Lambda invocations and exposes the following endpoints:

| Endpoint           | Method | Description                          |
|--------------------|--------|--------------------------------------|
| `/commits`         | GET    | Retrieve latest commits              |
| `/files-changed`   | GET    | List changed files in recent commits |
| `/push-changelog`  | POST   | Push generated release notes to Git  |

These endpoints are defined in the OpenAPI schema and imported into API Gateway.

---

## 🚀 Setup Instructions

### 1. Open API Gateway Console

1. Go to [API Gateway Console](https://console.aws.amazon.com/apigateway).
2. Choose **REST API**.
3. Click **Create API** → Choose **Import**.

---

### 2. Import OpenAPI Schema

1. Upload the provided `swagger-apigateway-schema.yaml` file.
2. Ensure routes match the Lambda function integration URL format:
   ```
   arn:aws:lambda:<region>:<account-id>:function:<lambda-name>
   ```
   Example:
   ```
   arn:aws:lambda:ap-southeast-1:123456789012:function:DevOpsUtilityHandler
   ```

---

### 3. Configure Route Integrations

Ensure each route (e.g., `/commits`, `/files-changed`, `/push-changelog`) is linked to the same Lambda function created earlier (e.g., `DevOpsUtilityHandler`).

Use **Lambda Proxy integration**.

---

### 4. Enable CORS (Optional)

You may optionally enable CORS if you plan to invoke this API from a frontend or testing tool.

---

### 5. Deploy the API

- Click **Deployments**
- Choose or create a new **stage** (e.g., `prod`)
- Note the **Invoke URL** (e.g., `https://xxxxxx.execute-api.ap-southeast-1.amazonaws.com/prod`)

Use this URL in your action group Lambda function (`API_GATEWAY_BASE_URL` constant).

---

## 📂 Files

- `openapi-apigateway-import.yaml`: OpenAPI v3.0 schema for defining routes and operations in API Gateway

---

## 🔗 Connect to Bedrock

Once deployed, the Bedrock Agent’s Lambda function will use this API to handle action group requests like commit fetch and changelog updates.

