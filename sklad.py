import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.service_account import Credentials
import gspread

# ---------- Авторизация ----------
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = Credentials.from_service_account_info(st.secrets["gsheets"], scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hcxv4gQRZaGRaeu9fRuA1SILbkJlRSxdLvcMFuXU4Aw/edit").sheet1
    
except Exception as e:
    st.error("❌ Ошибка подключения к Google Sheets")
    import traceback
    st.text(traceback.format_exc())
    st.stop()

# ---------- Продукты ----------
products = [
    # 🥦 Овощи
    "Помидоры / עגבניות", "Огурцы / מלפפונים", "Перец болгарский / פלפל",
    "Капуста / כרוב", "Морковь / גזר", "Картофель / תפוחי אדמה",
    "Лук / בצל", "Чеснок / שום", "Баклажаны / חצילים", "Кабачки / קישואים",
    "Свёкла / סלק", "Редис / צנונית", "Фасоль / שעועית",
    "Горошек / אפונה", "Кукуруза / תירס",
    # 🍎 Фрукты
    "Яблоки / תפוחים", "Апельсины / תפוזים", "Бананы / בננות",
    "Мандарины / קלמנטינות", "Виноград / ענבים",
    # 🌿 Зелень и грибы
    "Петрушка / פטרוזיליה", "Кинза / כוסברה", "Сельдерей / סלרי",
    "Салат / חסה", "Укроп / שמיר", "Грибы / פטריות"
]

# ---------- Streamlit init ----------
st.set_page_config(layout="wide")
st.title("📦 Учёт остатков и закупов (для кухни)")
st.markdown("##### Укажите, сколько осталось и сколько нужно заказать. ИИ подскажет прогноз.")

# ---------- Состояние ----------
for p in products:
    st.session_state.setdefault(f"remain_{p}", 0.0)
    st.session_state.setdefault(f"order_{p}", "")
    st.session_state.setdefault(f"final_order_{p}", None)

# ---------- Заголовки таблицы ----------
headers = ["Продукт", "Остаток (ИИ)", "Осталось", "Приход", "+", "–", "Закуп (ИИ)", "Хочу заказать", "✓", "✗"]
cols = st.columns([2.5, 1, 1, 1, 0.6, 0.6, 1, 1.4, 0.6, 0.6])
for h, c in zip(headers, cols):
    c.markdown(f"<small><b>{h}</b></small>", unsafe_allow_html=True)

# ---------- Интерфейс продукта ----------
for product in products:
    st.session_state.setdefault(f"last_purchase_{product}", 0)  # ← заглушка под закуп

    cols = st.columns([2.5, 1, 1, 1, 0.6, 0.6, 1, 1.4, 0.6, 0.6])
    with cols[0]:
        st.markdown(f"<small>{product}</small>", unsafe_allow_html=True)
    with cols[1]:
        st.text_input("ИИ остаток", value="0", disabled=True, label_visibility="collapsed", key=f"ai_now_{product}")
    with cols[2]:
        st.markdown(f"<small>{st.session_state[f'remain_{product}']:.1f} кг</small>", unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"<small>{st.session_state[f'last_purchase_{product}']} кг</small>", unsafe_allow_html=True)
    with cols[4]:
        if st.button("+0.5", key=f"plus_{product}"):
            st.session_state[f"remain_{product}"] += 0.5
    with cols[5]:
        if st.button("-0.5", key=f"minus_{product}"):
            st.session_state[f"remain_{product}"] = max(0, st.session_state[f"remain_{product}"] - 0.5)
    with cols[6]:
        st.text_input("ИИ закуп", value="0", disabled=True, label_visibility="collapsed", key=f"ai_rec_{product}")
    with cols[7]:
        st.session_state[f"order_{product}"] = st.text_input("Хочу заказать", label_visibility="collapsed", key=f"input_{product}")
    with cols[8]:
        if st.button("✔", key=f"confirm_{product}"):
            st.session_state[f"final_order_{product}"] = st.session_state[f"order_{product}"]
    with cols[9]:
        if st.button("✘", key=f"cancel_{product}"):
            st.session_state[f"final_order_{product}"] = None

# ---------- Сформировать заказ ----------
st.markdown("---")
if st.button("📄 Сформировать заказ"):
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for p in products:
        qty = st.session_state.get(f"final_order_{p}")
        if qty:
            remain = st.session_state[f"remain_{p}"]
            rows.append([timestamp, p, remain, qty])

    if rows:
        try:
            for row in rows:
                sheet.append_row(row)
            st.success(f"✅ Заказ из {len(rows)} строк успешно сохранён")
        except Exception as e:
            st.error(f"❌ Ошибка при сохранении: {e}")
    else:
        st.warning("Нет подтверждённых позиций.")

# ---------- Список на печать / копипаст ----------
st.markdown("## 🧾 Сформировать отчёт для поставщика")

if st.button("📤 Создать текстовый заказ"):
    confirmed = {
        p: st.session_state[f"final_order_{p}"]
        for p in products if st.session_state.get(f"final_order_{p}")
    }

    if confirmed:
        st.success("Скопируй текст и отправь поставщику:")
        report = "\n".join([f"{p.split('/')[0].strip()}: {v} кг" for p, v in confirmed.items()])
        st.text_area("📝 Заказ:", report, height=300)
    else:
        st.info("Нет выбранных позиций для заказа.")

