import os
import secrets
import logging
import time
from urllib.parse import urlencode
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from civic_guide import get_fallback_answer, get_checklist, find_service, SERVICE_DATA, LOCALIZED

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("nagrik-ai")

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-only-change-this-secret"),
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)

OFFICIAL_LINKS = {
    "Aaple Sarkar (Maharashtra)": "https://aaplesarkar.mahaonline.gov.in/",
    "DigiLocker": "https://www.digilocker.gov.in/",
    "Income Tax / PAN": "https://www.incometax.gov.in/",
    "National Scholarship Portal": "https://scholarships.gov.in/",
    "UMANG": "https://web.umang.gov.in/",
}

def digilocker_configured():
    required = [
        "DIGILOCKER_CLIENT_ID",
        "DIGILOCKER_CLIENT_SECRET",
        "DIGILOCKER_REDIRECT_URI",
        "DIGILOCKER_AUTHORIZE_URL",
        "DIGILOCKER_TOKEN_URL",
    ]
    return all(os.getenv(k, "").strip() for k in required)

@app.get("/")
def home():
    return render_template("index.html", official_links=OFFICIAL_LINKS)

@app.get("/service/<service_id>")
def service_page(service_id):
    if service_id not in SERVICE_DATA:
        return redirect(url_for("home"))
    language = request.args.get("lang", "Hindi")[:30]
    if language not in {"Hindi", "Marathi", "English"}:
        language = "Hindi"
    if language == "English":
        details = SERVICE_DATA[service_id]
    else:
        details = LOCALIZED.get(language, {}).get(service_id, SERVICE_DATA[service_id])
    return render_template("service.html", service_id=service_id, details=details, language=language)

@app.get("/track")
def track_application():
    return render_template("tracker.html")


# Only fixed, known public portals are checked. User-supplied URLs are never fetched.
PORTAL_HEALTH_TARGETS = {
    "aaple-sarkar": ("Aaple Sarkar (Maharashtra)", "https://aaplesarkar.mahaonline.gov.in/"),
    "digilocker": ("DigiLocker", "https://www.digilocker.gov.in/"),
    "scholarship": ("National Scholarship Portal", "https://scholarships.gov.in/"),
    "umang": ("UMANG", "https://web.umang.gov.in/"),
}

