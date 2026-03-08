"""
PostgreSQL Database operations for class recording management
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

# Load environment variables
load_dotenv()

# PostgreSQL connection configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'class_recording'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Deepdive')
}

# Connection pool
connection_pool = None


def init_connection_pool():
    """Initialize the connection pool."""
    global connection_pool
    if connection_pool is None:
        connection_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            **DB_CONFIG
        )


def get_connection():
    """Get a connection from the pool."""
    if connection_pool is None:
        init_connection_pool()
    return connection_pool.getconn()


def return_connection(conn):
    """Return a connection to the pool."""
    if connection_pool:
        connection_pool.putconn(conn)


def init_database():
    """Initialize the database with the recordings and audit_logs tables."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create recordings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordings (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                school_name TEXT NOT NULL,
                class TEXT NOT NULL,
                section TEXT,
                subject TEXT,
                recording_subject TEXT,
                audio_filename TEXT NOT NULL,
                combined_md TEXT,
                job_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                school_name TEXT NOT NULL,
                class TEXT NOT NULL,
                section TEXT,
                subject TEXT,
                recording_subject TEXT,
                audio_filename TEXT NOT NULL,
                combined_md TEXT,
                job_id TEXT,
                activity TEXT NOT NULL,
                activity_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP
            )
        """)
        
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def log_activity(recording_data: Dict[str, Any], activity: str):
    """
    Log an activity to the audit_logs table.
    
    Args:
        recording_data: Dictionary containing recording information
        activity: Description of the activity (e.g., 'CREATED', 'DELETED', 'PROCESSED')
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        log_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO audit_logs (
                id, date, school_name, class, section, subject, recording_subject,
                audio_filename, combined_md, job_id, activity, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            log_id,
            recording_data.get('date'),
            recording_data.get('school_name'),
            recording_data.get('class'),
            recording_data.get('section'),
            recording_data.get('subject'),
            recording_data.get('recording_subject'),
            recording_data.get('audio_filename'),
            recording_data.get('combined_md'),
            recording_data.get('job_id'),
            activity,
            recording_data.get('created_at')
        ))
        
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def insert_recording(
    school_name: str,
    class_name: str,
    subject: Optional[str],
    audio_filename: str,
    job_id: str,
    section: Optional[str] = None,
    recording_subject: Optional[str] = None
) -> str:
    """
    Insert a new recording entry into the database.
    
    Returns:
        str: The UUID of the inserted record
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        record_id = str(uuid.uuid4())
        current_date = datetime.now().strftime("%Y-%m-%d")
        created_at = datetime.now()
        
        cursor.execute("""
            INSERT INTO recordings (id, date, school_name, class, section, subject, recording_subject, audio_filename, job_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (record_id, current_date, school_name, class_name, section, subject, recording_subject, audio_filename, job_id, created_at))
        
        conn.commit()
        
        # Log the activity
        log_activity({
            'date': current_date,
            'school_name': school_name,
            'class': class_name,
            'section': section,
            'subject': subject,
            'recording_subject': recording_subject,
            'audio_filename': audio_filename,
            'job_id': job_id,
            'created_at': created_at
        }, 'CREATED')
        
        return record_id
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def update_combined_md(job_id: str, combined_md: str):
    """Update the combined_md field for a specific job."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the recording first
        cursor.execute("""
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, job_id, created_at
            FROM recordings
            WHERE job_id = %s
        """, (job_id,))
        
        recording = cursor.fetchone()
        
        # Update the recording
        cursor.execute("""
            UPDATE recordings
            SET combined_md = %s
            WHERE job_id = %s
        """, (combined_md, job_id))
        
        conn.commit()
        
        # Log the activity
        if recording:
            log_activity({
                'date': recording['date'],
                'school_name': recording['school_name'],
                'class': recording['class'],
                'section': recording['section'],
                'subject': recording['subject'],
                'recording_subject': recording['recording_subject'],
                'audio_filename': recording['audio_filename'],
                'combined_md': combined_md,
                'job_id': job_id,
                'created_at': recording['created_at']
            }, 'PROCESSED')
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def get_recording_by_job_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Get a recording by job_id."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, combined_md, job_id, created_at
            FROM recordings
            WHERE job_id = %s
        """, (job_id,))
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    finally:
        if conn:
            return_connection(conn)


