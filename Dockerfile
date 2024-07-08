FROM python:3.9.0

WORKDIR /app/

COPY .env /
COPY ./main.py /app/
COPY ./certification-master.json /
COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

CMD uvicorn --host=0.0.0.0 --port 8000 main:app
