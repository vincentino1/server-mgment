FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create configs folder
RUN mkdir -p configs

# Copy rest of the application
COPY . .

RUN mkdir -p configs

EXPOSE 8050

CMD ["python", "src/app.py"]
