# Libreoffice document conversion API in Docker container

This is a simple HTTP service that converts (Libreoffice) documents to many other formats. It is built using Flask and runs in a Docker container.

## Usage

### Build the Docker image

The image needs libreoffice and some other stuff, which is quite large. the resulting image is around 1GB, so it might take a while to build.

```shell
docker build -t libreoffice-converter .
```

### Run the Docker container

```shell
docker run -d -p 5000:5000 libreoffice-converter
```

### Or use the provided `compose.yml`

```shell
docker compose up
```

### Convert a document

Now you can visit the convert page at http://localhost:5000/v1/convert and test it manually.

You can also convert using automated HTTP requests: send a POST request to the `/v1/convert` endpoint with the document file as a form field named `file`, and the target format in a form field named `format_to`. The converted document will be returned as a response.
Formats can be specified by their extension or by their filter name. The filter name is the name that Libreoffice uses to identify the format. See the [Libreoffice docs](https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html) for details

```shell
curl -X POST -F "file=@/path/to/document.docx" -F "format_to=pdf" http://localhost:5000/v1/convert > converted.pdf

# Or specify the filter name
curl -X POST -F "file=@/path/to/document.docx" -F "format_to=doc:MS Word 97" http://localhost:5000/v1/convert > converted.doc
```

### Supported formats

The supported formats are the ones that Libreoffice supports. You can see the list of supported formats by reading the libreoffice listed on the convert page.
By default, only a set of common formats are allowed, but you can change this by setting the `APP_ALLOWED_FORMATS` environment variable. The format is a list of extensions, optionally followed by a filter, separated by commas.

```shell
# Limit to only these formats
APP_ALLOWED_FORMATS="pdf,docx,odt"
# Allow formats with specific filters:
APP_ALLOWED_FORMATS="txt:Text (encoded):UTF8"
```

## Development

It's also possible to run the app outside of a Docker container for development purposes.

### Install dependencies

The dependencies are listed in `pyproject.toml`. You can install them using pip:

```shell
pip install .
```

### Run the Flask development server

```shell
export FLASK_APP=libreoffice_converter
flask run --debug
```

### Review generated files

To review the conversion process, you can save all uploaded and converted files.

To do so, set the environment variables `APP_TEMP_DIR` and `APP_DELETE_FILES`.

In a shell:
```shell
export APP_TEMP_DIR=./temp
export APP_DELETE_FILES=false
export FLASK_APP=libreoffice_converter
flask run --debug
```

Or in compose.yaml:
```compose-yaml
# Or better: use the provided compose.env.example
environment:
  - APP_TEMP_DIR=/app/temp
  - APP_DELETE_FILES=false
volumes:
  - ./temp:/app/temp
```


## Thanks

Projects below were used as inspiration for this one. They solve the same problem in a similar way, but were not flexible enough for my needs.

- https://github.com/jesseinit/flask_libreoffice_api
- https://github.com/miotto/server_fileconverter_flasksoffice/tree/master
