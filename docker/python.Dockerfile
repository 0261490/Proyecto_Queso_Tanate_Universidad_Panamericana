FROM python:3.12.13-slim

WORKDIR /workspace

COPY model-export/requirements.lock.txt /tmp/requirements.lock.txt

RUN python -m pip install --no-cache-dir pip==26.2.1 && python -m pip install --no-cache-dir -r /tmp/requirements.lock.txt

COPY . .

CMD ["bash"]