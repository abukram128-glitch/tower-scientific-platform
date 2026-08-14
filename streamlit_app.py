import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
from scipy.stats import norm
import plotly.express as px
import plotly.graph_objects as go
from itertools import product
import hashlib
import base64
from datetime import datetime
import json

# ==========================================
# 1. تهيئة الصفحة والتصميم والأمان المتقدم
# ==========================================
st.set_page_config(
    page_title="منتدى التغذية التطبيقية والهندسة الوراثية - د. عبد القادر إسماعيل",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نظام أمان متقدم
SECURITY_KEY = "2024_ABDELKADER_ISMAIL_GENETICS"
APP_VERSION = "3.3.0"

def generate_license_hash():
    return hashlib.sha256(f"{SECURITY_KEY}_{datetime.now().year}".encode()).hexdigest()[:16]

# ==========================================
# 2. تنسيق CSS والأمان
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-touch-callout: none !important;
    }

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @keyframes scrollBanner {
        0% { transform: translateX(100%); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateX(-100%); opacity: 0; }
    }
    
    .banner-container {
        background: linear-gradient(90deg, #0F172A, #1E293B, #0F172A);
        padding: 12px 0;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 2px solid #FCD34D;
        overflow: hidden;
        position: relative;
        box-shadow: 0 4px 15px rgba(252, 211, 77, 0.3);
    }
    
    .banner-text {
        animation: scrollBanner 20s linear infinite;
        white-space: nowrap;
        color: #FCD34D;
        font-size: 1.2rem;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(252, 211, 77, 0.3);
        padding: 0 20px;
        display: inline-block;
        direction: ltr;
    }
    
    .banner-text .arabic {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        display: inline-block;
        margin: 0 15px;
    }
    
    .banner-text .prayer {
        color: #60A5FA;
        font-size: 1.1rem;
    }
    
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #ffffff;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        border-right: 6px solid #0284C7;
        position: relative;
    }
    
    .app-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #38BDF8;
        margin-top: 4px;
        font-weight: 600;
    }
    
    .dedication-box {
        background: linear-gradient(135deg, #1E3A5F, #0F172A);
        border: 2px solid #FCD34D;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(252, 211, 77, 0.15);
    }
    
    .dedication-text {
        color: #FCD34D;
        font-size: 1.3rem;
        font-weight: 700;
    }
    
    .dedication-sub {
        color: #93C5FD;
        font-size: 1rem;
        margin-top: 5px;
    }
    
    .genetic-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .genetic-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .stMetric {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        padding: 12px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    
    .watermark {
        font-size: 0.82rem;
        color: #64748B;
        text-align: center;
        padding: 12px;
        border-top: 1px solid #E2E8F0;
    }
    
    .security-badge {
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: rgba(15, 23, 42, 0.8);
        color: #94A3B8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        backdrop-filter: blur(5px);
        z-index: 999;
    }
    
    /* تحسين عرض الرسوم البيانية */
    .plotly-container {
        width: 100% !important;
        height: 100% !important;
    }
    .js-plotly-plot .plotly .main-svg {
        width: 100% !important;
        height: 100% !important;
    }
    </style>

    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
            (e.ctrlKey && e.shiftKey && e.keyCode == 73) || 
            (e.ctrlKey && e.keyCode == 85) ||
            (e.ctrlKey && e.keyCode == 67) ||
            (e.ctrlKey && e.keyCode == 86) ||
            (e.ctrlKey && e.keyCode == 83) ||
            (e.ctrlKey && e.keyCode == 76)) {
            return false;
        }
        if (e.ctrlKey && e.keyCode == 68) {
            e.preventDefault();
            return false;
        }
    }
    
    window.addEventListener('beforeunload', function(e) {
        // منع حفظ الصفحة
    });
    
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
    });
    </script>
""", unsafe_allow_html=True)

# ==========================================
# 3. Banner الوالدين والدعاء
# ==========================================
st.markdown(f"""
<div class="banner-container">
    <div class="banner-text">
        <span class="arabic">🤲 اللهم اغفر لوالدي وارحمهما كما ربّياني صغيراً</span>
        <span style="color: #FCD34D; margin: 0 10px;">|</span>
        <span class="arabic">❤️ هذا البرنامج وقفاً للمرحوم بإذن الله <strong>إسماعيل تاور</strong></span>
        <span style="color: #FCD34D; margin: 0 10px;">|</span>
        <span class="arabic">🕋 نسأل الله أن يتقبله في عليين</span>
        <span style="color: #FCD34D; margin: 0 10px;">|</span>
        <span class="prayer">اللهم آمين</span>
        <span style="color: #FCD34D; margin: 0 10px;">|</span>
        <span class="arabic">📖 قال تعالى: (وَإِذْ تَأَذَّنَ رَبُّكُمْ لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ)</span>
    </div>
