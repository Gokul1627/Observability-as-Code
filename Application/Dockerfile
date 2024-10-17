FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install --upgrade opentelemetry-sdk
RUN pip install opentelemetry-distro && pip install flask requests 

COPY app.py app.py

CMD ["python", "app.py"]
