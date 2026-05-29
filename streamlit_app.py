import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import sqlite3
import urllib.parse
from datetime import datetime

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
# أكواد الدخول والصلاحيات
# ==========================================

USERS = {
    "202687": {"role": "owner", "name": "المالك 👑", "color": "#c62828"},
    "2020": {"role": "specialist", "name": "المختص 👨‍🔬", "color": "#1565c0"},
    "2026": {"role": "breeder", "name": "المربي 🌾", "color": "#2e7d32"}
}

# ==========================================
# تهيئة قاعدة البيانات
# ==========================================

@st.cache_resource
def init_database():
    """تهيئة قاعدة البيانات مع البيانات الافتراضية"""
    conn = sqlite3.connect('tower_feed.db', check_same_thread=False)
    cursor = conn.cursor()
    
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
        max_limit REAL DEFAULT 100,
        min_limit REAL DEFAULT 0
    )
    ''')
    
    # جدول المخزون
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        feed_name TEXT PRIMARY KEY,
        quantity REAL DEFAULT 0,
        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # جدول التركيبات السابقة
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        formula TEXT,
        cost REAL,
        protein REAL
    )
    ''')
    
    # إضافة البيانات الافتراضية
    cursor.execute("SELECT COUNT(*) FROM feeds")
    if cursor.fetchone()[0] == 0:
        default_feeds = [
            # الحبوب ومصادر الطاقة
            ("ذرة صفراء", "🌾 حبوب", 8.5, 0.24, 0.17, 0.85, 80.0, 230, 100, 0),
            ("ذرة بيضاء", "🌾 حبوب", 8.8, 0.23, 0.16, 0.83, 78.0, 225, 100, 0),
            ("شعير مطحون", "🌾 حبوب", 11.5, 0.36, 0.19, 0.80, 71.0, 210, 100, 0),
            ("سورجم (فتريتة)", "🌾 حبوب", 10.0, 0.22, 0.15, 0.78, 70.0, 195, 100, 0),
            ("قمح", "🌾 حبوب", 12.0, 0.32, 0.21, 0.85, 75.0, 240, 100, 0),
            
            # مصادر البروتين
            ("كسب فول صويا 44%", "🥜 بروتين", 44.0, 2.70, 0.62, 0.90, 74.0, 440, 100, 0),
            ("كسب فول صويا 48%", "🥜 بروتين", 48.0, 2.90, 0.67, 0.91, 76.0, 480, 100, 0),
            ("كسب عباد الشمس", "🥜 بروتين", 36.0, 1.20, 0.75, 0.76, 42.0, 310, 100, 0),
            ("أمباز الفول السوداني", "🥜 بروتين", 46.0, 1.60, 0.52, 0.88, 73.0, 460, 100, 0),
            ("كسب بذور القطن", "🥜 بروتين", 41.0, 1.75, 0.64, 0.78, 55.0, 290, 100, 0),
            
            # مصادر بروتين حيواني
            ("مسحوق أسماك 60%", "🐟 بروتين حيواني", 60.0, 4.50, 1.65, 0.85, 65.0, 850, 100, 0),
            
            # المخلفات الزراعية
            ("نخالة قمح (ردة)", "🌾 مخلفات", 15.0, 0.58, 0.23, 0.72, 45.0, 150, 100, 0),
            ("مولاس قصب السكر", "🍯 مخلفات", 4.0, 0.05, 0.02, 0.95, 50.0, 120, 100, 0),
            
            # الأملاح والمعادن
            ("ملح الطعام", "🧂 أملاح", 0, 0, 0, 0, 0, 30, 100, 0),
            ("الحجر الجيري", "🧂 أملاح", 0, 0, 0, 0, 0, 40, 100, 0),
            ("فوسفات ثنائي الكالسيوم", "🧂 أملاح", 0, 0, 0, 0, 0, 280, 100, 0),
            
            # الإضافات
            ("بريمكس دواجن", "💊 إضافات", 0, 0, 0, 0, 0, 230, 100, 0),
            ("بريمكس مجترات", "💊 إضافات", 0, 0, 0, 0, 0, 230, 100, 0),
            ("إنزيمات", "💊 إضافات", 0, 0, 0, 0, 0, 230, 100, 0),
        ]
        
        cursor.executemany('''
            INSERT INTO feeds (name, category, protein, lysine, methionine, digestibility, energy, price, max_limit, min_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', default_feeds)
        
        # إضافة مخزون افتراضي
        cursor.execute("SELECT name FROM feeds")
        for row in cursor.fetchall():
            cursor.execute("INSERT OR IGNORE INTO inventory (feed_name, quantity) VALUES (?, ?)", (row[0], 10.0))
        
        conn.commit()
    
    return conn

# ==========================================
# دوال مساعدة
# ==========================================

def load_feeds():
    """تحميل جميع المواد العلفية"""
    conn = init_database()
    df = pd.read_sql_query("SELECT * FROM feeds ORDER BY category, name", conn)
    conn.close()
    return df

def load_inventory():
    """تحميل المخزون"""
    conn = init_database()
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def update_inventory(feed_name, quantity):
    """تحديث المخزون"""
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET quantity = ?, last_update = CURRENT_TIMESTAMP WHERE feed_name = ?", (quantity, feed_name))
    conn.commit()
    conn.close()

def deduct_inventory(formula, tons):
    """خصم كمية من المخزون حسب التركيبة"""
    conn = init_database()
    cursor = conn.cursor()
    for name, pct in formula.items():
        qty_to_deduct = (pct / 100) * tons
        cursor.execute("UPDATE inventory SET quantity = quantity - ?, last_update = CURRENT_TIMESTAMP WHERE feed_name = ?", (qty_to_deduct, name))
    conn.commit()
    conn.close()

def save_formula(formula, cost, protein):
    """حفظ التركيبة في قاعدة البيانات"""
    import json
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO formulas (formula, cost, protein) VALUES (?, ?, ?)", (json.dumps(formula), cost, protein))
    conn.commit()
    conn.close()

def calculate_optimal_formula(selected_feeds, prices, target_protein, use_digestible=False):
    """
    حساب التركيبة المثلى باستخدام البرمجة الخطية
    """
    n = len(selected_feeds)
    
    # دالة الهدف (التكلفة)
    c = prices
    
    # قيد المساواة: مجموع النسب = 100%
    A_eq = [[1.0] * n]
    b_eq = [100.0]
    
    # قيد البروتين
    protein_row = []
    for feed in selected_feeds:
        protein = feed.get('protein', 0)
        digestibility = feed.get('digestibility', 0.85) if use_digestible else 1.0
        protein_row.append(protein * digestibility)
    
    A_eq.append(protein_row)
    b_eq.append(target_protein)
    
    # حدود المكونات
    bounds = []
    for feed in selected_feeds:
        min_limit = feed.get('min_limit', 0)
        max_limit = feed.get('max_limit', 100)
        bounds.append((min_limit, max_limit))
    
    # حل المشكلة
    result = linprog(
        c, 
        A_eq=A_eq, 
        b_eq=b_eq, 
        bounds=bounds, 
        method='highs'
    )
    
    return result

# ==========================================
# واجهة تسجيل الدخول
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user_name = None

if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="color: #2e7d32; font-size: 48px; margin-bottom: 10px;">🌾 منصة تاور العلمية</h1>
        <h2 style="color: #555; font-size: 24px; margin-bottom: 5px;">للانتاج الحيواني وتركيب الاعلاف</h2>
        <p style="color: #888; font-size: 18px; margin-bottom: 30px;">الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code = st.text_input("🔑 كود الدخول", type="password", placeholder="أدخل الكود هنا")
        
        if st.button("تسجيل الدخول", type="primary", use_container_width=True):
            if code in USERS:
                st.session_state.logged_in = True
                st.session_state.role = USERS[code]["role"]
                st.session_state.user_name = USERS[code]["name"]
                st.rerun()
            else:
                st.error("❌ الكود الذي أدخلته غير صحيح")
        
        st.caption("🔐 للأمن والسلامة، هذا النظام محمي")
    
    st.stop()

# ==========================================
# الشريط الجانبي
# ==========================================

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <h3 style="color: #2e7d32; margin: 0;">{st.session_state.user_name}</h3>
        <p style="color: #888; font-size: 12px;">{st.session_state.role}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # معلومات سريعة
    st.markdown("### 📊 معلومات")
    
    conn = init_database()
    feeds_count = pd.read_sql_query("SELECT COUNT(*) as c FROM feeds", conn).iloc[0]['c']
    conn.close()
    
    st.metric("📦 المواد العلفية", feeds_count)
    
    if 'last_cost' in st.session_state:
        st.metric("💰 آخر تكلفة طن", f"${st.session_state.last_cost:.2f}")
    
    st.markdown("---")
    
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2026")
    st.caption("الاختصاصي م. عبد القادر إسماعيل تاور")

# ==========================================
# المحتوى الرئيسي
# ==========================================

# تهيئة قاعدة البيانات
init_database()

# تحميل البيانات
df_feeds = load_feeds()
df_inventory = load_inventory()

# العنوان
st.title("🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
st.caption("الاختصاصي م. عبد القادر إسماعيل تاور - نظام الاستمثال الخطي المتقدم")
st.markdown("---")

# ==========================================
# التبويبات الرئيسية
# ==========================================

tabs = st.tabs(["🔬 تركيب الأعلاف", "📦 إدارة المخزون", "📊 التركيبات السابقة", "📚 المساعدة والدليل"])

# ==========================================
# التبويب الأول: تركيب الأعلاف
# ==========================================

with tabs[0]:
    st.subheader("🎯 محرك تركيب الأعلاف الذكي (Least-Cost Formulation)")
    
    col1, col2 = st.columns(2)
    with col1:
        # إعدادات التركيب
        st.markdown("### ⚙️ إعدادات التركيب")
        
        target_protein = st.slider(
            "🎯 نسبة البروتين المستهدفة (%)", 
            min_value=5.0, 
            max_value=40.0, 
            value=16.0, 
            step=0.5,
            help="نسبة البروتين المطلوبة في العلف النهائي"
        )
        
        use_digestible = st.toggle(
            "🧬 استخدام البروتين المهضوم (DP)", 
            value=True,
            help="البروتين المهضوم يعطي دقة علمية أعلى من البروتين الخام"
        )
        
        # إضافة ملاحظة عن القطاع
        sector = st.selectbox(
            "🐏 القطاع الإنتاجي",
            ["عام", "دواجن لاحم", "دواجن بياض", "أبقار حلابة", "تسمين عجول", "أغنام وماعز", "خيول", "أسماك"],
            help="اختيار القطاع يساعد في ضبط التوصيات"
        )
    
    with col2:
        st.markdown("### 📦 المكونات المتاحة")
        st.info(f"📊 عدد المواد العلفية المتاحة: {len(df_feeds)} مادة")
        
        # عرض أسعار السوق
        with st.expander("📈 أسعار السوق الحالية"):
            for _, row in df_feeds.iterrows():
                st.write(f"**{row['name']}**: ${row['price']:.0f}/طن")
    
    st.markdown("---")
    
    # اختيار المكونات
    st.markdown("### ✅ اختر مكونات العلف المستخدمة")
    st.caption("💡 نصيحة: اختر 3-6 مكونات للحصول على أفضل نتيجة")
    
    selected_feeds = []
    selected_data = []
    prices = []
    
    # عرض المكونات في أعمدة
    cols = st.columns(3)
    for idx, row in df_feeds.iterrows():
        with cols[idx % 3]:
            # الحصول على الكمية من المخزون
            inv_qty = df_inventory[df_inventory['feed_name'] == row['name']]['quantity'].values
            inv_qty = inv_qty[0] if len(inv_qty) > 0 else 0
            
            # عرض المكون مع كميته
            label = f"{row['name']}"
            if inv_qty > 0:
                label += f" (متوفر: {inv_qty:.1f} طن)"
            
            if st.checkbox(label, key=f"select_{row['name']}"):
                selected_feeds.append(row['name'])
                
                # السعر (يمكن تعديله للمالك فقط)
                if st.session_state.role == "owner":
                    price = st.number_input(
                        f"سعر {row['name']} ($/طن)",
                        value=float(row['price']),
                        key=f"price_{row['name']}",
                        step=5.0
                    )
                else:
                    price = row['price']
                    st.caption(f"💰 السعر: ${price:.0f}/طن")
                
                prices.append(price)
                selected_data.append({
                    'name': row['name'],
                    'protein': row['protein'],
                    'digestibility': row['digestibility'],
                    'min_limit': row['min_limit'],
                    'max_limit': row['max_limit'],
                    'price': price
                })
    
    # زر التشغيل
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
            if len(selected_feeds) < 2:
                st.warning("⚠️ يرجى اختيار مكونين على الأقل (مثال: ذرة + كسب صويا)")
            else:
                with st.spinner("🧮 جاري حساب التركيبة المثلى..."):
                    try:
                        result = calculate_optimal_formula(
                            selected_data, 
                            prices, 
                            target_protein, 
                            use_digestible
                        )
                        
                        if result.success:
                            st.balloons()
                            st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                            
                            # عرض النتائج
                            res_col1, res_col2 = st.columns(2)
                            
                            with res_col1:
                                st.markdown("### 📝 المقادير لكل طن")
                                st.markdown("---")
                                
                                formula_dict = {}
                                for name, pct in zip(selected_feeds, result.x):
                                    if pct > 0.01:
                                        formula_dict[name] = pct
                                        # حساب الوزن بالكيلوجرام
                                        kg = pct * 10
                                        st.markdown(f"""
                                        <div style="background-color: #f0f8f0; padding: 10px 15px; margin: 8px 0; border-radius: 10px; border-right: 4px solid #2e7d32;">
                                            <span style="font-size: 16px; font-weight: bold;">🌾 {name}</span><br>
                                            <span style="font-size: 20px; font-weight: bold; color: #2e7d32;">{pct:.1f}%</span>
                                            <span style="font-size: 14px; color: #666;"> → {kg:.1f} كجم / طن</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                # حفظ التركيبة
                                st.session_state['last_formula'] = formula_dict
                                st.session_state['last_cost'] = result.fun
                                st.session_state['last_protein'] = target_protein
                                
                                # حفظ في قاعدة البيانات
                                save_formula(formula_dict, result.fun, target_protein)
                            
                            with res_col2:
                                st.markdown("### 💰 التكاليف والمواصفات")
                                st.markdown("---")
                                
                                st.metric("💰 تكلفة الطن الواحد", f"${result.fun:.2f}")
                                st.metric("🧬 نسبة البروتين", f"{target_protein:.1f}%")
                                
                                # حساب معادل النشاء التقريبي
                                st.markdown("---")
                                st.markdown("### 🎯 توصيات الاستخدام")
                                
                                if sector == "دواجن لاحم":
                                    st.info("🐔 مناسب لدواجن التسمين - أضف البريمكس المخصص")
                                elif sector == "دواجن بياض":
                                    st.info("🥚 مناسب للبياض - أضف كالسيوم إضافي")
                                elif sector == "أبقار حلابة":
                                    st.info("🐄 مناسب للأبقار الحلابة - أضف بيكربونات الصوديوم")
                                else:
                                    st.info("✅ يمكن استخدام هذه التركيبة مباشرة")
                            
                            # خيارات التصدير
                            st.markdown("---")
                            st.markdown("### 📎 تصدير التقرير")
                            
                            col_share, col_save = st.columns(2)
                            with col_share:
                                share_text = f"🌾 منصة تاور العلمية - خلطة علفية بتكلفة ${result.fun:.2f}/طن، بروتين {target_protein}%"
                                whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
                                st.link_button("📱 مشاركة عبر واتساب", whatsapp_url, use_container_width=True)
                            
                            with col_save:
                                # خصم من المخزون
                                if st.button("📦 خصم من المخزون", use_container_width=True):
                                    tons = st.number_input("الكمية المنتجة (طن)", min_value=0.1, value=1.0, step=0.5, key="deduct_tons_main")
                                    if tons > 0:
                                        deduct_inventory(formula_dict, tons)
                                        st.success(f"✅ تم خصم {tons} طن من المخزون")
                                        st.rerun()
                        
                        else:
                            st.error("❌ لم يتم إيجاد حل مناسب للتركيبة")
                            st.markdown("""
                            ### 💡 اقتراحات لحل المشكلة:
                            
                            1. **أضف المزيد من المكونات** - خاصة مصادر البروتين (كسب صويا، أمباز فول)
                            
                            2. **خفف نسبة البروتين** - جرب خفضها بمقدار 1-2%
                            
                            3. **تأكد من الأسعار** - الأسعار المنخفضة جداً قد تسبب مشاكل
                            
                            4. **أضف مكونات جديدة** - مثل كسب عباد الشمس أو كسب بذور القطن
                            """)
                    
                    except Exception as e:
                        st.error(f"حدث خطأ تقني: {str(e)}")

# ==========================================
# التبويب الثاني: إدارة المخزون
# ==========================================

with tabs[1]:
    st.subheader("📦 إدارة المخزون والمستودعات")
    
    # خصم سريع من آخر خلطة
    if 'last_formula' in st.session_state and st.session_state['last_formula']:
        with st.expander("🔄 خصم مكونات آخر خلطة من المخزون", expanded=False):
            col_tons, col_btn = st.columns([2, 1])
            with col_tons:
                tons = st.number_input("الكمية المنتجة (طن):", min_value=0.1, value=1.0, step=0.5, key="deduct_tons_inv")
            with col_btn:
                if st.button("تأكيد الخصم", type="primary"):
                    deduct_inventory(st.session_state['last_formula'], tons)
                    st.success(f"✅ تم خصم {tons} طن من المخزون")
                    st.rerun()
    
    st.markdown("---")
    
    # عرض المخزون الحالي
    st.markdown("### 📊 الأرصدة الحالية")
    
    # تحديث بيانات المخزون
    df_inventory = load_inventory()
    df_inventory = df_inventory.merge(df_feeds[['name', 'category']], left_on='feed_name', right_on='name', how='left')
    
    # عرض المخزون
    cols = st.columns(3)
    for idx, row in df_inventory.iterrows():
        with cols[idx % 3]:
            qty = row['quantity']
            name = row['feed_name']
            category = row.get('category', 'مواد')
            
            # تحديد الحالة واللون
            if qty <= 0:
                status = "🔴 نفد"
                color = "#ffebee"
                border_color = "#c62828"
            elif qty < 2:
                status = "🟡 حرج"
                color = "#fff3e0"
                border_color = "#f9a825"
            elif qty < 10:
                status = "🟢 منخفض"
                color = "#e8f5e9"
                border_color = "#2e7d32"
            else:
                status = "✅ جيد"
                color = "#c8e6c9"
                border_color = "#1b5e20"
            
            if st.session_state.role == "owner":
                new_qty = st.number_input(
                    f"{name}",
                    value=float(max(0, qty)),
                    key=f"inv_{name}",
                    step=1.0,
                    label_visibility="collapsed"
                )
                if new_qty != qty:
                    update_inventory(name, new_qty)
                st.caption(f"{category} - {status}")
            else:
                st.markdown(f"""
                <div style="background-color: {color}; padding: 12px; margin: 5px 0; border-radius: 10px; border-right: 4px solid {border_color};">
                    <b style="font-size: 14px;">{name}</b><br>
                    <span style="font-size: 22px; font-weight: bold;">{qty:.1f}</span>
                    <span style="font-size: 14px;"> طن</span><br>
                    <span style="font-size: 11px; color: #666;">{category} - {status}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # إضافة مواد جديدة للمالك فقط
    if st.session_state.role == "owner":
        st.markdown("---")
        with st.expander("➕ إضافة مادة علفية جديدة", expanded=False):
            col_new1, col_new2 = st.columns(2)
            with col_new1:
                new_name = st.text_input("اسم المادة")
                new_category = st.selectbox("التصنيف", ["🌾 حبوب", "🥜 بروتين", "🐟 بروتين حيواني", "🌾 مخلفات", "🧂 أملاح", "💊 إضافات"])
                new_protein = st.number_input("نسبة البروتين (%)", min_value=0.0, max_value=100.0, value=0.0)
            
            with col_new2:
                new_price = st.number_input("السعر ($/طن)", min_value=0.0, value=100.0)
                new_digestibility = st.slider("معامل الهضم", 0.0, 1.0, 0.85)
                new_energy = st.number_input("معادل النشاء (SE)", min_value=0.0, value=50.0)
            
            if st.button("💾 إضافة المادة", type="primary"):
                if new_name:
                    conn = init_database()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO feeds (name, category, protein, digestibility, energy, price, max_limit, min_limit)
                            VALUES (?, ?, ?, ?, ?, ?, 100, 0)
                        ''', (new_name, new_category, new_protein, new_digestibility, new_energy, new_price))
                        cursor.execute("INSERT INTO inventory (feed_name, quantity) VALUES (?, 0)", (new_name,))
                        conn.commit()
                        st.success(f"✅ تم إضافة {new_name} بنجاح")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                    finally:
                        conn.close()

