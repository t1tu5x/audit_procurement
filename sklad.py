import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# ---------- Авторизация ----------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = Credentials.from_service_account_info(
        st.secrets["gsheets"], scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1tQpSEG0P2GxeVyz5AAwkBQs4b96jTrtxviKU4_d0BX8/edit"
    ).sheet1
except Exception as e:
    import traceback
    st.error("❌ שגיאה בחיבור ל-Google Sheets")
    st.text(traceback.format_exc())
    st.stop()

# ---------- Настройки ----------
st.set_page_config(layout="wide")
st.title("👨‍🍳 ניהול מלאי למטבח מקצועי")

# ---------- רשימת מוצרים ----------
products = [
    ("🍅 עגבניות", "עגבניות"),
    ("🥒 מלפפונים", "מלפפונים"),
    ("🥬 כרוב", "כרוב"),
    ("🥕 גזר", "גזר"),
    ("🧅 בצל", "בצל"),
    ("🫑 פלפל", "פלפל"),
    ("🍆 חציל", "חציל"),
    ("🟢 קישוא", "קישוא"),
    ("🌿 שומר", "שומר"),
    ("🥦 קולורבי", "קולורבי"),
    ("🍒 עגבניות שרי", "עגבניות שרי"),
    ("🎃 דלעת", "דלעת"),
    ("🟥 סלק", "סלק"),
    ("🍠 בטטה", "בטטה"),
    ("🥔 תפוחי אדמה", "תפוחי אדמה"),
    ("🧅 בצל סגול", "בצל סגול"),
    ("🧄 שום", "שום"),
    ("🍏 תפוחים", "תפוחים"),
    ("🍊 תפוזים", "תפוזים"),
    ("🍊 קלמנטינות", "קלמנטינות"),
    ("🍌 בננות", "בננות"),
    ("🍑 אפרסקים", "אפרסקים")
]

# ---------- UI ----------
st.markdown("### 📋 רשימת מוצרים")

if "rows_to_order" not in st.session_state:
    st.session_state["rows_to_order"] = []

for i, (label, name) in enumerate(products):
    st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
    cols = st.columns([3, 2, 3, 2, 2, 1, 1])

    with cols[0]:
        st.markdown(f"**{label}**")

    with cols[1]:
        st.number_input("מלאי צפוי (AI)", value=0.0, step=0.5, disabled=True, key=f"ai_stock_{i}")

    with cols[2]:
        fact_key = f"fact_{i}"
        fact = st.number_input("מלאי בפועל", value=0.0, step=0.5, key=fact_key)

        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("שמור", key=f"save_fact_{i}"):
                now = datetime.now()
                try:
                    sheet.append_row([
                        now.strftime("%Y-%m-%d %H:%M:%S"),
                        name,
                        fact,
                        0.0
                    ])
                    st.success(f"📝 נשמר מלאי: {name} = {fact}")
                except Exception as e:
                    st.error(f"❌ שגיאה בשמירה: {e}")

        with btn_cols[1]:
            if st.button("בטל", key=f"cancel_fact_{i}"):
                st.session_state[fact_key] = 0.0

    with cols[3]:
        st.number_input("תחזית רכישה (AI)", value=0.0, step=0.5, disabled=True, key=f"ai_order_{i}")

    with cols[4]:
        st.number_input("רכישה נדרשת", value=0.0, step=0.5, key=f"order_{i}")

    with cols[5]:
        if st.button("✔", key=f"confirm_{name}"):
            now = datetime.now()
            row = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                name,
                st.session_state[f"fact_{i}"],
                st.session_state[f"order_{i}"]
            ]
            st.session_state.rows_to_order.append(row)
            st.success(f"✅ נוסף לרכישה: {name}")

    with cols[6]:
        if st.button("✖", key=f"cancel_order_{name}"):
            st.session_state[f"order_{i}"] = 0.0

# ---------- דוח רכישה ----------
st.markdown("---")
if st.button("📤 הפקת דוח רכישה"):
    if not st.session_state.rows_to_order:
        st.warning("אין שורות להזמנה.")
    else:
        st.success("🧾 להלן המוצרים להזמנה:")
        df_report = pd.DataFrame(
            st.session_state.rows_to_order,
            columns=["timestamp", "product", "fact", "order"]
        )
        st.dataframe(df_report[["product", "order"]], use_container_width=True)

        for row in st.session_state.rows_to_order:
            try:
                sheet.append_row(row)
            except Exception as e:
                st.error(f"❌ שגיאה בשמירה ({row[1]}): {e}")

        st.session_state.rows_to_order = []

# ---------- דוח מלאי נוכחי ----------
st.markdown("---")
if st.button("📦 הפקת דוח מלאי נוכחי"):
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty:
            df_today = df[df["timestamp"].str.startswith(datetime.now().strftime("%Y-%m-%d"))]
            stock_df = df_today.groupby("product")["fact"].sum().reset_index()
            stock_df.columns = ["מוצר", "סה\"כ מלאי"]
            st.dataframe(stock_df, use_container_width=True)
        else:
            st.info("📭 אין נתונים זמינים.")
    except Exception as e:
        st.error(f"שגיאה בדוח: {e}")
