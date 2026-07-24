import streamlit as st
import pandas as pd
import numpy as np
import itertools
from collections import Counter

# ==========================================
# 0. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="منصة التحسين الوراثي والخلط لحيوانات المزرعة",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧬 المنصة الشاملة للهندسة الوراثية والتحسين الوراثي لحيوانات المزرعة")
st.caption("برنامج بحثي تطبيقي لتوقع صفات الخلط والتهجين بين السلالات (F1 & F2) مع مربع بانيت والحسابات المندلية والكمية")

# ==========================================
# 1. قاعدة بيانات السلالات والصفات المرجعية
# ==========================================
BREEDS_DATABASE = {
    "الأبقار (Cattle)": {
        "هولشتاين (Holstein)": {"milk_mean": 8500, "growth_rate": 1100, "origin": "أوروبي", "traits": "إنتاج حليب مرتفع جداً"},
        "براون سويس (Brown Swiss)": {"milk_mean": 6500, "growth_rate": 1050, "origin": "أوروبي", "traits": "حليب عالي البروتين وتحمل للظروف"},
        "جيرسي (Jersey)": {"milk_mean": 5000, "growth_rate": 800, "origin": "أوروبي", "traits": "نسبة دهن عالية جداً في الحليب"},
        "بلاكبوس / أنغوس (Angus)": {"milk_mean": 2200, "growth_rate": 1450, "origin": "أوروبي", "traits": "إنتاج لحم ممتاز وجودة جثة عالية"},
        "سيمنتال (Simmental)": {"milk_mean": 5500, "growth_rate": 1350, "origin": "أوروبي", "traits": "ثنائي الغرض (حليب ولحم)"},
        "سلالة محلية / بلدي": {"milk_mean": 1800, "growth_rate": 650, "origin": "محلي", "traits": "مقاومة عالية للأمراض والحرارة"}
    },
    "الدواجن (Poultry)": {
        "لجهورن (Leghorn)": {"egg_mean": 280, "egg_weight": 62, "body_weight": 1.8, "traits": "إنتاج بيض قياسي عالي"},
        "رود آيلاند (Rhode Island Red)": {"egg_mean": 240, "egg_weight": 60, "body_weight": 2.9, "traits": "ثنائي الغرض (بيض ولحم) قشرة بني"},
        "فايومي (Fayoumi)": {"egg_mean": 180, "egg_weight": 46, "body_weight": 1.5, "traits": "مقاومة للأمراض ونضج جنسي مبكر"},
        "بليموث روك (Plymouth Rock)": {"egg_mean": 220, "egg_weight": 58, "body_weight": 3.0, "traits": "نمو سريع ورائع للخلط"},
        "دجاج بلدي محلي": {"egg_mean": 140, "egg_weight": 42, "body_weight": 1.4, "traits": "قوة أقلمة وتحمل للظروف البيئية"}
    },
    "الأغنام والماعز (Sheep & Goats)": {
        "نعيمي / العواسي": {"weaning_weight": 28, "litter_size": 1.15, "milk_yield": 150, "traits": "إنتاج حليب ولحم مع تحمل الصحراء"},
        "عسافي (Assaf)": {"weaning_weight": 32, "litter_size": 1.60, "milk_yield": 380, "traits": "إنتاج حليب مرتفع وتوأمية عالية"},
        "نجدي": {"weaning_weight": 29, "litter_size": 1.10, "milk_yield": 120, "traits": "قامة عالية وجودة لحم ممتازة"},
        "روماني / بورولا": {"weaning_weight": 22, "litter_size": 2.10, "milk_yield": 90, "traits": "خصوبة وتوأمية فائقة جداً"},
        "سلالة محلية": {"weaning_weight": 20, "litter_size": 1.10, "milk_yield": 80, "traits": "أقلمة ممتازة للبيئة المحلية"}
    }
}

# ==========================================
# 2. محرك مربع بانيت المحسن والمعالج
# ==========================================
def generate_gametes(genotype):
    """توليد الأمشاج بناء على التركيب الوراثي"""
    pairs = [genotype[i:i+2] for i in range(0, len(genotype), 2)]
    gamete_alleles = [list(pair) for pair in pairs]
    gametes = [''.join(g) for g in itertools.product(*gamete_alleles)]
    return gametes

