# API Documentation - Class Recording API

Complete API reference for the Class Recording processing service.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployment, implement API key authentication or OAuth2.

## Content Types

- **Request**: `multipart/form-data` (for file uploads), `application/json`
- **Response**: `application/json`, `text/plain` (for markdown endpoints)

## Rate Limiting

No rate limiting is currently implemented. Recommended for production: 100 requests per minute per IP.

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| POST | `/process` | Upload and process audio file |
| GET | `/status/{job_id}` | Check job processing status |
| GET | `/result/{job_id}/markdown` | Get result as markdown |
| GET | `/recordings` | List all recordings with filters |
| GET | `/recordings/{record_id}/markdown` | Get recording by ID as markdown |
| GET | `/recordings/markdown` | Get recording by filters as markdown |
| DELETE | `/recordings/{record_id}` | Delete recording by ID or filters |
| DELETE | `/recordings` | Delete all recordings |
| GET | `/audit-logs` | View audit logs with filters |

---

## 1. Root Endpoint

### GET `/`

Get API information and available endpoints.

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "message": "Class Recording API",
  "version": "1.0.0",
  "endpoints": {
    "POST /process": "Upload and process audio file",
    "GET /status/{job_id}": "Check job status",
    "GET /result/{job_id}/markdown": "Get processing result in markdown",
    "GET /recordings": "List all recordings with optional filters",
    "GET /recordings/{record_id}/markdown": "Get recording markdown with optional filters",
    "DELETE /recordings/{record_id}": "Delete a recording with optional filters",
    "DELETE /recordings": "Delete all recordings"
  }
}
```

**Status Codes:**
- `200 OK`: Success

---

## 2. Process Audio File

### POST `/process`

Upload and process an audio file through the complete pipeline.

**Request:**
```http
POST /process HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="audio_file"; filename="lecture.mp3"
Content-Type: audio/mpeg

[binary audio data]
--boundary
Content-Disposition: form-data; name="school_name"

Springfield High School
--boundary
Content-Disposition: form-data; name="class_name"

10th Grade
--boundary
Content-Disposition: form-data; name="subject"

Physics
--boundary
Content-Disposition: form-data; name="section"

A
--boundary
Content-Disposition: form-data; name="recording_subject"

Quantum Mechanics
--boundary--
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| audio_file | file | Yes | Audio/video file to process (mp3, wav, m4a, etc.) |
| school_name | string | Yes | Name of the school |
| class_name | string | Yes | Class/Grade (e.g., "10th Grade", "12th") |
| subject | string | No | Subject name (e.g., "Physics", "Mathematics") |
| section | string | No | Section (e.g., "A", "B") |
| recording_subject | string | No | Specific topic of the recording |

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "Job created successfully. Record ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Status Codes:**
- `200 OK`: Job created successfully
- `400 Bad Request`: Invalid parameters or file format
- `500 Internal Server Error`: Server error during processing

**Example (cURL):**
```bash
curl -X POST "http://localhost:8000/process" \
  -F "audio_file=@lecture.mp3" \
  -F "school_name=Springfield High School" \
  -F "class_name=10th Grade" \
  -F "subject=Physics" \
  -F "section=A" \
  -F "recording_subject=Quantum Mechanics"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/process"
files = {"audio_file": open("lecture.mp3", "rb")}
data = {
    "school_name": "Springfield High School",
    "class_name": "10th Grade",
    "subject": "Physics",
    "section": "A",
    "recording_subject": "Quantum Mechanics"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

---

## 3. Check Job Status

### GET `/status/{job_id}`

Check the current status of a processing job.

**Request:**
```http
GET /status/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Host: localhost:8000
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response (Processing):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": "Generating study materials...",
  "error": null
}
```

**Response (Completed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": "Processing complete",
  "error": null
}
```

**Response (Failed):**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "failed",
  "progress": null,
  "error": "Error message here"
}
```

**Status Values:**
- `pending`: Job is queued
- `processing`: Job is currently being processed
- `completed`: Job finished successfully
- `failed`: Job encountered an error
- `not_found`: Job ID doesn't exist

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Job ID not found

**Example (cURL):**
```bash
curl "http://localhost:8000/status/123e4567-e89b-12d3-a456-426614174000"
```

**Example (Python):**
```python
import requests