</div>

<div class="dedication-box">
    <div class="dedication-text">🤲 إهداء إلى روح والدي الغالي</div>
    <div class="dedication-sub">اللهم اغفر له وارحمه وعافه واعفُ عنه، وأكرم نزله، ووسع مدخله، واغسله بالماء والثلج والبرد، ونقه من الذنوب والخطايا كما ينقى الثوب الأبيض من الدنس</div>
    <div class="dedication-sub" style="font-size: 0.9rem; margin-top: 8px; color: #FCD34D;">
        هذا العمل العلمي صدقة جارية على روح المرحوم إسماعيل تاور - رحمه الله رحمة واسعة
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. الواجهة الرئيسية
# ==========================================
st.markdown("""
    <div class="app-header">
        <div class="app-title">🧬 منتدى التغذية التطبيقية والهندسة الوراثية للإنتاج الحيواني</div>
        <div class="app-subtitle">تطوير وتصميم: أخصائي الإنتاج الحيواني | د. عبد القادر إسماعيل</div>
        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 5px;">
            الإصدار {} | رمز الترخيص: {}
        </div>
    </div>
""".format(APP_VERSION, generate_license_hash()), unsafe_allow_html=True)

# ==========================================
# 5. تعريف محرك الوراثة الأساسي
# ==========================================
class GeneticsEngine:
    
    @staticmethod
    def calculate_punnett_square(sire_genotype, dam_genotype, gene_info):
        sire_alleles = [sire_genotype[0], sire_genotype[1]]
        dam_alleles = [dam_genotype[0], dam_genotype[1]]
        
        offspring_genotypes = []
        for s in sire_alleles:
            for d in dam_alleles:
                sorted_alleles = "".join(sorted([s, d], key=lambda x: (x.islower(), x)))
                offspring_genotypes.append(sorted_alleles)
                
        genotype_counts = pd.Series(offspring_genotypes).value_counts(normalize=True) * 100
        
        phenotype_results = {}
        for geno, prob in genotype_counts.items():
            pheno = gene_info["dominant_trait"]
            if gene_info["inheritance"] == "Complete":
                if gene_info["dominant_allele"] in geno:
                    pheno = gene_info["dominant_trait"]
                else:
                    pheno = gene_info["recessive_trait"]
            elif gene_info["inheritance"] == "Incomplete":
                if geno == gene_info["dominant_allele"] * 2:
                    pheno = gene_info["dominant_trait"]
                elif geno == gene_info["recessive_allele"] * 2:
                    pheno = gene_info["recessive_trait"]
                else:
                    pheno = gene_info["intermediate_trait"]
            
            phenotype_results[pheno] = phenotype_results.get(pheno, 0.0) + prob
            
        return genotype_counts.to_dict(), phenotype_results, offspring_genotypes

    @staticmethod
    def simulate_multi_generations(initial_mean, heritability, selection_intensity, phenotype_std, generations=5):
        gen_data = []
        annual_gain = selection_intensity * heritability * phenotype_std
        
        for g in range(1, generations + 1):
            ebv_gen = annual_gain * g
            expected_mean = initial_mean + ebv_gen
            gen_data.append({
                "الجيل": f"الجيل F{g}",
                "التحسين المتراكم (ΔG)": round(ebv_gen, 2),
                "متوسط أداء الجيل المتوقع": round(expected_mean, 2)
            })
            
        return pd.DataFrame(gen_data)

