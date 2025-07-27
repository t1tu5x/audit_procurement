import streamlit as st
import pandas as pd
from datetime import datetime, date
from zoneinfo import ZoneInfo
from google.oauth2.service_account import Credentials
import gspread

# ---------- Авторизация ----------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1tQpSEG0P2GxeVyz5AAwkBQs4b96jTrtxviKU4_d0BX8/edit").sheet1
except Exception as e:
    st.error("❌ שגיאה בחיבור ל-Google Sheets")
    st.stop()

# ---------- Конфигурация ----------
PRODUCTS = [
    ("עגבניות", "🍅"),
    ("מלפפונים", "🥒"),
    ("כרוב", "🥬"),
    ("גזר", "🥕"),
    ("בצל", "🧅"),
    ("פלפל", "🌶️"),
    ("חציל", "🍆"),
    ("קישוא", "🥒"),
    ("שומר", "🌿"),
    ("קולורבי", "🥦"),
    ("עגבניות שרי", "🍅"),
    ("דלת", "🎃"),
    ("סלק", "🥬"),
    ("באטט", "🍠"),
    ("תפוחי אדמה", "🥔"),
    ("בצל סגול", "🧅"),
    ("שום", "🧄"),
    ("תפוחים", "🍎"),
    ("תפוזים", "🍊"),
    ("תפוזים קטנים", "🍊"),
    ("בננות", "🍌"),
    ("שפרסקים", "🍑"),
]

st.set_page_config(layout="wide")

# ---------- Заголовок ----------
st.markdown("""
<h1 style='text-align: right; font-size: 36px;'>מחסן מלון גולן 🍅🍋🌿</h1>
<h3 style='text-align: right; font-size: 14px;'>שף יהודה</h3>
""", unsafe_allow_html=True)

# ---------- Получение данных из таблицы ----------
try:
    records = sheet.get_all_records()
    df = pd.DataFrame(records) if records else pd.DataFrame(columns=["timestamp", "date", "product", "fact", "order", "type"])
except Exception as e:
    st.warning("⚠️ שגיאה בקריאת הנתונים מהטבלה")
    df = pd.DataFrame(columns=["timestamp", "date", "product", "fact", "order", "type"])

# ---------- Интерфейс для каждого продукта ----------
for i, (product, emoji) in enumerate(PRODUCTS):
    st.markdown(f"<h2 style='text-align:right;font-size:24px;'>{emoji} {product}</h2>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 2, 1.5, 2])

    with col1:
        st.text("מלאי צפוי (AI)")
        st.number_input("", value=0.0, step=0.5, disabled=True, key=f"expected_{i}")

    with col2:
        st.text("מלאי בפועל")
        fact_key = f"fact_{i}"
        st.number_input(" ", step=0.5, format="%.2f", key=fact_key)

    with col3:
        st.text("תחזית רכישה (AI)")
        st.number_input("", value=0.0, step=0.5, disabled=True, key=f"rec_{i}")

    with col4:
        st.text("רכישה נדרשת")
        order_key = f"order_{i}"
        st.number_input("", step=0.5, format="%.2f", key=order_key)

    col_save, col_cancel, col_order_confirm, col_order_cancel = st.columns(4)

    with col_save:
        if st.button("שמור", key=f"save_{i}"):
            ts = datetime.now(ZoneInfo("Asia/Jerusalem"))
            sheet.append_row([ts.isoformat(), ts.date().isoformat(), product, st.session_state[fact_key], 0, "fact"])
            st.success("✅ נשמר")

    with col_cancel:
        if st.button("בטל", key=f"cancel_{i}"):
            ts = datetime.now(ZoneInfo("Asia/Jerusalem"))
            sheet.append_row([ts.isoformat(), ts.date().isoformat(), product, 0, 0, "cancel_fact"])
            st.info("🔁 לא נשמר. יש לרענן את הדף לאיפוס.")

    with col_order_confirm:
        if st.button("✔", key=f"confirm_{i}"):
            ts = datetime.now(ZoneInfo("Asia/Jerusalem"))
            sheet.append_row([ts.isoformat(), ts.date().isoformat(), product, 0, st.session_state[order_key], "order"])
            st.success(f"✅ נוסף לרכישה: {product}")

    with col_order_cancel:
        if st.button("✖", key=f"remove_{i}"):
            ts = datetime.now(ZoneInfo("Asia/Jerusalem"))
            sheet.append_row([ts.isoformat(), ts.date().isoformat(), product, 0, 0, "cancel_order"])
            st.info(f"🚫 בוטל רכישה: {product}")

    st.markdown("---")

# ---------- Отчёт по дате ----------
st.subheader("📋 דוח מלאי")
if st.button("הפק דוח"):
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if "timestamp" not in df.columns:
            st.warning("⚠️ הטבלה אינה כוללת עמודת timestamp.")
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            today = datetime.now(ZoneInfo("Asia/Jerusalem")).date()
            report = df[df["timestamp"].dt.date == today]
            st.dataframe(report, use_container_width=True)
    except Exception as e:
        st.error(f"שגיאה בדוח: {e}")
