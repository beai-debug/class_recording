# Class Recording API - Complete Documentation

A production-ready FastAPI service for processing class audio recordings and generating AI-powered study materials with teacher feedback using LangGraph pipeline architecture.

## 🚀 Features

- ✅ **Audio Transcription**: Converts audio/video to text using Whisper
- ✅ **AI-Powered Study Materials**: Generates notes, misconceptions, practice questions, and resources
- ✅ **Teacher Feedback**: Provides constructive, unbiased feedback to teachers for professional growth
- ✅ **Multi-Model Support**: Uses both OpenAI (GPT-4, GPT-4o-mini, GPT-5) and Gemini models
- ✅ **Async Job Processing**: Long-running pipeline with job_id tracking
- ✅ **PostgreSQL Database**: Production-ready database with connection pooling
- ✅ **Audit Logging**: Complete activity tracking for compliance
- ✅ **RESTful API**: Easy integration with any client
- ✅ **Markdown Export**: Download results in markdown format
- ✅ **Flexible Querying**: Optional record_id with filter-based search

## 📊 System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATION                          │
│                    (Web/Mobile/Desktop Client)                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTP/REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FASTAPI SERVER                             │
│                           (api.py)                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Endpoints: /process, /status, /result, /recordings, etc.   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────┬─────────────────────────────────┬───────────────────────────┘
        │                                 │
        │ Job Management                  │ Database Operations
        ▼                                 ▼
┌──────────────────┐            ┌─────────────────────────┐
│  WORKER THREAD   │            │   POSTGRESQL DATABASE   │
│   (worker.py)    │            │     (database.py)       │
│                  │            │                         │
│  - Job Queue     │◄───────────┤  Tables:                │
│  - Status Track  │            │  - recordings           │
│  - Processing    │            │  - audit_logs           │
└────────┬─────────┘            └─────────────────────────┘
         │
         │ Audio Processing
         ▼
┌──────────────────────────────────────────────────────────┐
│              AUDIO TRANSCRIPTION                         │
│        (audio_to_transcribe_whisper.py)                  │
│                                                          │
│  - Whisper Model                                         │
│  - Audio Format Conversion                               │
│  - Transcription to Text                                 │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ Transcript Text
                         ▼
┌──────────────────────────────────────────────────────────┐
│              LANGGRAPH PIPELINE                          │
│              (class_graph.py)                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              PARALLEL PROCESSING                   │ │
│  │                                                    │ │
│  │  ┌──────────────┐      ┌──────────────┐          │ │
│  │  │   NODE 1A    │      │   NODE 1B    │          │ │
│  │  │ Structured   │      │Misconception │          │ │
│  │  │    Notes     │      │  Detection   │          │ │
│  │  │  (GPT-4o)    │      │(GPT-4o-mini) │          │ │
│  │  └──────┬───────┘      └──────┬───────┘          │ │
│  │         │                     │                   │ │
│  │         └──────────┬──────────┘                   │ │
│  │                    │                              │ │
│  │         ┌──────────┴──────────┐                   │ │
│  │         │                     │                   │ │
│  │         ▼                     ▼                   │ │
│  │  ┌──────────────┐      ┌──────────────┐          │ │
│  │  │   NODE 2     │      │   NODE 3     │          │ │
│  │  │  Practice    │      │  Resources   │          │ │
│  │  │  Questions   │      │ & Real-life  │          │ │
│  │  │(GPT-4o-mini) │      │   (GPT-5)    │          │ │
│  │  └──────┬───────┘      └──────┬───────┘          │ │
│  │         │                     │                   │ │
│  │         └──────────┬──────────┘                   │ │
│  │                    │                              │ │
│  │                    ▼                              │ │
│  │            ┌──────────────┐                       │ │
│  │            │   NODE 4     │                       │ │
│  │            │ Study Plan & │                       │ │
│  │            │   Actions    │                       │ │
│  │            │(Gemini-2.5)  │                       │ │
│  │            └──────┬───────┘                       │ │
│  │                   │                               │ │
│  │                   ▼                               │ │
│  │            ┌──────────────┐                       │ │
│  │            │   NODE 5     │                       │ │
│  │            │   Teacher    │                       │ │
│  │            │   Feedback   │                       │ │
│  │            │   (GPT-4o)   │                       │ │
│  │            └──────────────┘                       │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────┘
                         │
                         │ Combined Markdown Output
                         ▼
