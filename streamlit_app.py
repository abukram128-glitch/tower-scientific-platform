import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from itertools import product
import hashlib
import base64
from datetime import datetime

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
APP_VERSION = "3.0.0"

def generate_license_hash():
    return hashlib.sha256(f"{SECURITY_KEY}_{datetime.now().year}".encode()).hexdigest()[:16]

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
    
    /* Banner متحرك للوقف */
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
    // منع جميع محاولات النسخ والوصول
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
    
    // حماية إضافية
    window.addEventListener('beforeunload', function(e) {
        // منع حفظ الصفحة
    });
    
    // منع اختيار النص
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
    });
    </script>
""", unsafe_allow_html=True)

# ==========================================
# 2. Banner الوالدين والدعاء
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
# 3. التطوير الشامل لقاعدة بيانات السلالات
# ==========================================
class PoultryDatabase:
    """قاعدة بيانات متكاملة لسلالات الدواجن"""
    
    @staticmethod
    def get_all_breeds():
        return {
            # سلالات البياض (Layer Breeds)
            "البياض": {
                "Hy-Line W-36": {
                    "type": "بياض", "origin": "USA", "egg_production": 320, 
                    "egg_weight": 62, "body_weight": 1.5, "feather_color": "أبيض",
                    "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.20
                },
                "Hy-Line W-80": {
                    "type": "بياض", "origin": "USA", "egg_production": 340,
                    "egg_weight": 60, "body_weight": 1.6, "feather_color": "أبيض",
                    "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.22
                },
                "Lohmann Brown": {
                    "type": "بياض", "origin": "Germany", "egg_production": 330,
                    "egg_weight": 63, "body_weight": 1.8, "feather_color": "بني",
                    "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.21
                },
                "Lohmann LSL": {
                    "type": "بياض", "origin": "Germany", "egg_production": 345,
                    "egg_weight": 61, "body_weight": 1.7, "feather_color": "أبيض",
                    "comb_type": "ورقي", "egg_color": "أبيض", "h2_egg": 0.23
                },
                "ISA Brown": {
                    "type": "بياض", "origin": "France", "egg_production": 335,
                    "egg_weight": 62, "body_weight": 1.9, "feather_color": "بني",
                    "comb_type": "ورقي", "egg_color": "بني", "h2_egg": 0.19
                },
                "Babcock B-300": {
                    "type": "بياض", "origin": "Canada", "egg_production": 325,
                    "egg_weight": 60, "body_weight": 1.6, "feather_color": "أبيض",
                    "comb_type": "ورقي", "egg_color": "أبيض", "h2_egg": 0.18
                }
            },
            # سلالات اللاحم (Broiler Breeds)
            "اللاحم": {
                "Cobb 500": {
                    "type": "لاحم", "origin": "USA", "weight_35d": 2.4,
                    "fcr": 1.52, "breast_yield": 22.5, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.40
                },
                "Cobb 700": {
                    "type": "لاحم", "origin": "USA", "weight_35d": 2.5,
                    "fcr": 1.50, "breast_yield": 23.0, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.42
                },
                "Ross 308": {
                    "type": "لاحم", "origin": "UK", "weight_35d": 2.38,
                    "fcr": 1.54, "breast_yield": 22.0, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.38
                },
                "Ross 708": {
                    "type": "لاحم", "origin": "UK", "weight_35d": 2.45,
                    "fcr": 1.51, "breast_yield": 22.8, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.41
                },
                "Arbor Acres": {
                    "type": "لاحم", "origin": "USA", "weight_35d": 2.42,
                    "fcr": 1.53, "breast_yield": 21.5, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.39
                },
                "Indian River": {
                    "type": "لاحم", "origin": "USA", "weight_35d": 2.36,
                    "fcr": 1.55, "breast_yield": 21.0, "feather_color": "أبيض",
                    "comb_type": "ورقي", "h2_weight": 0.37
                }
            },
            # سلالات الزينة والتراثية (Ornamental & Heritage)
            "الزينة": {
                "الدجاج البلدي المصري": {
                    "type": "زينة", "origin": "Egypt", "weight": 1.8,
                    "egg_production": 120, "feather_color": "متنوع",
                    "comb_type": "ورقي", "special": "مقاوم للحرارة"
                },
                "الدجاج الهندي (Aseel)": {
                    "type": "زينة", "origin": "India", "weight": 2.5,
                    "egg_production": 80, "feather_color": "أحمر/أسود",
                    "comb_type": "بازلائي", "special": "مقاتل"
                },
                "Brahma": {
                    "type": "زينة", "origin": "USA", "weight": 4.5,
                    "egg_production": 150, "feather_color": "رمادي/أبيض",
                    "comb_type": "بازلائي", "special": "عملاق"
                },
                "Cochin": {
                    "type": "زينة", "origin": "China", "weight": 4.0,
                    "egg_production": 130, "feather_color": "أسود/أبيض",
                    "comb_type": "ورقي", "special": "ريش كثيف"
                },
                "Orpington": {
                    "type": "زينة", "origin": "UK", "weight": 3.5,
                    "egg_production": 160, "feather_color": "بني/أسود",
                    "comb_type": "ورقي", "special": "طيب المزاج"
                },
                "Silkie": {
                    "type": "زينة", "origin": "China", "weight": 1.5,
                    "egg_production": 100, "feather_color": "أبيض/أسود",
                    "comb_type": "ورقي", "special": "ريش ناعم كالحرير"
                },
                "Phoenix": {
                    "type": "زينة", "origin": "Japan", "weight": 2.0,
                    "egg_production": 90, "feather_color": "ذهبي/أحمر",
                    "comb_type": "ورقي", "special": "ذيل طويل"
                },
                "Polish": {
                    "type": "زينة", "origin": "Poland", "weight": 2.2,
                    "egg_production": 140, "feather_color": "أبيض/أسود",
                    "comb_type": "ورقي", "special": "عرف كثيف"
                },
                "Sultan": {
                    "type": "زينة", "origin": "Turkey", "weight": 2.0,
                    "egg_production": 85, "feather_color": "أبيض",
                    "comb_type": "ورقي", "special": "أرجل كثيفة الريش"
                }
            }
        }
    
    @staticmethod
    def get_hybrid_predictions(breed1, breed2, breed3=None):
        """التنبؤ بخصائص الهجين من نوعين أو ثلاثة"""
        all_breeds = PoultryDatabase.get_all_breeds()
        breed_data = {}
        
        # جمع بيانات السلالات المختارة
        for category in all_breeds.values():
            if breed1 in category:
                breed_data['sire'] = category[breed1]
            if breed2 in category:
                breed_data['dam'] = category[breed2]
            if breed3 and breed3 in category:
                breed_data['third'] = category[breed3]
        
        if len(breed_data) < 2:
            return None
        
        # التنبؤ بخصائص الهجين
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
            predictions["قوة الهجين (Hybrid Vigor)"] = "عالية (تهجين ثلاثي)"
        
        # إضافة توقع شكل العرف
        comb_types = []
        for b in breed_data.values():
            comb_types.append(b.get('comb_type', 'ورقي'))
        if len(set(comb_types)) > 1:
            predictions["شكل العرف المتوقع"] = "متغير (ورقي/بازلائي)"
        
        return predictions

# ==========================================
# 4. محرك التهجين المتقدم
# ==========================================
class AdvancedGeneticsEngine(GeneticsEngine):
    
    @staticmethod
    def predict_offspring_appearance(sire_genotype, dam_genotype, traits):
        """
        التنبؤ بمظهر النسل بناءً على عدة صفات
        traits: قاموس يحتوي على معلومات الصفات
        """
        results = {}
        
        for trait_name, trait_info in traits.items():
            geno_prob, pheno_prob, _ = GeneticsEngine.calculate_punnett_square(
                sire_genotype, dam_genotype, trait_info
            )
            results[trait_name] = {
                "genotypes": geno_prob,
                "phenotypes": pheno_prob
            }
        
        return results

# ==========================================
# 5. تحديث محرك تركيب الأعلاف
# ==========================================
class EnhancedFeedOptimizer(AdvancedFeedOptimizer):
    
    def __init__(self, selected_df, target_cp, target_me, target_cf_max, target_ca, target_avp, 
                 target_lys=None, target_met=None, target_cys=None):
        super().__init__(selected_df, target_cp, target_me, target_cf_max, target_ca, target_avp)
        self.target_lys = target_lys
        self.target_met = target_met
        self.target_cys = target_cys
        
    def optimize(self):
        try:
            costs = self.df["Cost_Kg"].values
            cp = self.df["CP"].values
            me = self.df["ME_Kcal"].values
            cf = self.df["CF"].values
            ca = self.df["Ca"].values
            avp = self.df["AvP"].values
            max_bounds = self.df["Max_Include"].values / 100.0
            
            # إضافة الأحماض الأمينية إذا كانت متوفرة
            A_ub = [-cp, -me, cf, -ca, -avp]
            b_ub = [-self.target_cp, -self.target_me, self.target_cf_max, -self.target_ca, -self.target_avp]
            
            # إضافة قيود الأحماض الأمينية
            if self.target_lys is not None and 'Lys' in self.df.columns:
                A_ub.append(-self.df['Lys'].values)
                b_ub.append(-self.target_lys)
            
            if self.target_met is not None and 'Met' in self.df.columns:
                A_ub.append(-self.df['Met'].values)
                b_ub.append(-self.target_met)
            
            A_eq = [np.ones(len(costs))]
            b_eq = [1.0]
            
            bounds = [(0, b) for b in max_bounds]
            result = linprog(costs, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                           bounds=bounds, method='highs')
            
            return result
        except Exception as e:
            st.error(f"خطأ في تحسين العليقة: {str(e)}")
            return None

# ==========================================
# 6. الواجهة الرئيسية المطورة
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
# 7. القوائم الجانبية المطورة
# ==========================================
st.sidebar.markdown("### 🌟 أروقة المنتدى المتطورة")
app_mode = st.sidebar.radio("اختر التطبيق:", [
    "🧬 الهندسة الوراثية المتقدمة",
    "🐔 تهجين الدواجن العالمي",
    "🌾 تركيب العلائق المتطور",
    "📊 دراسات الإحلال الاقتصادي",
    "📚 الموسوعة الوراثية للسلالات"
])

# ==========================================
# 8. القسم الأول: الهندسة الوراثية المتقدمة
# ==========================================
if "الهندسة الوراثية" in app_mode:
    st.subheader("🧬 محرك الهندسة الوراثية المتقدمة")
    
    tab_advanced1, tab_advanced2 = st.tabs([
        "🔬 تحليل الصفات المتعددة", 
        "🧮 التنبؤ بالظواهر الجينية"
    ])
    
    with tab_advanced1:
        st.markdown("##### تحليل وراثي متقدم لصفات متعددة")
        st.info("يقوم هذا المحرك بتحليل توارث عدة صفات في وقت واحد")
        
        # اختيار الصفات المراد دراستها
        traits = {}
        trait_count = st.number_input("عدد الصفات المراد دراستها:", 1, 5, 2)
        
        for i in range(int(trait_count)):
            with st.expander(f"الصفة {i+1}"):
                trait_name = st.text_input(f"اسم الصفة {i+1}:", f"صفة {i+1}")
                dom_allele = st.text_input(f"الأليل السائد:", "A")
                rec_allele = st.text_input(f"الأليل المتنحي:", "a")
                dom_trait = st.text_input(f"الطراز المظهري السائد:", "سائد")
                rec_trait = st.text_input(f"الطراز المظهري المتنحي:", "متنحي")
                inh_type = st.selectbox(f"نمط السيادة:", ["سيادة تامة", "سيادة غير تامة"])
                
                traits[trait_name] = {
                    "dominant_allele": dom_allele,
                    "recessive_allele": rec_allele,
                    "dominant_trait": dom_trait,
                    "recessive_trait": rec_trait,
                    "intermediate_trait": "متوسط" if "غير" in inh_type else dom_trait,
                    "inheritance": "Complete" if "تامة" in inh_type else "Incomplete"
                }
        
        if st.button("تحليل الصفات المتعددة", type="primary"):
            st.subheader("نتائج التحليل الوراثي المتعدد")
            
            # محاكاة التهجين لكل صفة
            all_results = {}
            for trait_name, trait_info in traits.items():
                sire_geno = f"{trait_info['dominant_allele']}{trait_info['recessive_allele']}"
                dam_geno = f"{trait_info['dominant_allele']}{trait_info['recessive_allele']}"
                
                geno_prob, pheno_prob, _ = GeneticsEngine.calculate_punnett_square(
                    sire_geno, dam_geno, trait_info
                )
                all_results[trait_name] = {"genotypes": geno_prob, "phenotypes": pheno_prob}
            
            # عرض النتائج
            for trait_name, results in all_results.items():
                st.markdown(f"#### {trait_name}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**التوزيع الجيني:**")
                    for g, p in results["genotypes"].items():
                        st.write(f"- {g}: {p:.1f}%")
                with col2:
                    st.write("**التوزيع المظهري:**")
                    for p, prob in results["phenotypes"].items():
                        st.write(f"- {p}: {prob:.1f}%")

# ==========================================
# 9. القسم الثاني: تهجين الدواجن العالمي
# ==========================================
elif "تهجين الدواجن" in app_mode:
    st.subheader("🐔 نظام تهجين الدواجن العالمي المتقدم")
    
    # عرض السلالات المتاحة
    poultry_db = PoultryDatabase()
    all_breeds = poultry_db.get_all_breeds()
    
    with st.expander("📋 قائمة السلالات المتاحة للتهجين", expanded=True):
        for category, breeds in all_breeds.items():
            st.markdown(f"#### {category}")
            cols = st.columns(3)
            for idx, (name, data) in enumerate(breeds.items()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="genetic-card">
                        <strong>{name}</strong><br>
                        {data.get('origin', 'غير معروف')}<br>
                        {'🐣' + str(data.get('egg_production', 0)) + ' بيضة' if 'egg_production' in data else '⚖️ ' + str(data.get('weight_35d', 0))}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🔬 تصميم برنامج تهجين")
    
    # اختيار أنواع التهجين
    hybrid_type = st.radio("نوع التهجين:", ["تهجين ثنائي (2 سلالة)", "تهجين ثلاثي (3 سلالات)"])
    
    col_breed1, col_breed2 = st.columns(2)
    
    # تجميع كل السلالات في قائمة واحدة
    all_breed_names = []
    for category in all_breeds.values():
        all_breed_names.extend(list(category.keys()))
    
    with col_breed1:
        sire_breed = st.selectbox("اختر السلالة الأبوية (Sire):", all_breed_names, index=0)
    with col_breed2:
        dam_breed = st.selectbox("اختر السلالة الأمومية (Dam):", all_breed_names, index=1)
    
    third_breed = None
    if hybrid_type == "تهجين ثلاثي (3 سلالات)":
        third_breed = st.selectbox("اختر السلالة الثالثة:", all_breed_names, index=2)
    
    if st.button("🧬 تنبؤ خصائص الهجين", type="primary"):
        predictions = poultry_db.get_hybrid_predictions(sire_breed, dam_breed, third_breed)
        
        if predictions:
            st.markdown("### 📊 نتائج التنبؤ بالهجين")
            
            col_pred1, col_pred2, col_pred3 = st.columns(3)
            
            with col_pred1:
                st.metric("الوزن المتوقع", f"{predictions['الوزن المتوقع']:.2f} كجم")
                st.metric("لون الريش", predictions['لون الريش المتوقع'])
            
            with col_pred2:
                st.metric("شكل العرف", predictions['شكل العرف المتوقع'])
                if 'قوة الهجين (Hybrid Vigor)' in predictions:
                    st.metric("قوة الهجين", predictions['قوة الهجين (Hybrid Vigor)'])
            
            with col_pred3:
                st.metric("نوع الإنتاج", predictions['نوع الإنتاج'])
            
            # رسم بياني لتوزيع الأجيال
            st.markdown("### 📈 توزيع الأجيال المتوقعة")
            gen_data = pd.DataFrame({
                'الجيل': ['F1', 'F2', 'F3'],
                'التنوع الجيني': [85, 92, 95],
                'قوة الهجين': [100, 85, 70]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gen_data['الجيل'], y=gen_data['التنوع الجيني'],
                                    mode='lines+markers', name='التنوع الجيني'))
            fig.add_trace(go.Scatter(x=gen_data['الجيل'], y=gen_data['قوة الهجين'],
                                    mode='lines+markers', name='قوة الهجين'))
            fig.update_layout(title='تطور التنوع الجيني وقوة الهجين عبر الأجيال',
                             xaxis_title='الجيل', yaxis_title='النسبة المئوية')
            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 10. القسم الثالث: تركيب العلائق المتطور
# ==========================================
elif "تركيب العلائق" in app_mode:
    st.subheader("🌾 نظام تركيب العلائق المتطور (بمكونات متقدمة)")
    
    # تحميل قاعدة البيانات المطورة
    feed_df = DatabaseEngine.get_expanded_feed_ingredients()
    
    # إضافة أعمدة الأحماض الأمينية
    if 'Lys' not in feed_df.columns:
        feed_df['Lys'] = feed_df['CP'] * 0.06  # تقدير تقريبي
    if 'Met' not in feed_df.columns:
        feed_df['Met'] = feed_df['CP'] * 0.025  # تقدير تقريبي
    
    tab_advanced_feed1, tab_advanced_feed2 = st.tabs([
        "📋 اختيار الخامات", 
        "⚙️ تحديد الاحتياجات المتقدمة"
    ])
    
    with tab_advanced_feed1:
        st.markdown("##### جدول الخامات العلفية المتطور:")
        edited_df = st.data_editor(
            feed_df,
            column_config={
                "إدخال في العليقة": st.column_config.CheckboxColumn(
                    "إدخال في العليقة",
                    help="تحديد الخامات الداخلة في الحسابات",
                    default=True,
                ),
                "Lys": st.column_config.NumberColumn(
                    "اللايسين %",
                    help="نسبة اللايسين في المادة",
                    min_value=0,
                    max_value=100,
                    step=0.1,
                ),
                "Met": st.column_config.NumberColumn(
                    "المثيونين %",
                    help="نسبة المثيونين في المادة",
                    min_value=0,
                    max_value=100,
                    step=0.1,
                )
            },
            num_rows="dynamic",
            use_container_width=True
        )
    
    with tab_advanced_feed2:
        st.markdown("##### تحديد الاحتياجات الغذائية المتقدمة:")
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            req_cp = st.number_input("البروتين الخام (CP %):", 8.0, 30.0, 18.0, step=0.5)
            req_me = st.number_input("الطاقة (ME Kcal/Kg):", 1200, 3500, 2800, step=50)
        
        with col_adv2:
            req_cf_max = st.number_input("الألياف القصوى (CF %):", 2.0, 25.0, 6.0, step=0.5)
            req_ca = st.number_input("الكالسيوم الأدنى (Ca %):", 0.0, 5.0, 1.0, step=0.1)
            req_avp = st.number_input("الفوسفور المتاح (Av.P %):", 0.0, 2.0, 0.45, step=0.05)
        
        with col_adv3:
            req_lys = st.number_input("اللايسين الأدنى (Lys %):", 0.0, 2.0, 0.8, step=0.05)
            req_met = st.number_input("المثيونين الأدنى (Met %):", 0.0, 1.0, 0.35, step=0.05)
            req_met_cys = st.number_input("المثيونين + السيستين %:", 0.0, 1.5, 0.6, step=0.05)
    
    if st.button("🚀 حساب العليقة المثلى المتقدمة", type="primary", use_container_width=True):
        selected_df = edited_df[edited_df["إدخال في العليقة"] == True].reset_index(drop=True)
        
        if len(selected_df) == 0:
            st.error("⚠️ يجب اختيار مادة خام واحدة على الأقل!")
        else:
            optimizer = EnhancedFeedOptimizer(
                selected_df, req_cp, req_me, req_cf_max, req_ca, req_avp,
                req_lys, req_met
            )
            res = optimizer.optimize()
            
            if res is not None and res.success:
                st.success("✅ تم حساب التركيبة المثلى!")
                
                # عرض النتائج المفصلة
                result_df = selected_df[["المادة الخام", "Cost_Kg", "CP", "ME_Kcal", "CF", "Ca", "AvP", "Lys", "Met"]].copy()
                result_df["النسبة %"] = np.round(res.x * 100, 2)
                result_df["كجم/طن"] = np.round(res.x * 1000, 1)
                result_df["التكلفة/طن"] = np.round(res.x * 1000 * result_df["Cost_Kg"], 2)
                
                active_results = result_df[result_df["النسبة %"] > 0].reset_index(drop=True)
                
                # عرض المقاييس
                col_metric1, col_metric2, col_metric3 = st.columns(3)
                with col_metric1:
                    st.metric("تكلفة الكجم", f"${res.fun:.3f}")
                with col_metric2:
                    st.metric("تكلفة الطن", f"${res.fun * 1000:.2f}")
                with col_metric3:
                    st.metric("عدد المكونات", len(active_results))
                
                # عرض الجدول
                st.markdown("#### 📊 تركيب العليقة المحسوب")
                st.dataframe(active_results, use_container_width=True)
                
                # الرسوم البيانية
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    fig_pie = px.pie(active_results, values="النسبة %", names="المادة الخام",
                                    title="توزيع مكونات العليقة")
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_chart2:
                    fig_bar = px.bar(active_results, x="المادة الخام", y="النسبة %",
                                   title="نسب المكونات")
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.error("❌ الخامات المختارة غير كافية لتحقيق المستهدفات المطلوبة")

# ==========================================
# 11. القسم الرابع: دراسات الإحلال الاقتصادي
# ==========================================
elif "الإحلال الاقتصادي" in app_mode:
    st.subheader("📊 نظام دراسات الإحلال الاقتصادي المتقدم")
    
    # قائمة بدائل المواد الخام
    alternative_ingredients = {
        "كسبة زهرة الشمس": {
            "السعر الحالي": 2.10,
            "البدائل": {
                "كسبة فول الصويا": 3.10,
                "كسبة بذرة القطن": 2.20,
                "أمباز السمسم": 2.80
            }
        },
        "الذرة الصفراء": {
            "السعر الحالي": 1.35,
            "البدائل": {
                "الذرة الرفيعة": 1.20,
                "القمح": 1.50,
                "الشعير": 1.10
            }
        }
    }
    
    selected_ingredient = st.selectbox("اختر المادة للإحلال:", list(alternative_ingredients.keys()))
    ingredient_data = alternative_ingredients[selected_ingredient]
    
    st.markdown(f"#### السعر الحالي: ${ingredient_data['السعر الحالي']:.2f}/كجم")
    
    st.markdown("##### البدائل المتاحة:")
    for alt, price in ingredient_data["البدائل"].items():
        saving = ingredient_data["السعر الحالي"] - price
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{alt}** - ${price:.2f}/كجم")
        with col2:
            if saving > 0:
                st.success(f"توفير ${saving:.2f}")
            else:
                st.warning(f"خسارة ${-saving:.2f}")
    
    # حاسبة الإحلال
    st.markdown("---")
    st.markdown("### 💰 حاسبة التوفير من الإحلال")
    
    col_calc1, col_calc2 = st.columns(2)
    with col_calc1:
        current_usage = st.number_input("الاستهلاك الشهري (طن):", 0.1, 100.0, 10.0)
        replacement_pct = st.slider("نسبة الإحلال المطلوبة (%):", 0, 100, 30)
    
    with col_calc2:
        selected_alternative = st.selectbox("اختر البديل:", list(ingredient_data["البدائل"].keys()))
        alt_price = ingredient_data["البدائل"][selected_alternative]
        
    saving_per_ton = (ingredient_data["السعر الحالي"] - alt_price) * 1000 * (replacement_pct / 100)
    total_saving = saving_per_ton * current_usage
    
    st.metric("التوفير المتوقع شهرياً", f"${total_saving:,.2f}")
    st.metric("التوفير السنوي المتوقع", f"${total_saving * 12:,.2f}")

# ==========================================
# 12. القسم الخامس: الموسوعة الوراثية
# ==========================================
else:
    st.subheader("📚 الموسوعة الوراثية للسلالات العالمية")
    
    # فلتر البحث
    search_term = st.text_input("🔍 بحث في السلالات:", placeholder="اكتب اسم السلالة...")
    
    poultry_db = PoultryDatabase()
    all_breeds = poultry_db.get_all_breeds()
    
    for category, breeds in all_breeds.items():
        st.markdown(f"### {category}")
        
        filtered_breeds = breeds
        if search_term:
            filtered_breeds = {name: data for name, data in breeds.items() 
                             if search_term.lower() in name.lower()}
        
        if not filtered_breeds:
            continue
            
        cols = st.columns(3)
        for idx, (name, data) in enumerate(filtered_breeds.items()):
            with cols[idx % 3]:
                with st.expander(f"🐔 {name}"):
                    st.markdown(f"""
                    **النوع:** {data.get('type', 'غير محدد')}
                    
                    **المنشأ:** {data.get('origin', 'غير معروف')}
                    
                    **الوزن:** {data.get('weight', data.get('weight_35d', 'غير محدد'))} كجم
                    
                    **إنتاج البيض:** {data.get('egg_production', 'غير محدد')} بيضة/سنة
                    
                    **لون الريش:** {data.get('feather_color', 'غير محدد')}
                    
                    **شكل العرف:** {data.get('comb_type', 'غير محدد')}
                    
                    **مميزات خاصة:** {data.get('special', 'لا يوجد')}
                    """)

# ==========================================
# 13. أسفل الصفحة
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; padding: 20px;">
    <div style="font-size: 0.9rem;">
        🧬 هذا البرنامج مُسجل ومحمي بموجب حقوق الملكية الفكرية
    </div>
    <div style="font-size: 0.8rem; margin-top: 5px;">
        تم التطوير بواسطة: <strong>د. عبد القادر إسماعيل</strong> - أخصائي الإنتاج الحيواني
    </div>
    <div style="font-size: 0.7rem; margin-top: 5px; color: #64748B;">
        الإصدار 3.0.0 | جميع الحقوق محفوظة © 2024
    </div>
    <div style="font-size: 0.7rem; margin-top: 10px; color: #60A5FA; border-top: 1px solid #1E293B; padding-top: 10px;">
        <span style="color: #FCD34D;">🤲</span> 
        اللهم اجعل هذا العمل صدقة جارية لوالدي، واجعله في ميزان حسناتهما 
        <span style="color: #FCD34D;">🤲</span>
    </div>
</div>

<div class="security-badge">
    🔒 Secured v3.0 | License: {0}
</div>
""".format(generate_license_hash()), unsafe_allow_html=True)
