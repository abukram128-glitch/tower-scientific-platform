import streamlit as st
import pandas as pd
import numpy as np
import itertools
from collections import Counter

# ==========================================
# 0. إعدادات الصفحة والتنسيق العام
# ==========================================
st.set_page_config(
    page_title="منصة الهندسة الوراثية والتحسين الوراثي لحيوانات المزرعة",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط CSS مخصص لتحسين مظهر الجداول والمؤشرات
st.markdown("""
    <style>
    .main { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .punnett-table { text-align: center; font-weight: bold; }
    .section-header { color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 المنصة المتقدمة للهندسة الوراثية والتحسين الوراثي (BLUP & Punnett Simulator)")
st.caption("أداة للبحث العلمي التطبيقي لتوقع صفات الهجين (F1 & F2) ونسب السيادة والقيم التربوية لحيوانات المزرعة والدواجن")

# ==========================================
# 1. خوارزميات الوراثة المندلية (Punnett Engine)
# ==========================================
def generate_gametes(genotype):
    """توليد الأمشاج (Gametes) بناءً على التركيب الوراثي"""
    # تقسيم التركيب الوراثي إلى أزواج أليلات (مثال: 'RrPp' -> ['Rr', 'Pp'])
    pairs = [genotype[i:i+2] for i in range(0, len(genotype), 2)]
    gamete_alleles = [list(pair) for pair in pairs]
    gametes = [''.join(g) for g in itertools.product(*gamete_alleles)]
    return gametes

def run_punnett_square(sire_geno, dam_geno):
    """بناء مربع بانيت وحساب النسب المئوية للتركيب الوراثي"""
    sire_gametes = generate_gametes(sire_geno)
    dam_gametes = generate_gametes(dam_geno)
    
    matrix = []
    all_offspring = []
    
    for d in dam_gametes:
        row = []
        for s in sire_gametes:
            # تجميع الأليلات وترتيب السائد قبل المتنحي لكل جين
            offspring_geno = ""
            for i in range(len(d)):
                gene_pair = sorted([s[i], d[i]], key=lambda x: (x.lower(), x.isupper() == False))
                offspring_geno += "".join(gene_pair)
            row.append(offspring_geno)
            all_offspring.append(offspring_geno)
        matrix.append(row)
        
    df_punnett = pd.DataFrame(
        matrix, 
        index=[f"مشيج الأم: {g}" for g in dam_gametes], 
        columns=[f"مشيج الأب: {g}" for g in sire_gametes]
    )
    
    counts = Counter(all_offspring)
    total = len(all_offspring)
    genotype_ratios = {k: {"العدد": v, "النسبة المئوية": f"{(v/total)*100:.1f}%"} for k, v in counts.items()}
    
    return df_punnett, pd.DataFrame(genotype_ratios).T

# ==========================================
# 2. القائمة الجانبية وتحديد خيارات البحث
# ==========================================
st.sidebar.header("⚙️ إعدادات تجربة التهجين")

species = st.sidebar.selectbox(
    "1. اختر نوع الكائن الحي:",
    ["🐔 الدواجن (Poultry)", "🐄 الأبقار (Cattle)", "🐑 الأغنام والماعز (Sheep & Goats)"]
)

analysis_mode = st.sidebar.radio(
    "2. نوع التحليل الوراثي:",
    ["التحليل الشامل (مندلي F1/F2 + كمي BLUP)", "الوراثة المندلية ومربع بانيت فقط", "الوراثة الكمية والقيم التربوية (BLUP)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **نظام التسمية الأليلية:**\n* الحرف الكبير (A, R, P) = أليل سائد\n* الحرف الصغير (a, r, p) = أليل متنحي")

# ==========================================
# 3. قسم الدواجن (Poultry Module)
# ==========================================
if "الدواجن" in species:
    st.header("🐔 وحدة وراثة وتحسين الدواجن")
    
    tab1, tab2, tab3 = st.tabs(["🧬 الوراثة المندلية (العرف والريش)", "📈 الوراثة الكمية (البيض والوزن)", "📑 تقرير التوقع المباشر"])
    
    # ------------------ Tab 1: Mendelian Genetics ------------------
    with tab1:
        st.subheader("تحليل صفات شكل العرف ولون الريش (الجيل F1 والجيل F2)")
        col_m, col_f = st.columns(2)
        
        with col_m:
            st.markdown("### ♂️ الأب (Rooster)")
            comb_m_geno = st.selectbox("جينات العرف (R=وردية, P=بازلائية):", ["RRpP (جوزي)", "RRpp (وردي)", "rrPP (بازلائي)", "rrpp (مفرد)"], key="cmg")
            feather_m_geno = st.selectbox("جينات لون الريش (I=أبيض سائد, E=أسود):", ["IIEE (أبيض سائد)", "iiEE (أسود)", "iiee (أحمر/بري)"], key="fmg")
            
        with col_f:
            st.markdown("### ♀️ الأم (Hen)")
            comb_f_geno = st.selectbox("جينات العرف (R=وردية, P=بازلائية):", ["rrpp (مفرد)", "RRpp (وردي)", "rrPP (بازلائي)", "RrPp (جوزي)"], key="cfg")
            feather_f_geno = st.selectbox("جينات لون الريش (I=أبيض سائد, E=أسود):", ["iiee (أحمر/بري)", "iiEE (أسود)", "IIEE (أبيض سائد)"], key="ffg")
            
        # استخلاص التراكيب الوراثية المحددة
        sire_comb = comb_m_geno.split()[0]
        dam_comb = comb_f_geno.split()[0]
        
        st.markdown("#### 📐 مربع بانيت لتفاهنات شكل العرف (Comb shape cross)")
        df_p_comb, df_ratio_comb = run_punnett_square(sire_comb, dam_comb)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(df_p_comb, use_container_width=True)
        with c2:
            st.write("**نسب التراكيب الوراثية (Genotypes):**")
            st.dataframe(df_ratio_comb)
            
        # تفسير الظواهر (Phenotypes) العرف
        st.markdown("**التوزيع الظاهري المتوقع للعرف (Phenotypic Breakdown):**")
        walnut_count = sum([1 for g in df_p_comb.values.flatten() if ('R' in g and 'P' in g)])
        rose_count = sum([1 for g in df_p_comb.values.flatten() if ('R' in g and 'p' in g and 'P' not in g)])
        pea_count = sum([1 for g in df_p_comb.values.flatten() if ('r' in g and 'P' in g and 'R' not in g)])
        single_count = sum([1 for g in df_p_comb.values.flatten() if g == 'rrpp'])
        total_p = len(df_p_comb.values.flatten())
        
        st.progress(walnut_count/total_p, text=f"عرف جوزي (Walnut R_P_): {(walnut_count/total_p)*100:.1f}%")
        st.progress(rose_count/total_p, text=f"عرف وردي (Rose R_pp): {(rose_count/total_p)*100:.1f}%")
        st.progress(pea_count/total_p, text=f"عرف بازلائي (Pea rrP_): {(pea_count/total_p)*100:.1f}%")
        st.progress(single_count/total_p, text=f"عرف مفرد (Single rrpp): {(single_count/total_p)*100:.1f}%")

    # ------------------ Tab 2: Quantitative Genetics (BLUP & EBV) ------------------
    with tab2:
        st.subheader("توقع الصفات الإنتاجية اعتماداً على القيمة التربوية (EBV) وقوة الهجين (Heterosis)")
        
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            st.markdown("##### 📊 بيانات الأب والسلالة")
            sire_ebv_egg = st.number_input("القيمة التربوية للبيض للأب EBV (بيض/سنة):", value=15.0)
            sire_ebv_weight = st.number_input("القيمة التربوية للوزن للأب EBV (جرام):", value=250.0)
            
        with q_col2:
            st.markdown("##### 📊 بيانات الأم والسلالة")
            dam_pv_egg = st.number_input("إنتاج الأم المباشر من البيض (بيضة/سنة):", value=220.0)
            dam_pv_weight = st.number_input("وزن الأم عند 12 أسبوع (جرام):", value=1800.0)

        st.markdown("---")
        st.markdown("##### 🧬 المعاملات الوراثية للجامعة/المزرعة (Genetic Parameters)")
        p_c1, p_c2, p_c3 = st.columns(3)
        mean_egg = p_c1.number_input("متوسط إنتاج العشيرة/السلالة الأصيلة ($\mu$):", value=180.0)
        h2_egg = p_c2.slider("المكافئ الوراثي للبيض ($h^2$):", 0.05, 0.60, 0.25)
        heterosis_egg = p_c3.slider("نسبة قوة الهجين المتوقعة للبيض ($H\%$):", 0.0, 20.0, 8.0)
        
        # حسابات BLUP و EBV
        dam_ebv_egg = h2_egg * (dam_pv_egg - mean_egg)
        expected_ebv_offspring = 0.5 * sire_ebv_egg + 0.5 * dam_ebv_egg
        expected_performance_egg = (mean_egg + expected_ebv_offspring) * (1 + (heterosis_egg/100))
        
        st.success(f"🎯 **النتيجة:** القيمة التربوية المتوقعة للهجين (EBV_F1): **{expected_ebv_offspring:+.2f} بيضة**")
        st.info(f"📈 **إنتاج البيض المتوقع للأنثى الناتجة في الجيل الأول (F1):** **{expected_performance_egg:.1f} بيضة/سنة** (شاملة قوة الهجين)")

    # ------------------ Tab 3: Summary Report ------------------
    with tab3:
        st.subheader("📑 ملخص نتائج محاكاة التهجين")
        st.json({
            "الكائن": "دواجن",
            "تركيب العرف الأب": sire_comb,
            "تركيب العرف الأم": dam_comb,
            "إنتاج البيض المتوقع (F1)": f"{expected_performance_egg:.1f} بيضة",
            "القيمة التربوية المحسوبة (EBV)": f"{expected_ebv_offspring:+.2f}"
        })

# ==========================================
# 4. قسم الأبقار (Cattle Module)
# ==========================================
elif "الأبقار" in species:
    st.header("🐄 وحدة وراثة وتحسين الأبقار (ألبان ولحوم)")
    
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.subheader("♂️ بيانات الطروقة (Sire/Bull)")
        horns_sire = st.selectbox("صفة القرون (P=عديم القرون سائد, p=بقرون):", ["PP (عديم القرون نقي)", "Pp (عديم القرون خليط)", "pp (بقرون)"])
        coat_sire = st.selectbox("لون الشعر:", ["ED_ (أسود سائد)", "ee (أحمر متنحي)"])
        milk_ebv_sire = st.number_input("القيمة التربوية للحليب للأب EBV (كجم/موسم):", value=650.0)
        daily_gain_sire = st.number_input("معدل النمو اليومي للأب (جم/يوم):", value=1350)
        
    with t_c2:
        st.subheader("♀️ بيانات البقرة (Dam/Cow)")
        horns_dam = st.selectbox("صفة القرون للأم:", ["pp (بقرون)", "Pp (عديم القرون خليط)", "PP (عديم القرون نقي)"])
        coat_dam = st.selectbox("لون الشعر للأم:", ["ee (أحمر متنحي)", "ED_ (أسود سائد)"])
        milk_record_dam = st.number_input("إنتاج الأم المباشر للحليب (كجم/موسم):", value=5200.0)
        daily_gain_dam = st.number_input("معدل النمو اليومي للأم (جم/يوم):", value=950)

    st.markdown("---")
    st.subheader("📐 التحليل الوراثي للجيل الأول (F1 Cross Output)")
    
    # حساب القرون
    g_sire = horns_sire.split()[0]
    g_dam = horns_dam.split()[0]
    df_p_horns, df_r_horns = run_punnett_square(g_sire, g_dam)
    
    m1, m2, m3 = st.columns(3)
    
    # نسبة عديم القرون
    polled_percent = sum([1 for g in df_p_horns.values.flatten() if 'P' in g]) / len(df_p_horns.values.flatten()) * 100
    m1.metric("احتمالية ولادة مولود عديم القرون (Polled)", f"{polled_percent:.0f}%")
    
    # إنتاج الحليب المتوقع
    pop_mean_milk = 4500.0
    h2_milk = 0.30
    dam_ebv_milk = h2_milk * (milk_record_dam - pop_mean_milk)
    f1_milk_ebv = 0.5 * milk_ebv_sire + 0.5 * dam_ebv_milk
    f1_milk_pheno = (pop_mean_milk + f1_milk_ebv) * 1.06 # 6% Heterosis
    
    m2.metric("إنتاج الحليب المتوقع للهجين (F1)", f"{f1_milk_pheno:.0f} كجم")
    
    # معدل النمو اليومي (لحم)
    f1_gain = ((daily_gain_sire + daily_gain_dam) / 2) * 1.10 # 10% Heterosis
    m3.metric("معدل النمو اليومي المتوقع (F1)", f"{f1_gain:.0f} جم/يوم")

    with st.expander("🔍 عرض جدول مربع بانيت لتوارث صفة القرون"):
        st.dataframe(df_p_horns)

# ==========================================
# 5. قسم الأغنام والماعز (Sheep & Goats)
# ==========================================
else:
    st.header("🐑 وحدة وراثة وتناسل الأغنام والماعز")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.subheader("♂️ الكبش / التيس (Male)")
        sire_twinning_ebv = st.number_input("القيمة التربوية للتوأمية (EBV):", value=0.25)
        sire_weaning_wt = st.number_input("وزن الفطام للأب (كجم):", value=35.0)
        
    with s_col2:
        st.subheader("♀️ النعجة / العنزة (Female)")
        dam_litter_size = st.number_input("سجل التوأمية المباشر للأم (مولود/بطن):", value=1.8)
        dam_weaning_wt = st.number_input("وزن الفطام للأم (كجم):", value=24.0)

    st.markdown("---")
    st.subheader("📊 المؤشرات الوراثية المحسوبة")
    
    # حساب التوأمية بـ BLUP
    mean_litter = 1.25
    h2_litter = 0.12 # مكافئ وراثي منخفض
    dam_ebv_litter = h2_litter * (dam_litter_size - mean_litter)
    f1_litter_ebv = 0.5 * sire_twinning_ebv + 0.5 * dam_ebv_litter
    f1_expected_litter = (mean_litter + f1_litter_ebv) * 1.15 # 15% Heterosis عالية للتوأمية
    
    # وزن الفطام
    f1_weaning_wt = ((sire_weaning_wt + dam_weaning_wt) / 2) * 1.08
    
    res1, res2 = st.columns(2)
    res1.metric("معدل التوأمية المتوقع (Litter Size)", f"{f1_expected_litter:.2f} مولود / بطن")
    res2.metric("وزن الفطام المتوقع للنسل", f"{f1_weaning_wt:.1f} كجم")

# ==========================================
# 6. المراجع والتأصيل العلمي
# ==========================================
st.markdown("---")
with st.expander("📚 المعادلات والمبادئ الوراثية المستخدمة في البرنامج"):
    st.latex(r"EBV_{Offspring} = \frac{1}{2} EBV_{Sire} + \frac{1}{2} EBV_{Dam}")
    st.latex(r"P_{Expected} = (\mu + EBV_{Offspring}) \times \left(1 + \frac{Heterosis\%}{100}\right)")
    st.markdown("""
    * **EBV (Estimated Breeding Value):** القيمة التربوية المقدرة للحيوان.
    * **Heterosis (قوة الهجين):** التفوق الإنتاجي الناتج عن جينات السيادة الفائقة والتباين الوراثي عند خلط السلالات.
    * **Punnett Square:** المبدأ المندلي لتوزيع الأليلات واستخلاص نسب الجيل الأول والثاني ($F1$ & $F2$).
    """)
```eof

