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
import os
import pickle

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
APP_VERSION = "3.2.0"

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
# 6. قاعدة بيانات السلالات
# ==========================================
class PoultryDatabase:
    @staticmethod
    def get_all_breeds():
        return {
            "البياض": {
                "Hy-Line W-36": {"type": "بياض", "origin": "USA", "egg_production": 320, "egg_weight": 62, "body_weight": 1.5, "feather_color": "أبيض", "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.20},
                "Hy-Line W-80": {"type": "بياض", "origin": "USA", "egg_production": 340, "egg_weight": 60, "body_weight": 1.6, "feather_color": "أبيض", "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.22},
                "Lohmann Brown": {"type": "بياض", "origin": "Germany", "egg_production": 330, "egg_weight": 63, "body_weight": 1.8, "feather_color": "بني", "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.21},
                "Lohmann LSL": {"type": "بياض", "origin": "Germany", "egg_production": 345, "egg_weight": 61, "body_weight": 1.7, "feather_color": "أبيض", "comb_type": "ورقي", "egg_color": "أبيض", "h2_egg": 0.23},
                "ISA Brown": {"type": "بياض", "origin": "France", "egg_production": 335, "egg_weight": 62, "body_weight": 1.9, "feather_color": "بني", "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.19}
            },
            "اللاحم": {
                "Cobb 500": {"type": "لاحم", "origin": "USA", "weight_35d": 2.4, "fcr": 1.52, "breast_yield": 22.5, "feather_color": "أبيض", "comb_type": "ورقي", "h2_weight": 0.40},
                "Cobb 700": {"type": "لاحم", "origin": "USA", "weight_35d": 2.5, "fcr": 1.50, "breast_yield": 23.0, "feather_color": "أبيض", "comb_type": "ورقي", "h2_weight": 0.42},
                "Ross 308": {"type": "لاحم", "origin": "UK", "weight_35d": 2.38, "fcr": 1.54, "breast_yield": 22.0, "feather_color": "أبيض", "comb_type": "ورقي", "h2_weight": 0.38},
                "Ross 708": {"type": "لاحم", "origin": "UK", "weight_35d": 2.45, "fcr": 1.51, "breast_yield": 22.8, "feather_color": "أبيض", "comb_type": "ورقي", "h2_weight": 0.41}
            },
            "الزينة": {
                "الدجاج البلدي المصري": {"type": "زينة", "origin": "Egypt", "weight": 1.8, "egg_production": 120, "feather_color": "متنوع", "comb_type": "ورقي", "special": "مقاوم للحرارة"},
                "الدجاج الهندي (Aseel)": {"type": "زينة", "origin": "India", "weight": 2.5, "egg_production": 80, "feather_color": "أحمر/أسود", "comb_type": "بازلائي", "special": "مقاتل"},
                "Brahma": {"type": "زينة", "origin": "USA", "weight": 4.5, "egg_production": 150, "feather_color": "رمادي/أبيض", "comb_type": "بازلائي", "special": "عملاق"},
                "Silkie": {"type": "زينة", "origin": "China", "weight": 1.5, "egg_production": 100, "feather_color": "أبيض/أسود", "comb_type": "ورقي", "special": "ريش ناعم كالحرير"}
            }
        }
    
    @staticmethod
    def get_hybrid_predictions(breed1, breed2, breed3=None):
        all_breeds = PoultryDatabase.get_all_breeds()
        breed_data = {}
        
        for category in all_breeds.values():
            if breed1 in category:
                breed_data['sire'] = category[breed1]
            if breed2 in category:
                breed_data['dam'] = category[breed2]
            if breed3 and breed3 in category:
                breed_data['third'] = category[breed3]
        
        if len(breed_data) < 2:
            return None
        
        predictions = {
            "الوزن المتوقع": np.mean([breed_data['sire'].get('weight', breed_data['sire'].get('weight_35d', 2.0)),
                                     breed_data['dam'].get('weight', breed_data['dam'].get('weight_35d', 2.0))]),
            "لون الريش المتوقع": "متنوع (مزيج من الأبوين)",
            "شكل العرف المتوقع": breed_data['sire'].get('comb_type', 'ورقي'),
            "نوع الإنتاج": breed_data['sire'].get('type', 'متوسط')
        }
        
        if breed3:
            predictions["الوزن المتوقع"] = np.mean([
                predictions["الوزن المتوقع"],
                breed_data['third'].get('weight', breed_data['third'].get('weight_35d', 2.0))
            ])
            predictions["لون الريش المتوقع"] = "تنوع جيني عالٍ (ثلاثة أصول)"
            predictions["قوة الهجين"] = "عالية (تهجين ثلاثي)"
        
        return predictions

# ==========================================
# 7. قاعدة بيانات الأعلاف
# ==========================================
class DatabaseEngine:
    @staticmethod
    def get_expanded_feed_ingredients():
        return pd.DataFrame([
            {"إدخال في العليقة": True, "المادة الخام": "ذرة رفيعة", "CP": 9.0, "ME_Kcal": 3200, "CF": 2.5, "EE": 3.5, "Ca": 0.03, "AvP": 0.12, "Cost_Kg": 1.20, "Max_Include": 65.0},
            {"إدخال في العليقة": True, "المادة الخام": "ذرة صفراء", "CP": 8.5, "ME_Kcal": 3350, "CF": 2.2, "EE": 3.8, "Ca": 0.02, "AvP": 0.10, "Cost_Kg": 1.35, "Max_Include": 60.0},
            {"إدخال في العليقة": True, "المادة الخام": "كسبة زهرة الشمس", "CP": 36.0, "ME_Kcal": 2450, "CF": 12.0, "EE": 6.5, "Ca": 0.30, "AvP": 0.22, "Cost_Kg": 2.10, "Max_Include": 25.0},
            {"إدخال في العليقة": True, "المادة الخام": "كسبة فول الصويا", "CP": 44.0, "ME_Kcal": 2230, "CF": 6.0, "EE": 1.5, "Ca": 0.29, "AvP": 0.22, "Cost_Kg": 3.10, "Max_Include": 30.0},
            {"إدخال في العليقة": True, "المادة الخام": "نخالة القمح", "CP": 15.0, "ME_Kcal": 1300, "CF": 11.0, "EE": 4.0, "Ca": 0.14, "AvP": 0.28, "Cost_Kg": 0.95, "Max_Include": 25.0},
            {"إدخال في العليقة": True, "المادة الخام": "مولاس القصب", "CP": 4.0, "ME_Kcal": 1900, "CF": 0.0, "EE": 0.1, "Ca": 0.80, "AvP": 0.08, "Cost_Kg": 0.70, "Max_Include": 5.0},
            {"إدخال في العليقة": True, "المادة الخام": "حجر جيري", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 38.0, "AvP": 0.00, "Cost_Kg": 0.20, "Max_Include": 4.0},
            {"إدخال في العليقة": True, "المادة الخام": "DCP", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 22.0, "AvP": 18.0, "Cost_Kg": 2.20, "Max_Include": 2.0},
            {"إدخال في العليقة": True, "المادة الخام": "ملح الطعام", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 0.30, "Max_Include": 0.5},
            {"إدخال في العليقة": True, "المادة الخام": "Premix", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 8.00, "Max_Include": 0.5}
        ])

# ==========================================
# 8. محرك تركيب الأعلاف
# ==========================================
class FeedOptimizer:
    def __init__(self, selected_df, target_cp, target_me, target_cf_max, target_ca, target_avp):
        self.df = selected_df
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
# 9. نظام إدارة المزارع
# ==========================================
class FarmManagementSystem:
    def __init__(self):
        self.farms_file = "farms_data.pkl"
        self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(self.farms_file):
                with open(self.farms_file, 'rb') as f:
                    self.farms_data = pickle.load(f)
            else:
                self.farms_data = {}
        except:
            self.farms_data = {}
    
    def save_data(self):
        try:
            with open(self.farms_file, 'wb') as f:
                pickle.dump(self.farms_data, f)
            return True
        except:
            return False
    
    def register_farm(self, owner_name, farm_name, farm_type, location, contact):
        farm_id = hashlib.md5(f"{farm_name}_{owner_name}_{datetime.now()}".encode()).hexdigest()[:8]
        
        self.farms_data[farm_id] = {
            "farm_id": farm_id,
            "owner": owner_name,
            "farm_name": farm_name,
            "farm_type": farm_type,
            "location": location,
            "contact": contact,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "animals": {},
            "feed_records": [],
            "production_records": [],
            "health_records": [],
            "financial_records": []
        }
        self.save_data()
        return farm_id
    
    def add_animal(self, farm_id, animal_data):
        if farm_id in self.farms_data:
            animal_id = hashlib.md5(f"{animal_data['name']}_{datetime.now()}".encode()).hexdigest()[:6]
            animal_data["id"] = animal_id
            animal_data["added_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.farms_data[farm_id]["animals"][animal_id] = animal_data
            self.save_data()
            return animal_id
        return None
    
    def get_farm_data(self, farm_id):
        return self.farms_data.get(farm_id, None)
    
    def get_all_farms(self):
        return self.farms_data

# ==========================================
# 10. القوائم الجانبية
# ==========================================
st.sidebar.markdown("### 🌟 أروقة المنتدى")
app_mode = st.sidebar.radio("اختر التطبيق:", [
    "🏡 إدارة المزارع",
    "🧬 الهندسة الوراثية",
    "🐔 تهجين الدواجن",
    "🌾 تركيب العلائق",
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
# 11. القسم الأول: إدارة المزارع
# ==========================================
if "إدارة المزارع" in app_mode:
    st.subheader("🏡 نظام إدارة المزارع المتكامل")
    
    farm_system = FarmManagementSystem()
    farms = farm_system.get_all_farms()
    
    if farms:
        farm_options = [f"{data['farm_name']} - {data['owner']}" for data in farms.values()]
        selected_farm = st.selectbox("اختر مزرعة:", ["إنشاء مزرعة جديدة"] + farm_options)
        
        if selected_farm == "إنشاء مزرعة جديدة":
            with st.form("new_farm"):
                st.markdown("### 📝 تسجيل مزرعة جديدة")
                col1, col2 = st.columns(2)
                with col1:
                    owner_name = st.text_input("اسم المالك:")
                    farm_name = st.text_input("اسم المزرعة:")
                with col2:
                    farm_type = st.selectbox("نوع المزرعة:", ["أبقار", "دواجن", "أغنام", "ماعز"])
                    location = st.text_input("الموقع:")
                    contact = st.text_input("رقم الاتصال:")
                
                if st.form_submit_button("🚀 تسجيل المزرعة"):
                    if owner_name and farm_name:
                        farm_id = farm_system.register_farm(owner_name, farm_name, farm_type, location, contact)
                        st.success(f"✅ تم تسجيل المزرعة! المعرف: {farm_id}")
                        st.balloons()
                    else:
                        st.error("⚠️ يرجى إدخال جميع البيانات")
        else:
            for fid, data in farms.items():
                if f"{data['farm_name']} - {data['owner']}" == selected_farm:
                    farm_data = data
                    break
            
            st.markdown(f"""
            <div class="genetic-card">
                <h3>🏠 {farm_data['farm_name']}</h3>
                <p><strong>المالك:</strong> {farm_data['owner']}</p>
                <p><strong>النوع:</strong> {farm_data['farm_type']}</p>
                <p><strong>الموقع:</strong> {farm_data['location']}</p>
                <p><strong>تاريخ التسجيل:</strong> {farm_data['created_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            tabs = st.tabs(["🐄 الحيوانات", "📊 الإنتاج", "🌾 التغذية", "🏥 الصحة", "💰 المالية"])
            
            with tabs[0]:
                st.markdown("#### 🐄 إدارة الحيوانات")
                if st.button("➕ إضافة حيوان جديد"):
                    with st.form("add_animal"):
                        col1, col2 = st.columns(2)
                        with col1:
                            animal_name = st.text_input("اسم/رقم الحيوان:")
                            animal_type = st.selectbox("النوع:", ["بقرة", "جاموس", "دجاجة", "خروف"])
                        with col2:
                            breed = st.text_input("السلالة:")
                            weight = st.number_input("الوزن (كجم):", 0.0, 1000.0, 50.0)
                        
                        if st.form_submit_button("💾 حفظ"):
                            animal_data = {"name": animal_name, "type": animal_type, "breed": breed, "weight": weight}
                            animal_id = farm_system.add_animal(fid, animal_data)
                            if animal_id:
                                st.success(f"✅ تم إضافة الحيوان! المعرف: {animal_id}")
                                st.rerun()
                
                if farm_data["animals"]:
                    animals_df = pd.DataFrame(farm_data["animals"]).T
                    st.dataframe(animals_df, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("عدد الحيوانات", len(animals_df))
                    with col2:
                        total_weight = animals_df['weight'].sum() if 'weight' in animals_df else 0
                        st.metric("الوزن الإجمالي", f"{total_weight:.1f} كجم")
                    with col3:
                        avg_weight = animals_df['weight'].mean() if 'weight' in animals_df else 0
                        st.metric("متوسط الوزن", f"{avg_weight:.1f} كجم")
            
            with tabs[1]:
                st.markdown("#### 📊 السجلات الإنتاجية")
                with st.form("add_production"):
                    col1, col2 = st.columns(2)
                    with col1:
                        prod_type = st.selectbox("النوع:", ["حليب", "بيض", "لحم"])
                        quantity = st.number_input("الكمية:", 0.0, 10000.0, 10.0)
                    with col2:
                        unit = st.selectbox("الوحدة:", ["كجم", "لتر", "عدد"])
                        notes = st.text_input("ملاحظات:")
                    
                    if st.form_submit_button("💾 حفظ"):
                        record = {"type": prod_type, "quantity": quantity, "unit": unit, "notes": notes}
                        farm_data["production_records"].append(record)
                        farm_system.save_data()
                        st.success("✅ تم حفظ السجل")
                        st.rerun()
                
                if farm_data["production_records"]:
                    records_df = pd.DataFrame(farm_data["production_records"])
                    st.dataframe(records_df, use_container_width=True)
            
            with tabs[2]:
                st.markdown("#### 🌾 السجلات الغذائية")
                with st.form("add_feed"):
                    col1, col2 = st.columns(2)
                    with col1:
                        feed_name = st.text_input("اسم العلف:")
                        quantity = st.number_input("الكمية (كجم):", 0.0, 10000.0, 100.0)
                    with col2:
                        cost_per_kg = st.number_input("التكلفة/كجم:", 0.0, 100.0, 1.0)
                        notes = st.text_input("ملاحظات:")
                    
                    if st.form_submit_button("💾 حفظ"):
                        record = {"feed_name": feed_name, "quantity": quantity, "cost_per_kg": cost_per_kg, "total_cost": quantity * cost_per_kg, "notes": notes}
                        farm_data["feed_records"].append(record)
                        farm_system.save_data()
                        st.success("✅ تم حفظ السجل")
                        st.rerun()
                
                if farm_data["feed_records"]:
                    records_df = pd.DataFrame(farm_data["feed_records"])
                    st.dataframe(records_df, use_container_width=True)
                    total_cost = records_df['total_cost'].sum() if 'total_cost' in records_df else 0
                    st.metric("إجمالي تكاليف الأعلاف", f"${total_cost:,.2f}")
            
            with tabs[3]:
                st.markdown("#### 🏥 السجلات الصحية")
                with st.form("add_health"):
                    col1, col2 = st.columns(2)
                    with col1:
                        health_type = st.selectbox("النوع:", ["فحص", "علاج", "تحصين"])
                        diagnosis = st.text_input("التشخيص:")
                    with col2:
                        treatment = st.text_input("العلاج:")
                        notes = st.text_input("ملاحظات:")
                    
                    if st.form_submit_button("💾 حفظ"):
                        record = {"type": health_type, "diagnosis": diagnosis, "treatment": treatment, "notes": notes}
                        farm_data["health_records"].append(record)
                        farm_system.save_data()
                        st.success("✅ تم حفظ السجل")
                        st.rerun()
                
                if farm_data["health_records"]:
                    records_df = pd.DataFrame(farm_data["health_records"])
                    st.dataframe(records_df, use_container_width=True)
            
            with tabs[4]:
                st.markdown("#### 💰 السجلات المالية")
                with st.form("add_financial"):
                    col1, col2 = st.columns(2)
                    with col1:
                        trans_type = st.selectbox("النوع:", ["إيراد", "مصروف"])
                        category = st.selectbox("الفئة:", ["مبيعات", "مشتريات", "رواتب"])
                    with col2:
                        amount = st.number_input("المبلغ:", 0.0, 1000000.0, 100.0)
                        description = st.text_input("الوصف:")
                    
                    if st.form_submit_button("💾 حفظ"):
                        record = {"type": trans_type, "category": category, "amount": amount, "description": description}
                        farm_data["financial_records"].append(record)
                        farm_system.save_data()
                        st.success("✅ تم حفظ السجل")
                        st.rerun()
                
                if farm_data["financial_records"]:
                    records_df = pd.DataFrame(farm_data["financial_records"])
                    st.dataframe(records_df, use_container_width=True)
                    
                    income = records_df[records_df['type'] == 'إيراد']['amount'].sum()
                    expenses = records_df[records_df['type'] == 'مصروف']['amount'].sum()
                    profit = income - expenses
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("الإيرادات", f"${income:,.2f}")
                    with col2:
                        st.metric("المصروفات", f"${expenses:,.2f}")
                    with col3:
                        st.metric("صافي الربح", f"${profit:,.2f}")
    else:
        st.info("لا توجد مزارع مسجلة. قم بإنشاء مزرعة جديدة:")
        with st.form("first_farm"):
            col1, col2 = st.columns(2)
            with col1:
                owner_name = st.text_input("اسم المالك:")
                farm_name = st.text_input("اسم المزرعة:")
            with col2:
                farm_type = st.selectbox("نوع المزرعة:", ["أبقار", "دواجن", "أغنام", "ماعز"])
                location = st.text_input("الموقع:")
                contact = st.text_input("رقم الاتصال:")
            
            if st.form_submit_button("🚀 تسجيل المزرعة"):
                if owner_name and farm_name:
                    farm_id = farm_system.register_farm(owner_name, farm_name, farm_type, location, contact)
                    st.success(f"✅ تم تسجيل المزرعة! المعرف: {farm_id}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("⚠️ يرجى إدخال جميع البيانات")

# ==========================================
# 12. القسم الثاني: الهندسة الوراثية
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
                st.plotly_chart(fig, use_container_width=True)
            
            with col_res2:
                st.markdown("###### النسب المظهرية:")
                for p, prob in phenotype_prob.items():
                    st.write(f"- {p}: {prob:.1f}%")
                
                fig = px.pie(values=list(phenotype_prob.values()), names=list(phenotype_prob.keys()))
                st.plotly_chart(fig, use_container_width=True)
    
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
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 13. القسم الثالث: تهجين الدواجن
# ==========================================
elif "تهجين الدواجن" in app_mode:
    st.subheader("🐔 نظام تهجين الدواجن العالمي")
    
    poultry_db = PoultryDatabase()
    all_breeds = poultry_db.get_all_breeds()
    
    with st.expander("📋 السلالات المتاحة", expanded=True):
        for category, breeds in all_breeds.items():
            st.markdown(f"#### {category}")
            cols = st.columns(3)
            for idx, (name, data) in enumerate(breeds.items()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="genetic-card">
                        <strong>{name}</strong><br>
                        {data.get('origin', '')}<br>
                        {'🐣 ' + str(data.get('egg_production', '')) if 'egg_production' in data else '⚖️ ' + str(data.get('weight_35d', ''))}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔬 تصميم برنامج تهجين")
    
    hybrid_type = st.radio("نوع التهجين:", ["تهجين ثنائي", "تهجين ثلاثي"])
    
    all_names = []
    for category in all_breeds.values():
        all_names.extend(list(category.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        sire = st.selectbox("السلالة الأبوية:", all_names, index=0)
    with col2:
        dam = st.selectbox("السلالة الأمومية:", all_names, index=1)
    
    third = None
    if hybrid_type == "تهجين ثلاثي":
        third = st.selectbox("السلالة الثالثة:", all_names, index=2)
    
    if st.button("🧬 تنبؤ خصائص الهجين", type="primary"):
        predictions = poultry_db.get_hybrid_predictions(sire, dam, third)
        
        if predictions:
            st.markdown("### 📊 نتائج التنبؤ")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("الوزن المتوقع", f"{predictions['الوزن المتوقع']:.2f} كجم")
                st.metric("لون الريش", predictions['لون الريش المتوقع'])
            with col2:
                st.metric("شكل العرف", predictions['شكل العرف المتوقع'])
                if 'قوة الهجين' in predictions:
                    st.metric("قوة الهجين", predictions['قوة الهجين'])
            with col3:
                st.metric("نوع الإنتاج", predictions['نوع الإنتاج'])

# ==========================================
# 14. القسم الرابع: تركيب العلائق
# ==========================================
elif "تركيب العلائق" in app_mode:
    st.subheader("🌾 نظام تركيب العلائق الاقتصادية")
    
    feed_df = DatabaseEngine.get_expanded_feed_ingredients()
    
    st.markdown("##### اختيار الخامات:")
    edited_df = st.data_editor(
        feed_df,
        column_config={
            "إدخال في العليقة": st.column_config.CheckboxColumn("إدخال", default=True),
        },
        use_container_width=True
    )
    
    st.markdown("##### الاحتياجات الغذائية:")
    col1, col2, col3 = st.columns(3)
    with col1:
        req_cp = st.number_input("CP %:", 8.0, 30.0, 18.0)
        req_me = st.number_input("ME Kcal:", 1200, 3500, 2800)
    with col2:
        req_cf = st.number_input("CF %:", 2.0, 25.0, 6.0)
        req_ca = st.number_input("Ca %:", 0.0, 5.0, 1.0)
    with col3:
        req_avp = st.number_input("Av.P %:", 0.0, 2.0, 0.45)
    
    if st.button("🚀 حساب العليقة", type="primary"):
        selected_df = edited_df[edited_df["إدخال في العليقة"] == True].reset_index(drop=True)
        
        if len(selected_df) == 0:
            st.error("⚠️ اختر مادة خام واحدة على الأقل")
        else:
            optimizer = FeedOptimizer(selected_df, req_cp, req_me, req_cf, req_ca, req_avp)
            res = optimizer.optimize()
            
            if res is not None and res.success:
                st.success("✅ تم حساب التركيبة المثلى!")
                
                result_df = selected_df.copy()
                result_df["النسبة %"] = np.round(res.x * 100, 2)
                result_df["كجم/طن"] = np.round(res.x * 1000, 1)
                result_df["التكلفة/طن"] = np.round(res.x * 1000 * result_df["Cost_Kg"], 2)
                
                active = result_df[result_df["النسبة %"] > 0].reset_index(drop=True)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("تكلفة الكجم", f"${res.fun:.3f}")
                col2.metric("تكلفة الطن", f"${res.fun * 1000:.2f}")
                col3.metric("عدد المكونات", len(active))
                
                st.dataframe(active, use_container_width=True)
                
                fig = px.pie(active, values="النسبة %", names="المادة الخام", title="توزيع العليقة")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ الخامات غير كافية لتحقيق المستهدفات")

# ==========================================
# 15. القسم الخامس: الإحلال الاقتصادي
# ==========================================
elif "الإحلال الاقتصادي" in app_mode:
    st.subheader("📊 دراسات الإحلال الاقتصادي")
    
    alternatives = {
        "كسبة زهرة الشمس": {"السعر": 2.10, "البدائل": {"كسبة فول الصويا": 3.10, "كسبة بذرة القطن": 2.20, "أمباز السمسم": 2.80}},
        "الذرة الصفراء": {"السعر": 1.35, "البدائل": {"الذرة الرفيعة": 1.20, "القمح": 1.50, "الشعير": 1.10}}
    }
    
    ingredient = st.selectbox("اختر المادة:", list(alternatives.keys()))
    data = alternatives[ingredient]
    
    st.markdown(f"#### السعر الحالي: ${data['السعر']:.2f}/كجم")
    
    st.markdown("##### البدائل:")
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
# 16. القسم السادس: الموسوعة الوراثية
# ==========================================
else:
    st.subheader("📚 الموسوعة الوراثية للسلالات العالمية")
    
    search = st.text_input("🔍 بحث:", placeholder="اكتب اسم السلالة...")
    
    poultry_db = PoultryDatabase()
    all_breeds = poultry_db.get_all_breeds()
    
    for category, breeds in all_breeds.items():
        filtered = breeds
        if search:
            filtered = {name: data for name, data in breeds.items() if search.lower() in name.lower()}
        
        if filtered:
            st.markdown(f"### {category}")
            cols = st.columns(3)
            for idx, (name, data) in enumerate(filtered.items()):
                with cols[idx % 3]:
                    with st.expander(f"🐔 {name}"):
                        st.markdown(f"""
                        **النوع:** {data.get('type', '')}
                        **المنشأ:** {data.get('origin', '')}
                        **الوزن:** {data.get('weight', data.get('weight_35d', ''))} كجم
                        **إنتاج البيض:** {data.get('egg_production', '')} بيضة/سنة
                        **لون الريش:** {data.get('feather_color', '')}
                        **شكل العرف:** {data.get('comb_type', '')}
                        **مميزات:** {data.get('special', 'لا يوجد')}
                        """)

# ==========================================
# 17. أسفل الصفحة
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
