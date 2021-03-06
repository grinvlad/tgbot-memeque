# tgbot-memeque

## Description
Telegram bot for putting memes in a queue as media files or text and then 
sending those to your friend's chat. There is running bot that you can check out: [@memefam_bot](https://t.me/memefam_bot)

## Technology stack
- Language: `Python 3.10.4`
- Wrapper for [Telegram Bot API](https://core.telegram.org/bots/api): [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Database: `SQLite3` 

## Getting Started
First you need to set your env vars in [Dockerfile](Dockerfile):

`TELEGRAM_BOT_TOKEN` — token from [@BotFather](https://t.me/BotFather)

`TELEGRAM_GROUP_CHAT_ID` — chat where you want to send memes anonymously. [How to get it for your chat](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)

Then you build docker image and run a container: 
```
docker build -t tgbot-memeque .
docker run -d --name memeque -v /local_project_path/db:/app/db tgbot-memeque
```
For entering running container:
```
docker exec -it memeque bash
```