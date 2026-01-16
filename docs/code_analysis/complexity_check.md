# Logic Complexity Verification (SRP)

**Tool:** `ruff`
**Configuration File:** `pyproject.toml`

## 🎯 Objective
To enforce the **Single Responsibility Principle (SRP)** by limiting the Cyclomatic Complexity of functions. High complexity often indicates a function is doing too much.

## 🛠️ Usage
Check for functions exceeding the complexity threshold (Default: 10):
```bash
ruff check --select C901 --max-complexity 10 src/nikhil/pravaha
```

## ⚙️ Configuration
The McCabe complexity check (`C901`) is enabled in `pyproject.toml` via `ruff` or `flake8` settings.

### Thresholds
- **Good**: < 6 (Simple, readable)
- **Warning**: 6-9 (Starting to get complex)
- **Violation**: ≥ 10 (Needs refactoring)

## 📊 Reporting
Use the **Complexity Report Template** to document findings:
`docs/code_analysis/templates/complexity_report_template.md`

### Metric Definitions
- **Status**: ✅ Passing / ❌ Failing
- **Violations**: Count of functions with complexity ≥ 10.
- **Max Complexity**: The highest complexity score found in a module.

## 💡 Troubleshooting
- **Extract Method**: Break long functions into smaller, named helper methods.
- **Strategy Pattern**: Replace long `if/elif/else` chains with a dictionary mapping or polymorphism.
- **Guard Clauses**: Use early returns to reduce nesting depth.
