# CI/CD Pipeline Setup Guide

## Overview
Your K-Graph RAG project now has a simple CI/CD pipeline configured with GitHub Actions that tests your code on Python 3.13.

## What's Been Created

### 1. GitHub Actions Workflows
- `.github/workflows/ci-cd.yml` - Simple test workflow for Python 3.13

### 2. Testing Infrastructure
- `tests/` directory with test files:
  - `test_main.py` - FastAPI endpoint tests
  - `test_vector_store.py` - Vector store tests
  - `test_graph_store.py` - Graph store tests
- `pytest.ini` - Pytest configuration

### 3. Additional Files
- `.gitignore` - Git ignore rules (updated)

## CI/CD Pipeline

The workflow consists of a single job that:
1. Checks out your code
2. Sets up Python 3.13
3. Installs dependencies from `requirements.txt`
4. Installs pytest
5. Runs all tests in the `tests/` directory

## Getting Started

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

### Step 2: Monitor Workflows
1. Go to GitHub repository
2. Click on **Actions** tab
3. Watch the workflow run in real-time

## Customization

### Change Python Version
Edit `.github/workflows/ci-cd.yml`:
```yaml
- name: Set up Python 3.13
  uses: actions/setup-python@v4
  with:
    python-version: '3.13'  # Change to desired version
```

### Add More Tests
1. Create files in `tests/` following pattern `test_*.py`
2. Tests will automatically be discovered and run by pytest

## Monitoring

### View Workflow Status
- Go to repository → **Actions** tab
- Click a workflow run to see detailed logs
- View test output and any failures

## Troubleshooting

### Workflow Not Running
- Check if GitHub Actions is enabled in Settings
- Verify branch name is `main`

### Tests Failing in CI
- Run tests locally first: `pytest tests/ -v`
- Check Python 3.13 compatibility
- Verify all dependencies in `requirements.txt`

## Next Steps

1. Push changes to your repository
2. Monitor the workflow run in the Actions tab
3. Check test results and debug any failures
