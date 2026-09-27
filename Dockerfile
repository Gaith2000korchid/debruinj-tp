FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system assembler \
    && useradd --system --gid assembler --home-dir /app assembler \
    && mkdir -p /output /tmp/matplotlib \
    && chown assembler:assembler /output /tmp/matplotlib

COPY debruijn/ ./debruijn/

USER assembler
WORKDIR /output
ENTRYPOINT ["python", "-m", "debruijn.debruijn"]
CMD ["--help"]
