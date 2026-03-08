"""
FastAPI application for class recording processing
"""
import uuid
import shutil
from pathlib import Path
from typing import Optional, Annotated
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from models import (
    JobResponse,
    JobStatusResponse,
    JobResultResponse,
    RecordingResponse,
    RecordingsListResponse,
    DeleteAllResponse,
    AuditLogResponse,
    AuditLogsListResponse
)
from database import (
    insert_recording,
    get_recording_by_job_id,
    get_all_recordings,
    get_recording_by_id,
    delete_recording,
    delete_all_recordings,
    get_audit_logs
)
from worker import start_job, get_job_status


# Initialize FastAPI app
app = FastAPI(
    title="Class Recording API",
    description="API for processing class audio recordings and generating study materials",
    version="1.0.0"
)

# Add CORS middleware to handle large file uploads
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
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


@app.post("/process", response_model=JobResponse)
async def process_audio(
    audio_file: UploadFile = File(..., description="Audio file to process"),
    school_name: str = Form(..., description="School name"),
    subject: Optional[str] = Form(None, description="Subject name (optional)"),
    class_name: str = Form(..., description="Class/Grade (e.g., 10th, 12th)"),
    section: Optional[str] = Form(None, description="Section (optional)"),
    recording_subject: Optional[str] = Form(None, description="Recording subject (optional)")
):
    """
    Upload and process an audio file.
    
    This endpoint:
    1. Saves the uploaded audio file
    2. Creates a database entry
    3. Starts a background job for processing
    4. Returns job_id for tracking
    
    The processing includes:
    - Audio transcription
    - Study notes generation
    - Misconceptions detection
    - Practice questions creation
    - Resource recommendations
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file with job_id in filename
        file_extension = Path(audio_file.filename).suffix
        audio_filename = f"{job_id}{file_extension}"
        audio_path = UPLOADS_DIR / audio_filename
        
        # Save file to disk
        with audio_path.open("wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Insert record into database
        record_id = insert_recording(
            school_name=school_name,
            class_name=class_name,
            subject=subject,
            audio_filename=audio_filename,
            job_id=job_id,
            section=section,
            recording_subject=recording_subject
        )
        
        # Start background processing job
        start_job(
            job_id=job_id,
            audio_path=str(audio_path)
        )
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message=f"Job created successfully. Record ID: {record_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/status/{job_id}", response_model=JobStatusResponse)
def get_status(job_id: str):
    """
    Check the status of a processing job.
    
    Possible statuses:
    - pending: Job is queued
    - processing: Job is currently being processed
    - completed: Job finished successfully
    - failed: Job encountered an error
    - not_found: Job ID doesn't exist
    """
    job_status = get_job_status(job_id)
    
    if job_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_status["status"],
        progress=job_status.get("progress"),
        error=job_status.get("error")
    )


@app.get("/result/{job_id}/markdown", response_class=PlainTextResponse)
def get_result_markdown(job_id: str):
    """
    Get the result as plain markdown text (useful for direct download).
    """
    job_status = get_job_status(job_id)
    
    if job_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {job_status['status']}"
        )
    
    recording = get_recording_by_job_id(job_id)
    
    if not recording or not recording.get("combined_md"):
        raise HTTPException(status_code=404, detail="Result not found")
    
    return recording["combined_md"]


@app.get("/recordings", response_model=RecordingsListResponse)
def list_recordings(
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    school_name: Optional[str] = Query(None, description="Filter by school name"),
    class_name: Optional[str] = Query(None, description="Filter by class name", alias="class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    recording_subject: Optional[str] = Query(None, description="Filter by recording subject"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """
    List all recordings with pagination and optional filters.
    
    Args:
        limit: Maximum number of records to return (default: 100)
        offset: Number of records to skip (default: 0)
        school_name: Filter by school name (optional)
        class_name: Filter by class name (optional)
        section: Filter by section (optional)
        subject: Filter by subject (optional)
        recording_subject: Filter by recording subject (optional)
        date: Filter by date in YYYY-MM-DD format (optional)
    """
    recordings = get_all_recordings(
        limit=limit,
        offset=offset,
        school_name=school_name,
        class_name=class_name,
        section=section,
        subject=subject,
        recording_subject=recording_subject,
        date=date
    )
    
    # Convert to response model
    recording_responses = [
        RecordingResponse(
            id=rec["id"],
            date=rec["date"],
            school_name=rec["school_name"],
            class_name=rec["class"],
            section=rec["section"],
            subject=rec["subject"],
            recording_subject=rec["recording_subject"],
            audio_filename=rec["audio_filename"],
            job_id=rec["job_id"],
            created_at=str(rec["created_at"]) if rec.get("created_at") else None
        )
        for rec in recordings
    ]
    
    return RecordingsListResponse(
        recordings=recording_responses,
        total=len(recording_responses),
        limit=limit,
        offset=offset
    )


@app.get("/recordings/{record_id}/markdown", response_class=PlainTextResponse)
def get_recording_markdown(
    record_id: Optional[str] = None,
    school_name: Optional[str] = Query(None, description="Filter by school name"),
    class_name: Optional[str] = Query(None, description="Filter by class name", alias="class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    recording_subject: Optional[str] = Query(None, description="Filter by recording subject"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """
    Get a specific recording in markdown format.
    Can search by record_id or any combination of optional parameters.
    record_id is now optional - you can search using any combination of filters.
    """
    recording = get_recording_by_id(
        record_id=record_id,
        school_name=school_name,
        class_name=class_name,
        section=section,
        subject=subject,
        recording_subject=recording_subject,
        date=date
    )
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    if not recording.get("combined_md"):
        raise HTTPException(status_code=404, detail="Recording result not available yet")
    
    return recording["combined_md"]


@app.get("/recordings/markdown", response_class=PlainTextResponse)
def get_recording_markdown_without_id(
    school_name: Optional[str] = Query(None, description="Filter by school name"),
    class_name: Optional[str] = Query(None, description="Filter by class name", alias="class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    recording_subject: Optional[str] = Query(None, description="Filter by recording subject"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """
    Get a specific recording in markdown format without record_id.
    Search using any combination of optional parameters.
    """
    recording = get_recording_by_id(
        record_id=None,
        school_name=school_name,
        class_name=class_name,
        section=section,
        subject=subject,
        recording_subject=recording_subject,
        date=date
    )
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    if not recording.get("combined_md"):
        raise HTTPException(status_code=404, detail="Recording result not available yet")
    
    return recording["combined_md"]


@app.delete("/recordings/{record_id}")
def delete_recording_endpoint(
    record_id: Optional[str] = None,
    school_name: Optional[str] = Query(None, description="Filter by school name"),
    class_name: Optional[str] = Query(None, description="Filter by class name", alias="class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    recording_subject: Optional[str] = Query(None, description="Filter by recording subject"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)")
):
    """
    Delete a specific recording.
    Can search by record_id or any combination of optional parameters.
    """
    # First find the recording
    recording = get_recording_by_id(
        record_id=record_id,
        school_name=school_name,
        class_name=class_name,
        section=section,
        subject=subject,
        recording_subject=recording_subject,
        date=date
    )
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Delete using the found record's ID
    success = delete_recording(recording["id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return {"message": "Recording deleted successfully", "record_id": recording["id"]}


@app.delete("/recordings", response_model=DeleteAllResponse)
def delete_all_recordings_endpoint():
    """
    Delete all recordings from the database.
    
    WARNING: This operation cannot be undone!
    """
    deleted_count = delete_all_recordings()
    
    return DeleteAllResponse(
        message=f"Successfully deleted all recordings",
        deleted_count=deleted_count
    )


@app.get("/audit-logs", response_model=AuditLogsListResponse)
def list_audit_logs(
    limit: int = Query(100, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    school_name: Optional[str] = Query(None, description="Filter by school name"),
    class_name: Optional[str] = Query(None, description="Filter by class name", alias="class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    recording_subject: Optional[str] = Query(None, description="Filter by recording subject"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    activity: Optional[str] = Query(None, description="Filter by activity type (CREATED, PROCESSED, DELETED, DELETED_ALL)")
):
    """
    List all audit logs with pagination and optional filters.
    
    This endpoint shows the history of all activities performed on recordings:
    - CREATED: When a recording was created
    - PROCESSED: When audio processing completed
    - DELETED: When a recording was deleted
    - DELETED_ALL: When recordings were deleted in bulk
    
    Args:
        limit: Maximum number of records to return (default: 100)
        offset: Number of records to skip (default: 0)
        school_name: Filter by school name (optional)
        class_name: Filter by class name (optional)
        section: Filter by section (optional)
        subject: Filter by subject (optional)
        recording_subject: Filter by recording subject (optional)
        date: Filter by date in YYYY-MM-DD format (optional)
        activity: Filter by activity type (optional)
    """
    logs = get_audit_logs(
        limit=limit,
        offset=offset,
        school_name=school_name,
        class_name=class_name,
        section=section,
        subject=subject,
        recording_subject=recording_subject,
        date=date,
        activity=activity
    )
    
    # Convert to response model
    log_responses = [
        AuditLogResponse(
            id=log["id"],
            date=log["date"],
            school_name=log["school_name"],
            class_name=log["class"],
            section=log["section"],
            subject=log["subject"],
            recording_subject=log["recording_subject"],
            audio_filename=log["audio_filename"],
            job_id=log["job_id"],
            activity=log["activity"],
            activity_timestamp=str(log["activity_timestamp"]),
            created_at=str(log["created_at"]) if log.get("created_at") else None
        )
        for log in logs
    ]
    
    return AuditLogsListResponse(
        logs=log_responses,
        total=len(log_responses),
        limit=limit,
        offset=offset
    )


if __name__ == "__main__":
    import uvicorn
    # Increase timeout and request size limits for large file uploads
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=300,  # 5 minutes
        limit_max_requests=1000,
        limit_concurrency=100
    )
