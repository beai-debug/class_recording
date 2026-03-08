# Database Documentation - Class Recording API

Complete database reference for the PostgreSQL-based Class Recording system.

## Overview

The Class Recording API uses **PostgreSQL** as its production database system. The database stores class recording metadata, processing results, and maintains a complete audit log of all activities for compliance and monitoring.

## Database Architecture

### Technology Stack

- **Database**: PostgreSQL 12+
- **Connection Library**: psycopg2-binary
- **Connection Pooling**: ThreadedConnectionPool (1-20 connections)
- **ORM**: None (Direct SQL with parameterized queries)
- **Migration**: Automatic table creation on startup

### Connection Configuration

```python
# Environment Variables (.env file)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=class_recording
DB_USER=postgres
DB_PASSWORD=Deepdive
```

### Connection Pool

```python
ThreadedConnectionPool(
    minconn=1,      # Minimum connections
    maxconn=20,     # Maximum connections
    host='localhost',
    port=5432,
    database='class_recording',
    user='postgres',
    password='Deepdive'
)
```

---

## Database Schema

### 1. Recordings Table

Stores all recording metadata and processing results.

**Table Definition:**
```sql
CREATE TABLE recordings (
    id TEXT PRIMARY KEY,                    -- UUID for the recording
    date TEXT NOT NULL,                     -- Date of recording (YYYY-MM-DD)
    school_name TEXT NOT NULL,              -- Name of the school
    class TEXT NOT NULL,                    -- Class/Grade (e.g., 10th, 12th)
    section TEXT,                           -- Section (optional)
    subject TEXT,                           -- Subject name (optional)
    recording_subject TEXT,                 -- Recording subject/topic (optional)
    audio_filename TEXT NOT NULL,           -- Filename of the audio file
    combined_md TEXT,                       -- Generated markdown content
    job_id TEXT UNIQUE,                     -- Unique job identifier
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation timestamp
);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | TEXT | No | Primary key, UUID v4 format |
| date | TEXT | No | Recording date in YYYY-MM-DD format |
| school_name | TEXT | No | School name |
| class | TEXT | No | Class/Grade identifier |
| section | TEXT | Yes | Section identifier (A, B, C, etc.) |
| subject | TEXT | Yes | Subject name (Physics, Math, etc.) |
| recording_subject | TEXT | Yes | Specific topic of the recording |
| audio_filename | TEXT | No | Stored audio file name (UUID-based) |
| combined_md | TEXT | Yes | Generated study materials in markdown |
| job_id | TEXT | No | Unique job identifier (UUID v4) |
| created_at | TIMESTAMP | No | Auto-generated creation timestamp |

**Indexes:**
- Primary Key: `id`
- Unique Index: `job_id`

**Recommended Additional Indexes:**
```sql
CREATE INDEX idx_recordings_date ON recordings(date);
CREATE INDEX idx_recordings_school ON recordings(school_name);
CREATE INDEX idx_recordings_class ON recordings(class);
CREATE INDEX idx_recordings_created_at ON recordings(created_at DESC);
```

**Example Data:**
```sql
INSERT INTO recordings VALUES (
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    '2026-03-07',
    'Springfield High School',
    '10th Grade',
    'A',
    'Physics',
    'Quantum Mechanics',
    '123e4567-e89b-12d3-a456-426614174000.mp3',
    '# Class Tutor – Combined Output...',
    '123e4567-e89b-12d3-a456-426614174000',
    '2026-03-07 17:45:00'
);
```

---

### 2. Audit Logs Table

Tracks all activities performed on recordings for audit and compliance purposes.

**Table Definition:**
```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,                    -- UUID for the log entry
    date TEXT NOT NULL,                     -- Date of the recording
    school_name TEXT NOT NULL,              -- Name of the school
    class TEXT NOT NULL,                    -- Class/Grade
    section TEXT,                           -- Section (optional)
    subject TEXT,                           -- Subject name (optional)
    recording_subject TEXT,                 -- Recording subject/topic (optional)
    audio_filename TEXT NOT NULL,           -- Filename of the audio file
    combined_md TEXT,                       -- Generated markdown content (if applicable)
    job_id TEXT,                            -- Job identifier
    activity TEXT NOT NULL,                 -- Activity type (CREATED, PROCESSED, DELETED, DELETED_ALL)
    activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When the activity occurred
    created_at TIMESTAMP                    -- Original creation timestamp of the recording
);
```

**Columns:**

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | TEXT | No | Primary key, UUID v4 format |
| date | TEXT | No | Recording date in YYYY-MM-DD format |
| school_name | TEXT | No | School name |
| class | TEXT | No | Class/Grade identifier |
| section | TEXT | Yes | Section identifier |
| subject | TEXT | Yes | Subject name |
| recording_subject | TEXT | Yes | Specific topic |
| audio_filename | TEXT | No | Audio file name |
| combined_md | TEXT | Yes | Generated markdown (for PROCESSED activity) |
| job_id | TEXT | Yes | Job identifier |
| activity | TEXT | No | Activity type (see below) |
| activity_timestamp | TIMESTAMP | No | When activity occurred |
| created_at | TIMESTAMP | Yes | Original recording creation time |

**Activity Types:**

| Activity | Description | When Logged |
|----------|-------------|-------------|
| CREATED | Recording was created | When audio file is uploaded |
| PROCESSED | Processing completed | When study materials are generated |
| DELETED | Single recording deleted | When DELETE /recordings/{id} is called |
| DELETED_ALL | Bulk deletion | When DELETE /recordings is called |

**Indexes:**
- Primary Key: `id`

**Recommended Additional Indexes:**
```sql
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(activity_timestamp DESC);
CREATE INDEX idx_audit_logs_activity ON audit_logs(activity);
CREATE INDEX idx_audit_logs_job_id ON audit_logs(job_id);
CREATE INDEX idx_audit_logs_school ON audit_logs(school_name);
CREATE INDEX idx_audit_logs_date ON audit_logs(date);
```

**Example Data:**
```sql
-- CREATED activity
INSERT INTO audit_logs VALUES (
    'log-uuid-1',
    '2026-03-07',
    'Springfield High School',
    '10th Grade',
    'A',
    'Physics',
    'Quantum Mechanics',
    '123e4567.mp3',
    NULL,
    '123e4567-e89b-12d3-a456-426614174000',
    'CREATED',
    '2026-03-07 17:45:00',
    '2026-03-07 17:45:00'
);

