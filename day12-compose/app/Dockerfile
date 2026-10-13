FROM python:3.12-slim
WORKDIR /app

# Cache dependency layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run as non-root user (Security Best Practice)
RUN useradd -r appuser
USER appuser

EXPOSE 5000
CMD ["python", "app.py"]
