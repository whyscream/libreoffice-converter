FROM alpine:3.20.2

# Allow setting the UID and GID of the user running the application
ARG PUID=1000
ENV PUID=$PUID
ARG PGID=65533
ENV PGID=$PGID

# Install the required packages
RUN apk add --no-cache \
    libreoffice \
    font-misc-misc \
    font-terminus \
    font-inconsolata \
    font-dejavu \
    font-noto \
    font-noto-cjk \
    font-awesome \
    font-noto-extra \
    font-anonymous-pro-nerd \
    ttf-cantarell \
    ttf-dejavu \
    ttf-droid \
    ttf-font-awesome \
    ttf-freefont \
    ttf-hack \
    ttf-inconsolata \
    ttf-liberation \
    ttf-linux-libertine \
    ttf-mononoki \
    ttf-opensans \
    python3

# Create a virtualenv and install the required packages
RUN python3 -m venv /opt/venv

# Install the required dependencies
COPY pyproject.toml /app/pyproject.toml
RUN /opt/venv/bin/python -m pip install --no-cache /app

# Copy the application code
COPY . /app

RUN adduser -u $PUID -g $PGID -D -h /app app
USER app
WORKDIR /app

# Run the application
ENTRYPOINT ["/opt/venv/bin/python", "-m", "flask", "run", "--host", "0.0.0.0"]
