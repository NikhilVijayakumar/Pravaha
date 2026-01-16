# Storage Module - E2E Test Scenarios

**Status**: Planning
**Client Docs**: `docs/client/storage-module.md`

## 1. Output Workflow

### Scenario: Full Output Lifecycle
1.  **Init**: App starts with default storage config.
2.  **Save**: Use internal Provider (in simulated app task) to save `result_v1.json` to `output/v1.0/feature-a/gpt4/`.
3.  **Browse**: API call `GET /api/storage/output/browse?path=v1.0/feature-a` -> Sees `gpt4` folder.
4.  **Reference**: Browsing deeper sees `result_v1.json`.
5.  **Read**: API call `GET /api/storage/output/read?path=.../result_v1.json` -> Returns content.
6.  **Verify**: Response matches saved data.

## 2. Config & Dynamic Updates

### Scenario: Runtime Path Change
1.  **Check**: Get current config -> Default `./output`.
2.  **Update**: POST `/api/storage/config` with `output_path="/tmp/pravaha_test/out"`.
3.  **Verify**: Get config -> Shows new path.
4.  **Action**: Save new output file.
5.  **Check FS**: Verify file exists in `/tmp/pravaha_test/out`, NOT `./output`.

## 3. Knowledge Access

### Scenario: Documentation Browsing
1.  **Setup**: Create `knowledge/docs/guide.md` and `knowledge/schemas/data.json` on disk.
2.  **Browse Root**: API `GET /api/storage/knowledge/browse` -> Lists `docs` and `schemas`.
3.  **Browse Sub**: API `GET /api/storage/knowledge/browse?path=docs` -> Lists `guide.md`.
4.  **Read Text**: API `GET /api/storage/knowledge/read?path=docs/guide.md` -> Returns string content.
5.  **Read JSON**: API `GET /api/storage/knowledge/read?path=schemas/data.json` -> Returns JSON object.

## 4. Security

### Scenario: Path Traversal Attack
1.  **Attack**: API `GET /api/storage/knowledge/read?path=../../../../etc/passwd`.
2.  **Result**: 400 Bad Request / 403 Forbidden (handled by PathResolver).
