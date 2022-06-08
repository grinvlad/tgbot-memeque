FROM python:3.10.4

WORKDIR /app

ENV TELEGRAM_BOT_TOKEN="**********:***********************************"
ENV TELEGRAM_GROUP_CHAT_ID="**********"

COPY *.py .
COPY createdb.sql .
COPY requirements.txt .

RUN pip install -Ur requirements.txt  && apt-get update && apt-get install sqlite3

CMD ["python3", "memebot.py"]