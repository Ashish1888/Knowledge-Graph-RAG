# GitHub Actions CI/CD Setup for K-Graph RAG

This directory contains GitHub Actions workflows for testing your K-Graph RAG project.

## Workflows

### `ci-cd.yml` - Test Workflow
Runs on every push and pull request to `main` branch.

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch
- Manual workflow dispatch

**Job:**
- **Test**: Runs pytest on Python 3.13

## Setup Instructions

### 1. Enable Workflows in GitHub
1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Ensure "Actions permissions" is set to allow all actions

### 2. Configure Secrets (Optional)
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add any required secrets like `GROQ_API_KEY`

## Running Tests Locally

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_main.py -v
```

## Workflow Customization

### Modify Test Python Version
Edit `.github/workflows/ci-cd.yml`:
```yaml
- name: Set up Python 3.13
  uses: actions/setup-python@v4
  with:
    python-version: '3.13'  # Change version here
```

### Add Custom Tests
1. Create test files in `tests/` directory following naming pattern `test_*.py`
2. Tests will automatically be discovered and run by pytest

## Monitoring & Debugging

### View Workflow Runs
1. Go to repository → **Actions**
2. Click on workflow run to see detailed logs
3. Check the test output

### Common Issues

**Tests failing with import errors:**
- Ensure `requirements.txt` is up to date
- Check Python 3.13 compatibility

## Next Steps

1. Push changes to your repository
2. Monitor the workflow run in the Actions tab
3. Check test results
