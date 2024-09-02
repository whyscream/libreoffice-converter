import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_file(file, format_to):
    """Convert a file to a different format.

    Run a libreoffice command to convert the file to the desired format.
    """
    # Create a temporary directory to store the files
    app_tempdir = os.getenv("APP_TEMP_DIR", tempfile.gettempdir())
    app_delete_files = os.getenv("APP_DELETE_FILES", "true").lower() == "true"
    now = datetime.now().strftime("%Y%m%d-%H%M%S-")

    with tempfile.TemporaryDirectory(dir=app_tempdir, prefix=now, delete=app_delete_files) as temp_dir:
        # Save the original file to the temporary directory
        original_file_path = Path(temp_dir) / "original" / file.filename
        original_file_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(original_file_path)

        # Run the libreoffice command to convert the file
        outdir = Path(temp_dir) / "converted"
        process = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                format_to,
                "--outdir",
                str(outdir),
                str(original_file_path),
            ],
            capture_output=True,
            check=True,
        )
        # Output of the command contains the path to the file:
        # b'convert /tmp/tmpm0nkb7y8/test.odt -> /tmp/tmpm0nkb7y8/test.pdf using filter : writer_pdf_Export\n'

        converted_files = list(outdir.iterdir())
        if not converted_files:
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            if "Error: no export filter for" in stderr:
                raise Exception("No export filter found for the requested format and the uploaded file")

            logger.warning(f"Conversion failed: {file.filename}: {format_to=} {stdout=} {stderr=}")
            raise Exception("Conversion failed")

        elif len(converted_files) == 1:
            # Return the file directly if there is only one
            converted_file = converted_files[0]
            logger.warning(f"Converted file: {file.filename}: {converted_file}")
            return converted_file.open("rb")

        else:
            # Multiple files (f.i. xhtml + extracted images)
            logger.warning(f"Multiple converted files found: {file.filename}: {[f.name for f in converted_files]}")
            raise Exception("Conversion failed, multiple converted files found")
