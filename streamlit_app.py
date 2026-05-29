import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import sqlite3
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# إعدادات الصفحة
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# تهيئة قاعدة البيانات
# ==========================================

DB_NAME = "tower.db"

@st.cache_resource
def init_db():
    """تهيئة قاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        title TEXT
    )
    ''')
    
    # جدول المواد العلفية
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        protein REAL,
        energy REAL,
        price REAL,
        stock REAL
    )
    ''')
    
    # جدول التركيبات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        sector TEXT,
        ingredients TEXT,
        total_cost REAL,
        protein REAL,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    
    # إضافة المستخدمين الافتراضيين
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("tower", "202687", "owner", "الاختصاصي م. عبد القادر إسماعيل تاور", "المالك 👑"),
            ("specialist", "2020", "specialist", "الطبيب البيطري", "مختص تغذية 👨‍🔬"),
            ("breeder", "2026", "breeder", "المربي", "مربي منتج 🌾")
        ]
        cursor.executemany("INSERT INTO users (username, password, role, full_name, title) VALUES (?,?,?,?,?)", users)
        conn.commit()
    
    # إضافة المواد العلفية الافتراضية
    cursor.execute("SELECT COUNT(*) FROM feeds")
    if cursor.fetchone()[0] == 0:
        feeds = [
            ("ذرة صفراء", "🌾 حبوب", 8.5, 80, 230, 25),
            ("ذرة بيضاء", "🌾 حبوب", 8.8, 78, 225, 25),
            ("شعير مطحون", "🌾 حبوب", 11.5, 71, 210, 25),
            ("كسب فول صويا 44%", "🥜 بروتين", 44, 74, 440, 20),
            ("كسب فول صويا 48%", "🥜 بروتين", 48, 76, 480, 20),
            ("كسب عباد الشمس", "🥜 بروتين", 36, 42, 310, 20),
            ("نخالة قمح", "🌾 مخلفات", 15, 45, 150, 15),
            ("ملح الطعام", "🧂 أملاح", 0, 0, 30, 20),
            ("الحجر الجيري", "🧂 أملاح", 0, 0, 40, 20),
            ("بريمكس دواجن", "💊 إضافات", 0, 0, 230, 10)
        ]
        cursor.executemany("INSERT INTO feeds (name, category, protein, energy, price, stock) VALUES (?,?,?,?,?,?)", feeds)
        conn.commit()
    
    return conn

def get_feeds():
    """جلب المواد العلفية"""
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM feeds", conn)
    conn.close()
    return df

def update_stock(name, quantity):
    """تحديث المخزون"""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE feeds SET stock = ? WHERE name = ?", (quantity, name))
    conn.commit()
    conn.close()

def save_formula(name, sector, ingredients, cost, protein):
    """حفظ التركيبة"""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO formulas (name, sector, ingredients, total_cost, protein, created_at) VALUES (?,?,?,?,?,?)",
        (name, sector, json.dumps(ingredients), cost, protein, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def get_formulas():
    """جلب التركيبات المحفوظة"""
    conn = init_db()
    df = pd.read_sql_query("SELECT * FROM formulas ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df

def authenticate(username, password):
    """مصادقة المستخدم"""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "role": user[3], "full_name": user[4], "title": user[5]}
    return None

# ==========================================
# دوال التحسين
# ==========================================

def optimize(selected, prices, proteins, energies, target_protein):
    """حساب التركيبة المثلى"""
    n = len(selected)
    
    if n < 2:
        return None
    
    # دالة الهدف (تقليل التكلفة)
    c = prices
    
    # قيد المساواة: المجموع = 100%
    A_eq = [[1] * n]
    b_eq = [100]
    
    # قيد البروتين
    A_eq.append(proteins)
    b_eq.append(target_protein)
    
    # حدود المكونات
    bounds = [(0, 100) for _ in range(n)]
    
    try:
        result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        if result.success:
            percentages = {}
            total_cost = 0
            total_protein = 0
            
            for i, name in enumerate(selected):
                if result.x[i] > 0.01:
                    percentages[name] = result.x[i]
                    total_cost += result.x[i] * prices[i] / 100
                    total_protein += result.x[i] * proteins[i] / 100
            
            return {
                "success": True,
                "percentages": percentages,
                "total_cost": total_cost,
                "protein": total_protein
            }
        return {"success": False, "message": str(result.message)}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ==========================================
# واجهة تسجيل الدخول
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.name = None

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="color: #2e7d32;">🌾 منصة تاور العلمية</h1>
        <h3>للانتاج الحيواني وتركيب الاعلاف</h3>
        <p>الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("👤 اسم المستخدم", placeholder="tower / specialist / breeder")
        password = st.text_input("🔑 كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if username and password:
                user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.role = user["role"]
                    st.session_state.name = user["full_name"]
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            else:
                st.warning("⚠️ يرجى إدخال البيانات")
        
        with st.expander("ℹ️ معلومات الدخول"):
            st.markdown("""
            | الاسم | المستخدم | كلمة المرور |
            |-------|----------|-------------|
            | تاور | tower | 202687 |
            | مختص | specialist | 2020 |
            | مربي | breeder | 2026 |
            """)
    st.stop()

# ==========================================
# الشريط الجانبي
# ==========================================

init_db()

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 15px;">
        <h3 style="color: #2e7d32;">{st.session_state.name}</h3>
        <p style="color: #888;">{st.session_state.user['title']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio("القائمة", [
        "🏠 الرئيسية",
        "🔬 تركيب الأعلاف",
        "📦 المخزون",
        "📊 التركيبات السابقة",
        "📚 المساعدة"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("""
    <div style="text-align: center; font-size: 11px; color: #888; margin-top: 20px;">
        © 2026 منصة تاور العلمية<br>
        م. عبد القادر إسماعيل تاور
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# الصفحات
# ==========================================

