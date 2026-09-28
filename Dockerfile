FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*" \/>/<policy domain="path" rights="read | write" pattern="@\*" \/>/' /etc/ImageMagick-6/policy.xml

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
