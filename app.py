import streamlit as st

# MUST be first Streamlit command
st.set_page_config(page_title="IntelliSQL", layout="wide")

import os
import sqlite3
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted

# -----------------------------
# DATABASE (INLINE – NO FILE)
# -----------------------------
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS STUDENTS (
        NAME TEXT,
        CLASS TEXT,
        MARKS INTEGER,
        COMPANY TEXT
    )
    """)

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

# CALL AFTER DEFINITION
init_db()

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv(override=True)
api_key = os.getenv("API_KEY")

if not api_key:
    st.error("❌ API_KEY not found in .env file")
else:
    genai.configure(api_key=api_key)

# -----------------------------
# STYLING
# -----------------------------
def apply_styles():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #dbeafe, #f0f9ff);
    }
    h1 { color: #1e3a8a; text-align: center; }
    h3 { text-align: center; color: #475569; }
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

apply_styles()

# -----------------------------
# GEMINI → SQL
# -----------------------------
def get_response(question):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Convert English to SQL.
    Table: STUDENTS
    Columns: NAME, CLASS, MARKS, COMPANY
    Only return SQL.
    Question: {question}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except ResourceExhausted:
        return "Error: API quota exceeded"
    except Exception as e:
        return f"Error: {e}"

# -----------------------------
# RUN SQL SAFELY
# -----------------------------
def read_query(sql):
    sql = sql.replace("```sql", "").replace("```", "").strip()

    if not sql.upper().startswith("SELECT"):
        return "Only SELECT queries are allowed."

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    return pd.DataFrame(rows, columns=columns)

# -----------------------------
# PAGES
# -----------------------------
def page_home():
    st.markdown("<h1>✨ IntelliSQL</h1>", unsafe_allow_html=True)
    st.markdown("<h3>AI Powered SQL Assistant</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card">⚡ English → SQL</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">🔐 SELECT Only</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">🤖 Gemini AI</div>', unsafe_allow_html=True)

def page_query():
    st.title("🧠 Query Assistant")
    question = st.text_input("Ask a question")
    if st.button("Generate & Execute") and question:
        sql = get_response(question)
        st.code(sql, language="sql")
        result = read_query(sql)
        if isinstance(result, str):
            st.error(result)
        else:
            st.dataframe(result, use_container_width=True)

# -----------------------------
# MAIN
# -----------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Home", "Query Assistant"])

if page == "Home":
    page_home()
else:
    page_query()