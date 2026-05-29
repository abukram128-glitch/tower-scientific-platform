import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import sqlite3
import json
import hashlib
import secrets
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# إعدادات الصفحة
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==========================================
# إعدادات قاعدة البيانات
# ==========================================

DB_NAME = "tower_scientific.db"

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """تشفير كلمة المرور"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """التحقق من كلمة المرور"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed

@st.cache_resource
def init_database():
    """تهيئة قاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # جدول المواد العلفية
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        protein REAL DEFAULT 0,
        lysine REAL DEFAULT 0,
        methionine REAL DEFAULT 0,
        digestibility REAL DEFAULT 0.85,
        energy REAL DEFAULT 0,
        price REAL DEFAULT 0,
        stock REAL DEFAULT 0,
        max_limit REAL DEFAULT 100,
        min_limit REAL DEFAULT 0
    )
    ''')
    
    # جدول التركيبات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        ingredients TEXT,
        total_cost REAL,
        protein REAL,
        energy REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # إضافة المستخدمين الافتراضيين
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("owner", "202687", UserRole.OWNER.value, "م. عبد القادر إسماعيل تاور"),
            ("specialist", "2020", UserRole.SPECIALIST.value, "د. مختص تغذية"),
            ("breeder", "2026", UserRole.BREEDER.value, "مربي نموذجي")
        ]
        for username, password, role, full_name in default_users:
            hashed, salt = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, password_salt, role, full_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed, salt, role, full_name))
    
    # إضافة المواد العلفية الافتراضية
    cursor.execute("SELECT COUNT(*) FROM feeds")
    if cursor.fetchone()[0] == 0:
        default_feeds = [
            # حبوب
            ("ذرة صفراء", "🌾 حبوب", 8.5, 0.24, 0.17, 0.85, 80.0, 230, 100, 0, 10),
            ("ذرة بيضاء", "🌾 حبوب", 8.8, 0.23, 0.16, 0.83, 78.0, 225, 100, 0, 10),
            ("شعير مطحون", "🌾 حبوب", 11.5, 0.36, 0.19, 0.80, 71.0, 210, 100, 0, 10),
            ("سورجم", "🌾 حبوب", 10.0, 0.22, 0.15, 0.78, 70.0, 195, 100, 0, 10),
            # بروتين
            ("كسب فول صويا 44%", "🥜 بروتين", 44.0, 2.70, 0.62, 0.90, 74.0, 440, 100, 0, 10),
            ("كسب فول صويا 48%", "🥜 بروتين", 48.0, 2.90, 0.67, 0.91, 76.0, 480, 100, 0, 10),
            ("كسب عباد الشمس", "🥜 بروتين", 36.0, 1.20, 0.75, 0.76, 42.0, 310, 100, 0, 10),
            ("أمباز الفول السوداني", "🥜 بروتين", 46.0, 1.60, 0.52, 0.88, 73.0, 460, 100, 0, 10),
            # أملاح
            ("ملح الطعام", "🧂 أملاح", 0, 0, 0, 0, 0, 30, 5, 0.5, 10),
            ("الحجر الجيري", "🧂 أملاح", 0, 0, 0, 0, 0, 40, 8, 0.5, 10),
            ("فوسفات ثنائي الكالسيوم", "🧂 أملاح", 0, 0, 0, 0, 0, 280, 3, 0.5, 10),
            # إضافات
            ("بريمكس دواجن", "💊 إضافات", 0, 0, 0, 0, 0, 230, 1, 0.25, 10),
        ]
        
        for feed in default_feeds:
            cursor.execute('''
                INSERT INTO feeds (name, category, protein, lysine, methionine, 
                                 digestibility, energy, price, max_limit, min_limit, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', feed)
    
    conn.commit()
    return conn

# ==========================================
# كلاسات البيانات
# ==========================================

from enum import Enum

class UserRole(Enum):
    OWNER = "owner"
    SPECIALIST = "specialist"
    BREEDER = "breeder"

class FeedIngredient:
    def __init__(self, name, protein, digestibility, energy, price, min_limit=0, max_limit=100):
        self.name = name
        self.protein = protein
        self.digestibility = digestibility
        self.energy = energy
        self.price = price
        self.min_limit = min_limit
        self.max_limit = max_limit
    
    @property
    def digestible_protein(self):
        return self.protein * self.digestibility

# ==========================================
# دوال الحساب
# ==========================================

def optimize_formula(ingredients, target_protein, use_digestible=True):
    """
    حساب التركيبة المثلى باستخدام البرمجة الخطية
    """
    n = len(ingredients)
    
    # دالة الهدف (تقليل التكلفة)
    c = [ing.price for ing in ingredients]
    
    # قيد المساواة: مجموع النسب = 100%
    A_eq = [[1.0] * n]
    b_eq = [100.0]
    
    # قيد البروتين
    if use_digestible:
        protein_coeffs = [ing.digestible_protein for ing in ingredients]
    else:
        protein_coeffs = [ing.protein for ing in ingredients]
    
    A_eq.append(protein_coeffs)
    b_eq.append(target_protein)
    
    # حدود المكونات
    bounds = [(ing.min_limit, ing.max_limit) for ing in ingredients]
    
    # حل المشكلة
    try:
        result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if result.success:
            # حساب التكلفة الإجمالية
            total_cost = sum(result.x[i] * ingredients[i].price for i in range(n)) / 100
            
            # حساب القيم الغذائية
            protein_total = sum(result.x[i] * (ingredients[i].digestible_protein if use_digestible else ingredients[i].protein) 
                               for i in range(n)) / 100
            
            energy_total = sum(result.x[i] * ingredients[i].energy for i in range(n)) / 100
            
            # تجميع النتائج
            percentages = {}
            for i, ing in enumerate(ingredients):
                if result.x[i] > 0.01:
                    percentages[ing.name] = result.x[i]
            
            return {
                'success': True,
                'percentages': percentages,
                'total_cost': total_cost,
                'protein': protein_total,
                'energy': energy_total,
                'message': "تم الحل بنجاح"
            }
        else:
            return {
                'success': False,
                'message': f"لم يتم إيجاد حل: {result.message}"
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"خطأ في الحساب: {str(e)}"
        }

# ==========================================
# دوال قاعدة البيانات
# ==========================================

def get_all_feeds():
    """الحصول على جميع المواد العلفية"""
    conn = init_database()
    df = pd.read_sql_query("SELECT * FROM feeds ORDER BY category, name", conn)
    conn.close()
    return df

def update_stock(feed_name, quantity):
    """تحديث المخزون"""
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE feeds SET stock = ? WHERE name = ?", (quantity, feed_name))
    conn.commit()
    conn.close()

def save_formula(name, ingredients, cost, protein, energy):
    """حفظ التركيبة"""
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO formulas (name, ingredients, total_cost, protein, energy)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, json.dumps(ingredients), cost, protein, energy))
    conn.commit()
    formula_id = cursor.lastrowid
    conn.close()
    return formula_id

def get_formulas(limit=50):
    """الحصول على التركيبات السابقة"""
    conn = init_database()
    df = pd.read_sql_query(f"SELECT * FROM formulas ORDER BY created_at DESC LIMIT {limit}", conn)
    conn.close()
    return df

def authenticate_user(username, password):
    """مصادقة المستخدم"""
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2], user[3]):
        return {
            'id': user[0],
            'username': user[1],
            'role': user[4],
            'full_name': user[5]
        }
    return None

# ==========================================
# دوال الواجهة
# ==========================================

def apply_custom_css():
    """تطبيق التنسيقات"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0;
    }
    
    .formula-result {
        background: #f1f8e9;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-right: 4px solid #2e7d32;
    }
    
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2e7d32;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        text-align: center;
        font-size: 12px;
        color: #888;
    }
    
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# واجهة تسجيل الدخول
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.user_id = None

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🌾 منصة تاور العلمية</h1>
        <p>للانتاج الحيواني وتركيب الاعلاف</p>
        <p style="font-size: 14px; margin-top: 10px;">الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### 🔐 بوابة الدخول")
        username = st.text_input("👤 اسم المستخدم", placeholder="owner / specialist / breeder")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user['full_name']
                    st.session_state.role = user['role']
                    st.session_state.user_id = user['id']
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            else:
                st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
        
        with st.expander("ℹ️ معلومات الدخول"):
            st.markdown("""
            **أكواد الدخول الافتراضية:**
            - **المالك:** username: `owner` / password: `202687`
            - **المختص:** username: `specialist` / password: `2020`
            - **المربي:** username: `breeder` / password: `2026`
            """)
    st.stop()

