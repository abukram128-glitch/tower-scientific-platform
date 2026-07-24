import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. تهيئة الصفحة والأنماط (Page Configuration & CSS)
# ==========================================
st.set_page_config(
    page_title="المنصة الشاملة للهندسة الوراثية وتغذية الحيوان",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة CSS مخصص لتحسين الواجهة العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stMetric {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .custom-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        border-right: 5px solid #2563eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. قواعد البيانات المدمجة (Embedded Data Engine)
# ==========================================
class DatabaseEngine:
    @staticmethod
    def get_livestock_breeds():
        return {
            "الأبقار": {
                "الكنانة (سوداني)": {"milk": 1200, "heat_tol": 95, "meat": 60, "origin": "محلية"},
                "البتانة (سوداني)": {"milk": 1500, "heat_tol": 90, "meat": 65, "origin": "محلية"},
                "البقارة (سوداني)": {"milk": 600, "heat_tol": 98, "meat": 75, "origin": "محلية"},
                "هولشتاين (Holstein)": {"milk": 8000, "heat_tol": 40, "meat": 50, "origin": "عالمية"},
                "بلاكبوس أنغوس (Angus)": {"milk": 800, "heat_tol": 55, "meat": 95, "origin": "عالمية"}
            },
            "الأغنام والماعز": {
                "الحمري (سوداني)": {"milk": 200, "heat_tol": 95, "growth": 85, "origin": "محلية"},
                "الكباشي (سوداني)": {"milk": 150, "heat_tol": 98, "growth": 90, "origin": "محلية"},
                "الدباسي (سوداني)": {"milk": 180, "heat_tol": 92, "growth": 88, "origin": "محلية"},
                "الماعز النوبي": {"milk": 600, "heat_tol": 90, "growth": 60, "origin": "محلية"},
                "ماعز البور (Boer)": {"milk": 300, "heat_tol": 70, "growth": 98, "origin": "عالمية"},
                "غنم العساف (Assaf)": {"milk": 1200, "heat_tol": 65, "growth": 75, "origin": "عالمية"}
            },
            "طيور الزينة والدواجن": {
                "الدجاج البلدي السوداني": {"egg": 120, "heat_tol": 98, "weight": 1.3, "fcr": 4.5},
                "الفيومي": {"egg": 200, "heat_tol": 90, "weight": 1.5, "fcr": 3.8},
                "اللجهورن (Leghorn)": {"egg": 300, "heat_tol": 60, "weight": 1.8, "fcr": 2.1},
                "دجاج السيراما (Serama)": {"egg": 80, "heat_tol": 80, "weight": 0.5, "fcr": 5.0},
                "البادجي (زينة)": {"egg": 0, "heat_tol": 85, "weight": 0.04, "fcr": 0},
                "الكوكاتيل (زينة)": {"egg": 0, "heat_tol": 80, "weight": 0.09, "fcr": 0}
            }
        }

    @staticmethod
    def get_feed_ingredients():
        return pd.DataFrame([
            {"المادة الخام": "ذرة رفيعة (فتريتة)", "CP": 9.0, "ME_Kcal": 3200, "CF": 2.5, "EE": 3.5, "Cost_Kg": 1.20, "Max_Include": 65.0},
            {"المادة الخام": "عسبار عباد الشمس (Sunflower Cake)", "CP": 28.0, "ME_Kcal": 2200, "CF": 22.0, "EE": 6.0, "Cost_Kg": 1.75, "Max_Include": 25.0},
            {"المادة الخام": "أمباز السوداني (Groundnut Cake)", "CP": 45.0, "ME_Kcal": 2500, "CF": 6.5, "EE": 7.0, "Cost_Kg": 2.60, "Max_Include": 20.0},
            {"المادة الخام": "مركز مستورد (Concentrate 5%)", "CP": 40.0, "ME_Kcal": 2100, "CF": 3.0, "EE": 2.0, "Cost_Kg": 5.80, "Max_Include": 5.0},
            {"المادة الخام": "نخالة القمح (ردة)", "CP": 15.0, "ME_Kcal": 1300, "CF": 11.0, "EE": 4.0, "Cost_Kg": 0.95, "Max_Include": 25.0},
            {"المادة الخام": "حجر جيري (Limestone)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Cost_Kg": 0.20, "Max_Include": 2.0},
            {"المادة الخام": "مخلوط فيتامينات ومعادن (Premix)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Cost_Kg": 8.00, "Max_Include": 0.5}
        ])


# ==========================================
# 3. محرك الوراثة والأنساب (Genetics Engine)
# ==========================================
class GeneticSimulator:
    def __init__(self, sire_data, dam_data, mating_system):
        self.sire = sire_data
        self.dam = dam_data
        self.system = mating_system

    def calculate_blood_fractions(self):
        if "F1" in self.system:
            return 50.0, 50.0
        elif "Backcross to Sire" in self.system:
            return 75.0, 25.0
        elif "Backcross to Dam" in self.system:
            return 25.0, 75.0
        elif "F2" in self.system:
            return 50.0, 50.0
        return 50.0, 50.0

    def estimate_performance(self):
        s_frac, d_frac = [f / 100.0 for f in self.calculate_blood_fractions()]
        
        # قوة الهجين (Heterosis) تكون في أوجها في F1
        heterosis_factor = 1.12 if "F1" in self.system else (1.05 if "F2" in self.system else 1.02)
        
        predicted_metrics = {}
        for key in self.sire.keys():
            if isinstance(self.sire[key], (int, float)) and key in self.dam:
                base_val = (self.sire[key] * s_frac) + (self.dam[key] * d_frac)
                if key != "heat_tol":  # عدم تضخيم تحمل الحرارة بقوة الهجين
                    predicted_metrics[key] = round(base_val * heterosis_factor, 2)
                else:
                    predicted_metrics[key] = round(base_val, 2)
                    
        return predicted_metrics


# ==========================================
# 4. محرك التخطيط الخطي للتغذية (Optimization Engine)
# ==========================================
class FeedOptimizer:
    def __init__(self, ingredients_df, target_cp, target_me):
        self.df = ingredients_df
        self.target_cp = target_cp
        self.target_me = target_me

    def optimize(self):
        costs = self.df["Cost_Kg"].values
        cp = self.df["CP"].values
        me = self.df["ME_Kcal"].values
        max_bounds = self.df["Max_Include"].values / 100.0

        # قيد المجموع = 100% (1.0)
        A_eq = [np.ones(len(costs))]
        b_eq = [1.0]

        # قيود الحد الأدنى للبروتين والطاقة
        A_ub = [
            -cp,     # -CP <= -target_cp
            -me      # -ME <= -target_me
        ]
        b_ub = [
            -self.target_cp,
            -self.target_me
        ]

        bounds = [(0, b) for b in max_bounds]

        res = linprog(costs, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        return res


# ==========================================
# 5. واجهة المستخدم (Streamlit Application UI)
# ==========================================

# العنوان الرئيسي
st.markdown('<h1 style="color:#1e3a8a;">🧬 المنصة المتكاملة للإنتاج الحيواني والتغذية التطبيقية</h1>', unsafe_allow_html=True)
st.caption("تطبيق علمي هجين لإدارة تحسين الأنساب وصياغة العلائق الاقتصادية | د. عبد القادر إسماعيل")
st.markdown("---")

# القائمة الجانبية
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3043/3043884.png", width=100)
st.sidebar.title("لوحة التحكم والوحدات")
app_mode = st.sidebar.selectbox("اختر الوحدة البرمجية:", [
    "🧬 1. محاكي الوراثة وتحسين الأنساب",
    "🌾 2. تركيب العلائق بأقل تكلفة (Least-Cost)",
    "📊 3. تحليل إحلال عسبار عباد الشمس (Sunflower SSC)",
    "📚 4. السجلات والدليل الفني"
])

# ------------------------------------------
# الوحدة الأولى: الوراثة والأنساب
# ------------------------------------------
if app_mode == "🧬 1. محاكي الوراثة وتحسين الأنساب":
    st.header("🧬 وحدة التنبؤ الوراثي وتحسين الأنساب")
    st.write("تقوم هذه الوحدة بحساب القيمة التربوية المتوقعة ومستوى الأداء والمناعة للهجن الناتجة.")

    col_category, col_system = st.columns(2)
    
    breeds_db = DatabaseEngine.get_livestock_breeds()
    
    with col_category:
        selected_species = st.selectbox("اختر القطاع الإنتاجي:", list(breeds_db.keys()))
    
    with col_system:
        mating_sys = st.selectbox("نظام الخلط والتزاوج المستهدف:", [
            "الجيل الأول (F1 Cross - 50%)",
            "خلط رجعي للأب (Backcross to Sire - 75%)",
            "خلط رجعي للأم (Backcross to Dam - 75%)",
            "الجيل الثاني (F2 Generation)"
        ])

    st.markdown("### 🧬 اختيار الآباء (Parents Selection)")
    col_sire, col_dam = st.columns(2)

    available_breeds = list(breeds_db[selected_species].keys())

    with col_sire:
        sire_name = st.selectbox("♂️ اختيار سلالة الذكر (Sire):", available_breeds, index=3 if len(available_breeds)>3 else 0)
        sire_data = breeds_db[selected_species][sire_name]
        st.json(sire_data, expanded=False)

    with col_dam:
        dam_name = st.selectbox("♀️ اختيار سلالة الأنثى (Dam):", available_breeds, index=0)
        dam_data = breeds_db[selected_species][dam_name]
        st.json(dam_data, expanded=False)

    # تشغيل محاكي الوراثة
    sim = GeneticSimulator(sire_data, dam_data, mating_sys)
    s_frac, d_frac = sim.calculate_blood_fractions()
    results = sim.estimate_performance()

    st.markdown("---")
    st.subheader("📊 نتائج التنبؤ الوراثي للجيل الناتج")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("نسبة دم الذكر", f"{s_frac}%", sire_name)
    m2.metric("نسبة دم الأنثى", f"{d_frac}%", dam_name)
    m3.metric("مستوى تحمل البيئة والحرارة", f"{results.get('heat_tol', 'N/A')}%")
    m4.metric("معامل قوة الهجين", "12%+" if "F1" in mating_sys else "5%+")

    # رسم بياني لمقارنة الصفات
    st.subheader("📈 مقارنة أداء الهجين مع الأبوين")
    
    categories = [k for k in results.keys() if isinstance(results[k], (int, float))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[sire_data.get(k, 0) for k in categories], theta=categories, fill='toself', name=f'الأب: {sire_name}'))
    fig.add_trace(go.Scatterpolar(r=[dam_data.get(k, 0) for k in categories], theta=categories, fill='toself', name=f'الأم: {dam_name}'))
    fig.add_trace(go.Scatterpolar(r=[results.get(k, 0) for k in categories], theta=categories, fill='toself', name='الجيل الناتج (Offspring)'))
    
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# الوحدة الثانية: تركيب العلائق بأقل تكلفة
# ------------------------------------------
elif app_mode == "🌾 2. تركيب العلائق بأقل تكلفة (Least-Cost)":
    st.header("🌾 وحدة البرمجة الخطية لتصنيع العلائق الاقتصادية")
    st.write("حساب التركيبة المثالية مع الالتزام التام بالاحتياجات الغذائية والحدود القصوى لإدخال المواد الخام.")

    col_req1, col_req2 = st.columns(2)
    with col_req1:
        req_cp = st.number_input("الحد الأدنى للبروتين الخام المطلوبة (CP %):", 10.0, 30.0, 18.0, step=0.5)
    with col_req2:
        req_me = st.number_input("الحد الأدنى للطاقة الممثلة (ME Kcal/Kg):", 1500, 3500, 2800, step=50)

    st.markdown("### 📋 جدول المواد الخام المتاحة والتحليل الكيميائي")
    feed_data = DatabaseEngine.get_feed_ingredients()
    
    edited_feed_df = st.data_editor(feed_data, num_rows="dynamic", use_container_width=True)

    if st.button("🚀 تشغيل الخوارزمية وحساب العليقة المثالية", type="primary"):
        optimizer = FeedOptimizer(edited_feed_df, req_cp, req_me)
        res = optimizer.optimize()

        if res.success:
            st.success("✅ تم العثور على التركيبة الأقل تكلفة التي تلبي كافة الشروط الفنية!")
            
            solution_df = edited_feed_df[["المادة الخام", "Cost_Kg", "CP", "ME_Kcal"]].copy()
            solution_df["النسبة في العليقة (%)"] = np.round(res.x * 100, 2)
            solution_df["الوزن لكل طن (كجم)"] = np.round(res.x * 1000, 1)
            solution_df["التكلفة المباشرة (لكل طن)"] = np.round(res.x * 1000 * solution_df["Cost_Kg"], 2)

            col_table, col_summary = st.columns([2, 1])
            with col_table:
                st.dataframe(solution_df, use_container_width=True)
            
            with col_summary:
                total_cost_kg = res.fun
                st.metric("التكلفة الإجمالية للكيلوجرام", f"${total_cost_kg:.3f}")
                st.metric("التكلفة الإجمالية للطن", f"${total_cost_kg * 1000:.2f}")
                
                # رسم بياني لدائرة المكونات
                fig_pie = px.pie(solution_df, values="النسبة في العليقة (%)", names="المادة الخام", title="توزيع المكونات في العليقة")
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error("❌ لم تنجح الخوارزمية في إيجاد حل ضمن هذه القيود. يرجى تخفيف قيود الطاقة أو رفع الحدود القصوى للمكونات.")

# ------------------------------------------
# الوحدة الثالثة: بحث إحلال عسبار عباد الشمس
# ------------------------------------------
elif app_mode == "📊 3. تحليل إحلال عسبار عباد الشمس (Sunflower SSC)":
    st.header("📊 المحاكي التفاعلي لإحلال عسبار عباد الشمس المحلي (SSC)")
    st.write("تقييم الأثر الاقتصادي والإنتاجي لاستبدال المركز المستورد والأنباز المحلي بعسبار زهرة الشمس.")

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        ssc_replacement_rate = st.slider("نسبة الإحلال في العليقة (Sunflower Cake %):", 0, 30, 15, 1)
        imported_conc_reduction = st.slider("نسبة تقليل المركز المستورد (%):", 0, 100, 50, 5)

    with col_exp2:
        flock_size = st.number_input("حجم القطيع / المزرعة (عدد الطيور أو الرؤوس):", 100, 100000, 5000)
        daily_feed_per_head = st.number_input("معدل الاستهلاك اليومي (كجم/رأس أو طائر):", 0.05, 15.0, 0.110, step=0.01)

    # حسابات الأثر الاقتصادي
    daily_total_feed = flock_size * daily_feed_per_head  # كجم/يوم
    monthly_feed_tons = (daily_total_feed * 30) / 1000  # طن/شهر
    
    # افتراض توفير 60 دولار في الطن عند استخدام 15% عسبار بدلاً من التركيزات المستوردة
    saved_per_ton = ssc_replacement_rate * 3.8  
    total_monthly_savings = monthly_feed_tons * saved_per_ton

    st.markdown("---")
    st.subheader("💡 نتائج المحاكاة المباشرة")

    res_c1, res_c2, res_c3 = st.columns(3)
    res_c1.metric("الاستهلاك الشهري للعلف", f"{monthly_feed_tons:.1f} طن")
    res_c2.metric("التوفير التقديري لكل طن", f"${saved_per_ton:.2f}")
    res_c3.metric("إجمالي التوفير الشهري", f"${total_monthly_savings:.2f}", delta="توفير عملة صعبة")

    st.markdown("""
    <div class="custom-card">
    <h4>📝 التوصية الفنية والتطبيقية:</h4>
    <ul>
        <li>أثبتت النتائج الميدانية أن استخدام عسبار زهرة الشمس حتى مستوى <b>15%</b> في علائق الدواجن (البياض والتسمين) لا يؤثر سلباً على معامل التحويل الغذائي (FCR).</li>
        <li>ينصح بإضافة الأنزيمات الهاضمة للألياف (مثل Xylanase) عند زيادة النسبة عن 15% للسيطرة على معامل الألياف الخام (CF).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# الوحدة الرابعة: السجلات والدليل الفني
# ------------------------------------------
else:
    st.header("📚 الدليل الفني والسجلات الميدانية")
    st.write("مرجع سريع للقيم الغذائية القياسية ومواصفات السلالات المحلية.")

    tab_ref1, tab_ref2 = st.tabs(["📋 الاحتياجات الغذائية القياسية", "🧬 الأطلس الميداني للسلالات"])

    with tab_ref1:
        st.subheader("جدول الاحتياجات الغذائية الدنيا حسب نوع الإنتاج")
        st.table(pd.DataFrame({
            "نوع القطاع": ["دجاج تسمين (بادئ)", "دجاج بياض (إنتاج ذروة)", "أبقار حليب (عالية الإنتاج)", "أغنام تسمين"],
            "البروتين الخام (CP %)(الحد الأدنى)": ["22.0%", "17.5%", "16.5%", "14.0%"],
            "الطاقة الممثلة (ME Kcal/kg)": ["3000", "2750", "2600", "2700"],
            "الألياف القصوى (CF %)": ["3.5%", "5.0%", "16.0%", "12.0%"]
        }))

    with tab_ref2:
        st.subheader("خصائص السلالات السودانية المحلية")
        st.markdown("""
        * **أبقار الكنانة والبتانة:** سلالات حليب محلية ممتازة، تمتاز بمقاومة عالية لقراد الأبقار والحرارة المرتفعة مع معدل إنتاج يصل إلى 15 لتر/يوم تحت الإدارة المحسنة.
        * **الأغنام الحمرية والكباشية:** من أفضل سلالات اللحم في المنطقة، تمتاز بمعدلات نمو عالية وكفاءة ممتازة في تحويل العلائق الفقيرة.
        * **دجاج الفيومي والبلدي:** يمتلك مناعة عالية جداً ضد الأمراض الفيروسية الشائعة مثل الماريك والنيوكاسل مقارنة بالسلالات التجارية.
        """)
