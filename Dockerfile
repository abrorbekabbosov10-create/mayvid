FROM python:3.10-slim

# Kerakli tizim paketlarini o'rnatish
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# ImageMagick xavfsizlik cheklovini to'g'ri o'chirish
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read | write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml; \
    fi

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
