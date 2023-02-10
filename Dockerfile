FROM python:3.11.2-alpine

COPY . .

RUN apk update
RUN apk add ffmpeg 
RUN pip install -r requirements.txt
CMD [ "python", "bot/main.py" ]
