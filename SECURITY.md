# Security Guidelines for Public Repository

This document outlines security considerations, identified risks, and mitigation strategies for this open-source project.

## 🔒 Security Checklist

- ✅ No hard-coded API keys or credentials in source code
- ✅ Uses free/public APIs (Open-Meteo) — no API key required
- ✅ OLLAMA runs locally — no external credential exposure
- ⚠️ **CAUTION**: Test output may leak environment variables
- ✅ `.gitignore` configured to exclude `.env` files
- ✅ Dependencies sourced from trusted PyPI packages

## Identified Issues & Recommendations

### 🔴 CRITICAL: Credential Logging in Test Output

**Location:** [tests/conftest.py](tests/conftest.py#L34)

**Issue:**
```python
print("LangSmith Key:", os.getenv("LANGCHAIN_API_KEY", "NOT FOUND"))
print("LangSmith Project:", os.getenv("LANGCHAIN_PROJECT", "NOT FOUND"))
```

This prints environment variables during test initialization, which could expose real API keys if they're configured in CI/CD environments or developer machines.

**Risk Level:** 🟠 **HIGH** (in CI/CD environments)

**Mitigation:**
1. Remove debug print statements (DONE)
2. Use proper logging instead with masking for sensitive values
3. Ensure `.env` files are in `.gitignore`
4. Never commit `.env` files with real credentials

**Before (UNSAFE):**
```python
print("LangSmith Key:", os.getenv("LANGCHAIN_API_KEY", "NOT FOUND"))
```

**After (SAFE):**
```python
# Optionally log with masked/redacted values for debugging
key = os.getenv("LANGCHAIN_API_KEY", "NOT SET")
print(f"LangSmith configured: {'Yes' if key != 'NOT SET' else 'No'}")
```

---

## Best Practices for Public Repositories

### 1. Environment Variables

**DO:**
- ✅ Use `.env` files ONLY for local development
- ✅ Add `.env` and `.env.local` to `.gitignore`
- ✅ Document required env vars in README with example values
- ✅ Use `.env.example` template for developers

**DON'T:**
- ❌ Commit `.env` files with real credentials
- ❌ Print env vars in logs or test output
- ❌ Hard-code API keys in source files
- ❌ Use production credentials in development

### 2. API Keys & Secrets

**DO:**
- ✅ Use LangSmith API key ONLY through environment variables
- ✅ Use `.env.example` as template:
```env
# .env.example (NO real values!)
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=your_project_name
```

**DON'T:**
- ❌ Share API keys in issues or discussions
- ❌ Commit real keys even by accident
- ❌ Log API keys in debug output

### 3. Dependency Management

**Current:** Using community packages from PyPI
- ✅ All dependencies are open-source and verified
- ✅ Pin specific versions in `requirements.txt`
- ✅ Regularly update to security patches

**Recommendations:**
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies safely
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### 4. Repository Configuration

**Recommended `.gitignore` entries:**
```
# Environment variables
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
*.egg-info/
dist/
build/

# Reports & Logs
reports/
*.log

# Virtual environments
venv/
env/
```

### 5. CI/CD Security

**DO:**
- ✅ Store secrets in CI/CD platform's secret manager (GitHub Secrets, GitLab CI/CD Variables, etc.)
- ✅ Never echo secrets in logs
- ✅ Use `::add-mask::` in GitHub Actions to redact values
- ✅ Review secrets access regularly

**Example GitHub Actions security:**
```yaml
- name: Run tests
  env:
    LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
  run: pytest
```

---

## Third-Party Dependencies Security

### Current Dependencies Status

All dependencies are:
- ✅ Open-source and publicly available
- ✅ Actively maintained (as of 2024/2025)
- ✅ From trusted PyPI repository
- ✅ Do not require external credentials

**No credentials needed for:**
- requests — HTTP library
- FastAPI — Web framework
- pytest — Testing
- LangChain — LLM orchestration
- DeepEval — LLM evaluation
- OpenMeteo API — Free, public weather data

### Security Recommendations

1. **Pin versions** to avoid supply chain attacks:
```bash
# Review current versions
pip freeze > requirements.txt

# Regularly check for updates
pip list --outdated
```

2. **Use hash verification:**
```bash
# Generate hashes
pip install --require-hashes -r requirements.txt
```

3. **Periodic security audits:**
```bash
# Check for known vulnerabilities
pip install safety
safety check --json
```

---

## Data Privacy

### Data Collected & Used

| Data | Source | Usage | Storage |
|------|--------|-------|---------|
| Weather data | OpenMeteo API | Real-time results | Not persisted |
| City location | Nominatim Geocoding | Weather queries | Not persisted |
| Conversation history | Optional (agent memory) | Context for Chat | RAM only |
| API latency | Internal timing | Performance metrics | Test reports only |

### No Data Persisted

- ✅ No database storage of user queries
- ✅ No analytics or user tracking
- ✅ No personal information collected
- ✅ Weather data fetched on-demand from public APIs

---

## Incident Response

### If you accidentally committed credentials:

1. **Immediate action:**
```bash
# Remove from git history (GitHub: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
git filter-branch -f --index-filter 'git rm --cached --ignore-unmatch .env' HEAD

# Force push
git push origin main --force-with-lease
```

2. **Rotate credentials:**
   - Regenerate LangSmith API key
   - Update in CI/CD secrets
   - Review access logs

3. **Audit commits:**
   - Check git history: `git log -p -- .env`
   - Check for similar files

---

## Reporting Security Issues

⚠️ **DO NOT open GitHub issues for security vulnerabilities.**

Instead:
1. Email security concerns to: [maintainer email]
2. Include detailed description and reproduction steps
3. Allow 48-72 hours for response before public disclosure
4. Credit will be given in security advisory

---

## Compliance & Standards

This project follows:
- ✅ OWASP Top 10 best practices
- ✅ Python security recommendations
- ✅ Open Source security standards
- ✅ PII/Data privacy best practices

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_considerations.html)
- [GitHub Security Hardening](https://docs.github.com/en/code-security)
- [Bandit — Python Security Linter](https://bandit.readthedocs.io/)

---

**Last Updated:** March 2026
**Status:** ✅ Safe for public release
