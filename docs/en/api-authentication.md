<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>API Authentication</h1>
</div>
</div>

OpenHEXA provides JWT-based authentication for programmatic access to workspaces and their resources. This allows external applications and services to authenticate and interact with OpenHEXA workspaces securely.

## JWT Token Generation

### Overview

OpenHEXA can issue JWT (JSON Web Token) tokens for workspace access. These tokens contain workspace membership information and user identity claims, enabling external services to authenticate API requests.

### Issuing a Workspace Token

To issue a JWT token for a workspace, use the `issueWorkspaceToken` GraphQL mutation:

```graphql
mutation IssueWorkspaceToken($input: IssueWorkspaceTokenInput!) {
  issueWorkspaceToken(input: $input) {
    success
    token
    expiresAt
    workspace {
      id
      slug
    }
    role
    errors
  }
}
```

**Input Parameters:**

You must provide exactly one of the following:
- `workspaceId` (UUID) - The unique identifier of the workspace
- `workspaceSlug` (String) - The slug of the workspace

**Example:**

```graphql
{
  "input": {
    "workspaceSlug": "my-workspace"
  }
}
```

**Response:**

```json
{
  "success": true,
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9wdGlvbmFsLWtleS1pZCJ9...",
  "expiresAt": "2025-11-06T12:30:00Z",
  "workspace": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "slug": "my-workspace"
  },
  "role": "EDITOR",
  "errors": []
}
```

### Token Payload

The generated JWT token contains the following claims:

- **Standard Claims:**
  - `sub` - Subject (user ID)
  - `iss` - Issuer (default: https://app.openhexa.org)
  - `aud` - Audience (default: openhexa-clients)
  - `iat` - Issued at timestamp
  - `exp` - Expiration timestamp
  - `jti` - JWT ID (unique token identifier)

- **Custom Claims:**
  - `https://app.openhexa.org/claims/workspace` - Workspace information (id, slug)
  - `https://app.openhexa.org/claims/workspace_role` - User's role in the workspace (OWNER, ADMIN, EDITOR, VIEWER)
  - `https://app.openhexa.org/claims/user` - User information (id, email)

### Error Handling

The mutation may return the following errors:

- `AUTH_UNAUTHENTICATED` - User is not authenticated
- `INPUT_INVALID` - Both or neither of workspaceId/workspaceSlug were provided
- `WORKSPACE_NOT_FOUND` - Workspace does not exist
- `MEMBERSHIP_REQUIRED` - User is not a member of the workspace
- `CONFIG_MISSING_PRIVATE_KEY` - JWT private key is not configured on the server
- `ROLE_UNRESOLVED` - User's role in the workspace could not be determined
- `CLOCK_ERROR` - System clock error occurred

## Token Verification

### JWKS Endpoint

OpenHEXA exposes a JSON Web Key Set (JWKS) endpoint for token verification at:

```
GET /.well-known/jwks.json
```

This endpoint returns the public key(s) used to verify JWT tokens issued by OpenHEXA.

**Example Response:**

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "optional-key-id",
      "n": "base64url-encoded-modulus",
      "e": "base64url-encoded-exponent"
    }
  ]
}
```

### Verifying Tokens

External services can verify OpenHEXA JWT tokens using the public key from the JWKS endpoint. Most JWT libraries support JWKS-based verification.

**Example using Python:**

```python
import jwt
from jwt import PyJWKClient

# Fetch the public key from JWKS endpoint
jwks_client = PyJWKClient("https://your-openhexa-instance/.well-known/jwks.json")
signing_key = jwks_client.get_signing_key_from_jwt(token)

# Verify the token
decoded = jwt.decode(
    token,
    signing_key.key,
    algorithms=["RS256"],
    audience="openhexa-clients",
    issuer="https://app.openhexa.org"
)

# Access claims
workspace_id = decoded["https://app.openhexa.org/claims/workspace"]["id"]
user_role = decoded["https://app.openhexa.org/claims/workspace_role"]
```

## Configuration

### Server Configuration

To enable JWT token generation, configure the following environment variables on the OpenHEXA server:

- `OPENHEXA_JWT_PRIVATE_KEY` (required) - RSA private key in PEM format
- `OPENHEXA_JWT_KID` (optional) - Key identifier to include in token headers
- `OPENHEXA_JWT_ISSUER` (optional) - Token issuer, defaults to `https://app.openhexa.org`
- `OPENHEXA_JWT_AUDIENCE` (optional) - Token audience, defaults to `openhexa-clients`
- `OPENHEXA_JWT_TTL` (optional) - Token time-to-live in seconds, defaults to `3600` (1 hour)

**Example `.env` configuration:**

```bash
OPENHEXA_JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"
OPENHEXA_JWT_KID=my-key-identifier
OPENHEXA_JWT_TTL=7200
```

### Generating RSA Key Pair

You can generate an RSA key pair using OpenSSL:

```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Extract public key
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

## Security Considerations

- **Token Storage:** Store JWT tokens securely and never expose them in client-side code or logs
- **Token Expiration:** Tokens expire after the configured TTL (default 1 hour). Request new tokens as needed
- **HTTPS Only:** Always use HTTPS when transmitting JWT tokens
- **Key Rotation:** Regularly rotate RSA key pairs and update the server configuration
- **Scope Limitation:** Tokens are scoped to a specific workspace and user membership
- **Role-Based Access:** Token claims include the user's role, which should be enforced by consuming applications

## Use Cases

JWT tokens are useful for:

- **API Integration:** Authenticate external applications accessing OpenHEXA's GraphQL API
- **Service-to-Service Communication:** Enable secure communication between microservices
- **Third-Party Tools:** Integrate OpenHEXA with external analytics or monitoring tools
- **Custom Clients:** Build custom applications that interact with OpenHEXA workspaces
- **Automated Workflows:** Authenticate automated scripts and data pipelines running outside OpenHEXA