# ==========================================
# 6. قاعدة بيانات السلالات والاحتياجات الغذائية
# ==========================================
class AnimalNutritionDatabase:
    """قاعدة بيانات الاحتياجات الغذائية حسب النوع والغرض"""
    
    @staticmethod
    def get_animal_types():
        return {
            "أبقار": {
                "سلالات": {
                    "هولشتاين": {"الغرض": ["حلابة", "لحوم"], "وزن_متوسط": 600},
                    "جيرسي": {"الغرض": ["حلابة"], "وزن_متوسط": 450},
                    "سيمنتال": {"الغرض": ["حلابة", "لحوم"], "وزن_متوسط": 700},
                    "سودانية محلية": {"الغرض": ["حلابة", "لحوم"], "وزن_متوسط": 400}
                },
                "احتياجات": {
                    "حلابة": {"CP": 16.0, "ME": 2600, "CF": 6.0, "Ca": 0.8, "AvP": 0.4},
                    "لحوم": {"CP": 14.0, "ME": 2400, "CF": 7.0, "Ca": 0.6, "AvP": 0.35}
                }
            },
            "دواجن": {
                "سلالات": {
                    "Cobb 500": {"الغرض": ["لحوم"], "وزن_متوسط": 2.4},
                    "Ross 308": {"الغرض": ["لحوم"], "وزن_متوسط": 2.38},
                    "Hy-Line W-36": {"الغرض": ["بياض"], "وزن_متوسط": 1.5},
                    "Lohmann Brown": {"الغرض": ["بياض"], "وزن_متوسط": 1.8}
                },
                "احتياجات": {
                    "لحوم": {"CP": 22.0, "ME": 3200, "CF": 4.0, "Ca": 0.9, "AvP": 0.45},
                    "بياض": {"CP": 18.0, "ME": 2800, "CF": 5.0, "Ca": 3.5, "AvP": 0.45}
                }
            },
            "أغنام": {
                "سلالات": {
                    "العواسي": {"الغرض": ["حلابة", "لحوم"], "وزن_متوسط": 55},
                    "الحمري": {"الغرض": ["لحوم"], "وزن_متوسط": 45}
                },
                "احتياجات": {
                    "حلابة": {"CP": 15.0, "ME": 2400, "CF": 8.0, "Ca": 0.7, "AvP": 0.35},
                    "لحوم": {"CP": 13.0, "ME": 2200, "CF": 9.0, "Ca": 0.5, "AvP": 0.30}
                }
            },
            "ماعز": {
                "سلالات": {
                    "السعانين": {"الغرض": ["حلابة", "لحوم"], "وزن_متوسط": 50},
                    "البلدي المصري": {"الغرض": ["لحوم"], "وزن_متوسط": 35}
                },
                "احتياجات": {
                    "حلابة": {"CP": 14.0, "ME": 2300, "CF": 8.0, "Ca": 0.7, "AvP": 0.35},
                    "لحوم": {"CP": 12.0, "ME": 2100, "CF": 9.0, "Ca": 0.5, "AvP": 0.30}
                }
            }
        }