def run_punnett_square(sire_geno, dam_geno):
    """بناء مربع بانيت مع معالجة حوافز الجداول لمنع أخطاء PyArrow"""
    sire_gametes = generate_gametes(sire_geno)
    dam_gametes = generate_gametes(dam_geno)
    
    matrix = []
    all_offspring = []
    
    for d in dam_gametes:
        row = []
        for s in sire_gametes:
            offspring_geno = ""
            for i in range(min(len(d), len(s))):
                gene_pair = sorted([s[i], d[i]], key=lambda x: (x.lower(), not x.isupper()))
                offspring_geno += "".join(gene_pair)
            row.append(str(offspring_geno))
            all_offspring.append(str(offspring_geno))
        matrix.append(row)
        
    df_punnett = pd.DataFrame(
        matrix, 
        index=[f"مشيج الأنثى: {g}" for g in dam_gametes], 
        columns=[f"مشيج الذكر: {g}" for g in sire_gametes]
    )
    
    df_punnett = df_punnett.astype(str)
    counts = Counter(all_offspring)
    total = len(all_offspring)
    
    genotype_ratios = []
    for geno, count in counts.items():
        genotype_ratios.append({
            "التركيب الوراثي (Genotype)": geno,
            "العدد في المربع": count,
            "النسبة المئوية (%)": f"{(count/total)*100:.1f}%"
        })
        
    return df_punnett, pd.DataFrame(genotype_ratios)

# ==========================================
# 3. القائمة الجانبية وإدارة تجربة الخلط
# ==========================================
st.sidebar.header("⚙️ إعدادات الخلط والنوع")

