# genetics_data.py - قاعدة بيانات السلالات الممتدة (عالمية + سودانية + طيور زينة)

BREEDS_DATABASE = {
    "الأبقار (Cattle)": {
        # السلالات العالمية
        "هولشتاين (Holstein)": {"milk_mean": 8500, "growth_rate": 1100, "origin": "عالمي", "traits": "إنتاج حليب مرتفع جداً"},
        "بلاكبوس أنغوس (Angus)": {"milk_mean": 2200, "growth_rate": 1450, "origin": "عالمي", "traits": "لحم فريد وجودة جثة"},
        "سيمنتال (Simmental)": {"milk_mean": 5500, "growth_rate": 1350, "origin": "عالمي", "traits": "ثنائي الغرض"},
        
        # السلالات السودانية المحلية
        "الكنانة (Kenana - السودان)": {"milk_mean": 2800, "growth_rate": 750, "origin": "سوداني", "traits": "إنتاج حليب ممتاز وتحمل فائق للحرارة والجفاف"},
        "البتانة (Butana - السودان)": {"milk_mean": 3000, "growth_rate": 780, "origin": "سوداني", "traits": "من أفضل سلالات الحليب المدارية في أفريقيا"},
        "البقارة (Baggara - السودان)": {"milk_mean": 1200, "growth_rate": 850, "origin": "سوداني", "traits": "سلالة لحم وقوة جر وقدرة مشي عالية"},
        "الفولاني / النيلية": {"milk_mean": 1100, "growth_rate": 700, "origin": "أفريقي", "traits": "تحمل الطفيليات والظروف القاسية"}
    },
    
    "الأغنام (Sheep)": {
        # السلالات السودانية الصحراوية (Sudan Desert)
        "الحمري (Hamari - السودان)": {"weaning_weight": 34, "litter_size": 1.15, "milk_yield": 140, "origin": "سوداني", "traits": "جسم ضخم، وزن ممتاز، مرغوب جداً في التصدير"},
        "الأشقر / الخبشي (Ashgar - السودان)": {"weaning_weight": 32, "litter_size": 1.10, "milk_yield": 130, "origin": "سوداني", "traits": "جودة لحم عالية ولون أشقر حمري مميز"},
        "الكباشي (Kababish - السودان)": {"weaning_weight": 33, "litter_size": 1.10, "milk_yield": 120, "origin": "سوداني", "traits": "قامة عالية وتحمل رعي المسافات الطويلة"},
        "الدُّبّاسي (Dubasi - السودان)": {"weaning_weight": 31, "litter_size": 1.20, "milk_yield": 150, "origin": "سوداني", "traits": "لون أبيض بقع سوداء حول العينين وحليب جيد"},
        "النيلي (Nilotic Sheep - جنوب/سودان)": {"weaning_weight": 18, "litter_size": 1.30, "milk_yield": 60, "origin": "سوداني", "traits": "حجم صغير ومقاومة تامة لرطوبة المناطق الاستوائية"},
        
        # عالمية
        "عسافي (Assaf)": {"weaning_weight": 33, "litter_size": 1.60, "milk_yield": 380, "origin": "عالمي", "traits": "إنتاج حليب مرتفع جداً"},
        "دوربر (Dorper)": {"weaning_weight": 36, "litter_size": 1.40, "milk_yield": 100, "origin": "عالمي", "traits": "معدل نمو سريع وتغطية لحم ممتازة"}
    },
    
    "الماعز (Goats)": {
        # السودانية
        "النيوبي (Nubian Goat - السودان)": {"weaning_weight": 24, "litter_size": 1.80, "milk_yield": 280, "origin": "سوداني", "traits": "أصل الماعز النوبي العالمي، أذن طويلة وإنتاج حليب وفير"},
        "الصحراوي السوداني": {"weaning_weight": 22, "litter_size": 1.30, "milk_yield": 150, "origin": "سوداني", "traits": "إنتاج لحم وتحمل الجفاف"},
        "الجنوبي / النيلي (Nilotic Goat)": {"weaning_weight": 12, "litter_size": 1.50, "milk_yield": 50, "origin": "سوداني", "traits": "مقاومة لذبابة تسي تسي ومرض النوم"},
        
        # عالمية
        "السانين (Saanen)": {"weaning_weight": 26, "litter_size": 1.90, "milk_yield": 850, "origin": "عالمي", "traits": "قياسي في إنتاج الحليب"},
        "البور (Boer)": {"weaning_weight": 35, "litter_size": 1.70, "milk_yield": 120, "origin": "عالمي", "traits": "أفضل سلالة لحم في العالم"}
    },

    "طيور الزينة والدواجن (Ornamental Birds & Poultry)": {
        # طيور الزينة
        "البادجي / الحب (Budgerigar)": {"egg_mean": 6, "egg_weight": 2, "body_weight": 0.04, "traits": "طائر زينة، طفرات ألوان متعددة (أزرق/أصفر/أخضر)"},
        "الكوكاتيل (Cockatiel)": {"egg_mean": 5, "egg_weight": 5, "body_weight": 0.09, "traits": "عرف مرتفع، طفرات لوتينو ولون رمادي بري"},
        "دجاج السيراما (Serama - زينة)": {"egg_mean": 80, "egg_weight": 20, "body_weight": 0.40, "traits": "أصغر دجاج زينة في العالم وقامة قائمة"},
        "دجاج الحريري (Silkie - زينة)": {"egg_mean": 100, "egg_weight": 35, "body_weight": 1.10, "traits": "ريش ناعم كالحرير وشحمة أذن زرقاء ومزاج أليف"},
        "دجاج السبرات (Sebright - زينة)": {"egg_mean": 70, "egg_weight": 30, "body_weight": 0.60, "traits": "ريش محدد ومحاط بحواف سوداء دقيقة"},
        
        # الدواجن القياسية والسودانية
        "الدجاج البلدي السوداني": {"egg_mean": 130, "egg_weight": 40, "body_weight": 1.30, "traits": "أقلمة ممتازة ومقاومة فائقة للظروف المحلية"},
        "الفيومي (Fayoumi)": {"egg_mean": 180, "egg_weight": 45, "body_weight": 1.50, "traits": "مقاومة للأمراض ونضج جنسي مبكر"}
    }
}
