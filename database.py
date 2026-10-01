import sqlite3

DB_NAME = "projects.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_database():
    db = connect()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        min_capital REAL NOT NULL,
        startup_cost REAL NOT NULL,
        monthly_cost REAL NOT NULL,
        expected_revenue REAL NOT NULL,
        description TEXT,
        steps TEXT
    )
    """)

    db.commit()
    db.close()

def add_project(
    name,
    category,
    min_capital,
    startup_cost,
    monthly_cost,
    expected_revenue,
    description,
    steps
):
    db = connect()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO projects (
        name,
        category,
        min_capital,
        startup_cost,
        monthly_cost,
        expected_revenue,
        description,
        steps
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        category,
        min_capital,
        startup_cost,
        monthly_cost,
        expected_revenue,
        description,
        steps
    ))

    db.commit()
    db.close()


if __name__ == "__main__":
    create_database()

    print("قاعدة البيانات جاهزة ✅")
    print("تم إنشاء جدول المشاريع.")

