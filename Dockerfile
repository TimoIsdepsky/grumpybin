FROM python:3.14.0b3-slim

WORKDIR /app

COPY mqtt-requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./mqtt.py /app
COPY ./storage.py /app
COPY ./message.py /app
COPY ./lines /app

ENTRYPOINT ["python", "mqtt.py"]
