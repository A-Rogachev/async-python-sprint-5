FROM python:3.11-slim
WORKDIR /file_storage_app
COPY ../requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir