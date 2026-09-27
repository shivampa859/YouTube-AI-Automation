FROM python:3.11-slim

# Install FFmpeg and OpenCV system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

# Copy requirements first for Docker layer caching
COPY --chown=user requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=user . .

# Ensure application user can write generated files
RUN chown -R user:user /home/user/app

# Run application as non-root user
USER user

ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

# Hugging Face Spaces port
EXPOSE 7860

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]