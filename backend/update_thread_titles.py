"""
Script to update existing thread titles with meaningful names
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.database import ChatThread, ChatHistory
from app.api.threads import generate_thread_title
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_thread_titles():
    """Update all thread titles based on latest conversation"""
    db: Session = SessionLocal()
    
    try:
        # Get all threads
        threads = db.query(ChatThread).all()
        
        logger.info(f"Found {len(threads)} threads to update")
        
        for thread in threads:
            try:
                # Get last message from this thread (most recent conversation)
                last_message = db.query(ChatHistory).filter(
                    ChatHistory.thread_id == thread.id
                ).order_by(ChatHistory.created_at.desc()).first()
                
                if last_message:
                    # Generate new title based on last message
                    new_title = await generate_thread_title(last_message.message)
                    
                    # Update thread
                    thread.title = new_title
                    db.commit()
                    
                    logger.info(f"Updated thread {thread.id}: '{new_title}'")
                else:
                    logger.warning(f"Thread {thread.id} has no messages, skipping")
                    
            except Exception as e:
                logger.error(f"Error updating thread {thread.id}: {str(e)}")
                db.rollback()
                continue
        
        logger.info("Thread title update complete!")
        
    except Exception as e:
        logger.error(f"Error in update process: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(update_thread_titles())
