import os

from flask import Flask, request, send_file, render_template, redirect, url_for

from .convert import convert_file

TARGET_FORMATS = ("pdf", "docx", "odt", "txt", "html", "xml", "rtf", "epub", "xhtml")


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()

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

            # Get the format to convert to
            format_to = request.form["format"]
            if format_to not in TARGET_FORMATS:
                return "Unsupported format", 400

            # Convert the file
            converted_file = convert_file(file, format_to)
            converted_file_name = os.path.basename(converted_file.name)
            return send_file(converted_file, as_attachment=True, download_name=converted_file_name)
        else:
            return render_template("convert.html", formats=TARGET_FORMATS)

    return app
