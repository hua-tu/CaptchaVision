FROM python:3.11-slim

# opencv-python-headless 只需要少量基础库（无需 GUI 相关库）
RUN apt-get update -o Acquire::Retries=5 && \
    apt-get install -y --no-install-recommends \
        libglib2.0-0 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 仅复制必要文件（依赖清单 + 代码）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 把业务代码一起拷贝进镜像，避免模块缺失
COPY ai_get.py main.py trans.py connect.py ./

# 运行时环境变量：API Key 请在部署时注入
ENV FLASK_APP=main.py

EXPOSE 8011

# 按教程使用 gunicorn + gevent 运行，监听 8011
CMD ["gunicorn", "main:create_app()", "-k", "gevent", "--workers", "4", "-b", "0.0.0.0:8011"]

