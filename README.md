# EduGenie Frontend Upgrade

This version fixes the missing static-file mount and includes a refreshed responsive frontend.

## Run
Open this folder in VS Code, activate your existing `.venv` if needed, then run:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000

This is a local demo and does not call the Gemini API, so no API key or billing is needed.
