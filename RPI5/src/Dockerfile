# Use Python 3.11 slim (Debian-based)
FROM python:3.8-bullseye

# Set workdir
WORKDIR /app

# System deps for Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxrandr2 \
    libfreetype6 \
    libfontconfig1 \
    libgl1 \
    libglib2.0-0 \
    uvicorn\
    git\
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy deps first for caching
COPY requirements.txt .

# Upgrade pip first
RUN pip install --upgrade pip
RUN pip install torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu
# Install Python deps

RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# FastAPI default port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
