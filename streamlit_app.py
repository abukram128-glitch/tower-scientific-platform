import streamlit as st
import pandas as pd
import numpy as np
import itertools
from collections import Counter

# ==========================================
# 0. إعدادات واجهة التطبيق
# ==========================================
st.set_page_config(
    page_title="المُحاكي الوراثي المتكامل لحيوانات المزرعة وطيور الزينة",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧬 المنصة الشاملة للهندسة الوراثية، سجل الأنساب، وتتبع الأجيال")
st.caption("نظام بحثي تطبيقي متكامل للسلالات العالمية والسودانية المحلية وطيور الزينة مع حسابات Inbreeding & Breeding Values")

# ==========================================
# 1. قاعدة البيانات الضخمة الممتدة
# ==========================================
BREEDS_DATABASE = {
    "الأبقار (Cattle)": {
        # السلالات السودانية
        "الكنانة (Kenana - السودان)": {
            "type": "حليب", "origin": "سوداني", "milk_yield": 2800, "fat_pct": 4.5, 
            "growth_rate": 750, "heat_tolerance": "عالية جداً", "disease_res": "ممتازة",
            "traits": "حليب وفير في البيئات المدارية، نسبة دهن جيدة، متحملة للقراد والحرارة."
        },
        "البتانة (Butana - السودان)": {
            "type": "حليب", "origin": "سوداني", "milk_yield": 3100, "fat_pct": 4.6, 
            "growth_rate": 780, "heat_tolerance": "عالية جداً", "disease_res": "ممتازة",
            "traits": "أحد أفضل سلالات الحليب المدارية في أفريقيا، متأقلمة مع الجفاف."
        },
        "البقارة (Baggara - السودان)": {
            "type": "لحم / جر", "origin": "سوداني", "milk_yield": 1200, "fat_pct": 4.0, 
            "growth_rate": 850, "heat_tolerance": "عالية جداً", "disease_res": "عالية",
            "traits": "سلالة لحم وقوة تحمل، ممتازة في رعي المسافات الطويلة بالغرب السوداني."
        },
        "العنواك / النيلية (Nilotic Cattle)": {
            "type": "لحم / مناعة", "origin": "سوداني", "milk_yield": 900, "fat_pct": 3.8, 
            "growth_rate": 650, "heat_tolerance": "عالية", "disease_res": "فائقة",
            "traits": "قزمة/متوسطة، مقاومة عالية للحرارة المرتفعة ورطوبة المستنقعات وحشرات المياه."
        },
        # السلالات العالمية
        "هولشتاين (Holstein-Friesian)": {
            "type": "حليب", "origin": "عالمي (هولندا)", "milk_yield": 8500, "fat_pct": 3.7, 
            "growth_rate": 1100, "heat_tolerance": "منخفضة", "disease_res": "متوسطة",
            "traits": "الأعلى إنتاجاً للحليب عالمياً، تحتاج إدارة تغذية وبرودة عالية."
        },
        "براون سويس (Brown Swiss)": {
            "type": "ثنائي الغرض", "origin": "عالمي (سويسرا)", "milk_yield": 6500, "fat_pct": 4.0, 
            "growth_rate": 1150, "heat_tolerance": "متوسطة", "disease_res": "قوية",
            "traits": "حليب ممتاز لصناعة الأجبان، جثة ممتازة وقوية البنية."
        },
        "بلاكبوس أنغوس (Black Angus)": {
            "type": "لحم", "origin": "عالمي (إسكتلندا)", "milk_yield": 2200, "fat_pct": 3.9, 
            "growth_rate": 1450, "heat_tolerance": "متوسطة", "disease_res": "جيدة",
            "traits": "سلالة اللحم الأولى عالمياً، تصافٍ عالية وجودة مرملة للحم (Marbling)."
        },
        "سيمنتال (Simmental)": {
            "type": "ثنائي الغرض", "origin": "عالمي (سويسرا)", "milk_yield": 5800, "fat_pct": 3.9, 
            "growth_rate": 1380, "heat_tolerance": "متوسطة", "disease_res": "جيدة",
            "traits": "معدلات نمو ممتازة مع إنتاج حليب غزير للأمهات."
        }
    },
    
    "الأغنام (Sheep)": {
        # السلالات السودانية
        "الحمري (Hamari Desert Sheep)": {
            "type": "لحم / تصدير", "origin": "سوداني", "weaning_wt": 34, "adult_wt": 75, 
            "litter_size": 1.15, "milk_yield": 140, "traits": "جسم ضخم، مرغوبة جداً في أسواق التصدير، أذن طويلة لينة."
        },
        "الأشقر / الخبشي (Ashgar)": {
            "type": "لحم", "origin": "سوداني", "weaning_wt": 32, "adult_wt": 70, 
            "litter_size": 1.10, "milk_yield": 130, "traits": "لون أحمر/أشقر مميز، نسبة تصافٍ عالية ولحم ممتاز."
        },
        "الكباشي (Kababish Desert)": {
            "type": "لحم / رعي", "origin": "سوداني", "weaning_wt": 33, "adult_wt": 72, 
            "litter_size": 1.10, "milk_yield": 120, "traits": "أرجل طويلة، قدرة فائقة على قطع مسافات صحراوية شاسعة."
        },
        "الدُّبّاسي (Dubasi)": {
            "type": "لحم / حليب", "origin": "سوداني", "weaning_wt": 31, "adult_wt": 68, 
            "litter_size": 1.25, "milk_yield": 160, "traits": "لون أبيض بقع سوداء حول العينين والأرجل، درّارة للحليب."
        },
        "النيلي (Nilotic Sheep)": {
            "type": "لحم / مناعة", "origin": "سوداني", "weaning_wt": 18, "adult_wt": 35, 
            "litter_size": 1.35, "milk_yield": 60, "traits": "قصيرة القامة، مقاومة لأمراض الرطوبة والديدان الكبدية."
        },
        # السلالات العالمية
        "عسافي (Assaf)": {
            "type": "حليب / لحم", "origin": "عالمي", "weaning_wt": 33, "adult_wt": 85, 
            "litter_size": 1.65, "milk_yield": 380, "traits": "هجين العواسي والشرق فريزيان، إنتاج حليب قياسي."
        },
        "دوربر (Dorper)": {
            "type": "لحم قياسي", "origin": "عالمي (جنوب أفريقيا)", "weaning_wt": 36, "adult_wt": 95, 
            "litter_size": 1.45, "milk_yield": 100, "traits": "تساقط صوف ذاتي، معدل نمو عالي وسرعة بلوغ."
        },
        "روماني / بورولا (Romanov)": {
            "type": "خصوبة عالية", "origin": "عالمي (روسيا)", "weaning_wt": 22, "adult_wt": 55, 
            "litter_size": 2.80, "milk_yield": 110, "traits": "أعلى معدل خصوبة وتوأمية في العالم (تلد حتى 3-4 توائم)."
        }
    },
    
    "الماعز (Goats)": {
        # السلالات السودانية
        "النيوبي (Nubian Goat - السودان)": {
            "type": "حليب / تحسين", "origin": "سوداني", "milk_yield": 280, "fat_pct": 5.0, 
            "weaning_wt": 24, "litter_size": 1.80, "traits": "أصل الماعز النوبي العالمي، أذن طويلة ومظاهر أنثوية ممتازة."
        },
        "الصحراوي السوداني": {
            "type": "لحم / رعي", "origin": "سوداني", "milk_yield": 150, "fat_pct": 4.2, 
            "weaning_wt": 22, "litter_size": 1.30, "traits": "تحمل الجفاف وقلة الموارد المائية، قامة متوسطة."
        },
        "الماعز التاغري / الجبلي": {
            "type": "لحم", "origin": "سوداني", "milk_yield": 110, "fat_pct": 4.0, 
            "weaning_wt": 20, "litter_size": 1.40, "traits": "ممتلئة الجسم، متكيفة مع المناطق الجبلية والوعرة."
        },
        # السلالات العالمية
        "السانين (Saanen)": {
            "type": "حليب قياسي", "origin": "عالمي (سويسرا)", "milk_yield": 850, "fat_pct": 3.5, 
            "weaning_wt": 26, "litter_size": 1.95, "traits": "سيدة إنتاج الحليب في الماعز، لون أبيض ناصع."
        },
        "البور (Boer)": {
            "type": "لحم قياسي", "origin": "عالمي (جنوب أفريقيا)", "milk_yield": 120, "fat_pct": 4.0, 
            "weaning_wt": 35, "litter_size": 1.75, "traits": "أضخم سلالات الماعز في إنتاج اللحم والجثة."
        },
        "الألبين (Alpine)": {
            "type": "حليب", "origin": "عالمي (فرنسا)", "milk_yield": 750, "fat_pct": 3.6, 
            "weaning_wt": 25, "litter_size": 1.85, "traits": "تأقلم عالي مع البيئات المختلفة وإنتاج حليب غزير."
        }
    },

    "طيور الزينة والدواجن (Birds & Poultry)": {
        # طيور الزينة
        "طائر البادجي (Budgerigar)": {
            "category": "زينة", "origin": "أستراليا", "clutch_size": 6, "egg_wt": 2, 
            "body_wt": 0.04, "traits": "طفرات ألوان متعددة (أزرق، أخضر، لوتينو، أوبالين)."
        },
        "الكوكاتيل (Cockatiel)": {
            "category": "زينة", "origin": "أستراليا", "clutch_size": 5, "egg_wt": 5, 
            "body_wt": 0.09, "traits": "عرف مرتفع، خدود برتقالية، طفرات لوتينو والوايتبايس."
        },
        "دجاج السيراما (Serama)": {
            "category": "زينة قياسي", "origin": "ماليزيا", "clutch_size": 8, "egg_wt": 20, 
            "body_wt": 0.40, "traits": "أصغر دجاج زينة في العالم، صدر بارز وقامة رأسية."
        },
        "دجاج الحريري (Silkie)": {
            "category": "زينة", "origin": "الصين", "clutch_size": 10, "egg_wt": 35, 
            "body_wt": 1.10, "traits": "ريش يشبه الحرير، جلد وعظام سوداء، 5 أصابع بالأقدام."
        },
        "دجاج السبرات (Sebright)": {
            "category": "زينة", "origin": "بريطانيا", "clutch_size": 8, "egg_wt": 30, 
            "body_wt": 0.60, "traits": "ريش محدد ومحاط بحواف سوداء دقيقة للغاية."
        },
        # الدواجن القياسية والسودانية
        "الدجاج البلدي السوداني": {
            "category": "إنتاج / مناعة", "origin": "سوداني", "clutch_size": 130, "egg_wt": 42, 
            "body_wt": 1.35, "traits": "مقاومة فائقة لنيوكاسل والحرارة، وضع بيض في ظروف قاسية."
        },
        "الفيومي (Fayoumi)": {
            "category": "إنتاج / مناعة", "origin": "مصر", "clutch_size": 190, "egg_wt": 46, 
            "body_wt": 1.50, "traits": "نضج جنسي مبكر، مقاومة عالية للديدان والأمراض الفيروسية."
        },
        "اللجهورن (Leghorn)": {
            "category": "إنتاج بيض", "origin": "إيطاليا", "clutch_size": 280, "egg_wt": 62, 
            "body_wt": 1.80, "traits": "قياسي عالمي في تحويل العلف إلى بيض."
        }
    }
}

# ==========================================
# 2. محرك مربعات بانيت والوراثة المندلية
# ==========================================
def generate_gametes(genotype):
    if len(genotype) == 1:
        genotype = genotype + genotype
    pairs = [genotype[i:i+2] for i in range(0, len(genotype), 2)]
    gamete_alleles = [list(pair) for pair in pairs]
    return [''.join(g) for g in itertools.product(*gamete_alleles)]

def run_punnett_square(sire_geno, dam_geno):
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
    ).astype(str)
    
    counts = Counter(all_offspring)
    total = len(all_offspring)
    ratios = [{"التركيب الوراثي (Genotype)": k, "العدد": v, "النسبة المئوية": f"{(v/total)*100:.1f}%"} for k, v in counts.items()]
    
    return df_punnett, pd.DataFrame(ratios)

