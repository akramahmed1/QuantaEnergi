# Stage 1: Builder
FROM python:3.10-slim-buster AS builder

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential curl git cmake g++ && rm -rf /var/lib/apt/lists/*

# Build liboqs
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git && cd liboqs && cmake -S . -B build && make -j$(nproc) -C build && make -C build install && cd .. && rm -rf liboqs

# CmdStan for Prophet
RUN curl -L https://github.com/stan-dev/cmdstan/releases/download/v2.34.1/cmdstan-2.34.1.tar.gz | tar xz && cd cmdstan-2.34.1 && make build -j$(nproc)

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2: Final
FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1 APP_HOME=/app CMDSTAN=/cmdstan-2.34.1

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/liboqs.so /usr/local/lib/
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /cmdstan-2.34.1 /cmdstan-2.34.1

ENV PATH="/opt/venv/bin:$PATH" LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"

COPY . .

USER appuser:appgroup

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]