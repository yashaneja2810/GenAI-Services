# CI/CD Setup Guide

This guide helps you set up automated testing and deployment for PrayogAI.

## 📋 Overview

**CI (Continuous Integration)**: Automatically runs tests when you push code  
**CD (Continuous Deployment)**: Automatically deploys your app when tests pass

---

## 🔧 Setup for GitHub

### Step 1: Push Your Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit with CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Add Secrets to GitHub

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

**Backend Secrets:**
- `GROQ_API_KEY` - Your Groq API key
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anonymous key
- `QDRANT_URL` - Qdrant cloud URL
- `QDRANT_API_KEY` - Qdrant API key

**Deployment Secrets:**
- `RENDER_DEPLOY_HOOK_URL` - Render deploy hook (see Render dashboard)
- `VERCEL_TOKEN` - Vercel authentication token
- `VERCEL_ORG_ID` - Your Vercel organization ID
- `VERCEL_PROJECT_ID` - Your Vercel project ID

### Step 3: Enable GitHub Actions

- Go to **Actions** tab in your repository
- Click "I understand my workflows, go ahead and enable them"
- Workflows will now run automatically on push/pull requests

---

## 🎯 What Gets Automated

### On Every Push/Pull Request:
✅ Run all backend tests  
✅ Check code quality (linting, formatting)  
✅ Generate test coverage report  
✅ Security vulnerability scan

### On Push to Main Branch:
✅ Run all tests  
✅ Deploy backend to Render (if tests pass)  
✅ Deploy frontend to Vercel (if tests pass)

---

## 🧪 Testing Locally

Before pushing code, test locally:

```powershell
# Run tests
cd backend
.\run_tests.ps1

# Check code formatting
pip install black isort flake8
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

---

## 📊 Viewing CI/CD Results

### GitHub Actions:
1. Go to your repository on GitHub
2. Click the **Actions** tab
3. See all workflow runs and their status
4. Click any run to see detailed logs

### Test Coverage:
- Coverage reports are uploaded to Codecov automatically
- View at: https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO

---

## 🚀 Manual Deployment

If you want to deploy without pushing code:

1. Go to **Actions** tab
2. Select "Deploy Backend to Production"
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

---

## 🔒 Security Best Practices

✅ Never commit `.env` files  
✅ Always use GitHub Secrets for sensitive data  
✅ Review dependency security alerts  
✅ Keep dependencies updated  
✅ Enable branch protection rules on `main`

---

## 🛠️ Customizing Workflows

### Change Python Version:
Edit `.github/workflows/backend-tests.yml`:
```yaml
python-version: ['3.11']  # Change to ['3.10', '3.11'] to test multiple versions
```

### Change When Tests Run:
Edit the `on:` section:
```yaml
on:
  push:
    branches: [ main, develop, feature/* ]  # Run on these branches
```

### Skip CI for Commits:
Add `[skip ci]` to your commit message:
```bash
git commit -m "Update README [skip ci]"
```

---

## 📱 Status Badges

Add these to your README.md to show build status:

```markdown
![Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Backend%20Tests/badge.svg)
![Deploy](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Deploy%20Backend%20to%20Production/badge.svg)
```

---

## 🐛 Troubleshooting

### Tests Fail in CI but Pass Locally:
- Check environment variables in GitHub Secrets
- Verify Python version matches (3.11)
- Check if external services (Qdrant, Supabase) are accessible

### Deployment Fails:
- Verify deploy hook URLs are correct
- Check Render/Vercel deployment logs
- Ensure secrets are properly configured

### Workflow Doesn't Trigger:
- Check file paths in workflow `paths:` section
- Verify branch names match
- Check if Actions are enabled in repository settings

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render Deploy Hooks](https://render.com/docs/deploy-hooks)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [pytest Documentation](https://docs.pytest.org/)

---

## ✅ Verification Checklist

- [ ] Code pushed to GitHub
- [ ] All secrets added to GitHub
- [ ] Workflows enabled
- [ ] First test run completed successfully
- [ ] Deploy hooks configured
- [ ] Branch protection rules enabled (optional but recommended)

---

**Your CI/CD pipeline is now ready! 🎉**

Every time you push code, tests will run automatically. If you push to `main` and tests pass, your app deploys automatically!