def get_all_recordings(
    limit: int = 100,
    offset: int = 0,
    school_name: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    subject: Optional[str] = None,
    recording_subject: Optional[str] = None,
    date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all recordings with pagination and optional filters."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build dynamic query with filters
        query = """
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, job_id, created_at
            FROM recordings
            WHERE 1=1
        """
        params = []
        
        if school_name:
            query += " AND school_name = %s"
            params.append(school_name)
        
        if class_name:
            query += " AND class = %s"
            params.append(class_name)
        
        if section:
            query += " AND section = %s"
            params.append(section)
        
        if subject:
            query += " AND subject = %s"
            params.append(subject)
        
        if recording_subject:
            query += " AND recording_subject = %s"
            params.append(recording_subject)
        
        if date:
            query += " AND date = %s"
            params.append(date)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    finally:
        if conn:
            return_connection(conn)


def get_recording_by_id(
    record_id: Optional[str] = None,
    school_name: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    subject: Optional[str] = None,
    recording_subject: Optional[str] = None,
    date: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get a recording by ID or other optional filters."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build dynamic query with filters
        query = """
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, combined_md, job_id, created_at
            FROM recordings
            WHERE 1=1
        """
        params = []
        
        if record_id:
            query += " AND id = %s"
            params.append(record_id)
        
        if school_name:
            query += " AND school_name = %s"
            params.append(school_name)
        
        if class_name:
            query += " AND class = %s"
            params.append(class_name)
        
        if section:
            query += " AND section = %s"
            params.append(section)
        
        if subject:
            query += " AND subject = %s"
            params.append(subject)
        
        if recording_subject:
            query += " AND recording_subject = %s"
            params.append(recording_subject)
        
        if date:
            query += " AND date = %s"
            params.append(date)
        
        query += " LIMIT 1"
        
        cursor.execute(query, params)
        
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
        
    finally:
        if conn:
            return_connection(conn)


def delete_recording(record_id: str) -> bool:
    """
    Delete a recording by ID.
    
    Returns:
        bool: True if deleted, False if not found
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the recording first for logging
        cursor.execute("""
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, combined_md, job_id, created_at
            FROM recordings
            WHERE id = %s
        """, (record_id,))
        
        recording = cursor.fetchone()
        
        # Delete the recording
        cursor.execute("""
            DELETE FROM recordings
            WHERE id = %s
        """, (record_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
        
        # Log the activity
        if deleted and recording:
            log_activity(dict(recording), 'DELETED')
        
        return deleted
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def delete_all_recordings() -> int:
    """
    Delete all recordings from the database.
    
    Returns:
        int: Number of records deleted
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all recordings first for logging
        cursor.execute("""
            SELECT id, date, school_name, class, section, subject, recording_subject, audio_filename, combined_md, job_id, created_at
            FROM recordings
        """)
        
        recordings = cursor.fetchall()
        
        # Delete all recordings
        cursor.execute("DELETE FROM recordings")
        
        conn.commit()
        deleted_count = cursor.rowcount
        
        # Log the activity for each deleted recording
        for recording in recordings:
            log_activity(dict(recording), 'DELETED_ALL')
        
        return deleted_count
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    school_name: Optional[str] = None,
    class_name: Optional[str] = None,
    section: Optional[str] = None,
    subject: Optional[str] = None,
    recording_subject: Optional[str] = None,
    date: Optional[str] = None,
    activity: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get audit logs with pagination and optional filters."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build dynamic query with filters
        query = """
            SELECT id, date, school_name, class, section, subject, recording_subject, 
                   audio_filename, job_id, activity, activity_timestamp, created_at
            FROM audit_logs
            WHERE 1=1
        """
        params = []
        
        if school_name:
            query += " AND school_name = %s"
            params.append(school_name)
        
        if class_name:
            query += " AND class = %s"
            params.append(class_name)
        
        if section:
            query += " AND section = %s"
            params.append(section)
        
        if subject:
            query += " AND subject = %s"
            params.append(subject)
        
        if recording_subject:
            query += " AND recording_subject = %s"
            params.append(recording_subject)
        
        if date:
            query += " AND date = %s"
            params.append(date)
        
        if activity:
            query += " AND activity = %s"
            params.append(activity)
        
        query += " ORDER BY activity_timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    finally:
        if conn:
            return_connection(conn)


# Initialize database on module import
init_database()
