import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# Авторизация
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1tQpSEG0P2GxeVyz5AAwkBQs4b96jTrtxviKU4_d0BX8/edit").sheet1
except Exception as e:
    st.error("❌ שגיאה בחיבור ל-Google Sheets")
    st.stop()

# Настройка интерфейса
st.set_page_config(layout="wide")
st.markdown("""
    <h1 style='text-align:right; font-size:40px;'>📦 מחסן מלון גולן! 🥬🍎🍋</h1>
    <h3 style='text-align:right; color:gray;'>Titus Solutions</h3>
""", unsafe_allow_html=True)

# Загрузка CSV с продуктами
aliases_path = "data/product_aliases.csv"
try:
    df_products = pd.read_csv(aliases_path)
    product_names = df_products["main_name_he"].dropna().tolist()
except Exception as e:
    st.error(f"שגיאה בטעינת קובץ המוצרים: {e}")
    st.stop()

if "rows_to_order" not in st.session_state:
    st.session_state["rows_to_order"] = []

# Отображение интерфейса продуктов
for i, name in enumerate(product_names):
    st.markdown("------")
    cols = st.columns([3, 3, 2, 2, 1, 1])
    with cols[0]:
        st.markdown(f"<h2 style='text-align:right; font-size:32px;'>{name}</h2>", unsafe_allow_html=True)

    with cols[1]:
        fact_key = f"fact_{i}"
        fact = st.number_input("מלאי בפועל", step=0.5, key=fact_key)

        bcol1, bcol2 = st.columns(2)
        with bcol1:
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
        with bcol2:
            if st.button("בטל", key=f"cancel_fact_{i}"):
                st.warning(f"🔁 לא נשמר. יש לעדכן מחדש אם צריך.")

    with cols[2]:
        st.number_input("רכישה נדרשת", value=0.0, step=0.5, key=f"order_{i}")

    with cols[3]:
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

    with cols[4]:
        if st.button("✖", key=f"cancel_order_{name}"):
            st.warning(f"❌ הרכישה בוטלה עבור {name}")
            st.experimental_rerun()

# Действие: сформировать отчёт на закуп
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

# Действие: сформировать отчёт по остаткам
st.markdown("---")
if st.button("📦 הפקת דוח מלאי נוכחי"):
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if "timestamp" not in df.columns:
            st.warning("🔴 חסרה עמודת timestamp.")
        elif df.empty:
            st.info("📭 אין נתונים זמינים.")
        else:
            df_today = df[df["timestamp"].str.startswith(datetime.now().strftime("%Y-%m-%d"))]
            stock_df = df_today.groupby("product")["fact"].sum().reset_index()
            stock_df.columns = ["מוצר", "סה\"כ מלאי"]
            st.dataframe(stock_df, use_container_width=True)
    except Exception as e:
        st.error(f"שגיאה בדוח: {e}")
