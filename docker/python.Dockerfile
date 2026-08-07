FROM python:3.12-slim

WORKDIR /workspace

COPY . .

RUN pip install --upgrade pip

RUN pip install \
    pgmpy \
    pandas \
    numpy \
    networkx \
    scipy

CMD ["bash"]