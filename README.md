# 🧠 Mental Health Bot

A comprehensive Telegram bot for mental health monitoring with daily/weekly check-ins, analytics, AI-powered predictions, and personalized insights.

## ✨ Features

- **📋 Multi-Step Onboarding**: Collect demographics, lifestyle, and baseline mental health data
- **📊 Daily Check-ins**: Track stress, anxiety, heart rate, sleep, and habits
- **📅 Weekly Assessments**: Comprehensive weekly mental health surveys
- **📈 Statistics & Charts**: Visualize trends with matplotlib-generated charts
- **🔮 AI Predictions**: Placeholder for AI model integration for anxiety predictions
- **⚙️ User Settings**: Edit profile, manage notifications, download data, delete account
- **👑 Admin Panel**: User management, statistics, and data export capabilities
- **🔔 Scheduled Reminders**: APScheduler-based weekly reminders

## 🛠️ Tech Stack

- **Python 3.11+**
- **aiogram 3.x** - Modern async Telegram Bot Framework
- **SQLAlchemy 2.0** - Async ORM with aiosqlite
- **APScheduler** - Background job scheduling
- **matplotlib** - Chart generation
- **pydantic-settings** - Configuration management
- **loguru** - Advanced logging

## 📁 Project Structure

```
MentalHealthBot/
├── bot.py                  # Main entry point
├── config.py               # Configuration settings
├── scheduler.py            # APScheduler setup
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── database/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models
│   └── session.py          # Database session management
├── handlers/
│   ├── __init__.py
│   ├── common.py           # Start, help, menu handlers
│   ├── onboarding.py       # Onboarding wizard
│   ├── daily_check.py      # Daily check-in handlers
│   ├── weekly_check.py     # Weekly assessment handlers
│   ├── stats.py            # Statistics and charts
│   ├── settings.py         # User settings
│   └── admin.py            # Admin panel
├── keyboards/
│   ├── __init__.py
│   └── keyboards.py        # Inline keyboard builders
├── middlewares/
│   ├── __init__.py
│   └── middlewares.py      # Bot middlewares
├── services/
│   ├── __init__.py
│   ├── user_service.py     # User CRUD operations
│   ├── analytics_service.py # Analytics and exports
│   └── ai_service.py       # AI model integration
├── states/
│   ├── __init__.py
│   └── states.py           # FSM states
└── utils/
    ├── __init__.py
    ├── constants.py        # Messages and constants
    ├── helpers.py          # Utility functions
    └── charts.py           # Chart generators
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/MentalHealthBot.git
cd MentalHealthBot
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: BOT_TOKEN
# Optional: ADMIN_IDS, AI_API_URL
```

5. **Run the bot**
```bash
python bot.py
```

## ⚙️ Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram Bot API token | ✅ | - |
| `DATABASE_URL` | SQLAlchemy database URL | ❌ | `sqlite+aiosqlite:///mental_health_bot.db` |
| `ADMIN_IDS` | Comma-separated admin user IDs | ❌ | - |
| `AI_API_URL` | AI prediction service URL | ❌ | - |
| `AI_API_KEY` | AI service API key | ❌ | - |
| `RATE_LIMIT` | Max requests per period | ❌ | 30 |
| `RATE_LIMIT_PERIOD` | Rate limit period (seconds) | ❌ | 60 |
| `SESSION_TIMEOUT` | FSM session timeout (seconds) | ❌ | 3600 |

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show help information |
| `/menu` | Open the main menu |
| `/cancel` | Cancel current operation |

## 🔮 AI Integration

The bot includes a placeholder for AI model integration. To connect your own AI service:

1. **Update `services/ai_service.py`**

```python
async def call_ai_model(user_data: dict) -> dict:
    """
    Call your AI prediction service.
    
    Expected input:
    - demographics (age, gender, occupation)
    - lifestyle data (sleep, activity, diet)
    - current check-in data (stress, anxiety, etc.)
    
    Expected output:
    {
        "predicted_anxiety_level": float,  # 1-10 scale
        "confidence": float,               # 0-1
        "advice": str,                     # Personalized recommendation
        "risk_level": str                  # low/medium/high
    }
    """
    # Implement your AI service call here
    async with aiohttp.ClientSession() as session:
        async with session.post(
            settings.ai_api_url,
            json=user_data,
            headers={"Authorization": f"Bearer {settings.ai_api_key}"}
        ) as response:
            return await response.json()
```

2. **Expected AI Model Features**

The bot collects these features for prediction:
- Demographics: age, gender, occupation, family status
- Lifestyle: sleep hours, physical activity, diet quality
- Habits: alcohol, caffeine, smoking
- Current state: stress level, anxiety level, heart rate, breathing rate

## 📊 Database Schema

### Core Models

- **User**: Telegram user data and settings
- **UserProfile**: Demographics and lifestyle information
- **DailyAnswer**: Daily check-in responses
- **WeeklyAnswer**: Weekly assessment responses
- **Prediction**: AI prediction results
- **Feedback**: User feedback on predictions
- **Reminder**: Notification tracking
- **History**: User activity log

## 🛡️ Security Features

- **Rate Limiting**: Prevents spam and abuse
- **Session Timeout**: Auto-clears inactive FSM states
- **Admin Authentication**: Middleware-based admin verification
- **Data Export**: Users can download their data (GDPR compliance)
- **Account Deletion**: Complete data removal option

## 📈 Monitoring & Logging

The bot uses `loguru` for comprehensive logging:

```python
# Logs are written to:
# - Console (INFO level)
# - logs/bot_{date}.log (DEBUG level)
```

## 🔄 Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Weekly Reminder | Sunday 10:00 UTC | Sends reminder to all users with notifications enabled |
| Daily Reminder | 21:00 UTC (optional) | Reminds users who haven't completed daily check-in |

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest tests/ -v
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot is designed for educational and self-monitoring purposes only. It is **NOT** a substitute for professional mental health care. If you're experiencing mental health issues, please seek help from qualified healthcare professionals.

---

Made with ❤️ for mental wellness
