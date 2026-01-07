# Pravaha Storage API Issues Analysis

## 1. LLM Config Used?
- **Analysis**: The code *does* attempt to use `self.llm_config.resolve_output_config(alias)` inside `_scan_dir`.
  ```python
  config = self.llm_config.resolve_output_config(alias)
  display_name = config.get("display_name", alias)
  ```
- **Issue**: The `resolve_output_config` method in `LLMConfigManager` (seen previously) does a flat search or simple traversal. If the model alias logic relies on `models -> key -> output_config`, but the actual `llm_config.yaml` has a different structure or missing `output_config`, it falls back to the alias.
  - In `llm_config.yaml` we saw, `models` entries like `gemma` do NOT have `output_config` fields. They only have `base_url`, `model`, `api_key`.
  - **Conclusion**: The code *tries* to use it, but the default/existing configuration schema doesn't support the metadata `StorageAPIProvider` expects (like `folder_name`, `display_name`). Thus, it defaults to raw filenames.

## 2. Versioning Support
- **Analysis**: The `_scan_dir` method has this logic:
  ```python
  parts = stem.rsplit("_", 1)
  version = 1
  alias = stem
  if len(parts) == 2 and parts[1].isdigit():
      alias = parts[0]
      version = int(parts[1]) + 1  # Why +1? 0-indexed assumed?
  ```
- **Issue**:
  - It simply parses the filename to *extract* a version number.
  - It then appends this as a flat entry to `artifacts`:
    ```python
    artifacts.append({ ..., "model": alias, "version": version, ... })
    ```
  - **Crucially**: It returns a **flat list** of artifacts. It does **not** group them by alias.
  - If I have `script_1.json` and `script_2.json`, the API returns **two** items.
  - The UI (consuming this) likely sees them as separate entries rather than "One artifact with multiple versions".
  - **User Complaint**: "the api still shows as file and directory". This confirms the API is just listing them out, perhaps slightly enriched, but not structurally solving the versioning UX.

## 3. Read API Versioning
- **Analysis**: The `read` handler takes a `path`.
  ```python
  async def handler(path: str):
      file_path = Path(path).resolve()
  ```
- **Issue**: The `read` API works on *absolute paths* (or relative to root). It defines "read this specific file". It has **zero awareness** of versioning. You can't ask "give me version 2 of artifact X". You must ask "give me file /path/to/X_2.json".
- **Conclusion**: The user is right. The API is a simple file reader. The abstract concept of "Artifact Version" is not enforced or utilized in the `read` endpoint.

## 4. Browse API Structure
- **Analysis**: `_create_browse_handler` delegates to `_list_artifacts_logic`.
- **Logic**: It iterates directories.
  - `intermediate`: `base_root / feature`.
  - `final`: `base_root / product / feature` OR `base_root / feature`.
- **Issue**: It seems to make assumptions about directory structure (`feature`/`product`). If the user has a different structure (e.g. flat, or by date), this scanner might fail or produce weird results.

## 5. Missing Routes (CRITICAL)
- **Analysis**: The `browse` and `read` endpoints return 404 Not Found.
- **Investigation**:
  - `inspect_routes.py` and `inspect_all_routes.py` showed NO `browse` or `read` routes registered.
  - Source code inspection of `StorageAPIProvider.py` shows `_setup_routes` is effectively empty or incomplete:
    ```python
    def _setup_routes(self):
        # ...
        # Hybrid Endpoints
        # ... (rest of the code) -- This suggests missing implementation!
    ```
  - `grep` confirmed `_create_browse_handler` is defined but **never called**.
- **Conclusion**: The code to register `browse` and `read` routes is **missing** from the installed library version. This is why the endpoints are unreachable.


Summary
The Pravaha Storage API implementation has significant gaps that prevent it from functioning as expected, particularly regarding Metadata enrichment, Versioning support, and Endpoint availability.

1. Missing Endpoints (Critical)
The browse and read endpoints are NOT registered in the application, leading to 404 Not Found errors.

Root Cause: The StorageAPIProvider class defines handler creation methods (_create_browse_handler, _create_read_handler) but never calls them in _setup_routes.
Impact: Automatic UI generation features that rely on these endpoints will fail completely.
2. LLM Config Integration Missing
The api/llm/config is not effectively used to enrich artifact metadata.

Analysis: The _scan_dir method attempts to resolve display_name using llm_config.resolve_output_config(alias).
Issue: The implementation of resolve_output_config relies on a structure (output_config) that is often missing from standard model definitions in 

llm_config.yaml
.
Result: The UI falls back to raw filenames/aliases, making the "Knowledge" or "Display Name" features ineffective.
3. Poor Versioning Support
The API does not handle file versioning semantically.

Analysis: The _list_artifacts_logic parses filenames (e.g., script_1.json) to extract version numbers but returns them as separate, flat entries in the list.
Issue:
script_1.json -> { model: "script", version: 2 } (Wait, logic is int(parts[1]) + 1?)
script_2.json -> { model: "script", version: 3 }
There is no aggregation. The client receives a list where the same "artifact" appears multiple times, cluttering the UI.
Read API: The read endpoint operates on file paths, ignoring version abstraction. You cannot request "latest version of X".
Recommendations for Pravaha Team
Fix Route Registration: Implement the missing calls in StorageAPIProvider._setup_routes to actually register /{category}/browse and /{category}/read.
Refactor Versioning:
Group artifacts by alias in the browse response.
Return a structure like { alias: "script", versions: [1, 2], latest: 2 }.
Enhance LLM Config:
Update LLMConfigManager to more robustly find metadata.
Standardize where output_config should live in the YAML.