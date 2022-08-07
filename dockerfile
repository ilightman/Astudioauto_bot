FROM python:alpine

RUN apt-get update && \
    apt-get install -y build-essential libzbar-dev && \
    pip install zbar

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]