
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "support_tickets.db"


def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            created_at TEXT,
            customer_name TEXT,
            customer_email TEXT,
            category TEXT,
            priority TEXT,
            sentiment TEXT,
            customer_query TEXT,
            assistant_answer TEXT,
            web_search_answer TEXT,
            email_draft TEXT
        )
    """)

    connection.commit()
    connection.close()


def generate_ticket_id():
    return "TKT-" + uuid.uuid4().hex[:8].upper()


def save_ticket(customer_name, customer_email, category,
                priority, sentiment, customer_query,
                assistant_answer, web_search_answer,
                email_draft=""):

    ticket_id = generate_ticket_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, created_at, customer_name, customer_email,
        category, priority, sentiment, customer_query,
        assistant_answer, web_search_answer, email_draft
    ))

    connection.commit()
    connection.close()

    return ticket_id


def get_all_tickets():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")

    tickets = cursor.fetchall()
    connection.close()

    return tickets


if __name__ == "__main__":
    initialize_database()
    print("Ticket management functions are ready!")
