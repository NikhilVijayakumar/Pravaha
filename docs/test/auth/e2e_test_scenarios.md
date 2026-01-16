# Authentication Module - E2E Test Scenarios

**Status**: Planning
**Client Docs**: `docs/client/authentication-module.md`

## 1. Lifecycle Workflows

### Scenario: Full Key Lifecycle
**Description**: Verify the entire life of an API key from creation to revocation.

1.  **Bootstrap**: Use admin script (or equivalent API) to create an Admin Key.
2.  **Provision**: Admin creates a new "Client Key" with `STORAGE` permission.
3.  **Verify Access**: 
    *   Client Key calls `/api/storage/browse` -> **Success (200)**.
    *   Client Key calls `/api/workflow/list` -> **Fail (403)**.
4.  **Discovery**: Client Key calls `/api/auth/capabilities` -> Returns `["storage"]`.
5.  **Audit**: Admin lists keys -> Sees Client Key and updated `last_used` timestamp.
6.  **Revoke**: Admin revokes Client Key.
7.  **Deny**: Client Key calls `/api/storage/browse` -> **Fail (403)**.

## 2. Integration Flows

### Scenario: Frontend Feature Discovery
**Description**: Simulate a frontend app checking what features to enable.

1.  **Init**: Frontend has a key with `WORKFLOW` and `LLM`.
2.  **Query**: Call `/api/auth/capabilities`.
3.  **Verify**: Response contains correct `endpoints` map for Workflows and LLM.
4.  **Verify**: Response does **NOT** contain Bot or Storage endpoints.

### Scenario: Secure/Insecure Toggle
**Description**: Verify that disabling AuthConfig actually works.

1.  **Restart App**: Start with `AUTH_ENABLED=False`.
2.  **Access**: Call `/api/storage` WITHOUT header -> **Success (200)**.
3.  **Restart App**: Start with `AUTH_ENABLED=True`.
4.  **Access**: Call `/api/storage` WITHOUT header -> **Fail (401)**.