# ==========================================
# 3. القائمة الجانبية وتحديد المعطيات
# ==========================================
st.sidebar.header("⚙️ إعدادات النموذج والتخصيص")

selected_category = st.sidebar.selectbox("1. اختر التخصص الحيواني:", list(BREEDS_DATABASE.keys()))

generation_target = st.sidebar.radio(
    "2. الجيل المراد محاكاته وتربيته:",
    [
        "الجيل الأول (F1 Cross)", 
        "الجيل الثاني (F2 Generation - F1 × F1)", 
        "الجيل الثالث (F3 Generation)",
        "الخلط الرجعي (Backcross - F1 × Sire/Dam)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧬 خيارات التزاوج الداخلي")
inbreeding_check = st.sidebar.checkbox("حساب معامل التزاوج الداخلي (Inbreeding Coefficient)", value=False)
if inbreeding_check:
    inbreeding_level = st.sidebar.slider("نسبة قرابة الآباء (Relationship Degree):", 0.0, 0.5, 0.125, step=0.0625, help="0.25 = أشقاء، 0.125 = غيران")

# ==========================================
# 4. واجهة العرض واختيار السلالات
# ==========================================
breeds_dict = BREEDS_DATABASE[selected_category]
st.header(f"📊 برنامج تحسين وتتبع أجيال: {selected_category}")

c_sire, c_dam = st.columns(2)

with c_sire:
    st.subheader("♂️ خط الآباء / الذكور (Sire Line)")
    sire_breed = st.selectbox("سلالة الذكر (Sire Breed):", list(breeds_dict.keys()), index=0)
    sire_data = breeds_dict[sire_breed]
    st.success(f"📌 **الأصل:** {sire_data['origin']} | **الصفات:** {sire_data['traits']}")
    
    # اختيار الجينات الوصفية للذكر
    sire_geno = st.selectbox(
        "الجينات الوصفية للذكر (القرون / العرف / اللون):", 
        ["PP (سائد نقي - عديم القرون/عرف جوزي)", "Pp (خليط)", "pp (متنحي - بقرون/عرف مفرد)"], 
        key="s_geno_main"
    )

with c_dam:
    st.subheader("♀️ خط الأمهات / الإناث (Dam Line)")
    dam_breed = st.selectbox("سلالة الأنثى (Dam Breed):", list(breeds_dict.keys()), index=1 if len(breeds_dict)>1 else 0)
    dam_data = breeds_dict[dam_breed]
    st.warning(f"📌 **الأصل:** {dam_data['origin']} | **الصفات:** {dam_data['traits']}")
    
    # اختيار الجينات الوصفية للأنثى
    dam_geno = st.selectbox(
        "الجينات الوصفية للأنثى:", 
        ["pp (متنحي - بقرون/عرف مفرد)", "Pp (خليط)", "PP (سائد نقي - عديم القرون)"], 
        key="d_geno_main"
    )

st.markdown("---")

# ==========================================
# 5. محرك حسابات الهجين وتتبع الأجيال Mating Engine
# ==========================================
st.subheader(f"📈 نتائج ومؤشرات {generation_target}")

# حساب معامل قوة الهجين Heterosis ومعامل التفكك Breakup
if generation_target == "الجيل الأول (F1 Cross)":
    heterosis_factor = 1.12 if sire_breed != dam_breed else 1.00
    gen_desc = f"تزاوج مباشر (50% جينات {sire_breed} + 50% جينات {dam_breed}). أقصى قوة هجين متوقعة."
    sire_g_input = sire_geno.split()[0]
    dam_g_input = dam_geno.split()[0]
    sire_blood_pct = 50.0

elif generation_target == "الجيل الثاني (F2 Generation - F1 × F1)":
    heterosis_factor = 1.05 if sire_breed != dam_breed else 1.00 # فقدان نصف قوة الهجين
    gen_desc = f"تزاوج أفراد F1 داخلياً. انخفاض قوة الهجين بنسبة 50% وظهور الانعزالات الوراثية المندلية."
    sire_g_input = "Pp"
    dam_g_input = "Pp"
    sire_blood_pct = 50.0

elif generation_target == "الجيل الثالث (F3 Generation)":
    heterosis_factor = 1.02 if sire_breed != dam_breed else 1.00
    gen_desc = f"الجيل الثالث F3. استقرار الصفات وتثبيت السلالة المستحدثة (Composite Breed Creation)."
    sire_g_input = "Pp"
    dam_g_input = "Pp"
    sire_blood_pct = 50.0

else: # Backcross
    heterosis_factor = 1.04
    gen_desc = f"خلط رجعي (F1 × {sire_breed}). لاستعادة 75% من صفات سلالة الذكر الأصلي مع الاحتفاظ بمناعة الأم."
    sire_g_input = sire_geno.split()[0]
    dam_g_input = "Pp"
    sire_blood_pct = 75.0

# تأثير التزاوج الداخلي إذا تم تفعيله
if inbreeding_check:
    inbreeding_penalty = 1.0 - (inbreeding_level * 0.15) # خفض الأداء بسبب Inbreeding Depression
    heterosis_factor *= inbreeding_penalty
    st.error(f"⚠️ تم تطبيق خصم التزاوج الداخلي (Inbreeding Depression): خصم {inbreeding_level*15:.1f}% من الأداء الإنتاجي.")

st.info(f"💡 **وصف التركيب الوراثي والتوزيع:** {gen_desc}")

# العرض في تبويبات تفصيلية
tab_punnett, tab_performance, tab_pedigree = st.tabs([
    "🧬 مربع بانيت والانعزالات الجينية", 
    "📊 المتوقع الإنتاجي والمؤشرات الكمية", 
    "📜 خريطة النسل وسجل الأنساب (Pedigree)"
])

with tab_punnett:
    df_p, df_r = run_punnett_square(sire_g_input, dam_g_input)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.write(f"**جدول أمشاج مربع بانيت لـ ({generation_target}):**")
        st.table(df_p)
    with col_b:
        st.write("**توزيع النسب والجينوتيب:**")
        st.table(df_r)

with tab_performance:
    if "الأبقار" in selected_category:
        base_milk = (sire_data['milk_yield'] + dam_data['milk_yield']) / 2
        exp_milk = base_milk * heterosis_factor
        exp_growth = ((sire_data['growth_rate'] + dam_data['growth_rate']) / 2) * heterosis_factor
        exp_fat = (sire_data['fat_pct'] + dam_data['fat_pct']) / 2
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إنتاج الحليب المتوقع للنسل", f"{exp_milk:.0f} كجم/موسم")
        m2.metric("معدل النمو اليومي", f"{exp_growth:.0f} جم/يوم")
        m3.metric("نسبة الدهن المتوقعة", f"{exp_fat:.2f}%")
        m4.metric("نسبة دم السلالة الأولى (Sire)", f"{sire_blood_pct:.1f}%")

    elif "الأغنام" in selected_category or "الماعز" in selected_category:
        exp_wean = ((sire_data['weaning_wt'] + dam_data['weaning_wt']) / 2) * heterosis_factor
        exp_litter = ((sire_data['litter_size'] + dam_data['litter_size']) / 2) * (heterosis_factor if heterosis_factor > 1 else 1.0)
        exp_milk = ((sire_data['milk_yield'] + dam_data['milk_yield']) / 2) * heterosis_factor
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("وزن الفطام المتوقع", f"{exp_wean:.1f} كجم")
        m2.metric("معدل التوأمية المتوقع", f"{exp_litter:.2f} مولود/بطن")
        m3.metric("إنتاج الحليب المتوقع للأمهات", f"{exp_milk:.0f} كجم/موسم")
        m4.metric("نسبة دم الذكر (Sire Blood)", f"{sire_blood_pct:.1f}%")

    else: # طيور وزينة ودواجن
        exp_egg = ((sire_data['clutch_size'] + dam_data['clutch_size']) / 2) * heterosis_factor
        exp_body = (sire_data['body_wt'] + dam_data['body_wt']) / 2
        exp_egg_wt = (sire_data['egg_wt'] + dam_data['egg_wt']) / 2
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إنتاج البيض / حجم العش المتوقع", f"{exp_egg:.0f}")
        m2.metric("وزن الجسم المتوقع للناتج", f"{exp_body:.2f} كجم")
        m3.metric("متوسط وزن البيضة", f"{exp_egg_wt:.1f} جم")

with tab_pedigree:
    st.subheader("📜 سجل شجرة الأنساب المتوقعة (Pedigree Tree)")
    st.code(f"""
    [ الجيل الأبوي P1 ]
    ├── الأب (Sire): {sire_breed} (100% {sire_data['origin']})
    └── الأم (Dam): {dam_breed} (100% {dam_data['origin']})
          │
          ▼
    [ الناتج: {generation_target} ]
    ├── نسبة دم الأب: {sire_blood_pct}% {sire_breed}
    ├── نسبة دم الأم: {100-sire_blood_pct}% {dam_breed}
    └── الحالة الوراثية: {'هجين F1 ممتاز' if generation_target == 'الجيل الأول (F1 Cross)' else 'انعزالات وراثية وتثبيت خطوط'}
    """, language="text")