-- PROCESSED activity
INSERT INTO audit_logs VALUES (
    'log-uuid-2',
    '2026-03-07',
    'Springfield High School',
    '10th Grade',
    'A',
    'Physics',
    'Quantum Mechanics',
    '123e4567.mp3',
    '# Class Tutor – Combined Output...',
    '123e4567-e89b-12d3-a456-426614174000',
    'PROCESSED',
    '2026-03-07 17:50:00',
    '2026-03-07 17:45:00'
);
```

---

## Installation & Setup

### 1. Install PostgreSQL

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
```

#### macOS:
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Windows:
Download and install from: https://www.postgresql.org/download/windows/

### 2. Start PostgreSQL Service

#### Ubuntu/Debian:
```bash
sudo service postgresql start
sudo service postgresql status
```

#### macOS:
```bash
brew services start postgresql@15
brew services list
```

#### Windows:
PostgreSQL service starts automatically after installation.

### 3. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Or connect directly
psql -U postgres
```

**In PostgreSQL prompt:**
```sql
-- Create database
CREATE DATABASE class_recording;

-- Create user with password
CREATE USER postgres WITH PASSWORD 'Deepdive';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE class_recording TO postgres;

-- Connect to the database
\c class_recording

-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Exit
\q
```

### 4. Configure Application

Create or update `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=class_recording
DB_USER=postgres
DB_PASSWORD=Deepdive
```

### 5. Install Python Dependencies

```bash
pip install psycopg2-binary python-dotenv
```

### 6. Initialize Database Tables

The application automatically creates tables on first run:

```bash
python api.py
```

Or manually initialize:
```python
from database import init_database
init_database()
```

---

## Database Operations

### Connection Management

**Get Connection:**
```python
from database import get_connection, return_connection

conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recordings")
    results = cursor.fetchall()
finally:
    return_connection(conn)
```

**Connection Pool Status:**
```python
from database import connection_pool

print(f"Min connections: {connection_pool.minconn}")
print(f"Max connections: {connection_pool.maxconn}")
```

### CRUD Operations

#### Create (Insert)
```python
from database import insert_recording

record_id = insert_recording(
    school_name="Springfield High School",
    class_name="10th Grade",
    subject="Physics",
    audio_filename="audio.mp3",
    job_id="job-uuid",
    section="A",
    recording_subject="Quantum Mechanics"
)
```

#### Read (Select)
```python
from database import get_all_recordings, get_recording_by_id

# Get all recordings
recordings = get_all_recordings(limit=10, offset=0)

# Get specific recording
recording = get_recording_by_id(record_id="uuid")

# Get with filters
recording = get_recording_by_id(
    school_name="Springfield High School",
    class_name="10th Grade",
    date="2026-03-07"
)
```

#### Update
```python
from database import update_combined_md