job_id = "123e4567-e89b-12d3-a456-426614174000"
response = requests.get(f"http://localhost:8000/status/{job_id}")
print(response.json())
```

---

## 4. Get Result as Markdown

### GET `/result/{job_id}/markdown`

Get the processed result as plain text markdown.

**Request:**
```http
GET /result/123e4567-e89b-12d3-a456-426614174000/markdown HTTP/1.1
Host: localhost:8000
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | UUID of the job |

**Response:**
```markdown
# Class Tutor – Combined Output

## 1A – Structured Class Notes

[Generated notes content...]

## 1B – Likely Misconceptions

[Misconceptions content...]

## 2 – Practice & Challenges

[Practice questions content...]

## 3 – Real-life Applications & Resources

[Resources content...]

## 4 – Actions & Feedback

[Study plan content...]

## 5 – Teacher Feedback

[Teacher feedback content...]
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Job not completed yet
- `404 Not Found`: Job or result not found

**Example (cURL):**
```bash
curl "http://localhost:8000/result/123e4567-e89b-12d3-a456-426614174000/markdown" \
  -o study_materials.md
```

**Example (Python):**
```python
import requests

job_id = "123e4567-e89b-12d3-a456-426614174000"
response = requests.get(f"http://localhost:8000/result/{job_id}/markdown")

with open("study_materials.md", "w", encoding="utf-8") as f:
    f.write(response.text)
```

---

## 5. List All Recordings

### GET `/recordings`

Get a paginated list of all recordings with optional filters.

**Request:**
```http
GET /recordings?limit=10&offset=0&school_name=Springfield%20High%20School&class=10th%20Grade HTTP/1.1
Host: localhost:8000
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 100 | Maximum number of records to return |
| offset | integer | 0 | Number of records to skip |
| school_name | string | - | Filter by school name |
| class | string | - | Filter by class name |
| section | string | - | Filter by section |
| subject | string | - | Filter by subject |
| recording_subject | string | - | Filter by recording subject |
| date | string | - | Filter by date (YYYY-MM-DD) |

**Response:**
```json
{
  "recordings": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "date": "2026-03-07",
      "school_name": "Springfield High School",
      "class": "10th Grade",
      "section": "A",
      "subject": "Physics",
      "recording_subject": "Quantum Mechanics",
      "audio_filename": "123e4567-e89b-12d3-a456-426614174000.mp3",
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2026-03-07T17:45:00"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

**Status Codes:**
- `200 OK`: Success

**Example (cURL):**
```bash
# Get all recordings
curl "http://localhost:8000/recordings"

# Filter by school and class
curl "http://localhost:8000/recordings?school_name=Springfield%20High%20School&class=10th%20Grade"

# Pagination
curl "http://localhost:8000/recordings?limit=20&offset=40"
```

**Example (Python):**
```python
import requests

# Get all recordings
response = requests.get("http://localhost:8000/recordings")
print(response.json())

# With filters
params = {
    "school_name": "Springfield High School",
    "class": "10th Grade",
    "limit": 20
}
response = requests.get("http://localhost:8000/recordings", params=params)
print(response.json())
```

---

## 6. Get Recording by ID (Markdown)

### GET `/recordings/{record_id}/markdown`

Get a specific recording's result in markdown format by ID or filters.

**Request:**
```http
GET /recordings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/markdown HTTP/1.1
Host: localhost:8000
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| record_id | string | UUID of the recording (optional if using filters) |

**Query Parameters (Optional):**

| Parameter | Type | Description |
|-----------|------|-------------|
| school_name | string | Filter by school name |
| class | string | Filter by class name |
| section | string | Filter by section |
| subject | string | Filter by subject |
| recording_subject | string | Filter by recording subject |
| date | string | Filter by date (YYYY-MM-DD) |

**Response:**
```markdown
# Class Tutor – Combined Output

[Full markdown content...]
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Recording not found or result not available

**Example (cURL):**
```bash
# By record_id
curl "http://localhost:8000/recordings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/markdown" \
  -o recording.md

# By record_id with additional filters
curl "http://localhost:8000/recordings/a1b2c3d4/markdown?school_name=Springfield%20High%20School" \
  -o recording.md
```

**Example (Python):**
```python
import requests

# By record_id
record_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
response = requests.get(f"http://localhost:8000/recordings/{record_id}/markdown")

with open("recording.md", "w", encoding="utf-8") as f:
    f.write(response.text)
