import logging
import os
import secrets

from flask import Flask, request, send_file, render_template, redirect, url_for

from .convert import convert_file

logging.basicConfig(level=logging.INFO)

# See the link for all possible conversions
# https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html
DEFAULT_ALLOWED_FORMATS = "pdf,docx,odt,txt,html,xml,rtf,epub,xhtml,csv,pages,xlsx,ods,xls"
ALLOWED_FORMATS = os.getenv("APP_ALLOWED_FORMATS", DEFAULT_ALLOWED_FORMATS).split(",")

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    if not app.config.get("MAX_CONTENT_LENGTH"):
        app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_urlsafe(32)

    @app.route("/")
    def index():
        """Redirect to the convert page."""
        return redirect(url_for("convert"))

    @app.route("/v1/convert", methods=["GET", "POST"])
    def convert():
        """
        Convert a document to a different format.
        """
        if request.method == "POST":
            # Get the file from the request
            file = request.files["file"]
            if not file:
                return "No file provided", 400

            # Get the format to convert to
            format_to = request.form["format_to"]
            if not format_to:
                return "No format provided", 400

            if format_to not in ALLOWED_FORMATS:
                return f"Invalid format: {format_to}", 400

            # Convert the file
            try:
                converted_file = convert_file(file, format_to)
            except Exception as e:
                return str(e), 500

            converted_file_name = os.path.basename(converted_file.name)
            return send_file(converted_file, as_attachment=True, download_name=converted_file_name)
        else:
            return render_template("convert.html", formats=ALLOWED_FORMATS)

    return app
