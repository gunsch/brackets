FROM python:3.8-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the config file first --- but it may be overwritten by an actual config.py
COPY config.py.DOCKER ./config.py
COPY *.py ./
COPY static/ ./static/
COPY templates/ ./templates/
CMD ["python", "app.py"]
