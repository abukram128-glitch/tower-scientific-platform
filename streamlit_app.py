import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS
import io

# ==========================================
# 1. تهيئة الصفحة والتصميم والأمان
# ==========================================
st.set_page_config(
    page_title="منتدى التغذية التطبيقية والهندسة الوراثية - د. عبد القادر إسماعيل",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #ffffff;
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        border-right: 6px solid #0284C7;
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
    }

    .book-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-right: 5px solid #0284C7;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
    }
    </style>

    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
            (e.ctrlKey && e.shiftKey && e.keyCode == 73) || 
            (e.ctrlKey && e.keyCode == 85)) {
            return false;
        }
    }
    
    function speakText(text) {
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
    }
    </script>
""", unsafe_allow_html=True)


# ==========================================
# 2. محرك الحسابات الوراثية وتتبع الأجيال
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
# 3. قواعد البيانات والمراجع
# ==========================================
class DatabaseEngine:
    @staticmethod
    def get_expanded_feed_ingredients():
        return pd.DataFrame([
            {"إدخال في العليقة": True, "المادة الخام": "ذرة رفيعة (فتريتة)", "CP": 9.0, "ME_Kcal": 3200, "CF": 2.5, "EE": 3.5, "Ca": 0.03, "AvP": 0.12, "Cost_Kg": 1.20, "Max_Include": 65.0},
            {"إدخال في العليقة": True, "المادة الخام": "ذرة صفراء مجروشة", "CP": 8.5, "ME_Kcal": 3350, "CF": 2.2, "EE": 3.8, "Ca": 0.02, "AvP": 0.10, "Cost_Kg": 1.35, "Max_Include": 60.0},
            {"إدخال في العليقة": False, "المادة الخام": "أمباز / كسبة زهرة الشمس (SSC - عالي الألياف)", "CP": 28.0, "ME_Kcal": 2100, "CF": 24.0, "EE": 5.5, "Ca": 0.35, "AvP": 0.20, "Cost_Kg": 1.60, "Max_Include": 20.0},
            {"إدخال في العليقة": True, "المادة الخام": "أمباز / كسبة زهرة الشمس مقشورة (SSC - منخفض الألياف)", "CP": 36.0, "ME_Kcal": 2450, "CF": 12.0, "EE": 6.5, "Ca": 0.30, "AvP": 0.22, "Cost_Kg": 2.10, "Max_Include": 25.0},
            {"إدخال في العليقة": True, "المادة الخام": "أمباز السوداني (Groundnut Cake)", "CP": 45.0, "ME_Kcal": 2500, "CF": 6.5, "EE": 7.0, "Ca": 0.20, "AvP": 0.18, "Cost_Kg": 2.60, "Max_Include": 20.0},
            {"إدخال في العليقة": False, "المادة الخام": "أمباز السمسم (Sesame Cake)", "CP": 40.0, "ME_Kcal": 2600, "CF": 6.0, "EE": 10.0, "Ca": 2.10, "AvP": 0.55, "Cost_Kg": 2.80, "Max_Include": 15.0},
            {"إدخال في العليقة": False, "المادة الخام": "كسبة بذرة القطن (Cottonseed Meal)", "CP": 38.0, "ME_Kcal": 2000, "CF": 11.0, "EE": 4.0, "Ca": 0.20, "AvP": 0.25, "Cost_Kg": 2.20, "Max_Include": 10.0},
            {"إدخال في العليقة": True, "المادة الخام": "كسبة فول الصويا (44%)", "CP": 44.0, "ME_Kcal": 2230, "CF": 6.0, "EE": 1.5, "Ca": 0.29, "AvP": 0.22, "Cost_Kg": 3.10, "Max_Include": 30.0},
            {"إدخال في العليقة": False, "المادة الخام": "كسبة فول الصويا (48%)", "CP": 48.0, "ME_Kcal": 2440, "CF": 3.5, "EE": 1.0, "Ca": 0.27, "AvP": 0.20, "Cost_Kg": 3.40, "Max_Include": 30.0},
            {"إدخال في العليقة": True, "المادة الخام": "مركز بياض/تسمين مستورد (5%)", "CP": 40.0, "ME_Kcal": 2100, "CF": 3.0, "EE": 2.0, "Ca": 6.50, "AvP": 3.00, "Cost_Kg": 5.80, "Max_Include": 5.0},
            {"إدخال في العليقة": True, "المادة الخام": "نخالة القمح (ردة)", "CP": 15.0, "ME_Kcal": 1300, "CF": 11.0, "EE": 4.0, "Ca": 0.14, "AvP": 0.28, "Cost_Kg": 0.95, "Max_Include": 25.0},
            {"إدخال في العليقة": True, "المادة الخام": "مولاس القصب", "CP": 4.0, "ME_Kcal": 1900, "CF": 0.0, "EE": 0.1, "Ca": 0.80, "AvP": 0.08, "Cost_Kg": 0.70, "Max_Include": 5.0},
            {"إدخال في العليقة": True, "المادة الخام": "حجر جيري (Limestone)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 38.0, "AvP": 0.00, "Cost_Kg": 0.20, "Max_Include": 4.0},
            {"إدخال في العليقة": True, "المادة الخام": "ثنائي فوسفات الكالسيوم (DCP)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 22.0, "AvP": 18.0, "Cost_Kg": 2.20, "Max_Include": 2.0},
            {"إدخال في العليقة": False, "المادة الخام": "DL-Methionine (مثيونين نقي)", "CP": 58.0, "ME_Kcal": 5000, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 12.00, "Max_Include": 0.3},
            {"إدخال في العليقة": False, "المادة الخام": "L-Lysine HCl (لايسين نقي)", "CP": 94.0, "ME_Kcal": 4100, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 9.50, "Max_Include": 0.4},
            {"إدخال في العليقة": True, "المادة الخام": "ملح الطعام (NaCl)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 0.30, "Max_Include": 0.5},
            {"إدخال في العليقة": True, "المادة الخام": "مخلوط فيتامينات ومعادن (Premix)", "CP": 0.0, "ME_Kcal": 0, "CF": 0.0, "EE": 0.0, "Ca": 0.00, "AvP": 0.00, "Cost_Kg": 8.00, "Max_Include": 0.5}
        ])

    @staticmethod
    def get_breed_database():
        return {
            "أبقار - هولشتاين (Holstein-Friesian)": {"type": "Cattle", "avg_milk": 7500, "fat_pct": 3.7, "h2_milk": 0.30, "h2_fat": 0.50},
            "أبقار - جيرسي (Jersey)": {"type": "Cattle", "avg_milk": 5000, "fat_pct": 4.8, "h2_milk": 0.28, "h2_fat": 0.52},
            "أبقار - سيمنتال (Simmental)": {"type": "Cattle", "avg_milk": 5500, "fat_pct": 4.0, "h2_milk": 0.32, "h2_fat": 0.48},
            "أبقار - سودانية محلية (Kena / Kenana)": {"type": "Cattle", "avg_milk": 1800, "fat_pct": 4.5, "h2_milk": 0.22, "h2_fat": 0.45},
            "دواجن - Cobb 500 (تسمين)": {"type": "Poultry", "avg_weight_35d": 2.4, "fcr": 1.52, "h2_weight": 0.40},
            "دواجن - Ross 308 (تسمين)": {"type": "Poultry", "avg_weight_35d": 2.38, "fcr": 1.54, "h2_weight": 0.38},
            "دواجن - Hy-Line W-36 (بياض)": {"type": "Poultry", "avg_eggs": 320, "egg_weight": 62.0, "h2_eggs": 0.20},
            "أغنام - العواسي / الحمري (Awassi)": {"type": "Sheep", "avg_milk": 280, "weaning_weight": 24, "h2_weight": 0.35}
        }

    @staticmethod
    def get_books_references():
        return [
            {
                "category": "Animal Nutrition (تغذية الحيوان)",
                "title": "McDonald's Animal Nutrition",
                "authors": "P. McDonald, R.A. Edwards, J.F.D. Greenhalgh et al.",
                "description": "This text provides a comprehensive introduction to the study of the nutrition of animals of agricultural importance. It introduces the fundamental principles of animal nutrition and covers nutrient digestion, metabolism, feed evaluation, and requirements for ruminants and monogastrics.",
                "summary": "The definitive bible for animal nutrition principles, covering digestion, energy evaluation, and formulation.",
                "link": "https://www.google.com/books/edition/McDonald_s_Animal_Nutrition/P9A0DwAAQBAJ"
            },
            {
                "category": "Animal Nutrition (تغذية الحيوان)",
                "title": "Basic Animal Nutrition and Feeding",
                "authors": "Wilson G. Pond, David C. Church, Kevin R. Pond",
                "description": "An essential reference detailing the chemical, biological, and practical aspects of livestock feeding and nutrient requirements.",
                "summary": "Focuses on fundamental chemical aspects of nutrients and practical feeding systems.",
                "link": "https://www.google.com/books/edition/Basic_Animal_Nutrition_and_Feeding/3E59AAAAMAAJ"
            },
            {
                "category": "Poultry Science (علوم الدواجن)",
                "title": "Commercial Poultry Nutrition",
                "authors": "Steve Leeson and John D. Summers",
                "description": "The standard worldwide reference for practical poultry formulation, covering detailed strain requirements for broilers, layers, and breeders.",
                "summary": "Essential guide for practical feed mill formulation and poultry ration optimization.",
                "link": "https://www.google.com/books/edition/Commercial_Poultry_Nutrition/XqK4QgAACAAJ"
            },
            {
                "category": "Poultry Systems (أنظمة الدواجن)",
                "title": "Poultry Production Systems: Behaviour, Management and Welfare",
                "authors": "M. S. Dawkins and A. Rothwell",
                "description": "Comprehensive reference covering modern poultry housing, environmental control, bird behavior, and commercial welfare standards.",
                "summary": "Covers commercial production systems, ventilation, stocking density, and welfare parameters.",
                "link": "https://www.google.com/books/edition/Poultry_Production_Systems/BTo9CwAAQBAJ"
            },
            {
                "category": "Livestock Management (أنظمة التربية)",
                "title": "Animal Feeding and Nutrition",
                "authors": "Marshall H. Jurgens, Kristin Brejda",
                "description": "Combines practical feeding management, ration evaluation, and specific requirements for beef, dairy, sheep, and poultry.",
                "summary": "Applied textbook bridging the gap between theoretical nutrition and farm feeding strategies.",
                "link": "https://www.google.com/books/edition/Animal_Feeding_and_Nutrition/zP0RAQAAMAAJ"
            }
        ]


# ==========================================
# 4. محرك التخطيط الخطي
# ==========================================
class AdvancedFeedOptimizer:
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
# 5. الواجهة الهيكلية الرئيسية
# ==========================================
st.markdown("""
    <div class="app-header">
        <div class="app-title">منتدى التغذية التطبيقية والحسابات الوراثية للإنتاج الحيواني</div>
        <div class="app-subtitle">تطوير وتصميم: أخصائي الإنتاج الحيواني | د. عبد القادر إسماعيل</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### أروقة المنتدى")
