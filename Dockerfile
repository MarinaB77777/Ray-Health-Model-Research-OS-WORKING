FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

# Измените api.main:app на путь к вашему приложению (например, main:app или api.main:app)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
