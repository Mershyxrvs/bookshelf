# စာအုပ်စင် BookShelf 📚

Myanmar's Telegram-first digital book platform. Browse and download 50+ books in Burmese and English — no app install required.

## Structure

```
bookshelf/
├── bot/                  # Telegram bot (python-telegram-bot)
│   ├── bot.py            # Bot commands: /search, /genres, /new, /premium, /status
│   ├── requirements.txt
│   ├── premium_users.json
│   └── .env.example
├── mini-app/             # Telegram Mini App (static site via Cloudflare Pages)
│   ├── public/
│   │   ├── index.html    # Book browser with genre/author/lang filters
│   │   ├── data/books.json
│   │   └── books/        # Book files (free/ and premium/)
│   ├── package.json
│   └── wrangler.toml
├── channel-content/      # Telegram channel post templates
│   └── posts.md
├── data/                 # Shared data
│   └── books.json        # Master book catalog (50 books)
└── content-plan.md       # 12-month content strategy
```

## Setup

### Bot

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
# Fill in BOT_TOKEN, ADMIN_IDS, MINI_APP_URL
python bot.py
```

### Mini App

```bash
cd mini-app
npm install
npx wrangler pages dev public
```

Deploy to Cloudflare Pages:
```bash
npx wrangler pages deploy public --project-name=bookshelf
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Open Mini App |
| `/search <query>` | Search books by title or author |
| `/genres` | List all genres |
| `/new` | This week's new arrivals |
| `/premium` | Premium membership info |
| `/status` | Check premium status |

## Books

- **50 books** — 27 Burmese, 23 English
- **16 genres** — Fiction, History, Poetry, Science, Psychology, Business, etc.
- **15 premium** books (requires subscription)
- **35 free** books (open to all users)

## Monetization

| Plan | Price |
|------|-------|
| Monthly | 3,000 MMK |
| Lifetime | 15,000 MMK |