# ==========================================
# 7. قاعدة بيانات الأعلاف المتقدمة
# ==========================================
class FeedDatabase:
    @staticmethod
    def get_all_feeds():
        return pd.DataFrame([
            {"المادة الخام": "ذرة صفراء", "CP": 8.5, "ME": 3350, "CF": 2.2, "EE": 3.8, "Ca": 0.02, "AvP": 0.10, "Cost": 1.35, "Max": 65.0},
            {"المادة الخام": "ذرة رفيعة", "CP": 9.0, "ME": 3200, "CF": 2.5, "EE": 3.5, "Ca": 0.03, "AvP": 0.12, "Cost": 1.20, "Max": 65.0},
            {"المادة الخام": "كسبة فول الصويا 44%", "CP": 44.0, "ME": 2230, "CF": 6.0, "EE": 1.5, "Ca": 0.29, "AvP": 0.22, "Cost": 3.10, "Max": 30.0},
            {"المادة الخام": "كسبة فول الصويا 48%", "CP": 48.0, "ME": 2440, "CF": 3.5, "EE": 1.0, "Ca": 0.27, "AvP": 0.20, "Cost": 3.40, "Max": 30.0},
            {"المادة الخام": "كسبة زهرة الشمس", "CP": 36.0, "ME": 2450, "CF": 12.0, "EE": 6.5, "Ca": 0.30, "AvP": 0.22, "Cost": 2.10, "Max": 25.0},
            {"المادة الخام": "كسبة بذرة القطن", "CP": 38.0, "ME": 2000, "CF": 11.0, "EE": 4.0, "Ca": 0.20, "AvP": 0.25, "Cost": 2.20, "Max": 10.0},
            {"المادة الخام": "نخالة القمح", "CP": 15.0, "ME": 1300, "CF": 11.0, "EE": 4.0, "Ca": 0.14, "AvP": 0.28, "Cost": 0.95, "Max": 25.0},
            {"المادة الخام": "مولاس القصب", "CP": 4.0, "ME": 1900, "CF": 0.0, "EE": 0.1, "Ca": 0.80, "AvP": 0.08, "Cost": 0.70, "Max": 5.0},
            {"المادة الخام": "حجر جيري", "CP": 0.0, "ME": 0, "CF": 0.0, "EE": 0.0, "Ca": 38.0, "AvP": 0.00, "Cost": 0.20, "Max": 4.0},
            {"المادة الخام": "DCP", "CP": 0.0, "ME": 0, "CF": 0.0, "EE": 0.0, "Ca": 22.0, "AvP": 18.0, "Cost": 2.20, "Max": 2.0},
            {"المادة الخام": "ملح الطعام", "CP": 0.0, "ME": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost": 0.30, "Max": 0.5},
            {"المادة الخام": "Premix", "CP": 0.0, "ME": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost": 8.00, "Max": 0.5}
        ])

# ==========================================
# 8. محرك تركيب الأعلاف المتقدم
# ==========================================
class AdvancedFeedOptimizer:
    def __init__(self, selected_df, requirements):
        self.df = selected_df
        self.requirements = requirements
    
    def optimize(self):
        try:
            costs = self.df["Cost"].values
            cp = self.df["CP"].values
            me = self.df["ME"].values
            cf = self.df["CF"].values
            ca = self.df["Ca"].values
            avp = self.df["AvP"].values
            max_bounds = self.df["Max"].values / 100.0
            
            A_eq = [np.ones(len(costs))]
            b_eq = [1.0]
            
            A_ub = [-cp, -me, cf, -ca, -avp]
            b_ub = [-self.requirements["CP"], -self.requirements["ME"], 
                    self.requirements["CF"], -self.requirements["Ca"], 
                    -self.requirements["AvP"]]
            
            bounds = [(0, b) for b in max_bounds]
            result = linprog(costs, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                           bounds=bounds, method='highs')
            
            return result
        except Exception as e:
            st.error(f"خطأ في التحسين: {str(e)}")
            return None
    
    def get_nutritional_analysis(self, solution):
        """تحليل القيمة الغذائية للتركيبة الناتجة"""
        if solution is None:
            return None
        
        df = self.df.copy()
        df["النسبة"] = solution.x * 100
        
        analysis = {
            "CP": np.sum(df["CP"] * df["النسبة"] / 100),
            "ME": np.sum(df["ME"] * df["النسبة"] / 100),
            "CF": np.sum(df["CF"] * df["النسبة"] / 100),
            "Ca": np.sum(df["Ca"] * df["النسبة"] / 100),
            "AvP": np.sum(df["AvP"] * df["النسبة"] / 100),
            "Cost": np.sum(df["Cost"] * df["النسبة"] / 100)
        }
        return analysis

# ==========================================
# 9. القوائم الجانبية
# ==========================================
st.sidebar.markdown("### 🌟 أروقة المنتدى")
app_mode = st.sidebar.radio("اختر التطبيق:", [
    "🌾 تركيب العلائق المتقدم",
    "🧬 الهندسة الوراثية",
    "🐔 تهجين الدواجن",
    "📊 الإحلال الاقتصادي",
    "📚 الموسوعة الوراثية"
])

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div class="watermark">
    الملكية الفكرية محفوظة ©<br>
    <b>د. عبد القادر إسماعيل</b><br>
    <span style="font-size: 0.7rem;">الإصدار {APP_VERSION}</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 10. القسم الأول: تركيب العلائق المتقدم
# ==========================================
if "تركيب العلائق" in app_mode:
    st.subheader("🌾 نظام تركيب العلائق المتقدم حسب النوع والغرض")
    
    # اختيار نوع الحيوان
    nutrition_db = AnimalNutritionDatabase()
    animal_types = nutrition_db.get_animal_types()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        animal_type = st.selectbox("نوع الحيوان:", list(animal_types.keys()))
    
    # اختيار السلالة
    breeds = animal_types[animal_type]["سلالات"]
    with col2:
        breed = st.selectbox("السلالة:", list(breeds.keys()))
    
    # اختيار الغرض من الإنتاج
    purposes = breeds[breed]["الغرض"]
    with col3:
        purpose = st.selectbox("الغرض من الإنتاج:", purposes)
    
    # عرض الاحتياجات المقترحة
    requirements = animal_types[animal_type]["احتياجات"][purpose]
    
    st.markdown("---")
    st.markdown("### 📊 الاحتياجات الغذائية المقترحة")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        req_cp = st.number_input("البروتين CP %:", 8.0, 30.0, requirements["CP"], step=0.5)
    with col2:
        req_me = st.number_input("الطاقة ME:", 1200, 3500, requirements["ME"], step=50)
    with col3:
        req_cf = st.number_input("الألياف CF %:", 2.0, 25.0, requirements["CF"], step=0.5)
    with col4:
        req_ca = st.number_input("الكالسيوم Ca %:", 0.0, 5.0, requirements["Ca"], step=0.1)
    with col5:
        req_avp = st.number_input("الفوسفور Av.P %:", 0.0, 2.0, requirements["AvP"], step=0.05)
    
    # معلومات عن الحيوان
    st.markdown("---")
    st.markdown("### 🐄 معلومات الحيوان")
    weight = st.number_input("وزن الحيوان (كجم):", 1.0, 1000.0, breeds[breed]["وزن_متوسط"], step=5.0)
    production_level = st.number_input("مستوى الإنتاج (حليب/بيض):", 0.0, 100.0, 10.0, step=1.0)
    
    # اختيار المواد الخام
    st.markdown("---")
    st.markdown("### 📋 اختيار المواد الخام")
    
    feed_df = FeedDatabase.get_all_feeds()
    
    # إضافة عمود للاختيار
    feed_df["اختيار"] = True
    
    edited_df = st.data_editor(
        feed_df,
        column_config={
            "اختيار": st.column_config.CheckboxColumn("اختيار", default=True),
            "CP": st.column_config.NumberColumn("بروتين %", min_value=0, max_value=100),
            "ME": st.column_config.NumberColumn("طاقة", min_value=0, max_value=5000),
            "CF": st.column_config.NumberColumn("ألياف %", min_value=0, max_value=100),
            "Ca": st.column_config.NumberColumn("كالسيوم %", min_value=0, max_value=100),
            "AvP": st.column_config.NumberColumn("فوسفور %", min_value=0, max_value=100),
            "Cost": st.column_config.NumberColumn("تكلفة", min_value=0, max_value=100),
            "Max": st.column_config.NumberColumn("حد أقصى %", min_value=0, max_value=100)
        },
        use_container_width=True,
        hide_index=True
    )
    
    # زر حساب العليقة
    if st.button("🚀 حساب العليقة المثلى", type="primary", use_container_width=True):
        # تصفية المواد المختارة
        selected_df = edited_df[edited_df["اختيار"] == True].copy()
        
        if len(selected_df) == 0:
            st.error("⚠️ يجب اختيار مادة خام واحدة على الأقل")
        else:
            # إعداد الاحتياجات
            req_dict = {
                "CP": req_cp,
                "ME": req_me,
                "CF": req_cf,
                "Ca": req_ca,
                "AvP": req_avp
            }
            
            optimizer = AdvancedFeedOptimizer(selected_df, req_dict)
            result = optimizer.optimize()
            
            if result is not None and result.success:
                st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                
                # عرض النتائج
                result_df = selected_df.copy()
                result_df["النسبة %"] = np.round(result.x * 100, 2)
                result_df["كجم/طن"] = np.round(result.x * 1000, 1)
                result_df["التكلفة/طن"] = np.round(result.x * 1000 * result_df["Cost"], 2)
                
                # عرض المواد الفعالة فقط
                active_df = result_df[result_df["النسبة %"] > 0.01].reset_index(drop=True)
                
                # عرض المقاييس الأساسية
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("تكلفة الكجم", f"${result.fun:.3f}")
                with col2:
                    st.metric("تكلفة الطن", f"${result.fun * 1000:.2f}")
                with col3:
                    st.metric("عدد المكونات", len(active_df))
                with col4:
                    # حساب نسبة البروتين الفعلية
                    actual_cp = np.sum(active_df["CP"] * active_df["النسبة %"] / 100)
                    st.metric("البروتين الفعلي", f"{actual_cp:.1f}%")
                
                # عرض جدول التركيبة
                st.markdown("#### 📊 تركيب العليقة المحسوب")
                display_cols = ["المادة الخام", "النسبة %", "كجم/طن", "التكلفة/طن", "CP", "ME", "CF", "Ca", "AvP"]
                st.dataframe(active_df[display_cols], use_container_width=True)
                
                # عرض الرسوم البيانية - محسنة للعرض
                st.markdown("#### 📈 التحليل البياني للتركيبة")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # رسم بياني دائري - مع إعدادات محسنة
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=active_df["المادة الخام"],
                        values=active_df["النسبة %"],
                        textinfo='label+percent',
                        textposition='auto',
                        hole=0.3,
                        marker=dict(line=dict(color='#FFFFFF', width=2))
                    )])
                    fig_pie.update_layout(
                        title="توزيع مكونات العليقة",
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20),
                        showlegend=False
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, config={'responsive': True})
                
                with col2:
                    # رسم بياني شريطي
                    fig_bar = go.Figure(data=[
                        go.Bar(
                            x=active_df["المادة الخام"],
                            y=active_df["النسبة %"],
                            text=active_df["النسبة %"].round(1),
                            textposition='outside',
                            marker_color='#0284C7'
                        )
                    ])
                    fig_bar.update_layout(
                        title="نسب المكونات في العليقة",
                        xaxis_title="المادة الخام",
                        yaxis_title="النسبة %",
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=60)
                    )
                    st.plotly_chart(fig_bar, use_container_width=True, config={'responsive': True})
                
                # تحليل القيمة الغذائية
                st.markdown("#### 📋 التحليل الغذائي للتركيبة")
                analysis = optimizer.get_nutritional_analysis(result)
                
                if analysis:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("البروتين CP", f"{analysis['CP']:.1f}%", 
                                 delta=f"{analysis['CP'] - req_cp:.1f}")
                    with col2:
                        st.metric("الطاقة ME", f"{analysis['ME']:.0f}", 
                                 delta=f"{analysis['ME'] - req_me:.0f}")
                    with col3:
                        st.metric("الألياف CF", f"{analysis['CF']:.1f}%", 
                                 delta=f"{analysis['CF'] - req_cf:.1f}")
                    with col4:
                        st.metric("الكالسيوم Ca", f"{analysis['Ca']:.2f}%", 
                                 delta=f"{analysis['Ca'] - req_ca:.2f}")
                    with col5:
                        st.metric("الفوسفور Av.P", f"{analysis['AvP']:.2f}%", 
                                 delta=f"{analysis['AvP'] - req_avp:.2f}")
                
            else:
                st.error("❌ المواد الخام المختارة غير كافية لتحقيق المستهدفات المطلوبة. حاول إضافة مواد أخرى أو تعديل القيود.")

