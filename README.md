# Nagrik AI — voice-first civic services prototype

A Flask + browser-voice demo for explaining Indian/Maharashtra public-service steps, likely document categories, and official starting points.

## Included
- English, Hindi and Marathi language selection.
- Browser speech recognition (where supported) and speech synthesis.
- Voice question input, read-aloud answers, optional listen-again toggle.
- Offline/local fallback guidance when AI API key, network, or quota is unavailable.
- Service checklist endpoint and browser-local checklist tick storage.
- DigiLocker integration status + OAuth configuration scaffold.
- Error handling, health endpoint, safe defaults, and Render deployment files.

## Run on Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```
Open `http://127.0.0.1:5000`.

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
You can also install dependencies without activating the virtual environment:
```powershell
py -m pip install -r requirements.txt
py app.py
```

## Optional AI
Set `OPENAI_API_KEY` in the local environment or hosting provider's secret settings. Do not paste secrets into chat, HTML, GitHub, or source code. If the API fails, the backend logs a generic provider failure and returns local guidance.

## DigiLocker: important limitations
By default, DigiLocker is in **demo mode**. The button opens the official DigiLocker site; it does not connect an account or retrieve documents. Real integration requires approval/credentials from the official DigiLocker requester/partner process and must follow the provider's current API contract.

The app includes a configurable OAuth authorization-code scaffold (`DIGILOCKER_CLIENT_ID`, `DIGILOCKER_CLIENT_SECRET`, `DIGILOCKER_REDIRECT_URI`, `DIGILOCKER_AUTHORIZE_URL`, `DIGILOCKER_TOKEN_URL`, optional `DIGILOCKER_SCOPE`). Do not fill these with guessed values. Configure only credentials and endpoint URLs issued for your approved integration. Confirm the precise OAuth parameters, token authentication method, scopes and document APIs with the official provider documentation before use.

The callback validates state and exchanges the code server-side, but deliberately does **not** persist/expose access tokens or retrieve documents. Before production, implement a secure server-side token vault, encryption at rest, access controls, consent and revocation handling, audit logging, retention limits, and the approved document API. The current `connected` flag only indicates that the sample code exchange succeeded in this process/session; it is not proof that documents are available.

Official site: https://www.digilocker.gov.in/
Maharashtra service portal: https://aaplesarkar.mahaonline.gov.in/

## Voice notes
Speech recognition depends on browser support, microphone permission and sometimes network access. Chrome/Edge are recommended for the demo. Browser voice input is not a secure place to speak OTPs, passwords, Aadhaar numbers or bank details. Use HTTPS in public deployment for microphone access.

## Deploy to Render
1. Push this folder to a GitHub repository; never commit `.env`.
2. Create a Render Web Service from the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Set `FLASK_SECRET_KEY` (Render YAML can generate one), and optionally `OPENAI_API_KEY`.
6. Set `COOKIE_SECURE=true` when serving over HTTPS.
7. Test `/health`, microphone permission, local fallback, and mobile layout.

## Safety
This is an independent prototype, not a government portal. It gives general guidance only and does not submit applications, make calls, check live application status, or retrieve DigiLocker documents in demo mode. Fees, document requirements, eligibility and processing times vary and must be verified on the official service portal.


## Smart Application Tracker (demo)

Open `/track` to use the application-tracking dashboard. It includes a document-readiness checklist, application-stage timeline, official-SLA-based indicative ETA, department-delay explanation, and a daily progress diary saved locally in the browser. The tracker is a prototype: it does not connect to government databases or verify uploaded documents. Enter the official processing-time limit from the relevant service portal/acknowledgement; without it, the app deliberately does not invent an ETA. Internal government delay reasons are shown as possibilities unless an official remark confirms them.


## Government Portal Health Monitor
The tracker includes an on-demand server-side availability check for a small allowlist of official portals (Aaple Sarkar, DigiLocker, National Scholarship Portal and UMANG). It reports HTTP errors, slow responses and timeouts cautiously. A timeout does not prove a government outage, and an HTTP response does not guarantee that every service on that portal is working. The monitor cannot see internal department queues, application-specific status, or the reason an officer has not processed a file. It does not automatically change the citizen’s application status. The user should retain their acknowledgement and follow official notices. Checks are on-demand; do not poll government portals frequently.
