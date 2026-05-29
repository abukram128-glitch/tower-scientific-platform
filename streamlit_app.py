import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize 
import linprog
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
)

# ==========================================
# أكواد الدخول
# ==========================================

CODES = {
    "202687": "owner",
    "2020": "specialist",
    "2026": "breeder"
}

ROLE_NAMES = {
    "owner": "المالك 👑",
    "specialist": "المختص 👨‍🔬",
    "breeder": "المربي 🌾"
}

# ==========================================
# تهيئة قاعدة البيانات
# ==========================================

@st.cache_resource
def get_db():
    conn = sqlite3.connect('tower.db', check_same_thread=False)
    c = conn.cursor()
    
    # إنشاء جدول المكونات
    c.execute('''
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            protein REAL,
            price REAL
        )
    ''')
    
    # إضافة بيانات افتراضية
    c.execute("SELECT COUNT(*) FROM feeds")
    if c.fetchone()[0] == 0:
        default_feeds = [
            ("ذرة صفراء", "حبوب", 8.5, 230),
            ("ذرة بيضاء", "حبوب", 8.8, 225),
            ("شعير", "حبوب", 11.5, 210),
            ("كسب فول صويا 44%", "بروتين", 44.0, 440),
            ("كسب فول صويا 48%", "بروتين", 48.0, 480),
            ("كسب عباد الشمس", "بروتين", 36.0, 310),
            ("ملح الطعام", "أملاح", 0, 30),
            ("الحجر الجيري", "أملاح", 0, 40),
            ("فوسفات ثنائي الكالسيوم", "أملاح", 0, 280),
        ]
        c.executemany("INSERT INTO feeds (name, category, protein, price) VALUES (?, ?, ?, ?)", default_feeds)
        conn.commit()
    
    return conn

# ==========================================
# دوال الحساب
# ==========================================

def calculate_formula(selected_feeds, target_protein):
    """حساب التركيبة المثلى باستخدام البرمجة الخطية"""
    
    n = len(selected_feeds)
    
    # مصفوفة التكلفة
    c = [feed["price"] for feed in selected_feeds]
    
    # قيد المساواة: مجموع النسب = 100
    A_eq = [[1] * n]
    b_eq = [100]
    
    # قيد البروتين
    protein_row = [feed["protein"] for feed in selected_feeds]
    A_eq.append(protein_row)
    b_eq.append(target_protein)
    
    # حدود المكونات (0% إلى 100%)
    bounds = [(0, 100) for _ in range(n)]
    
    # حل المشكلة
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    return result

# ==========================================
# واجهة تسجيل الدخول
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    # شاشة تسجيل الدخول
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="color: #2e7d32;">🌾 منصة تاور العلمية</h1>
        <h3>للانتاج الحيواني وتركيب الاعلاف</h3>
        <p style="color: #666;">الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code = st.text_input("🔑 كود الدخول", type="password", placeholder="أدخل الكود هنا")
        if st.button("دخول", type="primary", use_container_width=True):
            if code in CODES:
                st.session_state.logged_in = True
                st.session_state.role = CODES[code]
                st.rerun()
            else:
                st.error("❌ الكود غير صحيح")
    st.stop()

# ==========================================
# الشريط الجانبي
# ==========================================

