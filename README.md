# 🎓 TechRealm Backend - Complete Flask + Pandas System

A comprehensive backend system for educational program discovery with web scraping, analytics, RAG-powered chatbot, and email automation.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development Guide](#development-guide)

## ✨ Features

### 1. **Web Scraping System**
- Active ApplyBoard program scraper
- Extracts 15+ data points per program
- Automatic duplicate handling
- CSV persistence

### 2. **Program Management**
- Full CRUD operations
- Advanced search & filtering
- CSV import/export
- Application tracking

### 3. **Analytics & Event Tracking**
- Real-time event logging (clicks, views, hovers)
- Detailed analytics by program/user
- Summary reports & visualizations
- Time-based insights

### 4. **RAG-Powered Chatbot**
- Intelligent program recommendations
- Context-aware responses
- TF-IDF + OpenAI embeddings
- Chat history management

### 5. **Email Automation**
- Brevo API integration
- Application confirmations
- Custom email templates
- Email tracking & logs

## 🛠 Tech Stack

- **Framework**: Flask 3.0
- **Data Processing**: Pandas 2.1
- **Web Scraping**: BeautifulSoup4, Requests
- **AI/ML**: scikit-learn, OpenAI API (optional)
- **Email**: Brevo (SendinBlue) API
- **Storage**: CSV files (easily upgradable to database)

## 📁 Project Structure

```
techrealm-backend/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
│
├── scraper/
│   └── applyboard_scraper.py  # Web scraping module
│
├── api/
│   ├── programs.py            # Program CRUD & management
│   ├── analytics.py           # Event tracking & analytics
│   ├── chatbot.py             # RAG chatbot endpoints
│   └── emails.py              # Email automation
│
├── utils/
│   ├── save_load.py           # Data persistence utilities
│   └── rag_engine.py          # RAG/ML engine
│
└── data/
    ├── programs.csv           # Program database
    ├── analytics.csv          # Analytics logs
    ├── emails.csv             # Email records
    ├── chats.csv              # Chat history
    └── applications.csv       # Application records
```

## 🚀 Installation

### 1. Clone or Create Project

```bash
mkdir techrealm-backend
cd techrealm-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment

Create `.env` file with your configuration:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Initialize Data Directory

```bash
mkdir data
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000

# OpenAI (Optional - for advanced RAG)
OPENAI_API_KEY=your-openai-key

# Brevo Email API
BREVO_API_KEY=your-brevo-key
FROM_EMAIL=noreply@techrealm.com
FROM_NAME=TechRealm

# Scraper Settings
MAX_PROGRAMS=100
SCRAPER_DELAY=2
```

### Getting API Keys

1. **Brevo (Email)**: Sign up at [brevo.com](https://www.brevo.com)
2. **OpenAI (Optional)**: Get key at [platform.openai.com](https://platform.openai.com)

## 🎯 API Documentation

### Programs API

#### `POST /api/auto-scrape`
Trigger automatic program scraping
```json
{
  "max_programs": 50
}
```

#### `GET /api/programs`
Get all programs (paginated)
```
?page=1&per_page=20
```

#### `POST /api/programs`
Create new program
```json
{
  "program_name": "Master of Computer Science",
  "university": "University of Toronto",
  "degree_type": "Master's",
  "tuition_fee": "$25,000",
  "duration": "2 years"
}
```

#### `GET /api/programs/{id}`
Get single program

#### `PATCH /api/programs/{id}`
Update program

#### `DELETE /api/programs/{id}`
Delete program

#### `GET /api/programs/search?q=computer`
Search programs

#### `GET /api/export-programs`
Export programs to CSV

#### `POST /api/applied-to-program`
Log program application
```json
{
  "program_id": "uuid",
  "program_name": "CS Program",
  "user_email": "user@email.com"
}
```

### Analytics API

#### `POST /api/log-event`
Log user event
```json
{
  "project_id": "program-uuid",
  "event_type": "click",
  "user_id": "user123"
}
```

#### `GET /api/get-data`
Get all events

#### `GET /api/analytics/project/{id}`
Get program-specific analytics

#### `GET /api/analytics/summary`
Get analytics summary

#### `GET /api/analytics/user/{user_id}`
Get user analytics

### Chatbot API

#### `POST /api/chat-instance`
Create new chat
```json
{
  "user_id": "user123"
}
```

#### `POST /api/chat/{chat_id}`
Send message
```json
{
  "message": "Show me computer science programs in Canada"
}
```

#### `GET /api/chat/{chat_id}`
Get chat history

#### `POST /api/chat/quick-ask`
Quick question without chat instance
```json
{
  "message": "What are the best universities?"
}
```

#### `POST /api/rag/retrain`
Retrain RAG model

#### `POST /api/rag/search`
Direct RAG search
```json
{
  "query": "artificial intelligence",
  "top_k": 5
}
```

### Email API

#### `POST /api/emails/send`
Send custom email
```json
{
  "to": "user@email.com",
  "subject": "Subject",
  "content": "<html>...</html>",
  "program_id": "uuid"
}
```

#### `POST /api/emails/send-application`
Send application confirmation
```json
{
  "to": "user@email.com",
  "program_name": "CS Program",
  "university": "University",
  "program_id": "uuid"
}
```

#### `GET /api/emails`
Get all emails

#### `GET /api/emails/stats`
Get email statistics

#### `POST /api/emails/test`
Send test email

## 💻 Usage Examples

### Starting the Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

### Example Workflow

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 1. Scrape programs
response = requests.post(f"{BASE_URL}/auto-scrape", 
    json={"max_programs": 50})
print(response.json())

# 2. Search programs
response = requests.get(f"{BASE_URL}/programs/search?q=computer")
programs = response.json()['results']

# 3. Log event
requests.post(f"{BASE_URL}/log-event", json={
    "project_id": programs[0]['program_id'],
    "event_type": "view",
    "user_id": "user123"
})

# 4. Chat with bot
chat_response = requests.post(f"{BASE_URL}/chat/quick-ask", json={
    "message": "Show me AI programs in Canada"
})
print(chat_response.json()['response'])

# 5. Apply to program
requests.post(f"{BASE_URL}/applied-to-program", json={
    "program_id": programs[0]['program_id'],
    "program_name": programs[0]['program_name'],
    "user_email": "student@email.com"
})

# 6. Get analytics
analytics = requests.get(f"{BASE_URL}/analytics/summary")
print(analytics.json())
```

## 🔧 Development Guide

### Adding New Features

1. **New API Endpoint**: Add to appropriate blueprint in `/api`
2. **New Data Model**: Update `save_load.py` with new DataFrame
3. **New Scraper**: Extend `applyboard_scraper.py`

### Testing

```bash
# Test all endpoints
curl http://localhost:5000/health

# Test scraper
curl -X POST http://localhost:5000/api/auto-scrape \
  -H "Content-Type: application/json" \
  -d '{"max_programs": 10}'

# Test chatbot
curl -X POST http://localhost:5000/api/chat/quick-ask \
  -H "Content-Type: application/json" \
  -d '{"message": "Find engineering programs"}'
```

### Data Backup

```python
from utils.save_load import data_manager
data_manager.backup_all()
```

## 📊 Data Models

### Programs DataFrame
- program_id, program_name, university
- degree_type, duration, tuition_fee
- application_fee, start_date, deadline
- country, requirements, english_test_required
- description, url, intake, scraped_at

### Analytics DataFrame
- event_id, project_id, event_type
- user_id, timestamp

### Emails DataFrame
- email_id, program_id, to
- subject, timestamp, status, message_id

### Chats DataFrame
- chat_id, user_id, messages (JSON)
- created_at, updated_at

### Applications DataFrame
- application_id, program_id, program_name
- user_email, applied_at

## 🚀 Deployment

### Production Settings

```bash
# .env for production
FLASK_ENV=production
SECRET_KEY=strong-random-key
```

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔒 Security Best Practices

1. **Never commit .env file**
2. **Use strong SECRET_KEY**
3. **Validate all user inputs**
4. **Rate limit API endpoints**
5. **Use HTTPS in production**

## 📈 Performance Tips

1. **Pagination**: Always use pagination for large datasets
2. **Caching**: Consider Redis for frequently accessed data
3. **Background Tasks**: Use Celery for heavy scraping
4. **Database**: Migrate to PostgreSQL for production scale

## 🐛 Troubleshooting

### Common Issues

**ImportError**: Install missing dependencies
```bash
pip install -r requirements.txt
```

**Port in use**: Change PORT in .env
```bash
PORT=8000
```

**Email not sending**: Check BREVO_API_KEY
```bash
# Test with mock mode (development)
# Emails will be logged but not sent
```

## 📝 License

MIT License - Feel free to use for your projects!

## 👥 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push and create PR

## 📧 Support

For issues and questions:
- Create GitHub issue
- Email: support@techrealm.com

---

**Built with ❤️ for TechRealm | Backend Delivery Plan Complete** 🎉