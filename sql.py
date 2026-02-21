import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS STUDENTS(
        NAME TEXT,
        CLASS TEXT,
        MARKS INTEGER,
        COMPANY TEXT
    )
    """)

    # Clear existing data to avoid duplicates
    cursor.execute("DELETE FROM STUDENTS")

    students = [
        ("Sijo", "BTech", 75, "JSW"),
        ("Lijo", "MTech", 69, "TCS"),
        ("Rijo", "BSc", 79, "WIPRO"),
        ("Sibin", "MSc", 89, "INFOSYS"),
        ("Dilsha", "MCom", 99, "Cyient")
    ]

    cursor.executemany(
        "INSERT INTO STUDENTS VALUES (?, ?, ?, ?)",
        students
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()