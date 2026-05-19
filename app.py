"""Stylometric Comparison Tool — Flask app.

Routes:
  GET  /          → input form
  GET  /glossary  → in-app glossary with examples
  POST /compare   → run analysis; render HTML report (or Markdown attachment)
  GET  /healthz   → health check
"""

from __future__ import annotations

from datetime import datetime

from flask import Flask, Response, render_template, request

from analyzer import compare as run_compare
from analyzer.pipeline import analyze as run_analyze
from analyzer.extract import ExtractionError, UnsupportedFileError, extract_text
from analyzer.glossary import GLOSSARY
from analyzer.markdown_export import render_markdown, render_markdown_single


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB max submission


@app.context_processor
def _inject_glossary():
    return {"glossary": GLOSSARY}


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
