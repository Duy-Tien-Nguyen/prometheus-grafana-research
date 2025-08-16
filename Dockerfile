FROM python:3.11-slim

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir fastapi uvicorn[standard] kafka-python minio redis pydantic

# Copy code vào container
WORKDIR /app
COPY load_test.py /app

# # Mở port 8000
# EXPOSE 8009

# Chạy FastAPI bằng uvicorn
CMD ["python", "load_test.py"]