species = st.sidebar.selectbox(
    "1. اختر نوع الحيوان المراد دراسته:",
    list(BREEDS_DATABASE.keys())
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **شرح ترميز الجينات:**\n* **P / p:** صفة القرون (P سائد عديم القرون، p متنحي بقرون).\n* **R / P:** شكل العرف (R_p_ وردي، r_P_ بازلائي، R_P_ جوزي، rrpp مفرد).\n* **I / E:** لون الريش (I حجب سائد، E أسود سائد).")

# ==========================================
# 4. قسم الأبقار الشامل
# ==========================================
if "الأبقار" in species:
    st.header("🐄 وحدة دراسة خلط سلالات الأبقار")
    
    tab_cross, tab_punnett, tab_quantitative = st.tabs([
        "🔀 تحديد السلالات والجنس للخلط", 
        "🧬 تحليل مربع بانيت للصفات الوصفية", 
        "📈 القيمة التربوية وتوقعات الحليب واللحم"
    ])
    
    with tab_cross:
        st.subheader("اختيار الأبوين والسلالات والمرجع الإنتاجي")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### ♂️ الأب (الذكر / الطروقة)")
            sire_breed = st.selectbox("اختر سلالة الذكر:", list(BREEDS_DATABASE["الأبقار (Cattle)"].keys()), index=0)
            sire_info = BREEDS_DATABASE["الأبقار (Cattle)"][sire_breed]
            st.info(f"📌 **خصائص سلالة {sire_breed}:** {sire_info['traits']}")
            sire_ebv_milk = st.number_input("القيمة التربوية للبن للذكر EBV (كجم):", value=500.0)
            sire_horns = st.selectbox("تركيب القرون للذكر:", ["PP (عديم القرون نقي)", "Pp (عديم القرون خليط)", "pp (بقرون)"], key="sh_c")

        with c2:
            st.markdown("### ♀️ الأم (الأنثى / البقرة)")
            dam_breed = st.selectbox("اختر سلالة الأنثى:", list(BREEDS_DATABASE["الأبقار (Cattle)"].keys()), index=5)
            dam_info = BREEDS_DATABASE["الأبقار (Cattle)"][dam_breed]
            st.info(f"📌 **خصائص سلالة {dam_breed}:** {dam_info['traits']}")
            dam_milk_actual = st.number_input("إنتاج الأم المباشر للحليب (كجم/موسم):", value=float(dam_info['milk_mean']))
            dam_horns = st.selectbox("تركيب القرون للأنثى:", ["pp (بقرون)", "Pp (عديم القرون خليط)", "PP (عديم القرون نقي)"], key="dh_c")

    with tab_punnett:
        st.subheader("تحليل مربع بانيت لصفة القرون (Polled vs Horned)")
        g_sire = sire_horns.split()[0]
        g_dam = dam_horns.split()[0]
        
        df_p_horns, df_r_horns = run_punnett_square(g_sire, g_dam)
        
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            st.write("**مربع بانيت لمزيج الأمشاج:**")
            st.table(df_p_horns)
        with col_p2:
            st.write("**توزيع الجينات والنسب المئوية:**")
            st.table(df_r_horns)

        polled_count = sum([1 for g in df_p_horns.values.flatten() if 'P' in g])
        total_count = len(df_p_horns.values.flatten())
        st.success(f"🎯 **احتمالية ولادة عجل عديم القرون (Polled Phenotype):** **{(polled_count/total_count)*100:.1f}%**")

    with tab_quantitative:
        st.subheader("التنبؤ بإنتاج اللبن ومعدل النمو للجيل الأول (F1)")
        
        # حساب التوقعات بالقيم التربوية
        pop_mean = (sire_info['milk_mean'] + dam_info['milk_mean']) / 2
        h2_milk = 0.30  # المكافئ الوراثي
        
        dam_ebv_milk = h2_milk * (dam_milk_actual - dam_info['milk_mean'])
        expected_f1_ebv = 0.5 * sire_ebv_milk + 0.5 * dam_ebv_milk
        
        # معامل قوة الهجين عند الخلط بين سلالتين مختلفين
        heterosis_rate = 1.08 if sire_breed != dam_breed else 1.00
        expected_f1_milk = (pop_mean + expected_f1_ebv) * heterosis_rate
        
        # النمو اليومي
        expected_gain = ((sire_info['growth_rate'] + dam_info['growth_rate']) / 2) * (1.10 if sire_breed != dam_breed else 1.0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("السلالة الناتجة (F1 Cross)", f"{sire_breed[:6]} × {dam_breed[:6]}")
        m2.metric("القيمة التربوية للنسل (EBV)", f"{expected_f1_ebv:+.1f} كجم")
        m3.metric("إنتاج الحليب المتوقع للمولود الأنثى", f"{expected_f1_milk:.0f} كجم/موسم")
        m4.metric("معدل النمو اليومي المتوقع", f"{expected_gain:.0f} جم/يوم")

# ==========================================
# 5. قسم الدواجن الشامل
# ==========================================
elif "الدواجن" in species:
    st.header("🐔 وحدة تهجين وتحسين الدواجن")
    
    t1, t2, t3 = st.tabs(["🔀 تحديد السلالة والجنس", "🧬 الوراثة المندلية (العرف والريش)", "📈 توقعات إنتاج البيض والوزن"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ♂️ الديك (Male Rooster)")
            sire_p_breed = st.selectbox("سلالة الديك:", list(BREEDS_DATABASE["الدواجن (Poultry)"].keys()), index=0)
            comb_m = st.selectbox("جينات العرف للديك:", ["RrPp (جوزي خليط)", "RRpp (وردي نقي)", "rrPP (بازلائي نقي)", "rrpp (مفرد)"], key="cm_p")
            feather_m = st.selectbox("جينات لون الريش للديك:", ["IIEE (أبيض سائد نقي)", "iiEE (أسود نقي)", "iiee (ملون/أحمر بري)"], key="fm_p")
            
        with c2:
            st.markdown("### ♀️ الدجاجة (Female Hen)")
            dam_p_breed = st.selectbox("سلالة الدجاجة:", list(BREEDS_DATABASE["الدواجن (Poultry)"].keys()), index=4)
            comb_f = st.selectbox("جينات العرف للدجاجة:", ["rrpp (مفرد)", "RRpp (وردي نقي)", "rrPP (بازلائي نقي)", "RrPp (جوزي خليط)"], key="cf_p")
            feather_f = st.selectbox("جينات لون الريش للدجاجة:", ["iiee (ملون/أحمر بري)", "iiEE (أسود نقي)", "IIEE (أبيض سائد نقي)"], key="ff_p")

    with t2:
        st.subheader("تحليل وراثة العرف ومربع بانيت")
        df_p_comb, df_r_comb = run_punnett_square(comb_m.split()[0], comb_f.split()[0])
        
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.write("**مربع بانيت لوراثة العرف:**")
            st.table(df_p_comb)
        with col_b:
            st.write("**نسب التراكيب الوراثية:**")
            st.table(df_r_comb)
            
        # تحليل لون الريش
        st.markdown("---")
        st.subheader("توقع لون الريش للجيل الأول")
        if "II" in feather_m or "II" in feather_f or "Ii" in feather_m or "Ii" in feather_f:
            st.success("🎨 **اللون المتوقع للريش:** **أبيض سائد** (بسبب وجود جين الحجب السائد I)")
        elif "EE" in feather_m or "EE" in feather_f:
            st.info("🎨 **اللون المتوقع للريش:** **أسود / داكن** (جينات E السائدة)")
        else:
            st.warning("🎨 **اللون المتوقع للريش:** **ملون / أحمر بري**")

    with t3:
        st.subheader("توقع إنتاج البيض وحجم البيضة ووزن الجسم")
        sire_p_data = BREEDS_DATABASE["الدواجن (Poultry)"][sire_p_breed]
        dam_p_data = BREEDS_DATABASE["الدواجن (Poultry)"][dam_p_breed]
        
        # حساب قوة الهجين لإنتاج البيض (8%) والوزن (5%)
        heterosis_egg = 1.08 if sire_p_breed != dam_p_breed else 1.00
        heterosis_body = 1.05 if sire_p_breed != dam_p_breed else 1.00
        
        exp_egg_num = ((sire_p_data['egg_mean'] + dam_p_data['egg_mean']) / 2) * heterosis_egg
        exp_egg_wt = (sire_p_data['egg_weight'] + dam_p_data['egg_weight']) / 2
        exp_body_wt = ((sire_p_data['body_weight'] + dam_p_data['body_weight']) / 2) * heterosis_body
        
        r1, r2, r3 = st.columns(3)
        r1.metric("إنتاج البيض المتوقع للأنثى الناتجة", f"{exp_egg_num:.0f} بيضة/سنة")
        r2.metric("متوسط حجم/وزن البيضة", f"{exp_egg_wt:.1f} جرام")
        r3.metric("وزن الجسم عند النضج", f"{exp_body_wt:.2f} كجم")

# ==========================================
# 6. قسم الأغنام والماعز الشامل
# ==========================================
else:
    st.header("🐑 وحدة تهجين وتحسين الأغنام والماعز")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("♂️ تحديد الذكر (الكبش/التيس)")
        s_breed = st.selectbox("سلالة الذكر:", list(BREEDS_DATABASE["الأغنام والماعز (Sheep & Goats)"].keys()), index=1)
        s_data = BREEDS_DATABASE["الأغنام والماعز (Sheep & Goats)"][s_breed]
        s_wt = st.number_input("وزن الفطام للذكر (كجم):", value=float(s_data['weaning_weight']))
        s_litter_ebv = st.number_input("القيمة التربوية للتوأمية للأب:", value=0.20)

    with col2:
        st.subheader("♀️ تحديد الأنثى (النعجة/العنزة)")
        d_breed = st.selectbox("سلالة الأنثى:", list(BREEDS_DATABASE["الأغنام والماعز (Sheep & Goats)"].keys()), index=0)
        d_data = BREEDS_DATABASE["الأغنام والماعز (Sheep & Goats)"][d_breed]
        d_wt = st.number_input("وزن الفطام للأنثى (كجم):", value=float(d_data['weaning_weight']))
        d_litter_actual = st.number_input("سجل التوأمية المباشر للأم (مولود/بطن):", value=float(d_data['litter_size']))

    st.markdown("---")
    st.subheader(f"📊 مؤشرات خلط سلالة ({s_breed}) × سلالة ({d_breed})")
    
    # حساب قوة الهجين
    heterosis_litter = 1.12 if s_breed != d_breed else 1.00 # 12% للتوأمية
    heterosis_growth = 1.08 if s_breed != d_breed else 1.00 # 8% لوزن الفطام
    
    # حسابات التوأمية
    mean_litter_pop = (s_data['litter_size'] + d_data['litter_size']) / 2
    h2_litter = 0.12
    dam_ebv_litter = h2_litter * (d_litter_actual - d_data['litter_size'])
    f1_litter_ebv = 0.5 * s_litter_ebv + 0.5 * dam_ebv_litter
    exp_litter_size = (mean_litter_pop + f1_litter_ebv) * heterosis_litter
    
    exp_weaning_weight = ((s_wt + d_wt) / 2) * heterosis_growth
    
    m1, m2, m3 = st.columns(3)
    m1.metric("معدل التوأمية المتوقع (Litter Size)", f"{exp_litter_size:.2f} مولود / بطن")
    m2.metric("وزن الفطام المتوقع لهجين F1", f"{exp_weaning_weight:.1f} كجم")
    m3.metric("إنتاج الحليب للأمهات الناتجة", f"{((s_data['milk_yield'] + d_data['milk_yield'])/2)*1.05:.0f} كجم/موسم")
