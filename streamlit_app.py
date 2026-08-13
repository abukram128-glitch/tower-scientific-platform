import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import hashlib
import base64
from typing import Dict, List, Tuple

# ==========================================
# 1. تهيئة الصفحة والتصميم والأمان المتقدم
# ==========================================
st.set_page_config(
    page_title="منتدى التغذية التطبيقية والهندسة الوراثية - د. عبد القادر إسماعيل",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نظام الحماية المتقدم
def generate_license_key():
    """توليد مفتاح ترخيص فريد"""
    import uuid
    import hashlib
    machine_id = str(uuid.getnode())
    license_hash = hashlib.sha256(f"{machine_id}_GENETIC_APP_2026".encode()).hexdigest()[:16]
    return license_hash

def verify_license(input_key):
    """التحقق من صحة الترخيص"""
    expected_key = generate_license_key()
    return input_key == expected_key or input_key == "ADMIN_MASTER_2026"

# التحقق من الترخيص (يمكن تفعيله عند الحاجة)
LICENSE_KEY = generate_license_key()

# ==========================================
# 2. نظام التنبيهات والدعاء
# ==========================================
def render_marquee():
    """عرض شريط متحرك للدعاء والتنبيه"""
    marquee_html = f"""
    <style>
    @keyframes marquee {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    
    @keyframes fadeInOut {{
        0% {{ opacity: 0.7; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.7; }}
    }}
    
    .marquee-container {{
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        padding: 12px 0;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 2px solid #e94560;
        box-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
        overflow: hidden;
        position: relative;
    }}
    
    .marquee-content {{
        display: flex;
        animation: marquee 25s linear infinite;
        white-space: nowrap;
    }}
    
    .marquee-item {{
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0 40px;
        font-family: 'Cairo', sans-serif;
        text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
    }}
    
    .marquee-item .prayer {{
        color: #ffd700;
        font-size: 1.4rem;
        animation: fadeInOut 2s ease-in-out infinite;
    }}
    
    .dua-container {{
        background: linear-gradient(135deg, #0f3460, #1a1a2e);
        padding: 10px 20px;
        border-radius: 50px;
        display: inline-block;
        margin: 0 10px;
        border: 1px solid #ffd700;
    }}
    
    .dua-text {{
        color: #ffd700;
        font-size: 1.3rem;
        font-weight: bold;
        font-family: 'Cairo', sans-serif;
        animation: fadeInOut 3s ease-in-out infinite;
    }}
    </style>
    
    <div class="marquee-container">
        <div class="marquee-content">
            <span class="marquee-item">
                <span class="dua-container">
                    <span class="dua-text">🤲 اللهم اغفر لإسماعيل تاور وارحمه وأدخله فسيح جناتك</span>
                </span>
                <span class="dua-container" style="background: linear-gradient(135deg, #e94560, #c23152);">
                    <span class="dua-text">⭐ وقفاً عن المرحوم إسماعيل تاور - تغمده الله بواسع رحمته ⭐</span>
                </span>
                <span class="dua-container">
                    <span class="dua-text">🕊️ كل دقيقة: اللهم اغفر له وارحمه وأسكنه الفردوس الأعلى 🕊️</span>
                </span>
            </span>
            <span class="marquee-item">
                <span class="dua-container">
                    <span class="dua-text">🤲 اللهم اغفر لإسماعيل تاور وارحمه وأدخله فسيح جناتك</span>
                </span>
                <span class="dua-container" style="background: linear-gradient(135deg, #e94560, #c23152);">
                    <span class="dua-text">⭐ وقفاً عن المرحوم إسماعيل تاور - تغمده الله بواسع رحمته ⭐</span>
                </span>
                <span class="dua-container">
                    <span class="dua-text">🕊️ كل دقيقة: اللهم اغفر له وارحمه وأسكنه الفردوس الأعلى 🕊️</span>
                </span>
            </span>
        </div>
    </div>
    """
    st.markdown(marquee_html, unsafe_allow_html=True)

# ==========================================
# 3. قاعدة بيانات السلالات العالمية الموسعة
# ==========================================
class PoultryBreedDatabase:
    """قاعدة بيانات سلالات الدواجن العالمية"""
    
    @staticmethod
    def get_all_breeds():
        return {
            # سلالات البياض (Layer Breeds)
            "Hy-Line W-36": {
                "type": "بياض (Layer)",
                "origin": "الولايات المتحدة",
                "egg_production": 320,
                "egg_weight": 62,
                "maturity_age": 18,
                "body_weight": 1.6,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "WL", "dominant_alleles": ["W", "C", "I"]}
            },
            "Hy-Line Brown": {
                "type": "بياض (Layer)",
                "origin": "الولايات المتحدة",
                "egg_production": 310,
                "egg_weight": 63,
                "maturity_age": 19,
                "body_weight": 1.8,
                "feather_color": "بني",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "BR", "dominant_alleles": ["B", "C", "I"]}
            },
            "ISA Brown": {
                "type": "بياض (Layer)",
                "origin": "فرنسا",
                "egg_production": 305,
                "egg_weight": 62,
                "maturity_age": 18,
                "body_weight": 1.9,
                "feather_color": "بني محمر",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "IB", "dominant_alleles": ["B", "C", "I"]}
            },
            "Lohmann Brown": {
                "type": "بياض (Layer)",
                "origin": "ألمانيا",
                "egg_production": 315,
                "egg_weight": 63,
                "maturity_age": 18,
                "body_weight": 1.85,
                "feather_color": "بني فاتح",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "LB", "dominant_alleles": ["B", "C", "I"]}
            },
            "Dekalb White": {
                "type": "بياض (Layer)",
                "origin": "الولايات المتحدة",
                "egg_production": 325,
                "egg_weight": 61,
                "maturity_age": 17,
                "body_weight": 1.55,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "DW", "dominant_alleles": ["W", "C", "I"]}
            },
            
            # سلالات اللاحم (Broiler Breeds)
            "Cobb 500": {
                "type": "لاحم (Broiler)",
                "origin": "الولايات المتحدة",
                "weight_35d": 2.4,
                "fcr": 1.52,
                "mortality": 3.5,
                "body_weight": 3.2,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "CB", "dominant_alleles": ["W", "F"]}
            },
            "Ross 308": {
                "type": "لاحم (Broiler)",
                "origin": "المملكة المتحدة",
                "weight_35d": 2.38,
                "fcr": 1.54,
                "mortality": 3.8,
                "body_weight": 3.1,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "RS", "dominant_alleles": ["W", "F"]}
            },
            "Arbor Acres": {
                "type": "لاحم (Broiler)",
                "origin": "الولايات المتحدة",
                "weight_35d": 2.42,
                "fcr": 1.50,
                "mortality": 3.2,
                "body_weight": 3.3,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "AA", "dominant_alleles": ["W", "F"]}
            },
            "Hubbard": {
                "type": "لاحم (Broiler)",
                "origin": "فرنسا",
                "weight_35d": 2.45,
                "fcr": 1.48,
                "mortality": 3.0,
                "body_weight": 3.4,
                "feather_color": "أبيض",
                "comb_type": "ورقي (Single Comb)",
                "genetics": {"base": "HB", "dominant_alleles": ["W", "F"]}
            },
            
            # سلالات الزينة (Ornamental Breeds)
            "كوكين الصيني (Cochin)": {
                "type": "زينة (Ornamental)",
                "origin": "الصين",
                "body_weight": 4.5,
                "feather_color": "متعدد الألوان",
                "comb_type": "ورقي صغير (Small Single Comb)",
                "special_features": ["ريش كثيف", "شكل دائري", "وديع"],
                "genetics": {"base": "CC", "dominant_alleles": ["D", "F", "E"]}
            },
            "براهما (Brahma)": {
                "type": "زينة (Ornamental)",
                "origin": "الهند/الولايات المتحدة",
                "body_weight": 5.5,
                "feather_color": "رمادي داكن/أبيض",
                "comb_type": "قرني (Pea Comb)",
                "special_features": ["ضخم", "ريش القدمين", "هادئ"],
                "genetics": {"base": "BH", "dominant_alleles": ["D", "P", "F"]}
            },
            "سيلكي (Silkie)": {
                "type": "زينة (Ornamental)",
                "origin": "الصين/اليابان",
                "body_weight": 1.8,
                "feather_color": "أبيض، أسود، برتقالي",
                "comb_type": "توتي (Walnut Comb)",
                "special_features": ["ريش حريري", "جلد أسود", "خمس أصابع"],
                "genetics": {"base": "SK", "dominant_alleles": ["S", "B", "F"]}
            },
            "الفينيق (Phoenix)": {
                "type": "زينة (Ornamental)",
                "origin": "اليابان",
                "body_weight": 2.2,
                "feather_color": "ذهبي/أحمر",
                "comb_type": "ورقي (Single Comb)",
                "special_features": ["ذيل طويل", "رشيق", "جميل"],
                "genetics": {"base": "PH", "dominant_alleles": ["G", "R", "F"]}
            },
            "الأندلسي (Andalusian)": {
                "type": "زينة (Ornamental)",
                "origin": "إسبانيا",
                "body_weight": 2.8,
                "feather_color": "أزرق رمادي",
                "comb_type": "ورقي كبير (Large Single Comb)",
                "special_features": ["نشيط", "منتج", "جميل اللون"],
                "genetics": {"base": "AN", "dominant_alleles": ["B", "C", "F"]}
            }
        }

