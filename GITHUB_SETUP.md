# GitHub Setup Instructions

Since the current agent environment does not have access to the `git` executable, please run the following commands in your local terminal (Git Bash, PowerShell, or Command Prompt) to push this project to GitHub.

## 1. Navigate to Project

```bash
cd "c:\Users\DELL\OneDrive\Documentos\Antigravity\clinical-quality-med"
```

## 2. Initialize Git

```bash
git init
git add .
git commit -m "Initial commit: Clinical Quality & Med Safety Dashboard"
git branch -M main
```

## 3. Push to GitHub

### Option A: Using GitHub CLI (Recommended)

If you have `gh` installed:

```bash
gh repo create clinical-quality-med-safety-dashboard --public --source=. --push
```

### Option B: Manual Remote

1. Create a new **empty** repository on GitHub named `clinical-quality-med-safety-dashboard`.
2. Run the following (replace `YOUR_USERNAME`):

```bash
git remote add origin https://github.com/YOUR_USERNAME/clinical-quality-med-safety-dashboard.git
git push -u origin main
```

## 4. Deploy to Streamlit Cloud (Optional)

Once on GitHub:

1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Connect your repository.
3. Set **Main file path** to `app/app.py`.
4. Click **Deploy**.