```

---

## 7. Get Recording by Filters (Markdown)

### GET `/recordings/markdown`

Get a recording's result in markdown format using only filters (no record_id).

**Request:**
```http
GET /recordings/markdown?school_name=Springfield%20High%20School&class=10th%20Grade&date=2026-03-07 HTTP/1.1
Host: localhost:8000
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| school_name | string | Filter by school name |
| class | string | Filter by class name |
| section | string | Filter by section |
| subject | string | Filter by subject |
| recording_subject | string | Filter by recording subject |
| date | string | Filter by date (YYYY-MM-DD) |

**Response:**
```markdown
# Class Tutor – Combined Output

[Full markdown content...]
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Recording not found

**Example (cURL):**
```bash
curl "http://localhost:8000/recordings/markdown?school_name=Springfield%20High%20School&class=10th%20Grade&date=2026-03-07" \
  -o recording.md
```

**Example (Python):**
```python
import requests

params = {
    "school_name": "Springfield High School",
    "class": "10th Grade",
    "date": "2026-03-07"
}
response = requests.get("http://localhost:8000/recordings/markdown", params=params)

with open("recording.md", "w", encoding="utf-8") as f:
    f.write(response.text)
```

---

## 8. Delete Recording

### DELETE `/recordings/{record_id}`

Delete a specific recording by ID or filters.

**Request:**
```http
DELETE /recordings/a1b2c3d4-e5f6-7890-abcd-ef1234567890 HTTP/1.1
Host: localhost:8000
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| record_id | string | UUID of the recording (can be "dummy" if using only filters) |

**Query Parameters (Optional):**

| Parameter | Type | Description |
|-----------|------|-------------|
| school_name | string | Filter by school name |
| class | string | Filter by class name |
| section | string | Filter by section |
| subject | string | Filter by subject |
| recording_subject | string | Filter by recording subject |
| date | string | Filter by date (YYYY-MM-DD) |

**Response:**
```json
{
  "message": "Recording deleted successfully",
  "record_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Status Codes:**
- `200 OK`: Recording deleted successfully
- `404 Not Found`: Recording not found

**Example (cURL):**
```bash
# By record_id
curl -X DELETE "http://localhost:8000/recordings/a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# By filters
curl -X DELETE "http://localhost:8000/recordings/dummy?school_name=Springfield%20High%20School&class=10th%20Grade&date=2026-03-07"
```

**Example (Python):**
```python
import requests

# By record_id
record_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
response = requests.delete(f"http://localhost:8000/recordings/{record_id}")
print(response.json())

# By filters
params = {
    "school_name": "Springfield High School",
    "class": "10th Grade",
    "date": "2026-03-07"
}
response = requests.delete("http://localhost:8000/recordings/dummy", params=params)
print(response.json())
```

---

## 9. Delete All Recordings

### DELETE `/recordings`

Delete all recordings from the database.

**⚠️ WARNING:** This operation cannot be undone!

**Request:**
```http
DELETE /recordings HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "message": "Successfully deleted all recordings",
  "deleted_count": 42
}
```

**Status Codes:**
- `200 OK`: All recordings deleted successfully

**Example (cURL):**
```bash
curl -X DELETE "http://localhost:8000/recordings"
```

**Example (Python):**
```python
import requests

response = requests.delete("http://localhost:8000/recordings")
print(response.json())
```

---

## 10. View Audit Logs

### GET `/audit-logs`

View complete audit trail of all activities performed on recordings.

**Request:**
```http
GET /audit-logs?limit=10&offset=0&activity=CREATED HTTP/1.1
Host: localhost:8000
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 100 | Maximum number of records to return |
| offset | integer | 0 | Number of records to skip |
| school_name | string | - | Filter by school name |
| class | string | - | Filter by class name |
| section | string | - | Filter by section |
| subject | string | - | Filter by subject |
| recording_subject | string | - | Filter by recording subject |
| date | string | - | Filter by date (YYYY-MM-DD) |
| activity | string | - | Filter by activity type |

**Activity Types:**
- `CREATED`: When a recording was created
- `PROCESSED`: When audio processing completed
- `DELETED`: When a recording was deleted
- `DELETED_ALL`: When recordings were deleted in bulk

