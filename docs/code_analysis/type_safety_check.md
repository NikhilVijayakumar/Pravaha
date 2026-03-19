# Type Safety Verification

**Tool:** `mypy`
**Configuration File:** `pyproject.toml`

## 🎯 Objective
To eliminate runtime type errors and ensure strict contract adherence across the codebase.

## 🛠️ Usage
Run strict type checking on the entire source tree:
```bash
mypy --strict src/nikhil/pravaha
```

## ⚙️ Configuration
We enforce `strict` mode in `pyproject.toml` to maximize safety.

```toml
[tool.mypy]
strict = true
disallow_untyped_defs = true
warn_return_any = true
warn_unused_configs = true
```

### Key Rules
- **Explicit Types**: All function arguments and return values must be annotated.
- **No `Any`**: Avoid `Any` wherever possible; use `Generic`, `Union`, or specific protocols.
- **Strict Optional**: Variables that can be `None` must be explicitly typed as `Optional[T]`.

## 📊 Reporting
Use the **Type Safety Report Template** to document findings:
`docs/code_analysis/templates/type_safety_report_template.md`

### Metric Definitions
- **Status**: ✅ Passing / ❌ Failing
- **Errors**: Total number of type errors reported by mypy.

## 💡 Troubleshooting
- **Missing Imports**: Ensure all types are imported or forward-referenced (`"ClassName"`).
- **Third-Party Libs**: If a library lacks type stubs, add a `# type: ignore` with a justification comment, or install types (`types-requests`, etc.).
