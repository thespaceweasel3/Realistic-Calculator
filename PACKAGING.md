Packaging and GitHub
====================

This file summarizes short steps to build the Windows EXE and push the project to GitHub.

Build EXE (PyInstaller, PowerShell):

```powershell
# create and activate a venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# build
pyinstaller --onefile --windowed `
  --add-data "click_snap.wav;." `
  --add-data "click_thock.wav;." `
  --add-data "click_balanced.wav;." `
  --icon "path\to\icon.ico" `
  "c:\workspace\calculator.py"
```

Then find the EXE in `dist\calculator.exe`.

Create GitHub repo and push (using gh):

```powershell
git init
git add .
git commit -m "Initial commit"
# create repo on GitHub and push
gh repo create "Seven-Segment-Calculator" --public --source=. --remote=origin --push
```

If you don't have `gh`, create the repo on github.com and run:

```powershell
git remote add origin https://github.com/<your-user>/<repo>.git
git branch -M main
git push -u origin main
```
