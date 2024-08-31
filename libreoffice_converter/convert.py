import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime

logger = logging.getLogger(__name__)


def convert_file(file, format_to):
    """Convert a file to a different format.

    Run a libreoffice command to convert the file to the desired format.
    """
    # Create a temporary directory to store the files
    app_tempdir = os.getenv("APP_TEMP_DIR", tempfile.gettempdir())
    app_keep_files = os.getenv("APP_DELETE_FILES", "true").lower() == "true"
    now = datetime.now().strftime("%Y%m%d-%H%M%S-")

    with tempfile.TemporaryDirectory(dir=app_tempdir, prefix=now, delete=app_keep_files) as temp_dir:
        # Save the original file to the temporary directory
        original_file_path = os.path.join(temp_dir, file.filename)
        file.save(original_file_path)

        # Run the libreoffice command to convert the file
        process = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                format_to,
                "--outdir",
                temp_dir,
                original_file_path,
            ],
            capture_output=True,
            check=True,
        )
        # Output of the command contains the path to the file:
        # b'convert /tmp/tmpm0nkb7y8/test.odt -> /tmp/tmpm0nkb7y8/test.pdf using filter : writer_pdf_Export\n'

        # Get the converted file name from the output
        if match := re.match(r"convert (.*) -> (.*) using filter", process.stdout.decode()):
            converted_file_path = match.group(2)
            logger.warning(f"Converted file: {file.filename}: {converted_file_path}")

            # Open the converted file and return it, so the temporary directory can be cleaned up
            converted_file = open(converted_file_path, "rb")
            return converted_file
        else:
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            logger.warning(f"Conversion failed: {file.filename}: {format_to=} {stdout=} {stderr=}")
            if "Error: no export filter for" in stderr:
                raise Exception(f"Conversion failed, no export filter found for the format: {format_to}")
            else:
                raise Exception("Conversion failed")