┌──────────────────────────────────────────────────────────┐
│              RESULT STORAGE & DELIVERY                   │
│                                                          │
│  - Save to Database (combined_md)                        │
│  - Update Job Status (completed)                         │
│  - Create Audit Log (PROCESSED)                          │
│  - Return to Client via API                              │
└──────────────────────────────────────────────────────────┘
```

### LangGraph Pipeline Flow (Detailed)

```
                    ┌─────────────────┐
                    │   TRANSCRIPT    │
                    │     INPUT       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    NODE 1A      │
                    │ Structured Notes│
                    │    (GPT-4o)     │
                    └────┬───────┬────┘
                         │       │
              ┌──────────┘       └──────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐          ┌─────────────────┐
    │    NODE 1B      │          │    NODE 3       │
    │ Misconceptions  │          │   Resources &   │
    │  (GPT-4o-mini)  │          │   Real-life     │
    └────┬───────┬────┘          │    (GPT-5)      │
         │       │               └────────┬────────┘
         │       └──────┐                 │
         │              │                 │
         ▼              ▼                 │
    ┌─────────────────────┐              │
    │      NODE 2         │              │
    │ Practice Questions  │              │
    │   (GPT-4o-mini)     │              │
    └──────────┬──────────┘              │
               │                         │
               └────────┬────────────────┘
                        │
                        ▼
               ┌─────────────────┐
               │     NODE 4      │
               │  Study Plan &   │
               │    Actions      │
               │  (Gemini-2.5)   │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │     NODE 5      │
               │    Teacher      │
               │    Feedback     │
               │    (GPT-4o)     │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │   COMBINED MD   │
               │     OUTPUT      │
               └─────────────────┘
```

### Node Dependencies & Execution Order

```
NODE 1A (Notes) → Runs First
    ├─→ NODE 1B (Misconceptions) → Depends on NODE 1A
    │       ├─→ NODE 2 (Practice) → Depends on NODE 1A + NODE 1B
    │       └─→ NODE 4 (Actions) → Depends on NODE 1A + NODE 1B
    ├─→ NODE 3 (Resources) → Depends on NODE 1A
    └─→ NODE 5 (Feedback) → Depends on NODE 1A

All nodes converge to END state
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- FFmpeg (for audio processing)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd class_recording
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install PostgreSQL

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo service postgresql start
```

#### macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Windows:
Download from: https://www.postgresql.org/download/windows/

### Step 5: Install FFmpeg

#### Ubuntu/Debian:
```bash
sudo apt-get install -y ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

#### Windows:
Download from: https://ffmpeg.org/download.html

### Step 6: Setup Database

**Choose one of the following methods based on your environment:**

#### Method 1: Using psql directly (Recommended)
```bash
# Option A: Connect and enter password when prompted
psql -h localhost -U postgres -d postgres
# Enter password: Deepdive

# Option B: Use PGPASSWORD environment variable (no password prompt)
PGPASSWORD=Deepdive psql -h localhost -U postgres -d postgres

# Once connected, create database
CREATE DATABASE class_recording;

# Grant privileges (if needed)
GRANT ALL PRIVILEGES ON DATABASE class_recording TO postgres;

# Exit PostgreSQL
\q
```


#### Method 2: Using createdb command (Simplest)
```bash
# Option A: Enter password when prompted
createdb -h localhost -U postgres class_recording
# Enter password: Deepdive

# Option B: Use PGPASSWORD to avoid password prompt
PGPASSWORD=Deepdive createdb -h localhost -U postgres class_recording
```

#### Method 3: Auto-creation (For Codespaces/Docker)
```bash
# If PostgreSQL is already configured with your .env credentials,
# the application will automatically create tables on first run.
# Just ensure the database exists:

# Check if database exists
psql -h localhost -U postgres -l | grep class_recording

# If not found, create it:
createdb -h localhost -U postgres class_recording
```

