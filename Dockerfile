FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Create a volume mount point for agent data
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "src/web_server.py"]
