FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm /app/main.py
COPY . /app