**Response:**
```json
{
  "logs": [
    {
      "id": "log-uuid-1",
      "date": "2026-03-07",
      "school_name": "Springfield High School",
      "class": "10th Grade",
      "section": "A",
      "subject": "Physics",
      "recording_subject": "Quantum Mechanics",
      "audio_filename": "123e4567.mp3",
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "activity": "CREATED",
      "activity_timestamp": "2026-03-07T17:45:00",
      "created_at": "2026-03-07T17:45:00"
    },
    {
      "id": "log-uuid-2",
      "date": "2026-03-07",
      "school_name": "Springfield High School",
      "class": "10th Grade",
      "section": "A",
      "subject": "Physics",
      "recording_subject": "Quantum Mechanics",
      "audio_filename": "123e4567.mp3",
      "job_id": "123e4567-e89b-12d3-a456-426614174000",
      "activity": "PROCESSED",
      "activity_timestamp": "2026-03-07T17:50:00",
      "created_at": "2026-03-07T17:45:00"
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

**Status Codes:**
- `200 OK`: Success

**Example (cURL):**
```bash
# Get all audit logs
curl "http://localhost:8000/audit-logs"

# Filter by activity type
curl "http://localhost:8000/audit-logs?activity=CREATED"

# Filter by school and date
curl "http://localhost:8000/audit-logs?school_name=Springfield%20High%20School&date=2026-03-07"
```

**Example (Python):**
```python
import requests

# Get all audit logs
response = requests.get("http://localhost:8000/audit-logs")
logs = response.json()["logs"]

# Filter by activity
params = {"activity": "CREATED", "limit": 50}
response = requests.get("http://localhost:8000/audit-logs", params=params)

for log in response.json()["logs"]:
    print(f"{log['activity_timestamp']}: {log['activity']} - {log['school_name']}")
```

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "detail": "Error description here"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters or request format |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error during processing |

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints and their parameters
- Test API calls directly from the browser
- See request/response schemas
- Download OpenAPI specification

---

## Complete Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Step 1: Upload audio file
print("Step 1: Uploading audio file...")
with open("lecture.mp3", "rb") as audio_file:
    files = {"audio_file": audio_file}
    data = {
        "school_name": "Springfield High School",
        "class_name": "10th Grade",
        "subject": "Physics",
        "section": "A",
        "recording_subject": "Quantum Mechanics"
    }
    
    response = requests.post(f"{BASE_URL}/process", files=files, data=data)
    result = response.json()
    job_id = result["job_id"]
    record_id = result["message"].split(": ")[1]
    print(f"✓ Job ID: {job_id}")
    print(f"✓ Record ID: {record_id}")

# Step 2: Poll for completion
print("\nStep 2: Waiting for processing to complete...")
while True:
    response = requests.get(f"{BASE_URL}/status/{job_id}")
    status_data = response.json()
    status = status_data["status"]
    
    print(f"Status: {status} - {status_data.get('progress', '')}")
    
    if status == "completed":
        print("✓ Processing completed!")
        break
    elif status == "failed":
        print(f"✗ Failed: {status_data.get('error')}")
        exit(1)
    
    time.sleep(5)

# Step 3: Download result
print("\nStep 3: Downloading result...")
response = requests.get(f"{BASE_URL}/result/{job_id}/markdown")
with open("study_materials.md", "w", encoding="utf-8") as f:
    f.write(response.text)
print("✓ Saved to study_materials.md")

# Step 4: List recordings
print("\nStep 4: Listing recordings...")
response = requests.get(f"{BASE_URL}/recordings?limit=5")
data = response.json()
print(f"Total recordings: {data['total']}")

# Step 5: View audit logs
print("\nStep 5: Viewing audit logs...")
response = requests.get(f"{BASE_URL}/audit-logs?limit=5")
data = response.json()
for log in data['logs']:
    print(f"  {log['activity_timestamp']}: {log['activity']}")

print("\n✓ Workflow completed successfully!")
```

---

## Best Practices

1. **Polling**: When checking job status, use exponential backoff or fixed intervals (5-10 seconds)
2. **Error Handling**: Always check response status codes and handle errors appropriately
3. **File Size**: Keep audio files under 100MB for optimal performance
4. **Timeouts**: Set appropriate timeouts for long-running operations (5+ minutes)
5. **Filters**: Use specific filters to reduce response size and improve performance
6. **Pagination**: Use limit and offset for large result sets
7. **Audit Logs**: Regularly review audit logs for compliance and monitoring

---

## Rate Limiting (Recommended for Production)

Implement rate limiting to prevent abuse:

```python
# Example rate limiting configuration
RATE_LIMIT = "100/minute"  # 100 requests per minute per IP
```

---

## CORS Configuration

For production, configure CORS to allow only specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✅
