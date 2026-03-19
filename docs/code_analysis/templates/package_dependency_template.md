# Package Dependency Report

**Date:** {date}  
**Overall Status:** {overall_status}

---

## 📦 Executive Summary

| Metric | Value | Status |
| :--- | :---: | :---: |
| **Total Installed** | {installed_count} | |
| **Declared Dependencies** | {declared_count} | |
| **Up-to-date** | {up_to_date} | 🟢 |
| **Outdated** | {outdated} | {outdated_status} |
| **Major Updates Available** | {major_updates} | {major_status} |
| **Minor Updates Available** | {minor_updates} | 🟡 |
| **Patch Updates Available** | {patch_updates} | 🟢 |
| **Potentially Unused** | {unused} | ⚠️ |

---

## 📊 Dependency Health Score

**Score:** {health_score}/100

- ✅ Up-to-date packages: +{points_current}
- 🟡 Minor updates: -{points_minor}
- 🔴 Major updates: -{points_major}  
- ⚠️ Security issues: -{points_security}

> **Interpretation:** 90-100 = Excellent | 70-89 = Good | 50-69 = Needs Attention | <50 = Critical

---

## 📈 Package Status Overview

### Update Distribution

| Package | Current | Latest | Gap | Status | Priority |
| :--- | :---: | :---: | :---: | :---: | :---: |
{package_table}

---

## 🔴 Critical Updates

### Major Version Updates
*Review changelogs carefully - may contain breaking changes*

{major_updates_detail}

### Security Advisories
{security_advisories}

> **Action Required:** Major updates should be tested in a separate branch before merging.

---

## 🟡 Recommended Updates

### Minor Version Updates
*Generally safe, but test thoroughly*

{minor_updates_detail}

### Patch Updates  
*Bug fixes and security patches - low risk*

{patch_updates_detail}

---

## ⚠️ Dependency Hygiene

### Potentially Unused Dependencies
*Packages declared but not imported in source code*

{unused_deps_detail}

### Development vs Production
{dev_vs_prod_breakdown}

---

## 🛠️ Action Items

### Immediate (This Week)
{immediate_actions}

### Short-term (This Month)
{short_term_actions}

### Long-term (This Quarter)
{long_term_actions}

---

## 💡 Maintenance Tips

### Updating Packages
```bash
# Update a specific package
pip install --upgrade <package>

# Update to a specific version
pip install <package>==<version>

# Check what would be updated
pip list --outdated
```

### Testing After Updates
1. Run full test suite: `pytest`
2. Check type safety: `mypy`
3. Verify no regressions in critical paths
4. Update `pyproject.toml` with new versions

### Best Practices
- **Review Changelogs**: Always read release notes for major updates
- **Update Incrementally**: Don't update everything at once
- **Pin Versions**: Use exact versions in `pyproject.toml` for reproducibility
- **Regular Audits**: Run this report monthly
- **Security First**: Prioritize security updates over feature updates

---

## 📂 Full Dependency List

<details>
<summary>Click to expand all {installed_count} installed packages</summary>

{full_package_list}

</details>

---

## 🔗 Useful Resources

- [Python Package Index (PyPI)](https://pypi.org/)
- [pip documentation](https://pip.pypa.io/)
- [Semantic Versioning](https://semver.org/)
- [Security Advisories](https://github.com/pypa/advisory-database)
