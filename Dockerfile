FROM python:3.11.2-alpine

COPY . .

RUN apk update
RUN apk add ffmpeg 
RUN pip install -r requirements.txt
EXPOSE 8080/tcp
CMD [ "python", "bot/main.py" ]
