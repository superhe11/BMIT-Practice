# BMIT-Practice
  

A Telegram bot that uses OpenAI's API to respond to user messages.



## Video-guide (Click)
[![Watch the video](https://img.youtube.com/vi/dZxpM01JTj8/maxresdefault.jpg)](https://www.youtube.com/watch?v=dZxpM01JTj8) 

## Features

  

- Set custom AI roles with the `/role` command

- View conversation history with the `/history` command

- Clear conversation history but keep role settings with the `/clear` command

- Reset role settings with the `/reset` command

  


## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and add your API keys:
   
   ```
   cp .env.example .env
   ```
4. Edit `.env` and add your:
   - Telegram Bot Token (`TOKEN`)
   - OpenAI API Key (`OPENAI_API_KEY`)
  


## Running the Bot

### Using Docker

```bash
docker build -t gpt-bot .
docker run --env-file .env gpt-bot
```

### Using Docker Compose

```bash
docker-compose up --build
```

### Without Docker

1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```bash
   python main.py
   ```