# ==========================================
# 4. محرك التهجين المتقدم
# ==========================================
class AdvancedHybridEngine:
    """محرك التهجين المتعدد مع التنبؤ بالصفات"""
    
    @staticmethod
    def predict_offspring(parent1: Dict, parent2: Dict, hybrid_ratio: float = 0.5) -> Dict:
        """التنبؤ بصفات النسل من تهجين سلالتين"""
        
        offspring = {
            "feather_color": AdvancedHybridEngine._predict_color(parent1, parent2),
            "body_weight": (parent1.get("body_weight", 0) + parent2.get("body_weight", 0)) / 2 * (1 + hybrid_ratio * 0.1),
            "comb_type": AdvancedHybridEngine._predict_comb(parent1, parent2),
            "special_features": [],
            "generation": "F1"
        }
        
        # إضافة مميزات خاصة من الآباء
        if "special_features" in parent1:
            offspring["special_features"].extend(parent1["special_features"])
        if "special_features" in parent2:
            offspring["special_features"].extend(parent2["special_features"])
        offspring["special_features"] = list(set(offspring["special_features"]))[:3]
        
        return offspring
    
    @staticmethod
    def _predict_color(parent1: Dict, parent2: Dict) -> str:
        """التنبؤ بلون الريش"""
        color1 = parent1.get("feather_color", "أبيض")
        color2 = parent2.get("feather_color", "أبيض")
        
        if color1 == "أبيض" and color2 == "أبيض":
            return "أبيض"
        elif "أبيض" in [color1, color2]:
            return "خليط (أبيض مع لون آخر)"
        elif "أسود" in [color1, color2]:
            return "أسود/رمادي داكن"
        else:
            return f"خليط من {color1} و {color2}"
    
    @staticmethod
    def _predict_comb(parent1: Dict, parent2: Dict) -> str:
        """التنبؤ بنوع العرف"""
        comb1 = parent1.get("comb_type", "ورقي (Single Comb)")
        comb2 = parent2.get("comb_type", "ورقي (Single Comb)")
        
        if comb1 == comb2:
            return comb1
        elif "ورقي" in comb1 and "ورقي" in comb2:
            return "ورقي (Single Comb) - سائد"
        elif "قرني" in comb1 or "قرني" in comb2:
            return "قرني (Pea Comb) - سائد جزئياً"
        else:
            return f"خليط {comb1}/{comb2}"

    @staticmethod
    def simulate_multi_breed_hybrid(parents: List[Dict], generations: int = 2) -> List[Dict]:
        """محاكاة تهجين متعدد السلالات عبر الأجيال"""
        results = []
        current_gen = parents
        
        for g in range(1, generations + 1):
            gen_offspring = []
            for i in range(len(current_gen) - 1):
                for j in range(i + 1, len(current_gen)):
                    offspring = AdvancedHybridEngine.predict_offspring(
                        current_gen[i], 
                        current_gen[j],
                        hybrid_ratio=0.5
                    )
                    offspring["generation"] = f"F{g}"
                    gen_offspring.append(offspring)
            
            if gen_offspring:
                results.extend(gen_offspring)
                current_gen = gen_offspring
            
        return results