app_mode = st.sidebar.radio("", [
    "1. الحسابات الوراثية وتتبع الأجيال (Multi-Generational Breeding)",
    "2. تركيب العلائق بأقل تكلفة (Expanded Least-Cost)",
    "3. دراسة إحلال كسبة زهرة الشمس",
    "4. دليل السلالات والمواصفات القياسية",
    "5. المكتبة العلمية والقارئ الصوتي (References & Audio Reader)"
])

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='watermark'>الملكية الفكرية محفوظة ©<br><b>د. عبد القادر إسماعيل</b></div>", unsafe_allow_html=True)


# ==========================================
# 6. القسم الأول: التطبيق الوراثي
# ==========================================
if "1." in app_mode:
    st.subheader("🧬 التطبيق الوراثي وحساب التطور عبر الأجيال (Multi-Generational Engine)")
    
    tab_gen1, tab_gen2, tab_gen3 = st.tabs([
        "📊 وراثة صفات السيادة (Mendelian)", 
        "📈 القيمة التربوية (EBV)", 
        "🔄 تتبع التحسين عبر الأجيال (F1 - Fn)"
    ])

    with tab_gen1:
        st.markdown("##### 1. تحديد الصفة الوراثية ونوع السيادة:")
        col_gene, col_inheritance = st.columns(2)
        with col_gene:
            gene_choice = st.selectbox("الصفة المراد دراستها:", [
                "وجود القرون في الأبقار (Polled vs Horned - Gene P)",
                "لون الفراء/الجلد (Black vs Red - Gene B)",
                "صفة الريش السريع/البطيء في الدواجن (Gene K)",
                "صفة القزامى في الأغنام (Gene D)"
            ])
        
        with col_inheritance:
            inheritance_type = st.selectbox("نمط السيادة الوراثية:", [
                "سيادة تامة (Complete Dominance)",
                "سيادة غير تامة / غير كاملة (Incomplete Dominance)"
            ])

        inh_mode = "Complete" if "تامة" in inheritance_type and "غير" not in inheritance_type else "Incomplete"

        if "Polled" in gene_choice:
            g_info = {"dominant_allele": "P", "recessive_allele": "p", "dominant_trait": "عديم القرون (Polled)", "recessive_trait": "بقرون (Horned)", "intermediate_trait": "قرون ضامرة (Scars)", "inheritance": inh_mode}
        else:
            g_info = {"dominant_allele": "B", "recessive_allele": "b", "dominant_trait": "اللون الأسود (Black)", "recessive_trait": "اللون الأحمر (Red)", "intermediate_trait": "لون بني/رمادي (Intermediate)", "inheritance": inh_mode}

        st.markdown("---")
        st.markdown("##### 2. الطراز الوراثي للآباء (Parental Genotypes):")
        c_sire, c_dam = st.columns(2)
        
        dom = g_info["dominant_allele"]
        rec = g_info["recessive_allele"]

        options_sire_dam = [
            f"{dom}{dom} - نقاء سائد (Homozygous Dominant)",
            f"{dom}{rec} - خليط/هجين (Heterozygous)",
            f"{rec}{rec} - نقاء متنحي (Homozygous Recessive)"
        ]

        with c_sire:
            sire_geno_input = st.selectbox("الطراز الوراثي للذكر (Sire):", options_sire_dam, index=1)
            sire_code = sire_geno_input.split(" ")[0]
        with c_dam:
            dam_geno_input = st.selectbox("الطراز الوراثي للأنثى (Dam):", options_sire_dam, index=1)
            dam_code = dam_geno_input.split(" ")[0]

        geno_prob, pheno_prob, raw_offspring = GeneticsEngine.calculate_punnett_square(sire_code, dam_code, g_info)

        st.markdown("---")
        st.markdown("### 📋 النتائج العلمية للجيل الناتج (F1 Generation Output)")
        col_res_g, col_res_p = st.columns(2)
        
        with col_res_g:
            st.markdown("###### **نسب الطرز الوراثية المتوقعة (Genotypic Ratios):**")
            for g_code, prob in geno_prob.items():
                st.write(f"- **{g_code}**: بنسبة `{prob:.1f}%` ({'سائد نقي' if g_code==dom*2 else ('متنحي نقي' if g_code==rec*2 else 'هجين')})")
            fig_g = px.bar(x=list(geno_prob.keys()), y=list(geno_prob.values()), labels={'x':'الطراز الجيني', 'y':'الاحتمالية %'}, title="توزيع الطراز الجيني")
            st.plotly_chart(fig_g, use_container_width=True)

        with col_res_p:
            st.markdown("###### **نسب الطرز المظهرية المتوقعة (Phenotypic Ratios):**")
            for p_name, prob in pheno_prob.items():
                st.write(f"- **{p_name}**: بنسبة `{prob:.1f}%` احتمال ظهور")
            fig_p = px.pie(values=list(pheno_prob.values()), names=list(pheno_prob.keys()), title="توزيع الطراز المظهري الناتج")
            st.plotly_chart(fig_p, use_container_width=True)

    with tab_gen2:
        st.markdown("##### حساب القيمة التربوية المتوقعة (Estimated Breeding Value - EBV)")
        breeds_db = DatabaseEngine.get_breed_database()
        
        selected_breed_name = st.selectbox("اختر السلالة المراد تقييمها:", list(breeds_db.keys()))
        breed_data = breeds_db[selected_breed_name]
        
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            if breed_data["type"] == "Cattle":
                pop_avg_default = float(breed_data["avg_milk"])
                label_text = "إنتاج الحليب (كجم/موسم)"
                h2_default = breed_data["h2_milk"]
            elif breed_data["type"] == "Poultry":
                pop_avg_default = float(breed_data.get("avg_weight_35d", breed_data.get("avg_eggs", 2.0)))
                label_text = "الوزن/عدد البيض"
                h2_default = breed_data.get("h2_weight", breed_data.get("h2_eggs", 0.3))
            else:
                pop_avg_default = float(breed_data["avg_milk"])
                label_text = "الإنتاجية العامة"
                h2_default = 0.30

            st.text_input("الصفة المقاسة:", label_text, disabled=True)
        
        with col_h2:
            h2_val = st.number_input("المكافئ الوراثي ($h^2$):", 0.05, 0.99, h2_default, step=0.05)
        
        with col_h3:
            pop_avg = st.number_input("متوسط السلالة/القطيع ($\\bar{P}$):", 0.1, 20000.0, pop_avg_default)

        ind_perf = st.number_input("أداء الفرد المنتخب ($P$):", 0.1, 25000.0, pop_avg_default * 1.2)

        ebv = h2_val * (ind_perf - pop_avg)
        offspring_gain = ebv / 2.0

        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("الفارق الظاهري (Selection Differential)", f"{ind_perf - pop_avg:+.2f}")
        res2.metric("القيمة التربوية للفرد (EBV)", f"{ebv:+.2f}")
        res3.metric("التحسين المتوقع في الأبناء", f"{offspring_gain:+.2f}")

    with tab_gen3:
        st.markdown("##### 🧬 حساب التطور والتحسين الوراثي عبر الأجيال المتقدمة")
        c_g1, c_g2, c_g3, c_g4 = st.columns(4)
        with c_g1:
            base_perf = st.number_input("متوسط جيل الأساس ($P_0$):", 1.0, 15000.0, 3000.0)
        with c_g2:
            h2_gen = st.number_input("المكافئ الوراثي ($h^2$):", 0.05, 0.95, 0.30)
        with c_g3:
            intensity_i = st.slider("شدة الانتخاب ($i$ - Selection Intensity):", 0.5, 2.5, 1.4)
        with c_g4:
            sigma_p = st.number_input("الانحراف المعياري للصفة ($\\sigma_p$):", 1.0, 2000.0, 300.0)

        num_generations = st.slider("عدد الأجيال المراد حسابها:", 2, 10, 5)

        df_gen_res = GeneticsEngine.simulate_multi_generations(base_perf, h2_gen, intensity_i, sigma_p, num_generations)

        st.markdown("---")
        col_gt, col_gp = st.columns([1.2, 1.8])
        with col_gt:
            st.markdown("###### **جدول التراكم الوراثي للأجيال:**")
            st.dataframe(df_gen_res, use_container_width=True)

        with col_gp:
            fig_gen = px.line(df_gen_res, x="الجيل", y="متوسط أداء الجيل المتوقع", markers=True, 
                              title="مسار التحسين الوراثي عبر الأجيال",
                              text="متوسط أداء الجيل المتوقع")
            fig_gen.update_traces(textposition="top center")
            st.plotly_chart(fig_gen, use_container_width=True)


