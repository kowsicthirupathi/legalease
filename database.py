import sqlite3

DATABASE_NAME = "legalease.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_type TEXT NOT NULL,
            parties TEXT NOT NULL,
            terms TEXT NOT NULL,
            effective_date TEXT NOT NULL,
            generated_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_document(
    document_type,
    parties,
    terms,
    effective_date,
    generated_content
):
    connection = get_connection()

    connection.execute("""
        INSERT INTO documents
        (document_type, parties, terms, effective_date, generated_content)
        VALUES (?, ?, ?, ?, ?)
    """, (
        document_type,
        parties,
        terms,
        effective_date,
        generated_content
    ))

    connection.commit()
    connection.close()