# ==========================================
# التبويب الثالث: التركيبات السابقة
# ==========================================

with tabs[2]:
    st.subheader("📊 تاريخ التركيبات السابقة")
    
    conn = init_database()
    df_formulas = pd.read_sql_query("SELECT * FROM formulas ORDER BY date DESC", conn)
    conn.close()
    
    if len(df_formulas) > 0:
        st.markdown(f"📋 عدد التركيبات المحفوظة: **{len(df_formulas)}**")
        
        for idx, row in df_formulas.iterrows():
            with st.expander(f"📅 {row['date']} - تكلفة: ${row['cost']:.2f} - بروتين: {row['protein']:.1f}%"):
                import json
                formula = json.loads(row['formula'])
                for name, pct in formula.items():
                    st.write(f"• {name}: {pct:.1f}% ({pct*10:.1f} كجم/طن)")
    else:
        st.info("💡 لا توجد تركيبات سابقة. قم بتركيب علفة أولاً لحفظها هنا.")

# ==========================================
# التبويب الرابع: المساعدة والدليل
# ==========================================

with tabs[3]:
    st.subheader("📖 دليل المستخدم والمساعدة")
    
    col_guide1, col_guide2 = st.columns(2)
    
    with col_guide1:
        st.markdown("""
        ### 🔑 أكواد الدخول والصلاحيات
        
        | الكود | الصلاحية | الميزات |
        |-------|----------|---------|
        | `202687` | **مالك المنصة** 👑 | صلاحية كاملة - تعديل الأسعار، إضافة مواد، إدارة المخزون |
        | `2020` | **مختص / طبيب بيطري** 👨‍🔬 | صلاحية متقدمة - تركيب، مشاهدة المخزون |
        | `2026` | **مربي** 🌾 | صلاحية أساسية - تركيب الأعلاف فقط |
        
        ---
        
        ### 🎯 كيفية استخدام المنصة
        
        **الخطوة 1:** اختر المكونات العلفية المتوفرة لديك
        - يُفضل اختيار 4-6 مكونات للحصول على أفضل نتيجة
        - المكونات الأساسية الموصى بها: ذرة + كسب صويا + نخالة + أملاح
        
        **الخطوة 2:** حدد نسبة البروتين المستهدفة
        - دواجن لاحم: 21-23%
        - دواجن بياض: 16-18%
        - أبقار حلابة: 14-16%
        - تسمين عجول: 12-14%
        - أغنام وماعز: 12-16%
        
        **الخطوة 3:** اضغط "تشغيل محرك الاستمثال الخطي"
        
        **الخطوة 4:** استخدم النتيجة مباشرة في مزرعتك أو قم بخصمها من المخزون
        """)
    
    with col_guide2:
        st.markdown("""
        ### 💡 نصائح مهمة للنجاح
        
        1. **كلما زاد عدد المكونات**، كانت النتيجة أفضل والتكلفة أقل
        
        2. **تأكد من صحة الأسعار** المدخلة للحصول على تكلفة حقيقية
        
        3. **استخدم البروتين المهضوم (DP)** للحصول على دقة علمية أعلى
        
        4. **راقب المخزون** وتأكد من توفر المواد قبل الإنتاج
        
        5. **أضف البريمكسات** بنسبة 0.5-1% للتركيبات النهائية
        
        ---
        
        ### 📚 مصطلحات علمية
        
        - **البروتين المهضوم (DP):** البروتين الفعلي الذي يمتصه الحيوان
        - **معادل النشاء (SE):** مقياس لطاقة العلف
        - **البرمجة الخطية (LP):** تقنية رياضية لإيجاد أقل تكلفة
        
        ---
        
        ### 📞 التواصل والدعم
        
        للاستفسارات والاستشارات الفنية:
        """)
        
        if st.button("📱 تواصل عبر واتساب", use_container_width=True):
            st.info("سيتم إضافة رقم واتساب قريباً")
    
    st.markdown("---")
    st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور - جميع الحقوق محفوظة")
    st.caption("منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - الإصدار 2.0")

# ==========================================
# نهاية الكود
# ==========================================