# ==========================================
# 7. القسم الثاني: تركيب العلائق بأقل تكلفة
# ==========================================
elif "2." in app_mode:
    st.subheader("🌾 صياغة العلائق الاقتصادية بناءً على الخامات المختارة")
    st.write("ضع علامة (✔️) في خانة **'إدخال في العليقة'** أمام المكونات التي تريد التكوين منها فقط.")

    tab_req, tab_ingredients = st.tabs(["1️⃣ الاحتياجات الغذائية", "2️⃣ جدول الخامات واختيار المكونات"])

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
        st.markdown("##### جدول الخامات العلفية:")
        feed_df = DatabaseEngine.get_expanded_feed_ingredients()
        
        edited_df = st.data_editor(
            feed_df, 
            column_config={
                "إدخال في العليقة": st.column_config.CheckboxColumn(
                    "إدخال في العليقة",
                    help="تحديد الخامات الداخلة في الحسابات",
                    default=True,
                )
            },
            num_rows="dynamic", 
            use_container_width=True
        )

    st.markdown("---")
    if st.button("🚀 حساب العليقة الاقتصادية من الخامات المختارة", type="primary", use_container_width=True):
        selected_df = edited_df[edited_df["إدخال في العليقة"] == True].reset_index(drop=True)
        
        if len(selected_df) == 0:
            st.error("⚠️ لم تقم باختيار أي مادة خام! يُرجى وضع علامة (✔️) أمام مادة واحدة على الأقل في الجدول.")
        else:
            optimizer = AdvancedFeedOptimizer(selected_df, req_cp, req_me, req_cf_max, req_ca, req_avp)
            res = optimizer.optimize()

            if res is not None and res.success:
                st.success("✅ تم التوصل إلى التركيبة المثالية بالأقل تكلفة من المكونات المختارة فقط!")
                
                sol_df = selected_df[["المادة الخام", "Cost_Kg", "CP", "ME_Kcal", "CF", "Ca", "AvP"]].copy()
                sol_df["النسبة في العليقة (%)"] = np.round(res.x * 100, 2)
                sol_df["الوزن للطن (كجم)"] = np.round(res.x * 1000, 1)
                sol_df["تكلفة العنصر/طن"] = np.round(res.x * 1000 * sol_df["Cost_Kg"], 2)

                active_sol = sol_df[sol_df["النسبة في العليقة (%)"] > 0].reset_index(drop=True)

                total_cost_kg = res.fun
                c_cost1, c_cost2 = st.columns(2)
                c_cost1.metric("تكلفة الكيلوجرام الصافي", f"${total_cost_kg:.3f}")
                c_cost2.metric("التكلفة الإجمالية للطن", f"${total_cost_kg * 1000:.2f}")

                col_t, col_p = st.columns([1.8, 1.2])
                with col_t:
                    st.markdown("##### 📋 المكونات المحسوبة في العليقة الناتجة:")
                    st.dataframe(active_sol, use_container_width=True)
                
                with col_p:
                    fig_pie = px.pie(active_sol, values="النسبة في العليقة (%)", names="المادة الخام", title="توزيع مكونات العليقة")
                    st.plotly_chart(fig_pie, use_container_width=True)

            else:
                st.error("❌ الخامات المختارة وحدها غير كافية لتحقيق المستهدف الغذائي المطلوب. يُرجى تفعيل خامات إضافية أو تعديل القيود.")


