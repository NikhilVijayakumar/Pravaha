# Code Quality Checks & Verification

This index outlines the standard procedures for verifying code quality, architecture, and type safety in **Pravaha**.

## 📚 Detailed Guides

### 1. [Clean Architecture Verification](./architecture_check.md)
**Tool:** `import-linter`
Enforces the dependency rule: *Inner layers (Domain) must NOT depend on outer layers.*

### 2. [Type Safety Verification](./type_safety_check.md)
**Tool:** `mypy`
Enforces strict type annotation and checking to prevent runtime errors.

### 3. [Logic Complexity (SRP) Verification](./complexity_check.md)
**Tool:** `ruff` (C901)
Enforces low Cyclomatic Complexity to ensure maintainability and Single Responsibility.

---

## 📝 Reporting Templates

Use these templates to generate standardized reports for each check:

- **Architecture**: [`templates/architecture_report_template.md`](./templates/architecture_report_template.md)
- **Type Safety**: [`templates/type_safety_report_template.md`](./templates/type_safety_report_template.md)
- **Complexity**: [`templates/complexity_report_template.md`](./templates/complexity_report_template.md)

## 🔄 Workflow

1.  **Run Check**: Execute the command specified in the detailed guide.
2.  **Analyze Output**: Identify violations and categorize them by module.
3.  **Document**: Fill out the corresponding report template.
4.  **Resolve**: Refactor code to fix violations and re-run step 1.