**Note for Codespaces/Docker users:** If you encounter permission issues, the PostgreSQL user and database may already be configured. Simply verify the database exists and proceed to Step 7.

**Troubleshooting Database Setup:**
```bash
# Check if PostgreSQL is accessible
pg_isready -h localhost -p 5432

# Test connection with .env credentials
psql -h localhost -U postgres -d postgres -c "SELECT version();"

# List all databases
psql -h localhost -U postgres -l
```

### Step 7: Configure Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# LangSmith Configuration (Optional - for monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=SMART_CLASS_NOTES

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=class_recording
DB_USER=postgres
DB_PASSWORD=Deepdive
```

**Important:** Never commit the `.env` file to version control!

## 🚀 Running the Application

### Start the API Server

```bash
# Development mode with auto-reload
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: `http://localhost:8000`

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### 1. Process Audio File
```http
POST /process
Content-Type: multipart/form-data

Parameters:
- audio_file (file, required): Audio file to process
- school_name (string, required): School name
- class_name (string, required): Class/Grade
- subject (string, optional): Subject name
- section (string, optional): Section
- recording_subject (string, optional): Recording topic

Response:
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Job created successfully. Record ID: uuid"
}
```

### 2. Check Job Status
```http
GET /status/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": "Current step...",
  "error": null
}
```

### 3. Get Result as Markdown
```http
GET /result/{job_id}/markdown

Response: Plain text markdown content
```

### 4. List All Recordings
```http
GET /recordings?limit=100&offset=0&school_name=...&class=...

Response:
{
  "recordings": [...],
  "total": 10,
  "limit": 100,
  "offset": 0
}
```

### 5. Get Recording by ID or Filters
```http
GET /recordings/{record_id}/markdown
GET /recordings/markdown?school_name=...&class=...&date=YYYY-MM-DD

Response: Plain text markdown content
```

### 6. Delete Recording
```http
DELETE /recordings/{record_id}
DELETE /recordings/{record_id}?school_name=...&class=...

Response:
{
  "message": "Recording deleted successfully",
  "record_id": "uuid"
}
```

### 7. Delete All Recordings
```http
DELETE /recordings

Response:
{
  "message": "Successfully deleted all recordings",
  "deleted_count": 42
}
```

### 8. View Audit Logs
```http
GET /audit-logs?limit=100&offset=0&activity=CREATED

Response:
{
  "logs": [...],
  "total": 50,
  "limit": 100,
  "offset": 0
}
```

**For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

## 🗄️ Database Schema

### Recordings Table
```sql
CREATE TABLE recordings (
    id TEXT PRIMARY KEY,              -- UUID
    date TEXT NOT NULL,               -- YYYY-MM-DD
    school_name TEXT NOT NULL,
    class TEXT NOT NULL,
    section TEXT,
    subject TEXT,
    recording_subject TEXT,
    audio_filename TEXT NOT NULL,
    combined_md TEXT,                 -- Generated markdown
    job_id TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,              -- UUID
    date TEXT NOT NULL,
    school_name TEXT NOT NULL,
    class TEXT NOT NULL,
    section TEXT,
    subject TEXT,
    recording_subject TEXT,
    audio_filename TEXT NOT NULL,
    combined_md TEXT,
    job_id TEXT,
    activity TEXT NOT NULL,           -- CREATED, PROCESSED, DELETED, DELETED_ALL
    activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP
);
```

**For detailed database documentation, see [DATABASE.md](DATABASE.md)**

## 🤖 AI Models Configuration

| Node | Purpose | Model | Provider |
|------|---------|-------|----------|
| NODE 1A | Structured Notes | gpt-4o | OpenAI |
| NODE 1B | Misconception Detection | gpt-4o-mini | OpenAI |
| NODE 2 | Practice Questions | gpt-4o-mini | OpenAI |
| NODE 3 | Resources & Applications | gpt-5 | OpenAI |
| NODE 4 | Study Plan & Actions | gemini-2.5-flash | Google Gemini |
| NODE 5 | Teacher Feedback | gpt-4o | OpenAI |