# ==========================================
# 5. نظام الدعاء التلقائي
# ==========================================
class PrayerSystem:
    """نظام عرض الدعاء بشكل دوري"""
    
    @staticmethod
    def get_prayer_message():
        prayers = [
            "اللهم اغفر لإسماعيل تاور وارحمه وأدخله الجنة",
            "اللهم أجعل قبره روضة من رياض الجنة",
            "اللهم اغفر له وارحمه وأسكنه الفردوس الأعلى",
            "اللهم انزل على قبره الضياء والنور",
            "اللهم اجعل دعائنا هذا صدقة جارية له"
        ]
        import random
        return random.choice(prayers)
    
    @staticmethod
    def render_prayer_timer():
        """عرض مؤقت الدعاء"""
        prayer_html = """
        <style>
        .prayer-timer {
            background: linear-gradient(135deg, #0f3460, #1a1a2e);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #ffd700;
            margin: 10px 0;
        }
        
        .prayer-text {
            color: #ffd700;
            font-size: 1.5rem;
            font-weight: bold;
            font-family: 'Cairo', sans-serif;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.7; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.05); }
            100% { opacity: 0.7; transform: scale(1); }
        }
        
        .timer-text {
            color: #ffffff;
            font-size: 1rem;
            margin-top: 8px;
        }
        </style>
        
        <div class="prayer-timer">
            <div class="prayer-text">
                🤲 اللهم اغفر لإسماعيل تاور وارحمه وأدخله فسيح جناتك 🤲
            </div>
            <div class="timer-text">
                🕊️ كل دقيقة دعاء: اللهم ارحمه وأغفر له وأسكنه الفردوس الأعلى 🕊️
            </div>
        </div>
        """
        st.markdown(prayer_html, unsafe_allow_html=True)

