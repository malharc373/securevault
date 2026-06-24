FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install -r requirements.txt
COPY app/ .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]