## 📁 Project Structure

```
class_recording/
├── api.py                              # FastAPI application & endpoints
├── database.py                         # PostgreSQL operations & connection pool
├── models.py                           # Pydantic models for validation
├── worker.py                           # Background job processor
├── class_graph.py                      # LangGraph pipeline (6 nodes)
├── audio_to_transcribe_whisper.py      # Audio transcription with Whisper
├── main.py                             # CLI interface (optional)
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (not in git)
├── .gitignore                          # Git ignore rules
├── README.md                           # This file
├── API_DOCUMENTATION.md                # Detailed API documentation
├── DATABASE.md                         # Database documentation
└── uploads/                            # Uploaded audio files directory
    └── .gitkeep                        # Keep directory in git
```

## 📖 Complete Usage Example

```python
import requests
import time

# Configuration
BASE_URL = "http://localhost:8000"

# 1. Upload and process audio file
print("Uploading audio file...")
with open("lecture.mp3", "rb") as audio_file:
    files = {"audio_file": audio_file}
    data = {
        "school_name": "Springfield High School",
        "class_name": "10th Grade",
        "subject": "Physics",
        "section": "A",
        "recording_subject": "Quantum Mechanics Introduction"
    }
    
    response = requests.post(f"{BASE_URL}/process", files=files, data=data)
    result = response.json()
    
    job_id = result["job_id"]
    record_id = result["message"].split(": ")[1]
    
    print(f"✓ Job created: {job_id}")
    print(f"✓ Record ID: {record_id}")

# 2. Poll for job completion
print("\nProcessing audio...")
while True:
    status_response = requests.get(f"{BASE_URL}/status/{job_id}")
    status_data = status_response.json()
    
    status = status_data["status"]
    progress = status_data.get("progress", "")
    
    print(f"Status: {status} - {progress}")
    
    if status == "completed":
        print("✓ Processing completed!")
        break
    elif status == "failed":
        print(f"✗ Processing failed: {status_data.get('error')}")
        exit(1)
    
    time.sleep(5)  # Wait 5 seconds before checking again

# 3. Download the result
print("\nDownloading study materials...")
result_response = requests.get(f"{BASE_URL}/result/{job_id}/markdown")

with open("study_materials.md", "w", encoding="utf-8") as f:
    f.write(result_response.text)

print("✓ Study materials saved to study_materials.md")

# 4. List all recordings
print("\nListing all recordings...")
recordings_response = requests.get(f"{BASE_URL}/recordings?limit=10")
recordings_data = recordings_response.json()

print(f"Total recordings: {recordings_data['total']}")
for rec in recordings_data['recordings']:
    print(f"  - {rec['school_name']} | {rec['class_name']} | {rec['date']}")

# 5. Retrieve by filters (without record_id)
print("\nRetrieving by filters...")
params = {
    "school_name": "Springfield High School",
    "class": "10th Grade",
    "date": "2026-03-07"
}
filtered_response = requests.get(
    f"{BASE_URL}/recordings/markdown",
    params=params
)

with open("filtered_materials.md", "w", encoding="utf-8") as f:
    f.write(filtered_response.text)

print("✓ Filtered materials saved")

# 6. View audit logs
print("\nViewing recent audit logs...")
audit_response = requests.get(f"{BASE_URL}/audit-logs?limit=5")
audit_data = audit_response.json()

for log in audit_data['logs']:
    print(f"  {log['activity_timestamp']}: {log['activity']} - {log['school_name']}")

# 7. Delete recording (optional)
# delete_response = requests.delete(f"{BASE_URL}/recordings/{record_id}")
# print(f"\n✓ Recording deleted: {delete_response.json()}")

print("\n✓ All operations completed successfully!")
```

## 🔍 Monitoring & Debugging

### LangSmith Integration

All LLM calls are automatically tracked in LangSmith:
- Token usage per node
- Execution time per node
- Input/output for each node
- Cost analysis
- Error tracking

View traces at: https://smith.langchain.com

### Database Monitoring

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('class_recording'));

-- Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public';