with st.sidebar:
    st.markdown(f"### 👋 {ROLE_NAMES[st.session_state.role]}")
    st.markdown("---")
    
    if st.button("🚪 تسجيل خروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    st.markdown("---")
    st.caption("© 2026")
    st.caption("منصة تاور العلمية")

# ==========================================
# المحتوى الرئيسي
# ==========================================

# العنوان
st.title("🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
st.caption("الاختصاصي م. عبد القادر إسماعيل تاور")
st.markdown("---")

# تحميل البيانات
conn = get_db()
df = pd.read_sql_query("SELECT * FROM feeds", conn)

# ==========================================
# تبويب تركيب الأعلاف
# ==========================================

st.subheader("🎯 نظام تركيب الأعلاف الذكي (أقل تكلفة)")

col1, col2 = st.columns(2)
with col1:
    target_protein = st.slider("🎯 نسبة البروتين المستهدفة (%)", 5.0, 40.0, 16.0, 0.5)

st.markdown("### 📦 اختر مكونات العلف:")

# عرض المكونات في أعمدة
selected_feeds = []
prices = []
selected_data = []

cols = st.columns(3)
for idx, row in df.iterrows():
    with cols[idx % 3]:
        if st.checkbox(f"{row['name']} ({row['category']})", key=f"feed_{row['name']}"):
            selected_feeds.append(row['name'])
            price = st.number_input(
                f"سعر {row['name']} ($/طن)",
                value=float(row['price']),
                key=f"price_{row['name']}",
                step=5.0
            )
            prices.append(price)
            selected_data.append({
                "name": row['name'],
                "protein": row['protein'],
                "price": price
            })

# زر التشغيل
if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
    
    if len(selected_feeds) < 2:
        st.warning("⚠️ يرجى اختيار مكونين على الأقل (مثال: ذرة + كسب صويا)")
    
    else:
        with st.spinner("🧮 جاري حساب التركيبة المثلى..."):
            try:
                result = calculate_formula(selected_data, target_protein)
                
                if result.success:
                    st.balloons()
                    st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                    
                    # عرض النتائج في عمودين
                    col_result1, col_result2 = st.columns(2)
                    
                    with col_result1:
                        st.markdown("### 📝 المقادير لكل طن:")
                        
                        formula_dict = {}
                        for name, pct in zip(selected_feeds, result.x):
                            if pct > 0.01:
                                formula_dict[name] = pct
                                st.markdown(f"""
                                <div style="background-color: #f0f8f0; padding: 8px 12px; margin: 5px 0; border-radius: 8px; border-right: 3px solid #2e7d32;">
                                    <b>{name}</b>: {pct:.1f}% → <b>{pct*10:.1f} كجم</b> لكل طن
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # حفظ التركيبة للاستخدام لاحقاً
                        st.session_state['last_formula'] = formula_dict
                    
                    with col_result2:
                        st.markdown("### 💰 التكاليف والجودة:")
                        st.metric("💰 تكلفة الطن الواحد", f"${result.fun:.2f}")
                        st.metric("🧬 نسبة البروتين", f"{target_protein:.1f}%")
                        
                        # حساب معادل النشاء التقريبي
                        st.info("💡 يمكنك استخدام هذه التركيبة مباشرة في مزرعتك")
                    
                    # حفظ التكلفة
                    st.session_state['last_cost'] = result.fun
                    st.session_state['last_protein'] = target_protein
                
                else:
                    st.error("❌ لم يتم إيجاد حل مناسب")
                    st.markdown("""
                    ### 💡 اقتراحات لحل المشكلة:
                    1. **أضف المزيد من المكونات** - خاصة مصادر البروتين (كسب صويا، أمباز فول)
                    2. **خفف نسبة البروتين** - جرب خفضها بمقدار 1-2%
                    3. **تأكد من الأسعار** - الأسعار المنخفضة جداً قد تسبب مشاكل
                    """)
            
            except Exception as e:
                st.error(f"حدث خطأ تقني: {str(e)}")

# ==========================================
# تبويب إدارة المخزون
# ==========================================

st.markdown("---")
st.subheader("📊 إدارة المخزون والمستودعات")

if 'inventory' not in st.session_state:
    st.session_state.inventory = {row['name']: 10.0 for _, row in df.iterrows()}

# خصم تلقائي من آخر خلطة
if 'last_formula' in st.session_state and st.session_state['last_formula']:
    with st.expander("🔄 خصم مكونات آخر خلطة من المخزون", expanded=False):
        col_tons, col_btn = st.columns([2, 1])
        with col_tons:
            tons = st.number_input("الكمية المنتجة (طن):", min_value=0.1, value=1.0, step=0.5, key="deduct_tons")
        with col_btn:
            st.write("")
            if st.button("تأكيد الخصم", type="primary"):
                for name, pct in st.session_state['last_formula'].items():
                    if name in st.session_state.inventory:
                        consumed = (pct / 100) * tons
                        st.session_state.inventory[name] = max(0, st.session_state.inventory[name] - consumed)
                st.success(f"✅ تم خصم {tons} طن من المخزون")
                st.rerun()

# عرض المخزون
st.markdown("### 📦 الأرصدة الحالية:")

cols = st.columns(3)
for idx, (name, qty) in enumerate(st.session_state.inventory.items()):
    with cols[idx % 3]:
        # تحديد لون الحالة
        if qty < 2:
            status = "🔴 حرج"
            color = "#ffebee"
        elif qty < 5:
            status = "🟡 منخفض"
            color = "#fff3e0"
        else:
            status = "🟢 جيد"
            color = "#e8f5e9"
        
        if st.session_state.role == "owner":
            new_qty = st.number_input(
                f"{name}",
                value=float(qty),
                key=f"inv_{name}",
                step=1.0,
                label_visibility="collapsed"
            )
            st.session_state.inventory[name] = new_qty
            st.caption(f"الحالة: {status}")
        else:
            st.markdown(f"""
            <div style="background-color: {color}; padding: 10px; margin: 5px 0; border-radius: 8px;">
                <b>{name}</b><br>
                <span style="font-size: 20px; font-weight: bold;">{qty:.1f} طن</span><br>
                <span style="font-size: 12px;">{status}</span>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# تبويب المساعدة
# ==========================================

st.markdown("---")
st.subheader("📖 المساعدة والدليل")

with st.expander("📚 أكواد الدخول والصلاحيات", expanded=True):
    st.markdown("""
    | الكود | الصلاحية | الميزات |
    |-------|----------|---------|
    | `202687` | مالك المنصة | صلاحية كاملة - تعديل الأسعار والمخزون |
    | `2020` | مختص / طبيب بيطري | صلاحية متقدمة - تركيب ومشاهدة |
    | `2026` | مربي | صلاحية أساسية - تركيب فقط |
    """)

with st.expander("🎯 كيفية استخدام المنصة", expanded=False):
    st.markdown("""
    **الخطوة 1:** اختر المكونات العلفية المتوفرة لديك
    - يفضل اختيار 4-6 مكونات للحصول على أفضل نتيجة
    
    **الخطوة 2:** حدد نسبة البروتين المستهدفة
    - الدواجن اللاحم: 21-23%
    - الدواجن البياض: 16-18%
    - المجترات: 12-16%
    
    **الخطوة 3:** اضغط "تشغيل محرك الاستمثال الخطي"
    
    **الخطوة 4:** استخدم النتيجة مباشرة في مزرعتك
    """)

with st.expander("💡 نصائح مهمة", expanded=False):
    st.markdown("""
    1. **كلما زاد عدد المكونات**، كانت النتيجة أفضل والتكلفة أقل
    2. **تأكد من صحة الأسعار** المدخلة للحصول على تكلفة حقيقية
    3. **يمكنك تعديل المخزون** في قسم إدارة المخزون
    4. **البروتين المهضوم** يعطي دقة علمية أعلى من البروتين الخام
    """)

# ==========================================
# التذييل
# ==========================================

st.markdown("---")
st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور - جميع الحقوق محفوظة")
st.caption("منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف")
