import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. تهيئة الصفحة والأمان والحماية ضد النسخ
# ==========================================
st.set_page_config(
    page_title="منتدى التغذية التطبيقية والهندسة الوراثية - د. عبد القادر إسماعيل",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص CSS منظم لتحسين الواجهة وجعلها سهلة الاستخدام
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* منع تحديد النصوص للحماية من النسخ */
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* إخفاء عناصر Streamlit التلقائية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* الهيدر الرئيسي للمنتدى */
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #ffffff;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
        border-right: 6px solid #0284C7;
    }
    
    .app-title {
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0;
        color: #F8FAFC;
    }
    
    .app-subtitle {
        font-size: 0.9rem;
        color: #38BDF8;
        margin-top: 5px;
        font-weight: 600;
    }
    
    /* بطاقات النتائج */
    .stMetric {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 12px;
        border-radius: 8px;
    }
    
    .card-info {
        background-color: #F1F5F9;
        border-right: 4px solid #0284C7;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        color: #334155;
    }
    
    .watermark {
        font-size: 0.8rem;
        color: #64748B;
        text-align: center;
        padding: 10px;
    }
    </style>

    <!-- سكربت حماية لمنع الزر الأيمن واختصارات الفحص -->
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
            (e.ctrlKey && e.shiftKey && e.keyCode == 73) || 
            (e.ctrlKey && e.keyCode == 85)) {
            return false;
        }
    }
    </script>
