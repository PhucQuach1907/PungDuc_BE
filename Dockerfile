# Sử dụng image Python chính thức từ Docker Hub
FROM python:3.12

# Cài đặt các thư viện hệ thống cần thiết
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục cho ứng dụng Django
WORKDIR /app

# Copy mã nguồn ứng dụng vào container (bao gồm manage.py)
COPY . /app/

# Cài đặt các dependencies từ tệp requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Thực thi lệnh makemigrations và migrate sau khi mã nguồn đã được sao chép vào container
RUN python manage.py makemigrations
RUN python manage.py migrate

# Cấu hình các biến môi trường
ENV PYTHONUNBUFFERED 1

# Cấu hình các cổng cho ứng dụng
EXPOSE 8000

# Chạy lệnh để thực thi ứng dụng Django
CMD ["gunicorn", "--bind", "127.0.0.1:8000", "PungDuc_BE.wsgi:application"]