update_combined_md(
    job_id="job-uuid",
    combined_md="# Study Materials..."
)
```

#### Delete
```python
from database import delete_recording, delete_all_recordings

# Delete single recording
success = delete_recording(record_id="uuid")

# Delete all recordings
deleted_count = delete_all_recordings()
```

### Audit Logging

All operations automatically log to `audit_logs`:

```python
from database import log_activity

log_activity(
    recording_data={
        'date': '2026-03-07',
        'school_name': 'Springfield High School',
        'class': '10th Grade',
        'section': 'A',
        'subject': 'Physics',
        'recording_subject': 'Quantum Mechanics',
        'audio_filename': 'audio.mp3',
        'job_id': 'job-uuid',
        'created_at': datetime.now()
    },
    activity='CREATED'
)
```

### Query Audit Logs

```python
from database import get_audit_logs

# Get all logs
logs = get_audit_logs(limit=100, offset=0)

# Filter by activity
logs = get_audit_logs(activity='CREATED', limit=50)

# Filter by school and date
logs = get_audit_logs(
    school_name='Springfield High School',
    date='2026-03-07'
)
```

---

## SQL Queries

### Common Queries

#### Get All Recordings
```sql
SELECT id, date, school_name, class, section, subject, 
       recording_subject, audio_filename, job_id, created_at
FROM recordings
ORDER BY created_at DESC
LIMIT 100 OFFSET 0;
```

#### Get Recording by ID
```sql
SELECT id, date, school_name, class, section, subject,
       recording_subject, audio_filename, combined_md, job_id, created_at
FROM recordings
WHERE id = 'uuid-here';
```

#### Get Recordings with Filters
```sql
SELECT id, date, school_name, class, section, subject,
       recording_subject, audio_filename, job_id, created_at
FROM recordings
WHERE school_name = 'Springfield High School'
  AND class = '10th Grade'
  AND date = '2026-03-07'
ORDER BY created_at DESC;
```

#### Get Audit Logs
```sql
SELECT id, date, school_name, class, section, subject,
       recording_subject, audio_filename, job_id, activity,
       activity_timestamp, created_at
FROM audit_logs
WHERE activity = 'CREATED'
ORDER BY activity_timestamp DESC
LIMIT 100;
```

#### Count Recordings by School
```sql
SELECT school_name, COUNT(*) as total_recordings
FROM recordings
GROUP BY school_name
ORDER BY total_recordings DESC;
```

#### Count Activities by Type
```sql
SELECT activity, COUNT(*) as count
FROM audit_logs
GROUP BY activity
ORDER BY count DESC;
```

#### Get Recent Activities
```sql
SELECT activity, school_name, class, activity_timestamp
FROM audit_logs
ORDER BY activity_timestamp DESC
LIMIT 20;
```

---

## Backup and Restore

### Backup Database

#### Full Database Backup
```bash
# Backup to SQL file
pg_dump -h localhost -U postgres class_recording > backup_$(date +%Y%m%d).sql

# Backup with compression
pg_dump -h localhost -U postgres class_recording | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup specific tables
pg_dump -h localhost -U postgres -t recordings -t audit_logs class_recording > tables_backup.sql
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/class_recording"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U postgres class_recording | gzip > $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

### Restore Database

#### Restore from Backup
```bash
# Restore from SQL file
psql -h localhost -U postgres class_recording < backup_20260307.sql

# Restore from compressed backup
gunzip -c backup_20260307.sql.gz | psql -h localhost -U postgres class_recording

# Drop and recreate database before restore
dropdb -h localhost -U postgres class_recording
createdb -h localhost -U postgres class_recording
psql -h localhost -U postgres class_recording < backup_20260307.sql
```

---

## Monitoring & Maintenance

### Database Size

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('class_recording')) AS database_size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Active Connections

```sql
-- View active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'class_recording';

-- Count connections by state
SELECT state, COUNT(*) 
FROM pg_stat_activity 
WHERE datname = 'class_recording'
GROUP BY state;
```

### Table Statistics

```sql
-- View table statistics
SELECT 
    schemaname,
    tablename,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### Index Usage

```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Vacuum and Analyze

```sql
-- Vacuum tables
VACUUM VERBOSE recordings;
VACUUM VERBOSE audit_logs;

-- Analyze tables
ANALYZE recordings;
ANALYZE audit_logs;

-- Full vacuum (requires exclusive lock)
VACUUM FULL recordings;
```

---

## Performance Optimization

### Recommended Indexes

