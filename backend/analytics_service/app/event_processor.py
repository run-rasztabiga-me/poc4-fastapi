from datetime import datetime
from sqlalchemy.orm import Session
from . import models, database
import sys
sys.path.append('/app')
from .shared.rabbitmq_client import RabbitMQClient, USERS_EXCHANGE, NOTES_EXCHANGE, ANALYTICS_USERS_QUEUE, ANALYTICS_NOTES_QUEUE
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProcessor:
    """Processes events from RabbitMQ and updates analytics database"""

    def __init__(self):
        self.rabbitmq_client = RabbitMQClient()

    def process_user_event(self, event_data: dict):
        """Process user-related events"""
        db = database.SessionLocal()
        try:
            event_type = event_data.get("event_type")
            user_id = event_data.get("user_id")
            username = event_data.get("username")
            email = event_data.get("email")
            timestamp = datetime.fromisoformat(event_data.get("timestamp").replace("Z", "+00:00"))

            # Store event
            user_event = models.UserEvent(
                event_type=event_type,
                user_id=user_id,
                username=username,
                email=email,
                timestamp=timestamp
            )
            db.add(user_event)

            # Update user statistics
            user_stats = db.query(models.UserStatistics).filter(
                models.UserStatistics.user_id == user_id
            ).first()

            if not user_stats:
                user_stats = models.UserStatistics(
                    user_id=user_id,
                    registered_at=timestamp if event_type == "user.registered" else None
                )
                db.add(user_stats)

            # Update statistics based on event type
            if event_type == "user.registered":
                user_stats.registered_at = timestamp

            elif event_type == "user.logged_in":
                user_stats.total_logins += 1
                user_stats.last_login = timestamp

            user_stats.last_activity = timestamp

            db.commit()
            logger.info(f"Processed user event: {event_type} for user {user_id}")

        except Exception as e:
            logger.error(f"Error processing user event: {e}")
            db.rollback()
        finally:
            db.close()

    def process_note_event(self, event_data: dict):
        """Process note-related events"""
        db = database.SessionLocal()
        try:
            event_type = event_data.get("event_type")
            note_id = event_data.get("note_id")
            user_id = event_data.get("user_id")
            title = event_data.get("title")
            timestamp = datetime.fromisoformat(event_data.get("timestamp").replace("Z", "+00:00"))

            # Store event
            note_event = models.NoteEvent(
                event_type=event_type,
                note_id=note_id,
                user_id=user_id,
                title=title,
                timestamp=timestamp
            )
            db.add(note_event)

            # Update user statistics
            user_stats = db.query(models.UserStatistics).filter(
                models.UserStatistics.user_id == user_id
            ).first()

            if not user_stats:
                user_stats = models.UserStatistics(user_id=user_id)
                db.add(user_stats)

            # Update statistics based on event type
            if event_type == "note.created":
                user_stats.total_notes += 1
                user_stats.total_notes_created += 1

            elif event_type == "note.updated":
                user_stats.total_notes_updated += 1

            elif event_type == "note.deleted":
                user_stats.total_notes -= 1
                user_stats.total_notes_deleted += 1

            user_stats.last_activity = timestamp

            db.commit()
            logger.info(f"Processed note event: {event_type} for note {note_id}")

        except Exception as e:
            logger.error(f"Error processing note event: {e}")
            db.rollback()
        finally:
            db.close()

    def start_consuming_users(self):
        """Start consuming user events"""
        logger.info("Starting to consume user events...")
        try:
            self.rabbitmq_client.connect()
            self.rabbitmq_client.consume(
                queue_name=ANALYTICS_USERS_QUEUE,
                callback=self.process_user_event
            )
        except KeyboardInterrupt:
            logger.info("Stopped consuming user events")
        except Exception as e:
            logger.error(f"Error consuming user events: {e}")
        finally:
            self.rabbitmq_client.close()

    def start_consuming_notes(self):
        """Start consuming note events"""
        logger.info("Starting to consume note events...")
        try:
            self.rabbitmq_client.connect()
            self.rabbitmq_client.consume(
                queue_name=ANALYTICS_NOTES_QUEUE,
                callback=self.process_note_event
            )
        except KeyboardInterrupt:
            logger.info("Stopped consuming note events")
        except Exception as e:
            logger.error(f"Error consuming note events: {e}")
        finally:
            self.rabbitmq_client.close()

    def start_all_consumers(self):
        """Start all event consumers in separate threads"""
        # Create separate RabbitMQ clients for each consumer
        users_processor = EventProcessor()
        notes_processor = EventProcessor()

        # Start consumers in separate threads
        users_thread = threading.Thread(target=users_processor.start_consuming_users, daemon=True)
        notes_thread = threading.Thread(target=notes_processor.start_consuming_notes, daemon=True)

        users_thread.start()
        notes_thread.start()

        logger.info("All event consumers started")

        return users_thread, notes_thread