if menu == "🏠 الرئيسية":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1b5e20, #2e7d32); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <h1 style="color: white;">🌾 منصة تاور العلمية</h1>
        <p style="color: white;">للانتاج الحيواني وتركيب الاعلاف</p>
    </div>
    """, unsafe_allow_html=True)
    
    feeds = get_feeds()
    formulas = get_formulas()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 المواد العلفية", len(feeds))
    with col2:
        st.metric("📝 التركيبات", len(formulas))
    with col3:
        st.metric("📊 متوسط التكلفة", f"${formulas['total_cost'].mean():.0f}" if not formulas.empty else "$0")
    with col4:
        st.metric("⚠️ مواد منخفضة", len(feeds[feeds['stock'] < 5]))
    
    st.markdown("---")
    
    if not feeds.empty:
        fig = px.pie(feeds, names='category', title='توزيع المواد حسب التصنيف', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🔬 تركيب الأعلاف":
    st.subheader("🔬 محرك تركيب الأعلاف الذكي")
    
    feeds = get_feeds()
    
    col1, col2 = st.columns(2)
    with col1:
        sector = st.selectbox("القطاع الإنتاجي", ["دواجن لاحم", "دواجن بياض", "أبقار", "أغنام وماعز", "عام"])
        target_protein = st.slider("نسبة البروتين المستهدفة (%)", 5.0, 40.0, 16.0, 0.5)
    with col2:
        formula_name = st.text_input("اسم التركيبة", value=f"خلطة {datetime.now().strftime('%Y%m%d')}")
    
    st.markdown("---")
    st.subheader("اختر المكونات")
    
    selected = []
    prices = []
    proteins = []
    energies = []
    
    cols = st.columns(3)
    for idx, row in feeds.iterrows():
        with cols[idx % 3]:
            if st.checkbox(f"{row['name']} (المتبقي: {row['stock']:.1f} طن)"):
                price = st.number_input(f"سعر {row['name']}", value=float(row['price']), key=f"price_{row['id']}", step=5.0)
                selected.append(row['name'])
                prices.append(price)
                proteins.append(row['protein'])
                energies.append(row['energy'])
    
    if st.button("🚀 حساب التركيبة", type="primary", use_container_width=True):
        if len(selected) < 2:
            st.warning("⚠️ يرجى اختيار مكونين على الأقل")
        else:
            with st.spinner("جاري الحساب..."):
                result = optimize(selected, prices, proteins, energies, target_protein)
                
                if result and result["success"]:
                    st.balloons()
                    st.success("✅ تم حساب التركيبة بنجاح!")
                    
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        st.markdown("### المكونات")
                        for name, pct in result["percentages"].items():
                            st.markdown(f"- **{name}**: {pct:.1f}% ({pct*10:.1f} كجم/طن)")
                    
                    with col_r2:
                        st.markdown("### التكاليف")
                        st.metric("💰 تكلفة الطن", f"${result['total_cost']:.2f}")
                        st.metric("🥩 نسبة البروتين", f"{result['protein']:.1f}%")
                    
                    st.session_state.last_formula = result["percentages"]
                    st.session_state.last_cost = result["total_cost"]
                    
                    # حفظ التركيبة
                    save_formula(formula_name, sector, result["percentages"], result["total_cost"], result["protein"])
                    st.success("✅ تم حفظ التركيبة")
                    
                else:
                    st.error("❌ لم يتم إيجاد حل")
                    st.info("💡 نصيحة: أضف المزيد من المكونات أو خفض نسبة البروتين")

elif menu == "📦 المخزون":
    st.subheader("📦 إدارة المخزون")
    
    feeds = get_feeds()
    
    if 'last_formula' in st.session_state:
        with st.expander("🔄 خصم آخر خلطة", expanded=False):
            tons = st.number_input("الكمية (طن)", min_value=0.1, value=1.0, step=0.5)
            if st.button("خصم من المخزون"):
                for name, pct in st.session_state.last_formula.items():
                    feed = feeds[feeds['name'] == name]
                    if not feed.empty:
                        new_stock = feed.iloc[0]['stock'] - (pct / 100) * tons
                        update_stock(name, max(0, new_stock))
                st.success("تم الخصم")
                st.rerun()
    
    st.markdown("---")
    
    for _, row in feeds.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{row['name']}** - {row['category']}")
        with col2:
            if st.session_state.role == "owner":
                new_stock = st.number_input("طن", value=float(row['stock']), key=f"stock_{row['id']}", label_visibility="collapsed")
                if new_stock != row['stock']:
                    update_stock(row['name'], new_stock)
                    st.rerun()
            else:
                if row['stock'] < 2:
                    st.error(f"{row['stock']:.1f} طن 🔴")
                elif row['stock'] < 5:
                    st.warning(f"{row['stock']:.1f} طن 🟡")
                else:
                    st.success(f"{row['stock']:.1f} طن 🟢")

elif menu == "📊 التركيبات السابقة":
    st.subheader("📊 التركيبات السابقة")
    
    formulas = get_formulas()
    
    if formulas.empty:
        st.info("لا توجد تركيبات محفوظة")
    else:
        for _, row in formulas.iterrows():
            with st.expander(f"{row['created_at']} - {row['name']} - ${row['total_cost']:.2f}"):
                ingredients = json.loads(row['ingredients'])
                for name, pct in ingredients.items():
                    st.write(f"- {name}: {pct:.1f}% ({pct*10:.1f} كجم)")
                
                if st.button(f"استخدام", key=f"use_{row['id']}"):
                    st.session_state.last_formula = ingredients
                    st.session_state.last_cost = row['total_cost']
                    st.success("تم تحميل التركيبة")

elif menu == "📚 المساعدة":
    st.subheader("📚 المساعدة والدليل")
    
    tab1, tab2, tab3 = st.tabs(["📖 الدليل", "🔑 الصلاحيات", "❓ الأسئلة"])
    
    with tab1:
        st.markdown("""
        ### كيفية الاستخدام
        
        1. اختر القطاع الإنتاجي المناسب
        2. حدد نسبة البروتين المستهدفة
        3. اختر المكونات العلفية المتوفرة
        4. اضغط "حساب التركيبة"
        5. استخدم النتيجة في مزرعتك
        """)
    
    with tab2:
        st.markdown("""
        ### أكواد الدخول
        
        | الاسم | المستخدم | كلمة المرور |
        |-------|----------|-------------|
        | تاور (مالك) | tower | 202687 |
        | مختص | specialist | 2020 |
        | مربي | breeder | 2026 |
        """)
    
    with tab3:
        st.markdown("""
        ### أسئلة شائعة
        
        **ماذا أفعل إذا لم يظهر حل؟**
        أضف مكونات أكثر أو خفض نسبة البروتين.
        
        **كيف أعدل الأسعار؟**
        صلاحية المالك فقط.
        
        **للتواصل؟**
        تواصل مع الاختصاصي م. عبد القادر إسماعيل تاور
        """)

st.markdown("---")
st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور")