```sql
-- Recordings table indexes
CREATE INDEX IF NOT EXISTS idx_recordings_date ON recordings(date);
CREATE INDEX IF NOT EXISTS idx_recordings_school ON recordings(school_name);
CREATE INDEX IF NOT EXISTS idx_recordings_class ON recordings(class);
CREATE INDEX IF NOT EXISTS idx_recordings_created_at ON recordings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recordings_job_id ON recordings(job_id);

-- Audit logs table indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(activity_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_activity ON audit_logs(activity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_job_id ON audit_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_school ON audit_logs(school_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date ON audit_logs(date);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_recordings_school_class_date 
ON recordings(school_name, class, date);

CREATE INDEX IF NOT EXISTS idx_audit_logs_activity_timestamp 
ON audit_logs(activity, activity_timestamp DESC);
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

### Query Optimization

```sql
-- Use EXPLAIN to analyze queries
EXPLAIN ANALYZE
SELECT * FROM recordings
WHERE school_name = 'Springfield High School'
  AND date = '2026-03-07';

-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Security Best Practices

### 1. Password Security

```bash
# Change default password
ALTER USER postgres WITH PASSWORD 'your_strong_password_here';
```

### 2. Connection Security

```sql
-- Limit connections by IP
# Edit pg_hba.conf
host    class_recording    postgres    127.0.0.1/32    md5
host    class_recording    postgres    10.0.0.0/8      md5
```

### 3. User Permissions

```sql
-- Create read-only user
CREATE USER readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE class_recording TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Create application user with limited permissions
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT CONNECT ON DATABASE class_recording TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON recordings TO app_user;
GRANT SELECT, INSERT ON audit_logs TO app_user;
```

### 4. SSL/TLS Encryption

```bash
# Enable SSL in postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

### 5. Audit Logging

```sql
-- Enable PostgreSQL audit logging
# Add to postgresql.conf
log_statement = 'all'
log_connections = on
log_disconnections = on
log_duration = on
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to PostgreSQL

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Test connection
psql -h localhost -U postgres -d class_recording
```

### Permission Issues

**Problem:** Permission denied for database

**Solutions:**
```sql
-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE class_recording TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

### Port Already in Use

**Problem:** Port 5432 already in use

**Solutions:**
```bash
# Check what's using the port
sudo lsof -i :5432

# Change port in postgresql.conf
port = 5433

# Update .env file
DB_PORT=5433
```

### Out of Connections

**Problem:** Too many connections

**Solutions:**
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Increase max connections in postgresql.conf
max_connections = 200

-- Restart PostgreSQL
sudo service postgresql restart
```

### Slow Queries

**Problem:** Queries are slow

**Solutions:**
```sql
-- Add missing indexes
CREATE INDEX idx_name ON table_name(column_name);

-- Vacuum and analyze
VACUUM ANALYZE recordings;
VACUUM ANALYZE audit_logs;

-- Check query plan
EXPLAIN ANALYZE SELECT * FROM recordings WHERE ...;
```

---

## Production Deployment

### Recommended Configuration

```bash
# postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Managed Database Services

For production, consider using managed PostgreSQL services:

- **AWS RDS for PostgreSQL**
- **Google Cloud SQL for PostgreSQL**
- **Azure Database for PostgreSQL**
- **DigitalOcean Managed Databases**
- **Heroku Postgres**

### High Availability

```sql
-- Set up streaming replication
-- On primary server
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';

-- Configure pg_hba.conf
host replication replicator standby_ip/32 md5

-- On standby server
# recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=primary_ip port=5432 user=replicator password=repl_password'
```

---

## Migration Guide

### From SQLite to PostgreSQL

```python
# Export from SQLite
import sqlite3
import psycopg2

# Connect to SQLite
sqlite_conn = sqlite3.connect('recordings.db')
sqlite_cursor = sqlite_conn.cursor()

# Connect to PostgreSQL
pg_conn = psycopg2.connect(
    host='localhost',
    database='class_recording',
    user='postgres',
    password='Deepdive'
)
pg_cursor = pg_conn.cursor()

# Migrate recordings
sqlite_cursor.execute("SELECT * FROM recordings")
for row in sqlite_cursor.fetchall():
    pg_cursor.execute("""
        INSERT INTO recordings VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, row)

pg_conn.commit()
print("Migration completed!")
```

---

## Reference

### PostgreSQL Documentation
- Official Docs: https://www.postgresql.org/docs/
- psycopg2 Docs: https://www.psycopg.org/docs/

### Useful Commands

```bash
# PostgreSQL service management
sudo service postgresql start
sudo service postgresql stop
sudo service postgresql restart
sudo service postgresql status

# Database operations
createdb -U postgres class_recording
dropdb -U postgres class_recording
psql -U postgres -d class_recording

# User management
createuser -U postgres username
dropuser -U postgres username
```

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✅