-- View recent activities
SELECT * FROM audit_logs ORDER BY activity_timestamp DESC LIMIT 10;

-- Count recordings by school
SELECT school_name, COUNT(*) as count
FROM recordings
GROUP BY school_name;
```

## 🐛 Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to PostgreSQL

**Solutions:**
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check PostgreSQL service status (if you have sudo access)
sudo service postgresql status

# Start PostgreSQL (if you have sudo access)
sudo service postgresql start

# Test connection with .env credentials
psql -h localhost -U postgres -d postgres -c "SELECT version();"

# Check if database exists
psql -h localhost -U postgres -l | grep class_recording

# If database doesn't exist, create it
createdb -h localhost -U postgres class_recording
```

**For Codespaces/Docker environments without sudo:**
```bash
# Verify PostgreSQL is accessible
pg_isready -h localhost -p 5432

# If connection fails, check if PostgreSQL is configured
# The database service should be pre-configured in Codespaces

# Test with environment variables
export PGPASSWORD=Deepdive
psql -h localhost -U postgres -d postgres -c "\l"
unset PGPASSWORD

# Create database if needed
PGPASSWORD=Deepdive createdb -h localhost -U postgres class_recording
```

**Common Issues:**
- **"password authentication failed"**: Verify DB_PASSWORD in `.env` matches PostgreSQL user password
- **"database does not exist"**: Run `createdb -h localhost -U postgres class_recording`
- **"connection refused"**: PostgreSQL service may not be running or listening on localhost:5432
- **"role does not exist"**: The postgres user may need to be created (usually pre-configured)

### Job Processing Issues

**Problem:** Job stays in "pending" status

**Solutions:**
1. Check server logs for errors
2. Verify API keys in `.env` file
3. Ensure models are accessible
4. Check network connectivity

### Audio Processing Fails

**Problem:** Transcription errors

**Solutions:**
```bash
# Verify FFmpeg installation
ffmpeg -version

# Check audio file format
ffmpeg -i audio_file.mp3

# Test with a different audio file
```

### Out of Memory

**Problem:** Large audio files cause memory issues

**Solutions:**
1. Increase server memory
2. Process files in chunks
3. Use streaming for large files
4. Optimize audio quality before upload

## 📊 Performance Optimization

### Database Optimization

```sql
-- Create indexes for better query performance
CREATE INDEX idx_recordings_date ON recordings(date);
CREATE INDEX idx_recordings_school ON recordings(school_name);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(activity_timestamp DESC);
CREATE INDEX idx_audit_logs_activity ON audit_logs(activity);
```

### Connection Pool Tuning

Edit `database.py`:
```python
connection_pool = ThreadedConnectionPool(
    minconn=5,      # Increase for high concurrency
    maxconn=50,     # Increase for many simultaneous requests
    **DB_CONFIG
)
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **Strong Passwords**: Change default database password
3. **API Rate Limiting**: Implement rate limiting for production
4. **Input Validation**: All inputs are validated via Pydantic models
5. **SQL Injection**: Using parameterized queries (psycopg2)
6. **CORS**: Configure CORS for production environment
7. **HTTPS**: Use HTTPS in production
8. **Audit Logs**: Monitor audit logs regularly

## 📄 License

This project is part of the class recording system for educational purposes.

## 🤝 Contributing

For bug reports or feature requests, please create an issue in the repository.

## 📞 Support

For technical support:
- Check the documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md), [DATABASE.md](DATABASE.md)
- Review troubleshooting section above
- Check server logs for detailed error messages
- Verify all environment variables are set correctly

## 🎯 Key Features Summary

- **UUID-Based IDs**: Unique identifiers for all records
- **Parallel Processing**: LangGraph nodes run in parallel where possible
- **Multi-Model Support**: OpenAI GPT-4, GPT-5, and Google Gemini
- **Audit Trail**: Complete history of all operations
- **Flexible Querying**: Search by ID or any combination of filters
- **Markdown Export**: Easy sharing and documentation
- **Production Ready**: PostgreSQL, connection pooling, error handling
- **Monitoring**: LangSmith integration for LLM tracking
- **Scalable**: Designed for high-volume processing

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✅