""", unsafe_allow_html=True)


# ==========================================
# 2. قواعد البيانات والمدخلات الفنية الموسعة
# ==========================================
class DatabaseEngine:
    @staticmethod
    def get_livestock_breeds():
        return {
            "الأبقار": {
                "الكنانة (سوداني)": {"milk": 1200, "heat_tol": 95, "meat": 60},
                "البطانه (سوداني)": {"milk": 1500, "heat_tol": 90, "meat": 65},
                "البقارة (سوداني)": {"milk": 600, "heat_tol": 98, "meat": 75},
                "هولشتاين (Holstein)": {"milk": 8000, "heat_tol": 40, "meat": 50},
                "بلاكبوس أنغوس (Angus)": {"milk": 800, "heat_tol": 55, "meat": 95}
            },
            "الأغنام والماعز": {
                "الحمري (سوداني)": {"milk": 200, "heat_tol": 95, "growth": 85},
                "الكباشي (سوداني)": {"milk": 150, "heat_tol": 98, "growth": 90},
                "الدباسي (سوداني)": {"milk": 180, "heat_tol": 92, "growth": 88},
                "الماعز النوبي": {"milk": 600, "heat_tol": 90, "growth": 60},
                "ماعز البور (Boer)": {"milk": 300, "heat_tol": 70, "growth": 98},
                "غنم العساف (Assaf)": {"milk": 1200, "heat_tol": 65, "growth": 75}
            },
            "الدواجن وطيور الزينة": {
                "الدجاج البلدي السوداني": {"egg": 120, "heat_tol": 98, "weight": 1.3},
                "الفيومي": {"egg": 200, "heat_tol": 90, "weight": 1.5},
                "اللجهورن (Leghorn)": {"egg": 300, "heat_tol": 60, "weight": 1.8},
                "دجاج السيراما (Serama)": {"egg": 80, "heat_tol": 80, "weight": 0.5},
                "البادجي": {"egg": 0, "heat_tol": 85, "weight": 0.04},
                "الكوكاتيل": {"egg": 0, "heat_tol": 80, "weight": 0.09}
            }
        }

    @staticmethod
    def get_expanded_feed_ingredients():
        return pd.DataFrame([
            {"المادة الخام": "ذرة رفيعة (فتريتة)", "CP": 9.0, "ME_Kcal": 3200, "CF": 2.5, "EE": 3.5, "Ca": 0.03, "AvP": 0.12, "Cost_Kg": 1.20, "Max_Include": 65.0},
            {"المادة الخام": "ذرة صفراء مجروشة", "CP": 8.5, "ME_Kcal": 3350, "CF": 2.2, "EE": 3.8, "Ca": 0.02, "AvP": 0.10, "Cost_Kg": 1.35, "Max_Include": 60.0},
            {"المادة الخام": "أمباز / كسبة زهرة الشمس (SSC)", "CP": 28.0, "ME_Kcal": 2200, "CF": 22.0, "EE": 6.0, "Ca": 0.35, "AvP": 0.20, "Cost_Kg": 1.75, "Max_Include": 25.0},
            {"المادة الخام": "أمباز السوداني (Groundnut Cake)", "CP": 45.0, "ME_Kcal": 2500, "CF": 6.5, "EE": 7.0, "Ca": 0.20, "AvP": 0.18, "Cost_Kg": 2.60, "Max_Include": 20.0},
            {"المادة الخام": "كسبة فول الصويا (44%)", "CP": 44.0, "ME_Kcal": 2230, "CF": 6.0, "EE": 1.5, "Ca": 0.29, "AvP": 0.22, "Cost_Kg": 3.10, "Max_Include": 30.0},
            {"المادة الخام": "مركز بياض/تسمين مستورد (5%)", "CP": 40.0, "ME_Kcal": 2100, "CF": 3.0, "EE": 2.0, "Ca": 6.50, "AvP": 3.00, "Cost_Kg": 5.80, "Max_Include": 5.0},
            {"المادة الخام": "نخالة القمح (ردة)", "CP": 15.0, "ME_Kcal": 1300, "CF": 11.0, "EE": 4.0, "Ca": 0.14, "AvP": 0.28, "Cost_Kg": 0.95, "Max_Include": 25.0},
            {"المادة الخام": "مولاس القصب", "CP": 4.0, "ME_Kcal": 1900, "CF": 0.0, "EE": 0.1, "Ca": 0.80, "AvP": 0.08, "Cost_Kg": 0.70, "Max_Include": 5.0},
            {"المادة الخام": "حجر جيري (Limestone)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 38.0, "AvP": 0.00, "Cost_Kg": 0.20, "Max_Include": 4.0},
            {"المادة الخام": "ثنائي فوسفات الكالسيوم (DCP)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 22.0, "AvP": 18.0, "Cost_Kg": 2.20, "Max_Include": 2.0},
            {"المادة الخام": "ملح الطعام (NaCl)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 0.30, "Max_Include": 0.5},
            {"المادة الخام": "مخلوط فيتامينات ومعادن (Premix)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 8.00, "Max_Include": 0.5}
        ])


# ==========================================
# 3. محرك التخطيط الخطي المحمي
# ==========================================
class AdvancedFeedOptimizer:
    def __init__(self, ingredients_df, target_cp, target_me, target_cf_max, target_ca, target_avp):
        self.df = ingredients_df
        self.target_cp = target_cp
        self.target_me = target_me
        self.target_cf_max = target_cf_max
        self.target_ca = target_ca
        self.target_avp = target_avp

    def optimize(self):
        try:
            costs = self.df["Cost_Kg"].values
            cp = self.df["CP"].values
            me = self.df["ME_Kcal"].values
            cf = self.df["CF"].values
            ca = self.df["Ca"].values
            avp = self.df["AvP"].values
            max_bounds = self.df["Max_Include"].values / 100.0

            A_eq = [np.ones(len(costs))]
            b_eq = [1.0]

            A_ub = [-cp, -me, cf, -ca, -avp]
            b_ub = [-self.target_cp, -self.target_me, self.target_cf_max, -self.target_ca, -self.target_avp]

            bounds = [(0, b) for b in max_bounds]
            return linprog(costs, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        except Exception:
            return None


# ==========================================
# 4. الهيدر الرئيسي وتوثيق المنتدى
# ==========================================
st.markdown("""
    <div class="app-header">
        <div class="app-title">منتدى التغذية التطبيقية وتخطيط الأنساب للإنتاج الحيواني</div>
        <div class="app-subtitle">تطوير وتصميم: أخصائي الإنتاج الحيواني | د. عبد القادر إسماعيل</div>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# 5. القائمة الجانبية (Sidebar)
# ==========================================
st.sidebar.markdown("### أروقة المنتدى")
app_mode = st.sidebar.radio("", [
    "1. محاكي الأنساب والتنبؤ الوراثي",
    "2. تركيب العلائق بأقل تكلفة (Least-Cost)",
    "3. دراسة إحلال كسبة زهرة الشمس",
    "4. المراجع والمواصفات القياسية"
])

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='watermark'>الملكية الفكرية محفوظة ©<br><b>د. عبد القادر إسماعيل</b></div>", unsafe_allow_html=True)


