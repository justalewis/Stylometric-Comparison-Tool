"""Stylometric Comparison Tool — Flask app.

Routes:
  GET  /          → input form (auth required)
  POST /compare   → run analysis; render HTML report (or Markdown attachment)
  GET  /healthz   → unauthenticated health check
"""

from __future__ import annotations

import hmac
import os
from datetime import datetime

from flask import Flask, Response, render_template, request

from analyzer import compare as run_compare
from analyzer.extract import ExtractionError, UnsupportedFileError, extract_text
from analyzer.markdown_export import render_markdown


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB max submission

_BASIC_AUTH_USER = os.environ.get("STYLOMETRIC_USERNAME", "user")
_BASIC_AUTH_PASS = os.environ.get("STYLOMETRIC_PASSWORD", "")
_AUTH_REALM = "Stylometric Comparison"


def _credentials_ok(auth) -> bool:
    if auth is None or auth.type != "basic":
        return False
    user_ok = hmac.compare_digest(auth.username or "", _BASIC_AUTH_USER)
    pass_ok = hmac.compare_digest(auth.password or "", _BASIC_AUTH_PASS)
    return user_ok and pass_ok


@app.before_request
def _require_auth():
    if request.path == "/healthz" or request.path.startswith("/static/"):
        return None
    if not _BASIC_AUTH_PASS:
        # Fail closed if the deployment forgot to set a password.
        return Response(
            "Server is missing STYLOMETRIC_PASSWORD; refusing to serve.",
            status=503,
            mimetype="text/plain",
        )
    if not _credentials_ok(request.authorization):
        return Response(
            "Authentication required.",
            status=401,
            headers={"WWW-Authenticate": f'Basic realm="{_AUTH_REALM}"'},
            mimetype="text/plain",
        )
    return None


@app.route("/healthz", methods=["GET"])
def healthz():
    return Response("ok", mimetype="text/plain")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def _resolve_text(form_key: str, file_key: str, label: str, errors: list[str]) -> str:
    """Prefer an uploaded file over the textarea; return extracted plain text."""
    uploaded = request.files.get(file_key)
    if uploaded and uploaded.filename:
        try:
            data = uploaded.read()
            if not data:
                errors.append(f"{label}: uploaded file was empty.")
                return ""
            return extract_text(uploaded.filename, data).strip()
        except UnsupportedFileError as exc:
            errors.append(f"{label}: {exc}")
        except ExtractionError as exc:
            errors.append(f"{label}: {exc}")
        return ""
    return (request.form.get(form_key) or "").strip()


@app.route("/compare", methods=["POST"])
def compare_route():
    errors: list[str] = []
    text_a = _resolve_text("text_a", "file_a", "Text A", errors)
    text_b = _resolve_text("text_b", "file_b", "Text B", errors)
    topic = (request.form.get("topic") or "").strip() or None
    fmt = request.form.get("format", "html")

    if not text_a:
        errors.append("Text A is empty.")
    if not text_b:
        errors.append("Text B is empty.")
    if errors:
        return render_template(
            "index.html",
            errors=errors,
            text_a=text_a,
            text_b=text_b,
            topic=topic or "",
        )

    result = run_compare(text_a, text_b, topic)

    if fmt == "markdown":
        md = render_markdown(result)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return Response(
            md,
            mimetype="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="stylometric-report-{timestamp}.md"'
                ),
            },
        )

    return render_template(
        "report.html",
        result=result,
        text_a=text_a,
        text_b=text_b,
        topic=topic or "",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
