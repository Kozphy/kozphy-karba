# KARBA verifier image — pytest + ruff only. Runtime should use --network none.
FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pytest==8.3.5 ruff==0.6.9
WORKDIR /work
COPY run_verify_in_container.py /karba/run_verify_in_container.py
ENTRYPOINT ["python", "/karba/run_verify_in_container.py"]