# ==========================================
# 6. التبويب الأول: التحسين الوراثي
# ==========================================
if "1." in app_mode:
    st.subheader("🧬 محاكاة خلط الأنساب وحساب القيمة التربوية")
    st.write("اختر السلالات ونظام التهجين لحساب نسب الدم المتوقعة ومستوى التحمل البيئي.")

    col_cat, col_sys = st.columns(2)
    breeds_db = DatabaseEngine.get_livestock_breeds()
    
    with col_cat:
        selected_species = st.selectbox("القطاع الإنتاجي:", list(breeds_db.keys()))
    with col_sys:
        mating_sys = st.selectbox("نظام التهجين المستهدف:", [
            "الجيل الأول (F1 Cross - 50%)",
            "خلط رجعي للذكر (Backcross to Sire - 75%)",
            "خلط رجعي للأنثى (Backcross to Dam - 75%)",
            "الجيل الثاني (F2 Generation)"
        ])

    st.markdown("#### ♂️ ♀️ اختيار الآباء")
    col_sire, col_dam = st.columns(2)
    available_breeds = list(breeds_db[selected_species].keys())

    with col_sire:
        sire_name = st.selectbox("سلالة الذكر (Sire):", available_breeds, index=3 if len(available_breeds)>3 else 0)
        sire_data = breeds_db[selected_species][sire_name]

    with col_dam:
        dam_name = st.selectbox("سلالة الأنثى (Dam):", available_breeds, index=1 if "البطانه" in available_breeds else 0)
        dam_data = breeds_db[selected_species][dam_name]

    if "F1" in mating_sys or "F2" in mating_sys:
        s_frac, d_frac = 50.0, 50.0
    elif "Sire" in mating_sys:
        s_frac, d_frac = 75.0, 25.0
    else:
        s_frac, d_frac = 25.0, 75.0

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("نسبة دم الذكر", f"{s_frac}%", sire_name)
    m2.metric("نسبة دم الأنثى", f"{d_frac}%", dam_name)
    m3.metric("مستوى التكيف والتحمل البيئي", f"{int((sire_data.get('heat_tol', 50)*(s_frac/100)) + (dam_data.get('heat_tol', 50)*(d_frac/100)))}%")

    categories = [k for k in sire_data.keys() if isinstance(sire_data[k], (int, float))]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[sire_data.get(k, 0) for k in categories], theta=categories, fill='toself', name=f'الذكر: {sire_name}'))
    fig.add_trace(go.Scatterpolar(r=[dam_data.get(k, 0) for k in categories], theta=categories, fill='toself', name=f'الأنثى: {dam_name}'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 7. التبويب الثاني: تركيب العلائق (منظم ومبسط)
# ==========================================
elif "2." in app_mode:
    st.subheader("🌾 صياغة العلائق الاقتصادية متوازنة العناصر")
    st.write("تم تنظيم هذا القسم في تبويبات مخصصة لتبسيط إدخال البيانات وحساب التركيبة المثالية بسهولة.")

    # تقسيم الواجهة إلى تبويبات لسهولة الاستخدام
    tab_req, tab_ingredients = st.tabs(["1️⃣ الاحتياجات الغذائية", "2️⃣ جدول المواد الخام والقيم"])

    with tab_req:
        st.markdown("##### حدد الاحتياجات الكيميائية المستهدفة للتركيبة:")
        r1, r2, r3 = st.columns(3)
        with r1:
            req_cp = st.number_input("البروتين الخام (CP %):", 8.0, 30.0, 18.0, step=0.5)
            req_ca = st.number_input("الكالسيوم الأدنى (Ca %):", 0.0, 5.0, 1.0, step=0.1)
        with r2:
            req_me = st.number_input("الطاقة (ME Kcal/Kg):", 1200, 3500, 2800, step=50)
            req_avp = st.number_input("الفوسفور المتاح (Av.P %):", 0.0, 2.0, 0.45, step=0.05)
        with r3:
            req_cf_max = st.number_input("الألياف القصوى (CF %):", 2.0, 25.0, 6.0, step=0.5)

    with tab_ingredients:
        st.markdown("##### جدول المواد الخام المتاحة (يمكنك تعديل الأسعار والتحليل):")
        feed_df = DatabaseEngine.get_expanded_feed_ingredients()
        edited_df = st.data_editor(feed_df, num_rows="dynamic", use_container_width=True)

    st.markdown("---")
    if st.button("🚀 حساب العليقة الاقتصادية المثالية", type="primary", use_container_width=True):
        optimizer = AdvancedFeedOptimizer(edited_df, req_cp, req_me, req_cf_max, req_ca, req_avp)
        res = optimizer.optimize()

        if res is not None and res.success:
            st.success("✅ تم التوصل إلى التركيبة المثالية الحاصدة لأقل تكلفة بنجاح!")
            
            sol_df = edited_df[["المادة الخام", "Cost_Kg", "CP", "ME_Kcal", "CF", "Ca", "AvP"]].copy()
            sol_df["النسبة في العليقة (%)"] = np.round(res.x * 100, 2)
            sol_df["الوزن للطن (كجم)"] = np.round(res.x * 1000, 1)
            sol_df["تكلفة العنصر/طن"] = np.round(res.x * 1000 * sol_df["Cost_Kg"], 2)

            active_sol = sol_df[sol_df["النسبة في العليقة (%)"] > 0].reset_index(drop=True)

            # عرض التكلفة أولاً
            total_cost_kg = res.fun
            c_cost1, c_cost2 = st.columns(2)
            c_cost1.metric("تكلفة الكيلوجرام الصافي", f"${total_cost_kg:.3f}")
            c_cost2.metric("التكلفة الإجمالية للطن", f"${total_cost_kg * 1000:.2f}")

            col_t, col_p = st.columns([1.8, 1.2])
            with col_t:
                st.markdown("##### 📋 المكونات المحسوبة في العليقة:")
                st.dataframe(active_sol, use_container_width=True)
            
            with col_p:
                fig_pie = px.pie(active_sol, values="النسبة في العليقة (%)", names="المادة الخام", title="توزيع مكونات العليقة")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            st.markdown("##### 🧪 التحليل الكيميائي المحسوب للعليقة الناتجة:")
            calc_cp = np.sum(res.x * edited_df["CP"].values)
            calc_me = np.sum(res.x * edited_df["ME_Kcal"].values)
            calc_cf = np.sum(res.x * edited_df["CF"].values)
            calc_ca = np.sum(res.x * edited_df["Ca"].values)
            calc_avp = np.sum(res.x * edited_df["AvP"].values)

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("البروتين (CP)", f"{calc_cp:.2f}%")
            c2.metric("الطاقة (ME)", f"{int(calc_me)} Kcal")
            c3.metric("الألياف (CF)", f"{calc_cf:.2f}%")
            c4.metric("الكالسيوم (Ca)", f"{calc_ca:.2f}%")
            c5.metric("الفوسفور (Av.P)", f"{calc_avp:.2f}%")

        else:
            st.error("❌ لم يتم العثور على حل يطابق القيود المحددة. يُرجى رفع حد الألياف المسموح به أو تقليل نسبة الكالسيوم/الفوسفور المستهدفة.")


# ==========================================
# 8. التبويب الثالث: تجربة أمباز/كسبة زهرة الشمس
# ==========================================
elif "3." in app_mode:
    st.subheader("📊 تقييم إحلال أمباز/كسبة زهرة الشمس (Sunflower Seed Cake)")
    st.write("محاكاة الأثر الاقتصادي عند استبدال كسبة زهرة الشمس بالمكونات التقليدية المرتفعة السعر.")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ssc_rate = st.slider("نسبة الإحلال في العليقة (%):", 0, 30, 15)
        flock_size = st.number_input("حجم القطيع (عدد الرؤوس/الطيور):", 100, 100000, 5000)
    with col_e2:
        daily_feed = st.number_input("معدل الاستهلاك اليومي للرأس (كجم):", 0.05, 15.0, 0.110, step=0.01)

    monthly_tons = ((flock_size * daily_feed) * 30) / 1000
    saved_per_ton = ssc_rate * 3.8
    total_savings = monthly_tons * saved_per_ton

    st.markdown("---")
    m_res1, m_res2, m_res3 = st.columns(3)
    m_res1.metric("إجمالي استهلاك العلف الشهري", f"{monthly_tons:.1f} طن")
    m_res2.metric("مقدار التوفير في سعر الطن", f"${saved_per_ton:.2f}")
    m_res3.metric("إجمالي الوفر المالي الشهري", f"${total_savings:.2f}")

    st.markdown("""
        <div class="card-info">
        <b>توصية خبير التغذية:</b> إحلال أمباز/كسبة زهرة الشمس حتى مستوى 15% في العلائق يمنح كفاءة تحويل غذائي ممتازة، ويحد من تكلفة الاستيراد، مع مراعاة موازنة الألياف باستخدام الإنزيمات الهاضمة في النسب الأعلى.
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# 9. التبويب الرابع: الدليل الميداني
# ==========================================
else:
    st.subheader("📚 الدليل الفني والمواصفات القياسية للإنتاج الحيواني")
    
    st.markdown("#### السلالات المحلية وتأقلمها (أبقار البطانه والكنانة)")
    st.write("تمتاز أبقار البطانه والكنانة بالقدرة العالية على إنتاج الحليب تحت ظروف الحرارة المرتفعة والجفاف، وتعتبر حجر الزاوية في مشاريع التهجين والتحسين الوراثي في المنطقة.")

    st.markdown("#### جدول الاحتياجات الغذائية القياسية للقطاعات المختلفة")
    st.table(pd.DataFrame({
        "القطاع الإنتاجي": ["دجاج تسمين (بادئ)", "دجاج بياض (ذروة)", "أبقار حليب (متوسطة)", "أغنام تسمين"],
        "البروتين الخام (CP %)": ["22.0%", "17.5%", "16.5%", "14.0%"],
        "الطاقة الممثلة (ME Kcal/kg)": ["3000", "2750", "2600", "2700"],
        "الألياف القصوى (CF %)": ["3.5%", "5.0%", "15.0%", "12.0%"],
        "الكالسيوم (Ca %)": ["1.0%", "3.8%", "0.7%", "0.6%"]
    }))