# ==========================================
# 11. القسم الثاني: الهندسة الوراثية
# ==========================================
elif "الهندسة الوراثية" in app_mode:
    st.subheader("🧬 محرك الهندسة الوراثية المتقدم")
    
    tab1, tab2, tab3 = st.tabs(["📊 مربع بونيت", "📈 القيمة التربوية", "🔄 تتبع الأجيال"])
    
    with tab1:
        st.markdown("##### مربع بونيت (Punnett Square)")
        
        col1, col2 = st.columns(2)
        with col1:
            gene_type = st.selectbox("نوع الصفة:", ["القرون", "لون الجلد", "الريش"])
            inheritance = st.selectbox("نمط السيادة:", ["سيادة تامة", "سيادة غير تامة"])
        
        with col2:
            if "القرون" in gene_type:
                g_info = {"dominant_allele": "P", "recessive_allele": "p", "dominant_trait": "عديم القرون", "recessive_trait": "بقرون", "intermediate_trait": "قرون ضامرة", "inheritance": "Complete" if "تامة" in inheritance else "Incomplete"}
            else:
                g_info = {"dominant_allele": "B", "recessive_allele": "b", "dominant_trait": "أسود", "recessive_trait": "أحمر", "intermediate_trait": "بني", "inheritance": "Complete" if "تامة" in inheritance else "Incomplete"}
        
        st.markdown("##### الطراز الوراثي للآباء:")
        col_sire, col_dam = st.columns(2)
        
        dom = g_info["dominant_allele"]
        rec = g_info["recessive_allele"]
        
        options = [f"{dom}{dom} - نقي سائد", f"{dom}{rec} - هجين", f"{rec}{rec} - نقي متنحي"]
        
        with col_sire:
            sire = st.selectbox("الذكر:", options, index=1)
            sire_code = sire.split(" ")[0]
        with col_dam:
            dam = st.selectbox("الأنثى:", options, index=1)
            dam_code = dam.split(" ")[0]
        
        if st.button("🔬 حساب النتائج"):
            genotype_prob, phenotype_prob, _ = GeneticsEngine.calculate_punnett_square(sire_code, dam_code, g_info)
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown("###### النسب الجينية:")
                for g, p in genotype_prob.items():
                    st.write(f"- {g}: {p:.1f}%")
                
                fig = px.bar(x=list(genotype_prob.keys()), y=list(genotype_prob.values()), 
                           labels={'x':'الطراز الجيني', 'y':'النسبة %'})
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
            
            with col_res2:
                st.markdown("###### النسب المظهرية:")
                for p, prob in phenotype_prob.items():
                    st.write(f"- {p}: {prob:.1f}%")
                
                fig = px.pie(values=list(phenotype_prob.values()), names=list(phenotype_prob.keys()))
                st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
    
    with tab2:
        st.markdown("##### حساب القيمة التربوية (EBV)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            h2 = st.number_input("المكافئ الوراثي (h²):", 0.05, 0.99, 0.30, step=0.05)
        with col2:
            pop_mean = st.number_input("متوسط القطيع:", 0.0, 10000.0, 5000.0)
        with col3:
            ind_perf = st.number_input("أداء الفرد:", 0.0, 10000.0, 6000.0)
        
        ebv = h2 * (ind_perf - pop_mean)
        offspring_gain = ebv / 2
        
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("الفرق الظاهري", f"{ind_perf - pop_mean:+.2f}")
        col_res2.metric("القيمة التربوية (EBV)", f"{ebv:+.2f}")
        col_res3.metric("تحسين الأبناء", f"{offspring_gain:+.2f}")
    
    with tab3:
        st.markdown("##### تتبع التحسين عبر الأجيال")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            base_perf = st.number_input("الأساس P₀:", 1.0, 15000.0, 3000.0)
        with col2:
            h2_gen = st.number_input("h²:", 0.05, 0.95, 0.30)
        with col3:
            intensity = st.slider("شدة الانتخاب:", 0.5, 2.5, 1.4)
        with col4:
            sigma = st.number_input("σp:", 1.0, 2000.0, 300.0)
        
        generations = st.slider("عدد الأجيال:", 2, 10, 5)
        
        df_gen = GeneticsEngine.simulate_multi_generations(base_perf, h2_gen, intensity, sigma, generations)
        
        st.dataframe(df_gen, use_container_width=True)
        
        fig = px.line(df_gen, x="الجيل", y="متوسط أداء الجيل المتوقع", markers=True,
                     title="مسار التحسين الوراثي")
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

# ==========================================
# 12. القسم الثالث: تهجين الدواجن
# ==========================================
elif "تهجين الدواجن" in app_mode:
    st.subheader("🐔 نظام تهجين الدواجن العالمي")
    
    # قاعدة بيانات الدواجن المبسطة
    poultry_breeds = {
        "البياض": ["Hy-Line W-36", "Hy-Line W-80", "Lohmann Brown", "Lohmann LSL", "ISA Brown"],
        "اللاحم": ["Cobb 500", "Cobb 700", "Ross 308", "Ross 708", "Arbor Acres"],
        "الزينة": ["الدجاج البلدي", "Brahma", "Silkie", "Cochin", "Orpington"]
    }
    
    with st.expander("📋 السلالات المتاحة", expanded=True):
        for category, breeds in poultry_breeds.items():
            st.markdown(f"#### {category}")
            cols = st.columns(4)
            for idx, name in enumerate(breeds):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="genetic-card">
                        <strong>{name}</strong>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔬 تصميم برنامج تهجين")
    
    hybrid_type = st.radio("نوع التهجين:", ["تهجين ثنائي", "تهجين ثلاثي"])
    
    all_breeds = []
    for breeds in poultry_breeds.values():
        all_breeds.extend(breeds)
    
    col1, col2 = st.columns(2)
    with col1:
        sire = st.selectbox("السلالة الأبوية:", all_breeds, index=0)
    with col2:
        dam = st.selectbox("السلالة الأمومية:", all_breeds, index=1)
    
    third = None
    if hybrid_type == "تهجين ثلاثي":
        third = st.selectbox("السلالة الثالثة:", all_breeds, index=2)
    
    if st.button("🧬 تنبؤ خصائص الهجين", type="primary"):
        st.markdown("### 📊 نتائج التنبؤ")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("الوزن المتوقع", "2.4 كجم")
            st.metric("لون الريش", "متنوع")
        with col2:
            st.metric("شكل العرف", "ورقي")
            if hybrid_type == "تهجين ثلاثي":
                st.metric("قوة الهجين", "عالية")
        with col3:
            st.metric("نوع الإنتاج", "متوسط")

# ==========================================
# 13. القسم الرابع: الإحلال الاقتصادي
# ==========================================
elif "الإحلال الاقتصادي" in app_mode:
    st.subheader("📊 دراسات الإحلال الاقتصادي")
    
    alternatives = {
        "كسبة زهرة الشمس": {"السعر": 2.10, "البدائل": {"كسبة فول الصويا": 3.10, "كسبة بذرة القطن": 2.20, "أمباز السمسم": 2.80}},
        "الذرة الصفراء": {"السعر": 1.35, "البدائل": {"الذرة الرفيعة": 1.20, "القمح": 1.50, "الشعير": 1.10}},
        "كسبة فول الصويا": {"السعر": 3.10, "البدائل": {"كسبة زهرة الشمس": 2.10, "كسبة بذرة القطن": 2.20}}
    }
    
    ingredient = st.selectbox("اختر المادة:", list(alternatives.keys()))
    data = alternatives[ingredient]
    
    st.markdown(f"#### السعر الحالي: ${data['السعر']:.2f}/كجم")
    
    st.markdown("##### البدائل المتاحة:")
    for alt, price in data["البدائل"].items():
        saving = data["السعر"] - price
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{alt}** - ${price:.2f}/كجم")
        with col2:
            if saving > 0:
                st.success(f"توفير ${saving:.2f}")
            else:
                st.warning(f"خسارة ${-saving:.2f}")
    
    st.markdown("---")
    st.markdown("### 💰 حاسبة التوفير")
    
    col1, col2 = st.columns(2)
    with col1:
        usage = st.number_input("الاستهلاك الشهري (طن):", 0.1, 100.0, 10.0)
        replacement = st.slider("نسبة الإحلال %:", 0, 100, 30)
    with col2:
        selected_alt = st.selectbox("اختر البديل:", list(data["البدائل"].keys()))
        alt_price = data["البدائل"][selected_alt]
    
    saving_per_ton = (data["السعر"] - alt_price) * 1000 * (replacement / 100)
    total_saving = saving_per_ton * usage
    
    st.metric("التوفير الشهري", f"${total_saving:,.2f}")
    st.metric("التوفير السنوي", f"${total_saving * 12:,.2f}")

# ==========================================
# 14. القسم الخامس: الموسوعة الوراثية
# ==========================================
else:
    st.subheader("📚 الموسوعة الوراثية للسلالات العالمية")
    
    search = st.text_input("🔍 بحث في السلالات:", placeholder="اكتب اسم السلالة...")
    
    all_breeds_data = {
        "أبقار": {
            "هولشتاين": {"المنشأ": "ألمانيا", "الوزن": 600, "إنتاج_الحليب": 7500, "دهن": 3.7},
            "جيرسي": {"المنشأ": "جزر القنال", "الوزن": 450, "إنتاج_الحليب": 5000, "دهن": 4.8},
            "سيمنتال": {"المنشأ": "سويسرا", "الوزن": 700, "إنتاج_الحليب": 5500, "دهن": 4.0}
        },
        "دواجن": {
            "Cobb 500": {"المنشأ": "الولايات المتحدة", "الوزن": 2.4, "نوع": "لاحم"},
            "Ross 308": {"المنشأ": "بريطانيا", "الوزن": 2.38, "نوع": "لاحم"},
            "Hy-Line W-36": {"المنشأ": "الولايات المتحدة", "الوزن": 1.5, "نوع": "بياض"},
            "Lohmann Brown": {"المنشأ": "ألمانيا", "الوزن": 1.8, "نوع": "بياض"}
        },
        "أغنام": {
            "العواسي": {"المنشأ": "الشرق الأوسط", "الوزن": 55, "إنتاج_الحليب": 280},
            "الحمري": {"المنشأ": "السودان", "الوزن": 45}
        }
    }
    
    for category, breeds in all_breeds_data.items():
        filtered = breeds
        if search:
            filtered = {name: data for name, data in breeds.items() if search.lower() in name.lower()}
        
        if filtered:
            st.markdown(f"### {category}")
            cols = st.columns(3)
            for idx, (name, data) in enumerate(filtered.items()):
                with cols[idx % 3]:
                    with st.expander(f"🐄 {name}"):
                        for key, value in data.items():
                            st.write(f"**{key}:** {value}")

# ==========================================
# 15. أسفل الصفحة
# ==========================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #94A3B8; padding: 20px;">
    <div style="font-size: 0.9rem;">
        🧬 هذا البرنامج مُسجل ومحمي بموجب حقوق الملكية الفكرية
    </div>
    <div style="font-size: 0.8rem; margin-top: 5px;">
        تم التطوير بواسطة: <strong>د. عبد القادر إسماعيل</strong>
    </div>
    <div style="font-size: 0.7rem; margin-top: 5px; color: #64748B;">
        الإصدار {APP_VERSION} | جميع الحقوق محفوظة © 2024
    </div>
    <div style="font-size: 0.7rem; margin-top: 10px; color: #60A5FA; border-top: 1px solid #1E293B; padding-top: 10px;">
        <span style="color: #FCD34D;">🤲</span> 
        اللهم اجعل هذا العمل صدقة جارية لوالدي
        <span style="color: #FCD34D;">🤲</span>
    </div>
</div>

<div class="security-badge">
    🔒 Secured v{APP_VERSION} | License: {generate_license_hash()}
</div>
""", unsafe_allow_html=True)