# ==========================================
# 8. التبويب الثالث: تجربة أمباز زهرة الشمس
# ==========================================
elif "3." in app_mode:
    st.subheader("📊 تقييم إحلال أمباز/كسبة زهرة الشمس (Sunflower Seed Cake)")
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


# ==========================================
# 9. التبويب الرابع: الدليل الفني
# ==========================================
elif "4." in app_mode:
    st.subheader("📚 دليل السلالات والمواصفات القياسية للإنتاج الحيواني")
    breeds_data = DatabaseEngine.get_breed_database()
    st.json(breeds_data)


# ==========================================
# 10. القسم الخامس: المكتبة العلمية والقارئ الصوتي
# ==========================================
else:
    st.subheader("📖 المكتبة العلمية وقارئ الكتب الصوتي (Animal Science Literature & Audio Reader)")
    
    tab_lib, tab_audio = st.tabs(["📚 مراجع الإنتاج الحيواني والتغذية", "🔊 القارئ الصوتي المدمج للنصوص والـ PDF"])

    with tab_lib:
        st.markdown("##### أمهات الكتب والمراجع الأكاديمية باللغة الإنجليزية:")
        books = DatabaseEngine.get_books_references()
        
        for i, book in enumerate(books):
            st.markdown(f"""
            <div class="book-card">
                <span style="background-color: #0284C7; color: white; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem;">{book['category']}</span>
                <h4 style="margin-top: 8px; color: #0F172A;">{book['title']}</h4>
                <p style="color: #475569; font-size: 0.9rem;"><b>المؤلفون:</b> {book['authors']}</p>
                <p style="color: #334155; font-size: 0.95rem;">{book['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns([1, 2])
            with c_btn1:
                clean_text = book['title'] + ". " + book['summary']
                escaped_text = clean_text.replace("'", "\\'")
                st.components.v1.html(
                    f"""<button onclick="window.parent.speakText('{escaped_text}')" 
                        style="background-color: #0284C7; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-family: Cairo; width: 100%;">
                        🔊 استمع للملخص
                    </button>""",
                    height=45
                )
            with c_btn2:
                st.link_button("🔗 فتح / قراءة الكتاب (Read Book)", book["link"], use_container_width=True)

    with tab_audio:
        st.markdown("##### 🔊 القارئ الصوتي الذكي (Text-To-Speech Engine)")
        st.write("أدخل النص الذي تريد قراءته باللغة الإنجليزية أو قم برفع مقطع نصي للتحويل إلى صوت:")

        input_text = st.text_area(
            "النص المراد قراءته (English Text):", 
            value="McDonald's Animal Nutrition is a primary reference covering energy systems, crude protein evaluation, and feeding requirements for poultry and ruminants.",
            height=150
        )

        c_speed, c_lang = st.columns(2)
        with c_speed:
            speech_rate = st.select_slider("سرعة القراءة الصوتي:", options=["بطيء", "عادي"], value="عادي")
        with c_lang:
            lang_code = st.selectbox("اللغة:", ["الإنجليزية (English - US)"])

        if st.button("🎧 توليد الملف الصوتي والاستماع", type="primary"):
            if input_text.strip():
                with st.spinner("جاري معالجة النص وتحويله إلى مقطع صوتي..."):
                    try:
                        slow_flag = True if speech_rate == "بطيء" else False
                        tts = gTTS(text=input_text, lang='en', slow=slow_flag)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        
                        st.success("✅ تم تحويل النص إلى صوت بنجاح!")
                        st.audio(fp, format='audio/mp3')
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاتصال بالمحرك الصوتي: {str(e)}")
            else:
                st.warning("⚠️ يرجى إدخال نص أولاً للقراءة.")