# ==========================================
# تهيئة قاعدة البيانات
# ==========================================

init_database()
apply_custom_css()

# ==========================================
# الشريط الجانبي
# ==========================================

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 15px;">
        <div style="background: #2e7d32; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;">
            <span style="font-size: 30px;">🌾</span>
        </div>
        <h3 style="margin: 0; color: #2e7d32;">{st.session_state.user}</h3>
        <p style="color: #888; font-size: 12px;">{st.session_state.role}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # قائمة التنقل
    menu = {
        "home": "🏠 الرئيسية",
        "formulator": "🔬 تركيب الأعلاف",
        "inventory": "📦 المخزون",
        "history": "📊 التركيبات السابقة",
        "help": "📚 المساعدة"
    }
    
    for key, label in menu.items():
        if st.button(label, key=f"menu_{key}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()
    
    st.markdown("---")
    
    # إحصائيات سريعة
    feeds_df = get_all_feeds()
    st.metric("📦 المواد العلفية", len(feeds_df))
    
    formulas_df = get_formulas(100)
    st.metric("📝 التركيبات", len(formulas_df))
    
    if 'last_cost' in st.session_state:
        st.metric("💰 آخر تكلفة", f"${st.session_state.last_cost:.2f}")
    
    st.markdown("---")
    
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        for key in ['logged_in', 'user', 'role', 'user_id', 'current_page']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("""
    <div class="sidebar-footer">
        © 2026 منصة تاور العلمية<br>
        الاختصاصي م. عبد القادر إسماعيل تاور
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# الصفحة الرئيسية
# ==========================================

current_page = st.session_state.get('current_page', 'home')

if current_page == 'home':
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);">
        <h1>🏠 لوحة التحكم الرئيسية</h1>
        <p>مرحباً بك في منصة تاور العلمية</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_feeds = len(feeds_df)
    total_formulas = len(formulas_df)
    avg_cost = formulas_df['total_cost'].mean() if not formulas_df.empty else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_feeds}</div>
            <div class="metric-label">📦 مواد علفية</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_formulas}</div>
            <div class="metric-label">📝 تركيبة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_cost:.0f}</div>
            <div class="metric-label">📊 متوسط التكلفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(feeds_df[feeds_df['stock'] < 5])}</div>
            <div class="metric-label">⚠️ مواد منخفضة</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # رسم بياني لتوزيع المواد
    if not feeds_df.empty:
        st.subheader("📊 توزيع المواد حسب التصنيف")
        category_counts = feeds_df['category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index, hole=0.3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # آخر التركيبات
    st.subheader("📋 آخر التركيبات")
    if not formulas_df.empty:
        display_df = formulas_df[['name', 'total_cost', 'protein', 'created_at']].head(5)
        display_df.columns = ['الاسم', 'التكلفة ($)', 'البروتين (%)', 'التاريخ']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("لا توجد تركيبات محفوظة بعد")

# ==========================================
# صفحة تركيب الأعلاف
# ==========================================

elif current_page == 'formulator':
    st.markdown("""
    <div class="main-header">
        <h1>🔬 محرك تركيب الأعلاف الذكي</h1>
        <p>نظام الاستمثال الخطي (Least-Cost Formulation)</p>
    </div>
    """, unsafe_allow_html=True)
    
    feeds_df = get_all_feeds()
    
    col1, col2 = st.columns(2)
    with col1:
        target_protein = st.slider("🎯 نسبة البروتين المستهدفة (%)", 5.0, 40.0, 16.0, 0.5)
        use_digestible = st.toggle("🧬 استخدام البروتين المهضوم", value=True)
    
    with col2:
        formula_name = st.text_input("📝 اسم التركيبة", value=f"خلطة {datetime.now().strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    st.subheader("✅ اختر المكونات العلفية")
    
    selected_ingredients = []
    
    for category in feeds_df['category'].unique():
        with st.expander(f"📁 {category}", expanded=category in ["🌾 حبوب", "🥜 بروتين"]):
            category_feeds = feeds_df[feeds_df['category'] == category]
            cols = st.columns(3)
            for idx, (_, row) in enumerate(category_feeds.iterrows()):
                with cols[idx % 3]:
                    if st.checkbox(f"{row['name']} (المخزون: {row['stock']:.1f} طن)", key=f"select_{row['id']}"):
                        if st.session_state.role == UserRole.OWNER.value:
                            price = st.number_input(f"سعر {row['name']}", value=float(row['price']), key=f"price_{row['id']}", step=5.0)
                        else:
                            price = row['price']
                            st.caption(f"💰 السعر: ${price:.0f}/طن")
                        
                        selected_ingredients.append(FeedIngredient(
                            name=row['name'],
                            protein=row['protein'],
                            digestibility=row['digestibility'],
                            energy=row['energy'],
                            price=price,
                            min_limit=row['min_limit'],
                            max_limit=row['max_limit']
                        ))
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
            if len(selected_ingredients) < 2:
                st.warning("⚠️ يرجى اختيار مكونين على الأقل")
            else:
                with st.spinner("🧮 جاري حساب التركيبة المثلى..."):
                    result = optimize_formula(selected_ingredients, target_protein, use_digestible)
                    
                    if result['success']:
                        st.balloons()
                        st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                        
                        col_r1, col_r2 = st.columns(2)
                        
                        with col_r1:
                            st.subheader("📝 المقادير لكل طن")
                            for name, pct in result['percentages'].items():
                                kg = pct * 10
                                st.markdown(f"""
                                <div class="formula-result">
                                    <strong>🌾 {name}</strong><br>
                                    <span style="font-size: 20px; font-weight: bold; color: #2e7d32;">{pct:.1f}%</span>
                                    <span style="font-size: 14px;"> → {kg:.1f} كجم</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.session_state.last_formula = result['percentages']
                            st.session_state.last_cost = result['total_cost']
                            st.session_state.last_protein = result['protein']
                        
                        with col_r2:
                            st.subheader("💰 التكاليف والمواصفات")
                            st.metric("تكلفة الطن", f"${result['total_cost']:.2f}")
                            st.metric("البروتين", f"{result['protein']:.2f}%")
                            st.metric("معادل النشاء", f"{result['energy']:.1f}")
                        
                        # حفظ التركيبة
                        if formula_name:
                            save_formula(formula_name, result['percentages'], result['total_cost'], result['protein'], result['energy'])
                            st.success(f"✅ تم حفظ التركيبة: {formula_name}")
                    else:
                        st.error(f"❌ {result['message']}")
                        st.info("💡 نصيحة: حاول إضافة المزيد من المكونات أو خفض نسبة البروتين")

# ==========================================
# صفحة المخزون
# ==========================================

elif current_page == 'inventory':
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #ef6c00 0%, #f57c00 100%);">
        <h1>📦 إدارة المخزون والمستودعات</h1>
        <p>تتبع المواد العلفية والمخزون</p>
    </div>
    """, unsafe_allow_html=True)
    
    feeds_df = get_all_feeds()
    
    # خصم سريع
    if 'last_formula' in st.session_state and st.session_state.last_formula:
        with st.expander("🔄 خصم آخر خلطة من المخزون", expanded=False):
            col_tons, col_btn = st.columns([2, 1])
            with col_tons:
                tons = st.number_input("الكمية (طن)", min_value=0.1, value=1.0, step=0.5)
            with col_btn:
                if st.button("تأكيد الخصم", type="primary"):
                    for name, pct in st.session_state.last_formula.items():
                        feed_row = feeds_df[feeds_df['name'] == name]
                        if not feed_row.empty:
                            new_stock = feed_row.iloc[0]['stock'] - (pct / 100) * tons
                            update_stock(name, max(0, new_stock))
                    st.success(f"✅ تم خصم {tons} طن")
                    st.rerun()
    
    st.markdown("---")
    st.subheader("📊 الأرصدة الحالية")
    
    # بحث
    search = st.text_input("🔍 بحث", placeholder="ابحث عن مادة...")
    filtered_df = feeds_df
    if search:
        filtered_df = feeds_df[feeds_df['name'].str.contains(search, na=False)]
    
    # عرض المخزون
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with cols[idx % 3]:
            stock = row['stock']
            name = row['name']
            
            if stock <= 2:
                color = "#ffebee"
                status = "🔴 حرج"
            elif stock <= 5:
                color = "#fff3e0"
                status = "🟡 منخفض"
            else:
                color = "#e8f5e9"
                status = "🟢 جيد"
            
            if st.session_state.role == UserRole.OWNER.value:
                new_stock = st.number_input(name, value=float(stock), key=f"stock_{row['id']}", step=0.5, label_visibility="collapsed")
                if new_stock != stock:
                    update_stock(name, new_stock)
                    st.rerun()
            else:
                st.markdown(f"""
                <div style="background-color: {color}; padding: 12px; border-radius: 10px; margin: 5px 0; border-right: 4px solid #2e7d32;">
                    <strong>{name}</strong><br>
                    <span style="font-size: 22px; font-weight: bold;">{stock:.1f}</span>
                    <span style="font-size: 14px;"> طن</span><br>
                    <span style="font-size: 12px;">{status}</span>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# صفحة التركيبات السابقة
# ==========================================

elif current_page == 'history':
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #6a1b9a 0%, #7b1fa2 100%);">
        <h1>📊 التركيبات العلفية السابقة</h1>
        <p>جميع التركيبات المحفوظة</p>
    </div>
    """, unsafe_allow_html=True)
    
    formulas_df = get_formulas(100)
    
    if formulas_df.empty:
        st.info("لا توجد تركيبات محفوظة")
    else:
        for _, row in formulas_df.iterrows():
            with st.expander(f"📅 {row['created_at']} - {row['name']} - ${row['total_cost']:.2f}"):
                ingredients = json.loads(row['ingredients'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**المكونات:**")
                    for name, pct in ingredients.items():
                        st.write(f"• {name}: {pct:.1f}% ({pct*10:.1f} كجم)")
                
                with col2:
                    st.markdown("**المواصفات:**")
                    st.write(f"💰 التكلفة: ${row['total_cost']:.2f}/طن")
                    st.write(f"🧬 البروتين: {row['protein']:.1f}%")
                    st.write(f"⚡ الطاقة: {row['energy']:.1f} SE")
                
                if st.button(f"🔄 استخدام هذه التركيبة", key=f"use_{row['id']}"):
                    st.session_state.last_formula = ingredients
                    st.session_state.last_cost = row['total_cost']
                    st.session_state.last_protein = row['protein']
                    st.session_state.current_page = 'formulator'
                    st.success("تم تحميل التركيبة")
                    st.rerun()

# ==========================================
# صفحة المساعدة
# ==========================================

else:
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #37474f 0%, #455a64 100%);">
        <h1>📚 المساعدة والدليل</h1>
        <p>دليل استخدام المنصة</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📖 الدليل", "🔑 الصلاحيات", "❓ الأسئلة الشائعة"])
    
    with tab1:
        st.markdown("""
        ### 🎯 كيفية الاستخدام
        
        1. **اختر القطاع** المناسب لحيواناتك
        2. **اختر المكونات** العلفية المتوفرة
        3. **حدد نسبة البروتين** المستهدفة
        4. **اضغط تشغيل المحرك** للحصول على التركيبة المثلى
        5. **احفظ التركيبة** للاستخدام المستقبلي
        """)
    
    with tab2:
        st.markdown("""
        ### 🔑 أكواد الدخول
        
        | الدور | اسم المستخدم | كلمة المرور |
        |-------|--------------|-------------|
        | 👑 مالك | `owner` | `202687` |
        | 👨‍🔬 مختص | `specialist` | `2020` |
        | 🌾 مربي | `breeder` | `2026` |
        """)
    
    with tab3:
        st.markdown("""
        ### ❓ الأسئلة الشائعة
        
        **س: ماذا أفعل إذا لم يتم إيجاد حل؟**
        ج: أضف المزيد من المكونات أو خفض نسبة البروتين.
        
        **س: كيف أعدل الأسعار؟**
        ج: صلاحية المالك فقط، يمكن تعديل السعر عند اختيار المكون.
        
        **س: كيف أحفظ التركيبة؟**
        ج: بعد الحساب، اكتب اسم واضغط حفظ.
        """)
    
    st.markdown("---")
    st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور")
    st.caption("منصة تاور العلمية - الإصدار 3.0")

# ==========================================
# نهاية الكود
# ==========================================