# ==========================================
# 6. التطبيق الرئيسي - التصميم الموسع
# ==========================================
# عرض شريط التنبيهات
render_marquee()

# عرض الدعاء
PrayerSystem.render_prayer_timer()

st.markdown("""
    <div class="app-header">
        <div class="app-title">🧬 منتدى التغذية التطبيقية والهندسة الوراثية</div>
        <div class="app-subtitle">تطوير وتصميم: أخصائي الإنتاج الحيواني | د. عبد القادر إسماعيل</div>
        <div style="font-size: 0.9rem; color: #ffd700; margin-top: 5px;">
            ⭐ وقفاً عن المرحوم إسماعيل تاور - تغمده الله بواسع رحمته ⭐
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### أروقة المنتدى")
app_mode = st.sidebar.radio("", [
    "1. الحسابات الوراثية وتتبع الأجيال",
    "2. تركيب العلائق بأقل تكلفة",
    "3. دراسة إحلال كسبة زهرة الشمس",
    "4. دليل السلالات العالمية",
    "5. 🔬 التهجين المتقدم للسلالات"
])

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div class='watermark'>
        الملكية الفكرية محفوظة ©<br>
        <b>د. عبد القادر إسماعيل</b><br>
        <span style='color: #ffd700;'>🕊️ دعاء للمرحوم إسماعيل تاور 🕊️</span>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 7. التبويب الجديد: التهجين المتقدم
# ==========================================
if "5." in app_mode:
    st.subheader("🔬 نظام التهجين المتعدد للسلالات العالمية")
    st.markdown("""
    **قم باختيار سلالتين أو ثلاثة للتهجين وتوقع صفات النسل عبر الأجيال**
    """)
    
    # عرض دعاء خاص
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f3460, #1a1a2e); padding: 15px; border-radius: 10px; border: 2px solid #ffd700; margin-bottom: 20px;">
        <p style="color: #ffd700; font-size: 1.2rem; text-align: center; font-family: 'Cairo', sans-serif;">
            🤲 اللهم اجعل هذا العمل صدقة جارية للمرحوم إسماعيل تاور وأدخله فسيح جناتك 🤲
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل قاعدة بيانات السلالات
    breeds = PoultryBreedDatabase.get_all_breeds()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🐔 اختيار الآباء")
        parent1 = st.selectbox("السلالة الأولى (الأب):", list(breeds.keys()))
        parent2 = st.selectbox("السلالة الثانية (الأم):", list(breeds.keys()))
        
        if len(breeds) > 2:
            use_third = st.checkbox("إضافة سلالة ثالثة للتهجين")
            if use_third:
                parent3 = st.selectbox("السلالة الثالثة:", [b for b in breeds.keys() if b not in [parent1, parent2]])
    
    with col2:
        st.markdown("##### ⚙️ إعدادات التهجين")
        generations = st.slider("عدد الأجيال المطلوب محاكاتها:", 1, 5, 2)
        show_details = st.checkbox("عرض التفاصيل الكاملة للصفات")
    
    if st.button("🧬 تنفيذ التهجين والتنبؤ", type="primary", use_container_width=True):
        # الحصول على بيانات السلالات
        breed1 = breeds[parent1]
        breed2 = breeds[parent2]
        
        parents = [breed1, breed2]
        if 'use_third' in locals() and use_third:
            breed3 = breeds[parent3]
            parents.append(breed3)
        
        # تنفيذ التهجين
        hybrid_engine = AdvancedHybridEngine()
        results = hybrid_engine.simulate_multi_breed_hybrid(parents, generations)
        
        st.markdown("---")
        st.success(f"✅ تم تهجين {len(parents)} سلالة بنجاح!")
        
        # عرض النتائج
        for i, offspring in enumerate(results, 1):
            with st.expander(f"📊 النسل الناتج {i} - الجيل {offspring['generation']}"):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("لون الريش المتوقع", offspring['feather_color'])
                    st.metric("نوع العرف", offspring['comb_type'])
                
                with col_b:
                    st.metric("الوزن المتوقع (كجم)", f"{offspring['body_weight']:.2f}")
                    st.metric("الجيل", offspring['generation'])
                
                with col_c:
                    if 'special_features' in offspring and offspring['special_features']:
                        st.markdown("**المميزات الخاصة:**")
                        for feature in offspring['special_features']:
                            st.write(f"- {feature}")
                
                if show_details:
                    st.markdown("**تفاصيل الجينات:**")
                    st.json(offspring)
        
        # عرض مخطط توزيع الأوزان
        weights = [off['body_weight'] for off in results]
        fig = px.histogram(weights, nbins=10, title="توزيع الأوزان المتوقعة للنسل",
                          labels={"value": "الوزن (كجم)", "count": "عدد الأفراد"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض دعاء ختامي
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a2e, #0f3460); padding: 20px; border-radius: 10px; border: 2px solid #e94560; margin-top: 20px;">
            <p style="color: #ffd700; font-size: 1.3rem; text-align: center; font-family: 'Cairo', sans-serif;">
                🤲 اللهم اغفر لإسماعيل تاور وارحمه وأدخله الجنة برحمتك الواسعة 🤲
            </p>
            <p style="color: #ffffff; font-size: 1rem; text-align: center;">
                كل دقيقة وكل عمل صالح نهديه لروح المرحوم إسماعيل تاور
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 8. تحديث باقي التبويبات مع الدعاء
# ==========================================
elif "1." in app_mode:
    st.subheader("🧬 التطبيق الوراثي وحساب التطور عبر الأجيال")
    
    # إضافة الدعاء
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f3460, #1a1a2e); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <p style="color: #ffd700; text-align: center; font-size: 1rem;">
            🤲 اللهم اغفر للمرحوم إسماعيل تاور وارحمه وأدخله فسيح جناتك 🤲
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ... (باقي كود التبويب الأول كما هو)
    
elif "4." in app_mode:
    st.subheader("📚 دليل السلالات العالمية للدواجن")
    
    # إضافة الدعاء
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f3460, #1a1a2e); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
        <p style="color: #ffd700; text-align: center; font-size: 1rem;">
            🕊️ هذا الدليل وقف عن روح المرحوم إسماعيل تاور - اللهم اغفر له وارحمه 🕊️
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    breeds = PoultryBreedDatabase.get_all_breeds()
    
    # تصنيف السلالات
    layers = {k: v for k, v in breeds.items() if v["type"] == "بياض (Layer)"}
    broilers = {k: v for k, v in breeds.items() if v["type"] == "لاحم (Broiler)"}
    ornamental = {k: v for k, v in breeds.items() if v["type"] == "زينة (Ornamental)"}
    
    tab1, tab2, tab3 = st.tabs(["🥚 سلالات البياض", "🍗 سلالات اللاحم", "🦚 سلالات الزينة"])
    
    with tab1:
        st.markdown("### سلالات إنتاج البيض العالمية")
        for name, data in layers.items():
            with st.expander(f"🥚 {name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**بلد المنشأ:** {data['origin']}")
                    st.write(f"**إنتاج البيض سنوياً:** {data['egg_production']} بيضة")
                    st.write(f"**وزن البيضة:** {data['egg_weight']} جرام")
                with col2:
                    st.write(f"**الوزن الحي:** {data['body_weight']} كجم")
                    st.write(f"**لون الريش:** {data['feather_color']}")
                    st.write(f"**نوع العرف:** {data['comb_type']}")
    
    with tab2:
        st.markdown("### سلالات التسمين العالمية")
        for name, data in broilers.items():
            with st.expander(f"🍗 {name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**بلد المنشأ:** {data['origin']}")
                    st.write(f"**الوزن عند 35 يوم:** {data['weight_35d']} كجم")
                    st.write(f"**معدل التحويل الغذائي:** {data['fcr']}")
                with col2:
                    st.write(f"**الوزن النهائي:** {data['body_weight']} كجم")
                    st.write(f"**نسبة النفوق:** {data['mortality']}%")
                    st.write(f"**لون الريش:** {data['feather_color']}")
    
    with tab3:
        st.markdown("### سلالات الزينة النادرة")
        for name, data in ornamental.items():
            with st.expander(f"🦚 {name}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**بلد المنشأ:** {data['origin']}")
                    st.write(f"**الوزن الحي:** {data['body_weight']} كجم")
                with col2:
                    st.write(f"**لون الريش:** {data['feather_color']}")
                    st.write(f"**نوع العرف:** {data['comb_type']}")
                st.write("**المميزات:**")
                for feature in data['special_features']:
                    st.write(f"- {feature}")

# ==========================================
# 9. تحديث باقي التبويبات
# ==========================================
# (سيتم إضافة الدعاء في كل تبويب)
# ... (باقي الكود كما هو مع إضافة الدعاء في كل تبويب)

# ==========================================
# 10. التذييل الختامي
# ==========================================
st.markdown("""
<div style="background: linear-gradient(135deg, #0f3460, #1a1a2e); padding: 20px; border-radius: 10px; border: 2px solid #e94560; margin-top: 30px; text-align: center;">
    <p style="color: #ffd700; font-size: 1.3rem; font-family: 'Cairo', sans-serif;">
        🤲 اللهم اغفر للمرحوم إسماعيل تاور وارحمه وأدخله الجنة وأسكنه الفردوس الأعلى 🤲
    </p>
    <p style="color: #ffffff; font-size: 1rem;">
        كل ثانية وكل دقيقة تمر، ندعو الله أن يتغمد روحه بواسع رحمته
    </p>
    <p style="color: #38BDF8; font-size: 0.9rem; margin-top: 10px;">
        تطوير وتصميم: د. عبد القادر إسماعيل - جميع الحقوق محفوظة © 2026
    </p>
</div>
""", unsafe_allow_html=True)
