# Clean Architecture Verification

**Tool:** `import-linter`
**Configuration File:** `.importlinter`

## 🎯 Objective
To enforce the **Dependency Rule** of Clean Architecture:
*   **Inner Layers** (Domain) must NOT comply logic from **Outer Layers** (Infrastructure, API).
*   Dependencies must always point inwards.

## 🛠️ Usage
Run the following command from the project root:
```bash
import-linter
```

## ⚙️ Configuration
The rules are defined in `.importlinter`.

### Contract 1: Domain Independence
Ensures the core business logic remains framework-agnostic.
```ini
[importlinter:contract:1]
name = Domain layer must not import Infrastructure
type = forbidden
source_modules =
    nikhil.pravaha.domain
forbidden_modules =
    nikhil.pravaha.infrastructure
    nikhil.pravaha.api
```

## 📊 Reporting
Use the **Architecture Report Template** to document findings:
`docs/code_analysis/templates/architecture_report_template.md`

### Metric Definitions
- **Status**: ✅ Passing / ❌ Failing
- **Violations**: Number of forbidden imports detected.

## 💡 Troubleshooting
If a violation occurs:
1.  **Inversion of Control**: Introduce a Protocol in the Domain layer and implement it in the Infrastructure layer.
2.  **Move Logic**: If domain logic depends on a framework feature, extract the feature behind an abstraction.
