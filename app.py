"""Stylometric Comparison Tool — Flask app.

Routes:
  GET  /          → input form
  GET  /glossary  → in-app glossary with examples
  POST /compare   → run analysis; render HTML report (or Markdown attachment)
  GET  /healthz   → health check
"""

from __future__ import annotations

from datetime import datetime

from flask import Flask, Response, abort, render_template, request

from analyzer import compare as run_compare
from analyzer.deep_scan import run_from_text as run_deep_scan
from analyzer.deep_scan_export import render_docx, render_md, render_pdf
from analyzer.extract import ExtractionError, UnsupportedFileError, extract_text
from analyzer.glossary import GLOSSARY
from analyzer.markdown_export import render_markdown, render_markdown_single
from analyzer.pipeline import analyze as run_analyze


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB max submission


# Hosts where the deep-scan page is permitted to run. Anywhere else
# (including the public Fly deployment) returns 404 for those routes.
_LOCALHOST_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}


def _is_localhost() -> bool:
    host = (request.host or "").split(":")[0]
    return host in _LOCALHOST_HOSTS


def _require_localhost() -> None:
    if not _is_localhost():
        abort(404)


@app.context_processor
def _inject_globals():
    return {"glossary": GLOSSARY, "is_localhost": _is_localhost()}


@app.route("/healthz", methods=["GET"])
def healthz():
    return Response("ok", mimetype="text/plain")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/glossary", methods=["GET"])
def glossary_page():
    return render_template("glossary.html")


@app.route("/analyze", methods=["GET", "POST"])
def analyze_route():
    if request.method == "GET":
        return render_template("analyze.html")

    errors: list[str] = []
    text = _resolve_text("text", "file", "Text", errors)
    topic = (request.form.get("topic") or "").strip() or None
    fmt = request.form.get("format", "html")

    if not text:
        errors.append("Text is empty.")
    if errors:
        return render_template(
            "analyze.html",
            errors=errors,
            text=text,
            topic=topic or "",
        )

    profile = run_analyze(text, topic, label="Text")

    if fmt == "markdown":
        md = render_markdown_single(profile, topic)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return Response(
            md,
            mimetype="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="stylometric-analysis-{timestamp}.md"'
                ),
            },
        )

    return render_template(
        "report_single.html",
        profile=profile,
        text=text,
        topic=topic or "",
    )


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


# ============================================================
# Deep scan (localhost-only) — extended AI-writing-signs analysis
# ============================================================

def _read_deep_scan_input() -> tuple[str, str | None, list[str]]:
    errors: list[str] = []
    text = _resolve_text("text", "file", "Text", errors)
    topic = (request.form.get("topic") or "").strip() or None
    return text, topic, errors


@app.route("/deep-scan", methods=["GET", "POST"])
def deep_scan_route():
    _require_localhost()
    if request.method == "GET":
        return render_template("deep_scan.html")

    text, topic, errors = _read_deep_scan_input()
    if not text:
        errors.append("Text is empty.")
    if errors:
        return render_template(
            "deep_scan.html", errors=errors, text=text, topic=topic or "",
        )
    result = run_deep_scan(text, topic)
    return render_template(
        "deep_scan_profile.html",
        result=result, text=text, topic=topic or "",
    )


@app.route("/deep-scan/details", methods=["POST"])
def deep_scan_details_route():
    _require_localhost()
    text, topic, errors = _read_deep_scan_input()
    if not text:
        errors.append("Text is empty.")
    if errors:
        return render_template("deep_scan.html", errors=errors)
    result = run_deep_scan(text, topic)
    return render_template(
        "deep_scan_details.html",
        result=result, text=text, topic=topic or "",
    )


@app.route("/deep-scan/export", methods=["POST"])
def deep_scan_export_route():
    _require_localhost()
    text, topic, errors = _read_deep_scan_input()
    fmt = (request.form.get("format") or "md").lower()
    if errors or not text:
        return render_template(
            "deep_scan.html",
            errors=(errors or []) + (["Text is empty."] if not text else []),
        )
    result = run_deep_scan(text, topic)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    if fmt == "md":
        body = render_md(result, topic)
        mime = "text/markdown; charset=utf-8"
        ext = "md"
    elif fmt == "docx":
        body = render_docx(result, topic)
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ext = "docx"
    elif fmt == "pdf":
        body = render_pdf(result, topic)
        mime = "application/pdf"
        ext = "pdf"
    else:
        abort(400)

    return Response(
        body,
        mimetype=mime,
        headers={
            "Content-Disposition": f'attachment; filename="deep-scan-{timestamp}.{ext}"',
        },
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
