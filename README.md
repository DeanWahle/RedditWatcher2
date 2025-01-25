# Reddit iPad Monitor

Monitors r/appleswap and r/hardwareswap for iPad sales posts and sends email notifications.

## Features
- Monitors specified subreddits for iPad listings
- Filters for selling posts only ([H] tag)
- Email notifications for new listings
- Deduplication with time-based cache

## Setup

### Local Development
1. Clone repository:
```bash
git clone https://github.com/DeanWahle/RedditWatcher2.git
cd RedditWatcher2
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create .env file:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
EMAIL_FROM=your_email
EMAIL_TO=your_email
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_app_password
```

4. Run locally:
```bash
python redditWatcher2.py
```

### Heroku Deployment
1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create Heroku app:
```bash
heroku create
```

3. Configure environment variables:
```bash
heroku config:set REDDIT_CLIENT_ID=your_id
heroku config:set REDDIT_CLIENT_SECRET=your_secret
heroku config:set EMAIL_FROM=your_email
heroku config:set EMAIL_TO=your_email
heroku config:set EMAIL_USERNAME=your_email
heroku config:set EMAIL_PASSWORD=your_app_password
```

4. Deploy:
```bash
git push heroku main
```

5. Start worker:
```bash
heroku ps:scale worker=1
```