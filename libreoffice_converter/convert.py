import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

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
        original_file_path.parent.mkdir(parents=True, exist_ok=False)
        file.save(original_file_path)

        # Run the libreoffice command to convert the file
        outdir = Path(temp_dir) / "converted"
        outdir.mkdir(parents=True, exist_ok=False)
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

        converted_files = list(outdir.iterdir())
        if not converted_files:
            stdout = process.stdout.decode()
            stderr = process.stderr.decode()
            if "Error: no export filter for" in stderr:
                raise Exception("No export filter found for the requested format and the uploaded file")

            logger.warning(f"Conversion failed: {file.filename}: {format_to=} {stdout=} {stderr=} exitcode={process.returncode}")
            raise Exception("Conversion failed")

        elif len(converted_files) == 1:
            # Return the file directly if there is only one
            converted_file = converted_files[0]
            logger.info(f"Converted file: {file.filename} -> {converted_file.name}")
            return converted_file.open("rb")

        else:
            # Multiple files (f.i. xhtml + extracted images): create a zip file with all the converted files
            if ":" in format_to:
                suffix = format_to.split(":")[0]
            else:
                suffix = format_to
            # filename.docx -> filename.xhtml.zip
            zip_file = Path(file.filename).stem + f".{suffix}.zip"
            zip_path = Path(temp_dir) / zip_file
            with ZipFile(zip_path, "w") as zipf:
                for converted_file in converted_files:
                    zipf.write(converted_file, converted_file.name)

            logger.info(f"Converted file: {file.filename} -> {zip_file} {[f.name for f in converted_files]}")
            return zip_path.open("rb")
