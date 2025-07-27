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
    st.error("❌ Ошибка подключения к Google Sheets")
    st.text(traceback.format_exc())
    st.stop()

# ---------- Настройки ----------
st.set_page_config(layout="wide")

st.title("📦 Учёт склада — audit-procurement.csv")

products = [
    "Помидоры / עגבניות",
    "Огурцы / מלפפונים",
    "Капуста / כרוב",
    "Морковь / גזר",
    "Картошка / תפוחי אדמה",
    "Лук / בצל",
    "Перец / פלפל",
    "Баклажан / חציל",
    "Цукини / קישוא",
    "Свёкла / סלק",
    "Редис / צנון",
    "Чеснок / שום",
    "Тыква / דלעת",
    "Фенхель / שומר",
    "Батат / בטטה",
    "Яблоки / תפוחים",
    "Бананы / בננות",
    "Груши / אגסים",
    "Апельсины / תפוזים",
    "Мандарины / קלמנטינות",
    "Петрушка / פטרוזיליה",
    "Кинза / כוסברה",
    "Сельдерей / סלרי",
    "Салат / חסה",
    "Укроп / שמיר",
    "Грибы / פטריות"
]

st.markdown("### 🧾 Остатки и заказы")

if "rows_to_order" not in st.session_state:
    st.session_state["rows_to_order"] = []

for i, product in enumerate(products):
    st.markdown("""<hr style='margin: 8px 0;'>""", unsafe_allow_html=True)
    cols = st.columns([3, 2, 2, 2, 2, 1, 1])

    with cols[0]:
        st.markdown(f"**{product}**")

    with cols[1]:
        st.number_input("ИИ остаток", value=0.0, step=0.5, disabled=True, key=f"ai_stock_{i}")

    with cols[2]:
        fact = st.number_input("Факт", value=0.0, step=0.5, key=f"fact_{i}")
        col_plus, col_minus = st.columns(2)
        with col_plus:
            if st.button("+0.5", key=f"plus_{i}"):
                st.session_state[f"fact_{i}"] += 0.5
        with col_minus:
            if st.button("-0.5", key=f"minus_{i}"):
                st.session_state[f"fact_{i}"] = max(0.0, st.session_state[f"fact_{i}"] - 0.5)

    with cols[3]:
        st.number_input("ИИ закуп", value=0.0, step=0.5, disabled=True, key=f"ai_order_{i}")

    with cols[4]:
        order = st.number_input("Заказ", value=0.0, step=0.5, key=f"order_{i}")

    with cols[5]:
        if st.button("✔", key=f"confirm_{product}"):
            now = datetime.now()
            row = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                product,
                st.session_state[f"fact_{i}"],
                st.session_state[f"order_{i}"]
            ]
            st.session_state.rows_to_order.append(row)
            st.success(f"Добавлено: {product}")

    with cols[6]:
        if st.button("✖", key=f"cancel_{product}"):
            st.session_state[f"order_{i}"] = 0.0
            st.session_state[f"fact_{i}"] = 0.0

# ---------- Сформировать отчёт ----------
st.markdown("---")
if st.button("📤 Сформировать отчёт на заказ"):
    if not st.session_state.rows_to_order:
        st.warning("Нет строк для заказа.")
    else:
        st.success("Готово! Вот что заказать:")
        df_report = pd.DataFrame(
            st.session_state.rows_to_order,
            columns=["timestamp", "product", "fact", "order"]
        )
        st.dataframe(df_report[["product", "order"]])

        # Сохраняем в таблицу
        for row in st.session_state.rows_to_order:
            try:
                sheet.append_row(row)
            except Exception as e:
                st.error(f"❌ Не удалось сохранить {row[1]}: {e}")

        st.session_state.rows_to_order = []
