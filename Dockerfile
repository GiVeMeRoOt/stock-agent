FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Kolkata

WORKDIR /app

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install -e .[dev]

COPY dsp /app/dsp
COPY config /app/config
COPY models /app/models
COPY scripts /app/scripts
COPY tests /app/tests
COPY Makefile /app/Makefile

CMD ["uvicorn", "dsp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
