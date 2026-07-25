import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go

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
    
    .genetic-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
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
    </script>
""", unsafe_allow_html=True)


# ==========================================
# 2. محرك الحسابات الوراثية المحسن والمحمي
# ==========================================
class GeneticsEngine:
    """محرك تطبيقي لحساب الطرز الوراثية والمظهرية واستجابة الانتخاب"""
    
    @staticmethod
    def calculate_punnett_square(sire_genotype, dam_genotype, gene_info):
        """حساب مربعات بانيت والطرز المظهرية مع حماية كاملة من الأخطاء"""
        sire_alleles = [sire_genotype[0], sire_genotype[1]]
        dam_alleles = [dam_genotype[0], dam_genotype[1]]
        
        offspring_genotypes = []
        for s in sire_alleles:
            for d in dam_alleles:
                # ترتيب الأليل السائد (الكبير) أولاً
                sorted_alleles = "".join(sorted([s, d], key=lambda x: (x.islower(), x)))
                offspring_genotypes.append(sorted_alleles)
                
        # حساب النسب المئوية للطرز الجينية
        genotype_counts = pd.Series(offspring_genotypes).value_counts(normalize=True) * 100
        
        # تحديد الطراز المظهري مع تفادي خطأ UnboundLocalError
        phenotype_results = {}
        for geno, prob in genotype_counts.items():
            # تعيين قيمة افتراضية صريحة
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
    def calculate_breeding_value(heritability, individual_perf, population_avg):
        """حساب القيمة التربوية المتوقعة: EBV = h^2 * (P - P_bar)"""
        ebv = heritability * (individual_perf - population_avg)
        expected_offspring_gain = ebv / 2.0
        return ebv, expected_offspring_gain


# ==========================================
# 3. قواعد بيانات العليقة والاقتصاد
# ==========================================
class DatabaseEngine:
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
# 4. محرك التخطيط الخطي
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
    "1. الحسابات الوراثية وقوانين الأنساب (Applied Genetics)",
    "2. تركيب العلائق بأقل تكلفة (Least-Cost)",
    "3. دراسة إحلال كسبة زهرة الشمس",
    "4. المراجع والمواصفات القياسية"
])

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='watermark'>الملكية الفكرية محفوظة ©<br><b>د. عبد القادر إسماعيل</b></div>", unsafe_allow_html=True)


# ==========================================
# 6. القسم الأول: التطبيق الوراثي الحقيقي
# ==========================================
if "1." in app_mode:
    st.subheader("🧬 التطبيق الوراثي وحسابات التنبؤ الدقيق (Genetic Execution Engine)")
    st.write("تطبيق المعادلات العلمية للسيادة الجينية، الطرز المظهرية والوراثية، والقيمة التربوية للماشية والدواجن.")

    tab_gen1, tab_gen2 = st.tabs(["📊 التنبؤ بالطراز الجيني والمظهري (Mendelian)", "📈 المكافئ الوراثي والقيمة التربوية (EBV)"])

    # --- التبويب الأول: وراثة الصفات الوصفية والسيادة ---
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

        # ضبط شروط الرموز الوراثية
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

        # إجراء الحساب الوراثي الآمن
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

    # --- التبويب الثاني: القيمة التربوية ---
    with tab_gen2:
        st.markdown("##### حساب القيمة التربوية المتوقعة (Estimated Breeding Value - EBV)")
        st.write("تعتمد الحسابات على المعادلة العلمية: $EBV = h^2 \\times (P - \\bar{P})$")

        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            trait_selected = st.selectbox("الصفة الكمية:", ["إنتاج الحليب (كجم/موسم)", "وزن الفطام (كجم)", "نسبة الدهن (%)"])
            default_h2 = 0.30 if "الحليب" in trait_selected else (0.40 if "وزن" in trait_selected else 0.50)
        
        with col_h2:
            h2_val = st.number_input("المكافئ الوراثي للصفة ($h^2$):", 0.05, 0.99, default_h2, step=0.05)
        
        with col_h3:
            pop_avg = st.number_input("متوسط القطيع (Population Mean $\\bar{P}$):", 1.0, 15000.0, 2500.0 if "الحليب" in trait_selected else 22.0)

        ind_perf = st.number_input("أداء الفرد المراد انتخابه (Individual Performance $P$):", 1.0, 20000.0, 3200.0 if "الحليب" in trait_selected else 28.0)

        ebv, offspring_gain = GeneticsEngine.calculate_breeding_value(h2_val, ind_perf, pop_avg)

        st.markdown("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("الفارق الظاهري (Selection Differential)", f"{ind_perf - pop_avg:+.2f}")
        res2.metric("القيمة التربوية للفرد (EBV)", f"{ebv:+.2f}")
        res3.metric("التحسين المتوقع في الأبناء (Offspring Gain)", f"{offspring_gain:+.2f}")

        st.markdown(f"""
            <div class='genetic-card'>
            <b>التفسير العلمي:</b> استخدام هذا الفرد كأب/أم سيعطي تحسناً وراثياً متوقعاً لمجموعته الناتجة بمقدار <b>{offspring_gain:+.2f}</b> نقطة عن متوسط القطيع الحالي، بفضل المكافئ الوراثي المحسوب ($h^2 = {h2_val}$).
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# 7. التبويب الثاني: تركيب العلائق بأقل تكلفة
# ==========================================
elif "2." in app_mode:
    st.subheader("🌾 صياغة العلائق الاقتصادية متوازنة العناصر")
    st.write("حساب العليقة المثالية بأقل تكلفة المالية باستخدام الخوارزمية الخطية.")

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
        st.markdown("##### جدول المواد الخام المتاحة:")
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

        else:
            st.error("❌ لم يتم العثور على حل يطابق القيود المحددة. يُرجى تعديل النسب المطلوبة.")


# ==========================================
# 8. التبويب الثالث: تجربة أمباز زهرة الشمس
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


# ==========================================
# 9. التبويب الرابع: الدليل الميداني
# ==========================================
else:
    st.subheader("📚 الدليل الفني والمواصفات القياسية للإنتاج الحيواني")
    st.table(pd.DataFrame({
        "القطاع الإنتاجي": ["دجاج تسمين (بادئ)", "دجاج بياض (ذروة)", "أبقار حليب (متوسطة)", "أغنام تسمين"],
        "البروتين الخام (CP %)": ["22.0%", "17.5%", "16.5%", "14.0%"],
        "الطاقة الممثلة (ME Kcal/kg)": ["3000", "2750", "2600", "2700"],
        "الألياف القصوى (CF %)": ["3.5%", "5.0%", "15.0%", "12.0%"],
        "الكالسيوم (Ca %)": ["1.0%", "3.8%", "0.7%", "0.6%"]
    }))
