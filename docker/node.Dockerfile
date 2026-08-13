FROM node:24.19.0-bookworm

WORKDIR /workspace

COPY . .

CMD ["bash"]