@app.get("/api/portal-health")
def portal_health():
    portal_id = request.args.get("portal", "aaple-sarkar")
    target = PORTAL_HEALTH_TARGETS.get(portal_id)
    if not target:
        return jsonify({"status": "unknown", "message": "Choose a supported official portal."}), 400
    name, url = target
    if not requests:
        return jsonify({"status": "unknown", "portal": name, "message": "Portal check is unavailable on this server. Please open the official portal directly."})
    started = time.monotonic()
    try:
        response = requests.get(url, timeout=(4, 8), allow_redirects=False, headers={"User-Agent": "NagrikAI-PortalHealth/1.0"})
        elapsed = round((time.monotonic() - started) * 1000)
        code = response.status_code
        if code == 429:
            status, message = "busy", "The portal returned a rate-limit response. It may be receiving heavy traffic or limiting automated checks. Try again later."
        elif 500 <= code <= 599:
            status, message = "outage", "The portal returned a server error. The department website may be experiencing a temporary technical issue."
        elif 300 <= code <= 399:
            status, message = "unknown", "The portal redirected this check. We could not reliably confirm its current availability."
        elif code in (401, 403):
            status, message = "unknown", "The portal restricted this automated check. This does not prove the website is down."
        elif code >= 400:
            status, message = "unknown", f"The portal responded with HTTP {code}. Its application service may still be working; check the official website directly."
        elif elapsed >= 5000:
            status, message = "slow", "The portal responded slowly to this check. Heavy traffic or a temporary network delay may be affecting access."
        else:
            status, message = "online", "The portal responded to this check. Individual services may still be slow or unavailable."
        return jsonify({"status": status, "portal": name, "http_status": code, "response_ms": elapsed, "checked_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "message": message, "official_url": url})
    except requests.Timeout:
        elapsed = round((time.monotonic() - started) * 1000)
        return jsonify({"status": "timeout", "portal": name, "response_ms": elapsed, "checked_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), "message": "The portal did not respond before the check timed out. It may be overloaded, temporarily unavailable, or unreachable from this server. Please don't panic—your application is not automatically cancelled.", "official_url": url})
    except requests.RequestException:
        return jsonify({"status": "unknown", "portal": name, "message": "We could not complete the portal check because of a network or connection issue. Please open the official portal directly.", "official_url": url})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Nagrik AI", "digilocker": "configured" if digilocker_configured() else "demo"})

@app.get("/api/services")
def services():
    return jsonify({
        "services": [
            {"id": "income", "name": "Income Certificate", "description": "Documents, steps and official starting point"},
            {"id": "domicile", "name": "Domicile Certificate", "description": "Residence proof and application guidance"},
            {"id": "caste", "name": "Caste Certificate", "description": "Eligibility and document guidance"},
            {"id": "scholarship", "name": "Scholarship", "description": "Find the right scheme and prepare documents"},
            {"id": "pension", "name": "Pension", "description": "Pension application or restart guidance"},
            {"id": "pan", "name": "PAN Card", "description": "Official PAN application guidance"},
            {"id": "property-tax", "name": "Property Tax Correction", "description": "Prepare details for your local authority"},
            {"id": "birth", "name": "Birth Certificate", "description": "Registration and correction guidance"},
        ]
    })

@app.get("/api/checklist")
def checklist():
    service = request.args.get("service", "Other government service")[:100]
    try:
        language = request.args.get("language", "English")[:30]
        return jsonify({"service": service, "items": get_checklist(service, language)})
    except Exception:
        logger.exception("Checklist generation failed")
        return jsonify({"error": "Checklist is temporarily unavailable. Please try again."}), 500

@app.post("/api/assistant")
def assistant():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    language = str(data.get("language", "auto"))[:30]
    service = str(data.get("service", ""))[:100]

    if not message:
        return jsonify({"error": "Please type or speak your question."}), 400
    if len(message) > 5000:
        return jsonify({"error": "Please keep your question under 5,000 characters."}), 413

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key and requests:
        try:
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            system = (
                "You are Nagrik AI, a careful civic-services guide for India, especially Maharashtra. "
                "Reply in the user's preferred language (Hindi, Marathi or English), with simple numbered steps. "
                "Explain likely document categories, possible fees only when known, and what must be verified. "
                "Never invent exact fees, eligibility, processing times, portal status or guarantee approval. "
                "Requirements vary by state, district, scheme and applicant; verify on official portals. "
                "Never request Aadhaar numbers, OTPs, passwords, bank details, or uploaded identity documents in chat. "
                "Never ask users to read OTPs aloud. This prototype does not submit government applications, "
                "make calls, check live status, or fetch DigiLocker documents unless a separately approved integration "
                "has been implemented. Clearly say when information is general guidance. "
                "Official starting points: Maharashtra Aaple Sarkar https://aaplesarkar.mahaonline.gov.in/ ; "
                "DigiLocker https://www.digilocker.gov.in/ ; Income Tax https://www.incometax.gov.in/ ; "
                "National Scholarship Portal https://scholarships.gov.in/."
            )
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [
                    {"role": "system", "content": system + f"\nPreferred language: {language}. Selected service: {service}."},
                    {"role": "user", "content": message}
                ], "temperature": 0.25},
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            answer = payload["choices"][0]["message"]["content"].strip()
            if answer:
                return jsonify({"answer": answer, "mode": "ai", "detected_service": find_service(message, service)})
        except Exception as exc:
            # Do not return provider internals or API secrets to the browser.
            logger.warning("AI provider unavailable; using local guide (%s)", type(exc).__name__)

    try:
        answer = get_fallback_answer(message, language, service)
        return jsonify({
            "answer": answer,
            "mode": "guide",
            "notice": "Local guidance mode is active. Confirm current requirements on the official portal.",
            "detected_service": find_service(message, service)
        })
    except Exception:
        logger.exception("Local assistant failed")
        return jsonify({"error": "Nagrik AI could not prepare an answer. Please try again."}), 500

@app.get("/api/digilocker/status")
def digilocker_status():
    configured = digilocker_configured()
    return jsonify({
        "configured": configured,
        "mode": "oauth-ready" if configured else "demo",
        "connected": bool(session.get("digilocker_connected", False)),
        "message": (
            "OAuth settings are present. Connection still requires approved requester credentials and a tested provider flow."
            if configured else
            "Demo mode: no DigiLocker account is connected and no documents are being retrieved. Approved requester credentials are required for real integration."
        ),
        "official_url": "https://www.digilocker.gov.in/",
    })

@app.post("/api/digilocker/connect")
def digilocker_connect():
    # Do not collect DigiLocker passwords, Aadhaar numbers or OTPs in this app.
    if not digilocker_configured():
        return jsonify({
            "mode": "demo",
            "connected": False,
            "message": "DigiLocker demo mode only. Open the official DigiLocker website to sign in. This prototype cannot access or download your documents.",
            "official_url": "https://www.digilocker.gov.in/",
        })
    state = secrets.token_urlsafe(32)
    session["digilocker_oauth_state"] = state
    authorize_url = os.getenv("DIGILOCKER_AUTHORIZE_URL", "").strip()
    params = {
        "response_type": "code",
        "client_id": os.getenv("DIGILOCKER_CLIENT_ID", "").strip(),
        "redirect_uri": os.getenv("DIGILOCKER_REDIRECT_URI", "").strip(),
        "state": state,
    }
    scope = os.getenv("DIGILOCKER_SCOPE", "").strip()
    if scope:
        params["scope"] = scope
    return jsonify({"mode": "oauth", "redirect_url": authorize_url + ("&" if "?" in authorize_url else "?") + urlencode(params)})

@app.get("/digilocker/callback")
def digilocker_callback():
    expected_state = session.pop("digilocker_oauth_state", None)
    received_state = request.args.get("state", "")
    code = request.args.get("code", "")
    error = request.args.get("error", "")
    if error:
        return render_template("digilocker_result.html", title="Connection not completed", message="DigiLocker authorization was cancelled or denied. No documents were accessed.")
    if not expected_state or not received_state or not secrets.compare_digest(expected_state, received_state):
        return render_template("digilocker_result.html", title="Connection not verified", message="The security state check failed. Please start the connection again.")
    if not code:
        return render_template("digilocker_result.html", title="Connection incomplete", message="The provider did not return an authorization code.")
    if not requests:
        return render_template("digilocker_result.html", title="Integration not ready", message="The requests package is unavailable. Install requirements and try again.")
    # Exchange the code server-side. Never put client secret or access token in frontend/session cookies.
    try:
        token_response = requests.post(
            os.getenv("DIGILOCKER_TOKEN_URL", "").strip(),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.getenv("DIGILOCKER_REDIRECT_URI", "").strip(),
                "client_id": os.getenv("DIGILOCKER_CLIENT_ID", "").strip(),
                "client_secret": os.getenv("DIGILOCKER_CLIENT_SECRET", "").strip(),
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        if not token_data.get("access_token"):
            raise ValueError("Token response did not include access_token")
        # Intentionally do not persist or expose tokens. A secure server-side token vault
        # and approved document APIs must be implemented before document retrieval is enabled.
        session["digilocker_connected"] = True
        return render_template(
            "digilocker_result.html",
            title="Authorization successful",
            message="Authorization code exchange succeeded. This prototype does not store the access token or retrieve documents yet. Sign-in is not the same as document access.",
        )
    except Exception as exc:
        logger.warning("DigiLocker token exchange failed (%s)", type(exc).__name__)
        return render_template("digilocker_result.html", title="Connection failed", message="The authorization could not be completed. Check approved provider settings and redirect URI, then try again.")

@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API endpoint not found."}), 404
    return "Page not found", 404

@app.errorhandler(413)
def too_large(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Request too large. Please send a smaller request."}), 413
    return "Request too large", 413

@app.errorhandler(500)
def server_error(_error):
    logger.exception("Unhandled server error")
    if request.path.startswith("/api/"):
        return jsonify({"error": "A server error occurred. Please try again."}), 500
    return "A server error occurred. Please try again.", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
