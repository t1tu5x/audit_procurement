import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# 📦 Список продуктов
products = [
    "Помидоры / עגבניות", "Огурцы / מלפפונים", "Перец болгарский / פלפל",
    "Капуста / כרוב", "Морковь / גזר", "Картофель / תפוחי אדמה"
]

# 🧠 Инициализация состояния
for p in products:
    st.session_state.setdefault(f"remain_{p}", 0.0)
    st.session_state.setdefault(f"order_{p}", "")
    st.session_state.setdefault(f"final_order_{p}", None)

st.set_page_config(layout="wide")
st.title("📦 Учёт остатков и заказ продуктов")
st.markdown("##### Укажите остаток на складе и желаемое количество для закупа. Поля ИИ — не редактируются.")

# 🧱 Заголовки
headers = ["Продукт", "Остаток (ИИ)", "Осталось", "+", "–", "Закуп (ИИ)", "Хочу заказать", "✓", "✗"]
cols = st.columns([2.5, 1, 1, 0.6, 0.6, 1, 1.2, 0.7, 0.7])
for h, c in zip(headers, cols):
    c.markdown(f"<small><b>{h}</b></small>", unsafe_allow_html=True)

# 🧮 Строки продуктов
for product in products:
    cols = st.columns([2.5, 1, 1, 0.6, 0.6, 1, 1.2, 0.7, 0.7])

    with cols[0]:
        st.markdown(f"<small>{product}</small>", unsafe_allow_html=True)

    with cols[1]:
        st.text_input("ИИ остаток", value="0", disabled=True,
                      label_visibility="collapsed", key=f"ai_now_{product}")

    with cols[2]:
        st.markdown(f"<small>{st.session_state[f'remain_{product}']:.1f} кг</small>", unsafe_allow_html=True)

    with cols[3]:
        if st.button("+0.5", key=f"plus_{product}"):
            st.session_state[f"remain_{product}"] += 0.5

    with cols[4]:
        if st.button("-0.5", key=f"minus_{product}"):
            st.session_state[f"remain_{product}"] = max(0, st.session_state[f"remain_{product}"] - 0.5)

    with cols[5]:
        st.text_input("ИИ закуп", value="0", disabled=True,
                      label_visibility="collapsed", key=f"ai_rec_{product}")

    with cols[6]:
        st.session_state[f"order_{product}"] = st.text_input(
            label="Сколько заказать", label_visibility="collapsed", key=f"input_{product}"
        )

    with cols[7]:
        if st.button("✔", key=f"confirm_btn_{product}"):
            st.session_state[f"final_order_{product}"] = st.session_state[f"order_{product}"]

    with cols[8]:
        if st.button("✘", key=f"cancel_btn_{product}"):
            st.session_state[f"final_order_{product}"] = None

st.divider()

# 📥 Кнопка формирования итогового заказа
if st.button("📄 Сформировать заказ"):
    confirmed = {
        p: st.session_state[f"final_order_{p}"]
        for p in products if st.session_state[f"final_order_{p}"]
    }
    if confirmed:
        st.success("Итоговый заказ:")
        st.table(confirmed)
    else:
        st.warning("Ни один заказ не подтверждён.")

