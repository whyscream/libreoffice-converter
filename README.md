# Libreoffice document conversion API in Docker container

This is a simple API that converts (Libreoffice) documents to many other formats. It is built using Flask and runs in a Docker container.

## Usage

### Build the Docker image

```shell
docker build -t libreoffice-converter .
```

### Run the Docker container

```shell
docker run -d -p 5000:5000 libreoffice-converter
```

### Convert a document

Send a POST request to the `/convert` endpoint with the document file as a form field named `file`, and the target format in a form field named `format`. The converted document will be returned as a response.

```shell
curl -X POST -F "file=@/path/to/document.docx" -F "format=pdf" http://localhost:5000/v1/convert > converted.pdf
```

## Development

### Install dependencies

The dependencies are listed in `pyproject.toml`. You can install them using pip:
```shell
pip install .
```

### Run the Flask development server

```shell
flask run --debug
```

### Review generated files

To review the conversion process, you can save all uploaded and converted files.

To do so, set the environment variables `APP_TEMP_DIR` and `APP_DELETE_FILES`.

```shell
export APP_TEMP_DIR=./app_temp_dir
export APP_DELETE_FILES=false
flask run --debug
```

```compose-yaml
environment:
  - APP_TEMP_DIR=/tmp/app_temp_dir
  - APP_DELETE_FILES=false
volumes:
  - ./app_temp_dir:/tmp/app_temp_dir
```


## Thanks

Projects below were used as inspiration for this one. They solve the same problem in a similar way, but were not flexible enough for my needs.

- https://github.com/jesseinit/flask_libreoffice_api
- https://github.com/miotto/server_fileconverter_flasksoffice/tree/master
