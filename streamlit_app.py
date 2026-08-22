# ============================================================
# وحدة الخيول والفروسية المتكاملة - منصة تاور العلمية
# الإصدار 2.0 - متخصصة في الخيول فقط مع الوراثة والتهجين
# المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import hashlib

# ============================================================
# 1. قاعدة بيانات السلالات والوراثة
# ============================================================

# قاعدة بيانات شاملة للسلالات
HORSE_BREEDS_DATABASE = {
    "خيل عربي أصيل": {
        "الوصف": "أقدم سلالات الخيول في العالم، تتميز بالجمال والتحمل",
        "الموطن الأصلي": "شبه الجزيرة العربية",
        "الارتفاع (سم)": {"الذكر": 145-155, "الأنثى": 140-150},
        "الوزن (كجم)": {"الذكر": 400-500, "الأنثى": 350-450},
        "الألوان": ["أشقر", "كميت", "أحمر", "أسود", "أبيض"],
        "الصفات": {
            "التحمل": 9.5,
            "السرعة": 8.0,
            "الذكاء": 9.0,
            "الرشاقة": 8.5,
            "المظهر": 10.0
        },
        "الاستخدامات": ["التحمل", "العروض", "السباقات الطويلة", "التزاوج"],
        "الأمراض الشائعة": ["مغص", "التهابات المفاصل"],
        "نظام غذائي خاص": "غني بالألياف، بروتين متوسط 10-12%",
        "الجينات السائدة": ["تحمل عالي", "عظام قوية", "جهاز تنفسي ممتاز"],
        "الجينات المتنحية": ["حساسية للبرد", "بطء في النمو"]
    },
    "ثوروبريد (خيل أصيل إنجليزي)": {
        "الوصف": "سلالة سباقات عالمية، تتميز بالسرعة الفائقة",
        "الموطن الأصلي": "إنجلترا",
        "الارتفاع (سم)": {"الذكر": 155-170, "الأنثى": 150-165},
        "الوزن (كجم)": {"الذكر": 450-550, "الأنثى": 400-500},
        "الألوان": ["كميت", "أشقر", "رمادي", "أسود"],
        "الصفات": {
            "التحمل": 7.0,
            "السرعة": 10.0,
            "الذكاء": 8.0,
            "الرشاقة": 9.0,
            "المظهر": 9.0
        },
        "الاستخدامات": ["سباقات السرعة", "قفز الحواجز", "الركوب الترفيهي"],
        "الأمراض الشائعة": ["التهابات الرئة", "كسور العظام"],
        "نظام غذائي خاص": "غني بالطاقة، بروتين عالي 14-16%",
        "الجينات السائدة": ["سرعة عالية", "عضلات قوية", "قلب كبير"],
        "الجينات المتنحية": ["هشاشة العظام", "عمر قصير"]
    },
    "خيل بربري": {
        "الوصف": "سلالة شمال أفريقية، تجمع بين القوة والتحمل",
        "الموطن الأصلي": "شمال أفريقيا (المغرب، الجزائر، تونس)",
        "الارتفاع (سم)": {"الذكر": 150-160, "الأنثى": 145-155},
        "الوزن (كجم)": {"الذكر": 450-550, "الأنثى": 400-500},
        "الألوان": ["رمادي", "كميت", "أشقر", "أسود"],
        "الصفات": {
            "التحمل": 9.0,
            "السرعة": 8.5,
            "الذكاء": 8.5,
            "الرشاقة": 8.0,
            "المظهر": 8.0
        },
        "الاستخدامات": ["الركوب اليومي", "العروض التقليدية", "سباقات التحمل"],
        "الأمراض الشائعة": ["مشاكل الجهاز الهضمي"],
        "نظام غذائي خاص": "متوازن، بروتين 11-13%",
        "الجينات السائدة": ["مناعة قوية", "تكيف مع المناخ الحار", "قوة تحمل"],
        "الجينات المتنحية": ["بطء في التعلم", "عناد"]
    },
    "خيل فلاديجير": {
        "الوصف": "سلالة روسية ثقيلة، تستخدم للأعمال الثقيلة",
        "الموطن الأصلي": "روسيا",
        "الارتفاع (سم)": {"الذكر": 160-175, "الأنثى": 155-170},
        "الوزن (كجم)": {"الذكر": 600-750, "الأنثى": 550-650},
        "الألوان": ["أسود", "كميت", "رمادي"],
        "الصفات": {
            "التحمل": 6.0,
            "السرعة": 5.0,
            "الذكاء": 7.0,
            "الرشاقة": 5.0,
            "المظهر": 7.0
        },
        "الاستخدامات": ["الأعمال الزراعية", "جر العربات", "الركوب الترفيهي"],
        "الأمراض الشائعة": ["مشاكل المفاصل", "السمنة"],
        "نظام غذائي خاص": "غني بالألياف، بروتين منخفض 8-10%",
        "الجينات السائدة": ["قوة بدنية", "تحمل للبرد", "استقرار مزاجي"],
        "الجينات المتنحية": ["بطء", "قلة مرونة"]
    },
    "خيل فالابيلا": {
        "الوصف": "أصغر سلالات الخيول في العالم، من الأرجنتين",
        "الموطن الأصلي": "الأرجنتين",
        "الارتفاع (سم)": {"الذكر": 70-80, "الأنثى": 65-75},
        "الوزن (كجم)": {"الذكر": 50-70, "الأنثى": 40-60},
        "الألوان": ["جميع الألوان"],
        "الصفات": {
            "التحمل": 4.0,
            "السرعة": 4.0,
            "الذكاء": 8.0,
            "الرشاقة": 7.0,
            "المظهر": 9.5
        },
        "الاستخدامات": ["الحيوانات الأليفة", "العروض", "العلاج النفسي"],
        "الأمراض الشائعة": ["مشاكل الأسنان", "السمنة"],
        "نظام غذائي خاص": "مركز، بروتين 14-16%",
        "الجينات السائدة": ["حجم صغير", "عمر طويل", "ذكاء"],
        "الجينات المتنحية": ["ضعف عظام", "حساسية للبرد"]
    }
}

# ============================================================
# 2. نظام التهجين والوراثة
# ============================================================

class HorseGenetics:
    """نظام متقدم لإدارة الوراثة والتهجين في الخيول"""
    
    def __init__(self):
        self.breeds_db = HORSE_BREEDS_DATABASE
        
    def calculate_inheritance(self, breed1, breed2, trait_weight=0.5):
        """
        حساب وراثة الصفات من الأبوين
        
        المعاملات:
            breed1 (str): اسم السلالة الأولى
            breed2 (str): اسم السلالة الثانية
            trait_weight (float): وزن التأثير الجيني (0-1)
        
        الإرجاع:
            dict: الصفات الموروثة
        """
        if breed1 not in self.breeds_db or breed2 not in self.breeds_db:
            return {"error": "سلالة غير موجودة في قاعدة البيانات"}
        
        # جلب صفات الأبوين
        traits1 = self.breeds_db[breed1]["الصفات"]
        traits2 = self.breeds_db[breed2]["الصفات"]
        
        # حساب الصفات الموروثة (نموذج وراثي متوسط مع تفوق هجيني)
        inherited_traits = {}
        hybrid_vigor = 0.05  # قوة الهجين (زيادة 5%)
        
        for trait in traits1.keys():
            if trait in traits2:
                # المتوسط المرجح مع قوة هجين
                base_value = (traits1[trait] + traits2[trait]) / 2
                # إضافة تأثير السيادة (dominance)
                dominance_effect = abs(traits1[trait] - traits2[trait]) * 0.2
                # قوة الهجين
                hybrid_effect = base_value * hybrid_vigor * (1 - trait_weight)
                
                inherited_traits[trait] = min(10.0, base_value + dominance_effect + hybrid_effect)
            else:
                inherited_traits[trait] = traits1[trait]
        
        return inherited_traits
    
    def predict_offspring_characteristics(self, breed1, breed2):
        """
        التنبؤ بمواصفات الناتج الهجين
        
        المعاملات:
            breed1 (str): اسم السلالة الأولى
            breed2 (str): اسم السلالة الثانية
        
        الإرجاع:
            dict: المواصفات المتوقعة للناتج
        """
        if breed1 not in self.breeds_db or breed2 not in self.breeds_db:
            return {"error": "سلالة غير موجودة في قاعدة البيانات"}
        
        b1 = self.breeds_db[breed1]
        b2 = self.breeds_db[breed2]
        
        # حساب متوسط الارتفاع والوزن
        height_range = {
            "الذكر": (
                (b1["الارتفاع (سم)"]["الذكر"] + b2["الارتفاع (سم)"]["الذكر"]) / 2,
                (b1["الارتفاع (سم)"]["الذكر"] + b2["الارتفاع (سم)"]["الذكر"]) / 2 + 5
            ),
            "الأنثى": (
                (b1["الارتفاع (سم)"]["الأنثى"] + b2["الارتفاع (سم)"]["الأنثى"]) / 2,
                (b1["الارتفاع (سم)"]["الأنثى"] + b2["الارتفاع (سم)"]["الأنثى"]) / 2 + 5
            )
        }
        
        weight_range = {
            "الذكر": (
                (b1["الوزن (كجم)"]["الذكر"] + b2["الوزن (كجم)"]["الذكر"]) / 2,
                (b1["الوزن (كجم)"]["الذكر"] + b2["الوزن (كجم)"]["الذكر"]) / 2 + 20
            ),
            "الأنثى": (
                (b1["الوزن (كجم)"]["الأنثى"] + b2["الوزن (كجم)"]["الأنثى"]) / 2,
                (b1["الوزن (كجم)"]["الأنثى"] + b2["الوزن (كجم)"]["الأنثى"]) / 2 + 20
            )
        }
        
        # دمج الألوان المحتملة
        possible_colors = list(set(b1["الألوان"] + b2["الألوان"]))
        
        # الصفات الموروثة
        inherited_traits = self.calculate_inheritance(breed1, breed2)
        
        # الجينات السائدة والمتنحية في الناتج
        dominant_genes = list(set(b1["الجينات السائدة"] + b2["الجينات السائدة"]))[:4]
        recessive_genes = list(set(b1["الجينات المتنحية"] + b2["الجينات المتنحية"]))[:3]
        
        return {
            "الارتفاع المتوقع (سم)": height_range,
            "الوزن المتوقع (كجم)": weight_range,
            "الألوان المحتملة": possible_colors,
            "الصفات الموروثة": inherited_traits,
            "الجينات السائدة المتوقعة": dominant_genes,
            "الجينات المتنحية المتوقعة": recessive_genes,
            "الاستخدامات المقترحة": self._suggest_usage(breed1, breed2),
            "قوة الهجين المتوقعة": self._calculate_hybrid_vigor(breed1, breed2),
            "التوصيات الغذائية": self._suggest_diet(breed1, breed2)
        }
    
    def _suggest_usage(self, breed1, breed2):
        """اقتراح استخدامات للهجين"""
        b1 = self.breeds_db[breed1]
        b2 = self.breeds_db[breed2]
        
        common_uses = set(b1["الاستخدامات"]) & set(b2["الاستخدامات"])
        combined_uses = set(b1["الاستخدامات"]) | set(b2["الاستخدامات"])
        
        if common_uses:
            return list(common_uses)
        else:
            return list(combined_uses)[:3]
    
    def _calculate_hybrid_vigor(self, breed1, breed2):
        """حساب قوة الهجين (Heterosis)"""
        if breed1 == breed2:
            return "ضعيفة (نفس السلالة)"
        
        # حساب التباين الجيني
        traits1 = self.breeds_db[breed1]["الصفات"]
        traits2 = self.breeds_db[breed2]["الصفات"]
        
        variance = 0
        for trait in traits1.keys():
            if trait in traits2:
                variance += abs(traits1[trait] - traits2[trait])
        
        avg_variance = variance / len(traits1)
        
        if avg_variance > 3:
            return "قوية جداً (تنوع جيني عالي)"
        elif avg_variance > 2:
            return "قوية (تنوع جيني متوسط)"
        elif avg_variance > 1:
            return "متوسطة (تنوع جيني منخفض)"
        else:
            return "ضعيفة (تشابه جيني عالي)"
    
    def _suggest_diet(self, breed1, breed2):
        """توصيات غذائية للهجين"""
        b1 = self.breeds_db[breed1]
        b2 = self.breeds_db[breed2]
        
        diet1 = b1["نظام غذائي خاص"]
        diet2 = b2["نظام غذائي خاص"]
        
        # دمج التوصيات
        return f"توصيات مختلطة: {diet1} و {diet2} مع مراقبة الاستجابة"
    
    def compare_breeds(self, breed1, breed2):
        """مقارنة مفصلة بين سلالتين"""
        if breed1 not in self.breeds_db or breed2 not in self.breeds_db:
            return {"error": "سلالة غير موجودة"}
        
        b1 = self.breeds_db[breed1]
        b2 = self.breeds_db[breed2]
        
        comparison = {
            "السلالة الأولى": breed1,
            "السلالة الثانية": breed2,
            "مقارنة الصفات": {},
            "التشابه": 0,
            "الاختلاف": 0
        }
        
        # مقارنة الصفات
        traits1 = b1["الصفات"]
        traits2 = b2["الصفات"]
        
        similarity_count = 0
        total_traits = len(traits1)
        
        for trait in traits1.keys():
            if trait in traits2:
                diff = abs(traits1[trait] - traits2[trait])
                comparison["مقارنة الصفات"][trait] = {
                    breed1: traits1[trait],
                    breed2: traits2[trait],
                    "الفرق": diff
                }
                if diff < 1:
                    similarity_count += 1
        
        comparison["التشابه"] = (similarity_count / total_traits) * 100
        comparison["الاختلاف"] = 100 - comparison["التشابه"]
        
        return comparison

# ============================================================
# 3. نظام التغذية المتقدم للخيول
# ============================================================

# مكتبة الأعلاف المخصصة للخيول فقط
HORSE_FEEDS_LIBRARY = {
    "🌾 الحبوب ومصادر الطاقة": {
        "ذرة صفراء": {"CP": 8.5, "DC": 0.85, "SE": 80.0, "NDF": 9.5, "سعر": 250},
        "ذرة بيضاء": {"CP": 8.8, "DC": 0.83, "SE": 78.0, "NDF": 10.2, "سعر": 240},
        "شعير مطحون": {"CP": 11.5, "DC": 0.80, "SE": 71.0, "NDF": 18.5, "سعر": 220},
        "شوفان علفي": {"CP": 11.0, "DC": 0.76, "SE": 62.0, "NDF": 27.5, "سعر": 230},
        "قمح محلي": {"CP": 12.0, "DC": 0.85, "SE": 75.0, "NDF": 11.5, "سعر": 210}
    },
    "🌱 مصادر البروتين": {
        "كسب فول صويا 44%": {"CP": 44.0, "DC": 0.90, "SE": 74.0, "NDF": 13.5, "سعر": 450},
        "كسب عباد الشمس": {"CP": 36.0, "DC": 0.76, "SE": 42.0, "NDF": 38.5, "سعر": 350},
        "كسب بذور القطن": {"CP": 41.0, "DC": 0.78, "SE": 55.0, "NDF": 24.5, "سعر": 380},
        "أمباز الفول السوداني": {"CP": 46.0, "DC": 0.88, "SE": 73.0, "NDF": 15.5, "سعر": 420}
    },
    "🧬 مصادر البروتين الحيواني": {
        "مسحوق أسماك 60%": {"CP": 60.0, "DC": 0.85, "SE": 65.0, "NDF": 2.5, "سعر": 800},
        "مركزات خيول": {"CP": 36.0, "DC": 0.80, "SE": 55.0, "NDF": 15.5, "سعر": 500}
    },
    "🚜 الألياف والمواد الخشنة": {
        "نخالة قمح": {"CP": 15.0, "DC": 0.72, "SE": 45.0, "NDF": 35.5, "سعر": 180},
        "البرسيم الجاف": {"CP": 16.5, "DC": 0.60, "SE": 35.0, "NDF": 42.5, "سعر": 200},
        "مولاس قصب": {"CP": 4.0, "DC": 0.95, "SE": 50.0, "NDF": 1.5, "سعر": 150},
        "تبن القمح": {"CP": 3.5, "DC": 0.45, "SE": 25.0, "NDF": 65.0, "سعر": 120}
    },
    "🪨 المعادن والإضافات": {
        "ملح الطعام": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "سعر": 50},
        "حجر جيري": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "سعر": 60},
        "فوسفات ثنائي الكالسيوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "سعر": 120},
        "بيكربونات الصوديوم": {"CP": 0.0, "DC": 0.0, "SE": 0.0, "NDF": 0.0, "سعر": 90}
    }
}

# الإضافات الإلزامية للخيول
HORSE_FIXED_ADDITIVES = {
    "ملح الطعام": 0.5,
    "حجر جيري": 1.5,
    "فوسفات ثنائي الكالسيوم": 1.0
}

# الاحتياجات الغذائية حسب المرحلة
HORSE_NUTRITIONAL_REQUIREMENTS = {
    "خيول رياضة ونشاط مكثف": {
        "DP": 10.5,
        "SE": 68.0,
        "كالسيوم": 0.7,
        "فسفور": 0.5,
        "ملاحظات": "زيادة الدهون النباتية، فيتامين E"
    },
    "أمهار نامية صغيرة": {
        "DP": 13.0,
        "SE": 65.0,
        "كالسيوم": 0.9,
        "فسفور": 0.6,
        "ملاحظات": "بروتين عالي الجودة، معادن متوازنة"
    },
    "فرسات مرضعات": {
        "DP": 13.5,
        "SE": 62.0,
        "كالسيوم": 0.9,
        "فسفور": 0.6,
        "ملاحظات": "زيادة العلف 30-50%، طاقة عالية"
    },
    "خيول صيانة (بالغين)": {
        "DP": 8.5,
        "SE": 52.0,
        "كالسيوم": 0.5,
        "فسفور": 0.3,
        "ملاحظات": "علف متوازن، ألياف كافية"
    }
}

# ============================================================
# 4. دوال التغذية والحسابات
# ============================================================

def estimate_horse_weight(girth_cm, length_cm, breed_factor=1.0):
    """
    تقدير وزن الخيل بدقة حسب السلالة
    
    المعاملات:
        girth_cm (float): محيط الصدر
        length_cm (float): طول الجسم
        breed_factor (float): عامل تصحيح السلالة
    
    الإرجاع:
        float: الوزن التقديري
    """
    weight_factor = 11877
    return (girth_cm ** 2 * length_cm) / (weight_factor / breed_factor)

def calculate_horse_daily_feed(weight_kg, stage="خيول صيانة (بالغين)"):
    """
    حساب الاحتياج اليومي من المادة الجافة
    
    المعاملات:
        weight_kg (float): الوزن
        stage (str): مرحلة الإنتاج
    
    الإرجاع:
        float: الاحتياج اليومي
    """
    base_factor = 0.022
    
    # عوامل تعديل حسب المرحلة
    stage_factors = {
        "خيول رياضة ونشاط مكثف": 1.3,
        "أمهار نامية صغيرة": 1.2,
        "فرسات مرضعات": 1.4,
        "خيول صيانة (بالغين)": 1.0
    }
    
    factor = stage_factors.get(stage, 1.0)
    return weight_kg * base_factor * factor

def get_horse_nutrition_defaults(stage):
    """
    الحصول على الاحتياجات الغذائية الافتراضية
    
    المعاملات:
        stage (str): مرحلة الإنتاج
    
    الإرجاع:
        dict: الاحتياجات الغذائية
    """
    return HORSE_NUTRITIONAL_REQUIREMENTS.get(stage, HORSE_NUTRITIONAL_REQUIREMENTS["خيول صيانة (بالغين)"])

def analyze_horse_mixture(ingredients_dict):
    """
    تحليل خلطة علفية للخيول
    
    المعاملات:
        ingredients_dict (dict): المكونات والنسب
    
    الإرجاع:
        dict: نتائج التحليل
    """
    total_percent = sum(ingredients_dict.values())
    if abs(total_percent - 100) > 0.01:
        return {"error": f"مجموع النسب يجب أن يساوي 100% (الحالي: {total_percent:.1f}%)"}
    
    total_cp = 0.0
    total_dp = 0.0
    total_se = 0.0
    total_ndf = 0.0
    total_cost = 0.0
    
    results = {}
    
    for ingredient, percent in ingredients_dict.items():
        pct = percent / 100
        found = False
        
        for category in HORSE_FEEDS_LIBRARY.values():
            if ingredient in category:
                data = category[ingredient]
                ing_cp = data.get("CP", 0.0)
                ing_dc = data.get("DC", 0.0)
                ing_se = data.get("SE", 0.0)
                ing_ndf = data.get("NDF", 0.0)
                ing_price = data.get("سعر", 0.0)
                
                total_cp += pct * ing_cp
                total_dp += pct * (ing_cp * ing_dc)
                total_se += pct * ing_se
                total_ndf += pct * ing_ndf
                total_cost += pct * ing_price
                
                results[ingredient] = {
                    "percent": percent,
                    "cp": ing_cp,
                    "dc": ing_dc,
                    "se": ing_se,
                    "ndf": ing_ndf,
                    "cost": ing_price
                }
                found = True
                break
        
        if not found:
            results[ingredient] = {"percent": percent, "warning": "غير موجود في المكتبة"}
    
    # تقييم الخلطة
    recommendations = []
    status = "✅ ممتاز"
    
    if total_dp < 9.0:
        recommendations.append("⚠️ البروتين منخفض - أضف كسب فول صويا")
        status = "⚠️ يحتاج تحسين"
    elif total_dp > 14.0:
        recommendations.append("ℹ️ البروتين مرتفع - للخيول الرياضية فقط")
    
    if total_se < 55.0:
        recommendations.append("⚠️ الطاقة منخفضة - زد نسبة الذرة أو الشعير")
        status = "⚠️ يحتاج تحسين"
    
    if total_ndf > 25.0:
        recommendations.append("⚠️ الألياف مرتفعة - قد تؤثر على الهضم")
    
    # نسبة البروتين إلى الطاقة
    nutritive_ratio = total_se / total_dp if total_dp > 0 else 0
    
    return {
        "total_percent": total_percent,
        "cp_percent": total_cp,
        "dp_percent": total_dp,
        "se_percent": total_se,
        "ndf_percent": total_ndf,
        "nutritive_ratio": nutritive_ratio,
        "cost_per_ton": total_cost * 10,
        "recommendations": recommendations,
        "status": status,
        "details": results
    }

def optimize_horse_mixture(ingredients, prices, target_dp, target_se, fixed_additives=None):
    """
    محرك تحسين الخلطات باستخدام البرمجة الخطية
    
    المعاملات:
        ingredients (list): قائمة المكونات
        prices (dict): أسعار المكونات
        target_dp (float): البروتين المستهدف
        target_se (float): الطاقة المستهدفة
        fixed_additives (dict): الإضافات الإلزامية
    
    الإرجاع:
        dict: النتائج
    """
    try:
        from scipy.optimize import linprog
        
        if fixed_additives is None:
            fixed_additives = HORSE_FIXED_ADDITIVES
        
        ing_list = list(ingredients.keys())
        c = [prices.get(ing, 100.0) for ing in ing_list]
        
        # قيود المساواة: مجموع النسب = 100%
        A_eq = [[1.0 for _ in ing_list]]
        b_eq = [100.0]
        
        # قيود البروتين والطاقة
        dp_row = []
        se_row = []
        
        for ing in ing_list:
            found = False
            for category in HORSE_FEEDS_LIBRARY.values():
                if ing in category:
                    data = category[ing]
                    cp = data.get("CP", 0.0)
                    dc = data.get("DC", 0.0)
                    se = data.get("SE", 0.0)
                    dp_row.append(cp * dc)
                    se_row.append(se)
                    found = True
                    break
            if not found:
                dp_row.append(0.0)
                se_row.append(0.0)
        
        A_eq.append(dp_row)
        b_eq.append(target_dp * 100.0)
        
        # قيد الطاقة: SE >= target_se
        A_ub = [[-1.0 * x for x in se_row]]
        b_ub = [-1.0 * target_se * 100.0]
        
        # قيد الألياف
        ndf_row = []
        for ing in ing_list:
            found = False
            for category in HORSE_FEEDS_LIBRARY.values():
                if ing in category:
                    ndf = category[ing].get("NDF", 0.0)
                    ndf_row.append(ndf)
                    found = True
                    break
            if not found:
                ndf_row.append(0.0)
        A_ub.append(ndf_row)
        b_ub.append(28.0)
        
        # حدود المكونات
        bounds = []
        for ing in ing_list:
            if ing in fixed_additives:
                bounds.append((fixed_additives[ing], fixed_additives[ing]))
            else:
                bounds.append((0.0, 100.0))
        
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if res.success:
            formula = {}
            for idx, ing in enumerate(ing_list):
                if res.x[idx] > 0.001:
                    formula[ing] = res.x[idx]
            cost = res.fun / 100.0
            
            return {
                "success": True,
                "formula": formula,
                "cost": cost,
                "message": "تم الحل بنجاح"
            }
        else:
            return {
                "success": False,
                "message": "تعذر إيجاد حل رياضي. حاول إضافة المزيد من المكونات."
            }
            
    except ImportError:
        return {
            "success": False,
            "message": "مكتبة scipy غير مثبتة. يرجى تثبيتها: pip install scipy"
        }

# ============================================================
# 5. دوال واجهة المستخدم
# ============================================================

def render_genetics_and_breeding():
    """عرض واجهة الوراثة والتهجين"""
    st.markdown("### 🧬 نظام الوراثة والتهجين المتقدم")
    
    genetics = HorseGenetics()
    
    # اختيار السلالات
    col1, col2 = st.columns(2)
    
    with col1:
        breed1 = st.selectbox("🐎 السلالة الأبوية الأولى:", list(HORSE_BREEDS_DATABASE.keys()))
        st.info(f"**{breed1}**\n\n{genetics.breeds_db[breed1]['الوصف']}")
    
    with col2:
        breed2 = st.selectbox("🐎 السلالة الأبوية الثانية:", list(HORSE_BREEDS_DATABASE.keys()))
        st.info(f"**{breed2}**\n\n{genetics.breeds_db[breed2]['الوصف']}")
    
    # عرض معلومات السلالات
    if st.button("🔍 تحليل التهجين والوراثة", type="primary", use_container_width=True):
        st.markdown("---")
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            st.markdown("#### 🧬 النتائج الجينية")
            
            # التنبؤ بمواصفات الناتج
            offspring = genetics.predict_offspring_characteristics(breed1, breed2)
            
            if "error" not in offspring:
                # عرض المواصفات المتوقعة
                st.markdown("##### 📏 المواصفات المتوقعة:")
                
                height = offspring["الارتفاع المتوقع (سم)"]
                st.metric("الارتفاع (الذكر)", f"{height['الذكر'][0]:.0f}-{height['الذكر'][1]:.0f} سم")
                st.metric("الارتفاع (الأنثى)", f"{height['الأنثى'][0]:.0f}-{height['الأنثى'][1]:.0f} سم")
                
                weight = offspring["الوزن المتوقع (كجم)"]
                st.metric("الوزن (الذكر)", f"{weight['الذكر'][0]:.0f}-{weight['الذكر'][1]:.0f} كجم")
                st.metric("الوزن (الأنثى)", f"{weight['الأنثى'][0]:.0f}-{weight['الأنثى'][1]:.0f} كجم")
                
                # الألوان
                st.markdown("##### 🎨 الألوان المحتملة:")
                st.write(", ".join(offspring["الألوان المحتملة"][:5]))
                
                # الجينات
                st.markdown("##### 🧬 الجينات السائدة المتوقعة:")
                for gene in offspring["الجينات السائدة المتوقعة"]:
                    st.success(f"✅ {gene}")
                
                st.markdown("##### 🧬 الجينات المتنحية المتوقعة:")
                for gene in offspring["الجينات المتنحية المتوقعة"]:
                    st.warning(f"⚠️ {gene}")
                
                # قوة الهجين
                st.info(f"💪 قوة الهجين: {offspring['قوة الهجين المتوقعة']}")
                
                # الاستخدامات
                st.markdown("##### 🎯 الاستخدامات المقترحة:")
                for use in offspring["الاستخدامات المقترحة"]:
                    st.markdown(f"- {use}")
                
                # التغذية
                st.markdown("##### 🍽️ التوصيات الغذائية:")
                st.info(offspring["التوصيات الغذائية"])
        
        with col2:
            # عرض الصفات الموروثة
            st.markdown("#### 📊 الصفات الموروثة")
            
            traits = offspring["الصفات الموروثة"]
            
            # رسم بياني للصفات
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(traits.values()),
                theta=list(traits.keys()),
                fill='toself',
                name='الصفات الموروثة',
                line_color='#2e7d32'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                height=400,
                title="مخطط الصفات الموروثة"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # مقارنة السلالات
            st.markdown("#### 🔍 مقارنة السلالات")
            
            comparison = genetics.compare_breeds(breed1, breed2)
            
            if "error" not in comparison:
                st.metric("نسبة التشابه", f"{comparison['التشابه']:.1f}%")
                st.metric("نسبة الاختلاف", f"{comparison['الاختلاف']:.1f}%")
                
                # عرض مقارنة الصفات
                traits_comp = comparison["مقارنة الصفات"]
                for trait, values in traits_comp.items():
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric(f"{trait} - {breed1}", f"{values[breed1]:.1f}")
                    with col_b:
                        st.metric(f"{trait} - {breed2}", f"{values[breed2]:.1f}")
                    with col_c:
                        diff = values["الفرق"]
                        color = "green" if diff < 1 else "orange" if diff < 2 else "red"
                        st.metric("الفرق", f"{diff:.1f}", delta_color=color)

def render_breeds_database():
    """عرض قاعدة بيانات السلالات"""
    st.markdown("### 🐎 قاعدة بيانات سلالات الخيول")
    
    # اختيار السلالة
    breed = st.selectbox("اختر السلالة:", list(HORSE_BREEDS_DATABASE.keys()))
    
    if breed:
        data = HORSE_BREEDS_DATABASE[breed]
        
        col1, col2 = st.columns([0.6, 0.4])
        
        with col1:
            st.markdown(f"#### 📋 معلومات {breed}")
            st.markdown(f"**الوصف:** {data['الوصف']}")
            st.markdown(f"**الموطن الأصلي:** {data['الموطن الأصلي']}")
            
            st.markdown("##### 📏 القياسات:")
            st.metric("الارتفاع (الذكر)", f"{data['الارتفاع (سم)']['الذكر']} سم")
            st.metric("الارتفاع (الأنثى)", f"{data['الارتفاع (سم)']['الأنثى']} سم")
            st.metric("الوزن (الذكر)", f"{data['الوزن (كجم)']['الذكر']} كجم")
            st.metric("الوزن (الأنثى)", f"{data['الوزن (كجم)']['الأنثى']} كجم")
            
            st.markdown("##### 🎨 الألوان:")
            st.write(", ".join(data['الألوان']))
            
            st.markdown("##### 🎯 الاستخدامات:")
            for use in data['الاستخدامات']:
                st.markdown(f"- {use}")
            
            st.markdown("##### 🍽️ النظام الغذائي:")
            st.info(data['نظام غذائي خاص'])
        
        with col2:
            st.markdown("##### 📊 تقييم الصفات")
            
            # رسم بياني للصفات
            traits = data['الصفات']
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=list(traits.values()),
                theta=list(traits.keys()),
                fill='toself',
                name=breed,
                line_color='#1b5e20'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                height=350,
                title=f"صفات {breed}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("##### 🧬 الجينات:")
            st.markdown("**السائدة:**")
            for gene in data['الجينات السائدة']:
                st.success(f"✅ {gene}")
            
            st.markdown("**المتنحية:**")
            for gene in data['الجينات المتنحية']:
                st.warning(f"⚠️ {gene}")
            
            st.markdown("##### 🏥 الأمراض الشائعة:")
            for disease in data['الأمراض الشائعة']:
                st.markdown(f"- {disease}")

def render_horse_formulation():
    """عرض واجهة تركيب العلف للخيول"""
    st.markdown("### 🎯 تركيب علفة الخيول المثالية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # اختيار المرحلة
        stage = st.selectbox(
            "📋 مرحلة الإنتاج:",
            list(HORSE_NUTRITIONAL_REQUIREMENTS.keys())
        )
        
        # عرض الاحتياجات
        needs = get_horse_nutrition_defaults(stage)
        st.info(f"""
        **الاحتياجات الغذائية:**
        - البروتين المهضوم: {needs['DP']}%
        - معادل النشاء: {needs['SE']}
        - الكالسيوم: {needs['كالسيوم']}%
        - الفسفور: {needs['فسفور']}%
        - {needs['ملاحظات']}
        """)
    
    with col2:
        # القياسات الجسدية
        st.markdown("#### 📏 القياسات الجسدية")
        girth = st.number_input("محيط الصدر (سم):", 50.0, 300.0, 150.0)
        length = st.number_input("طول الجسم (سم):", 50.0, 300.0, 130.0)
        
        # اختيار السلالة للتعديل
        breed_for_weight = st.selectbox(
            "السلالة (لتعديل الوزن):",
            ["عام"] + list(HORSE_BREEDS_DATABASE.keys())
        )
        
        # حساب الوزن
        breed_factor = 1.0
        if breed_for_weight != "عام":
            # تقدير عامل التصحيح بناءً على السلالة
            avg_height = HORSE_BREEDS_DATABASE[breed_for_weight]["الارتفاع (سم)"]["الذكر"]
            breed_factor = avg_height / 155  # مقارنة بالمتوسط
        
        estimated_weight = estimate_horse_weight(girth, length, breed_factor)
        daily_feed = calculate_horse_daily_feed(estimated_weight, stage)
        
        st.success(f"""
        **الوزن التقديري:** {estimated_weight:.0f} كجم
        **الاحتياج اليومي:** {daily_feed:.2f} كجم مادة جافة
        """)
    
    # اختيار المكونات
    st.markdown("---")
    st.markdown("#### 📦 اختيار المكونات")
    
    selected_ingredients = {}
    ingredient_prices = {}
    
    # إضافة المكونات الإلزامية
    for additive, pct in HORSE_FIXED_ADDITIVES.items():
        selected_ingredients[additive] = pct
        ingredient_prices[additive] = 100.0
    
    # عرض المكونات الاختيارية
    for category_name, items in HORSE_FEEDS_LIBRARY.items():
        with st.expander(f"📁 {category_name}", expanded="الحبوب" in category_name):
            cols = st.columns(3)
            for idx, (ing_name, data) in enumerate(items.items()):
                with cols[idx % 3]:
                    is_default = ing_name in ["ذرة صفراء", "شعير مطحون", "كسب فول صويا 44%"]
                    checked = st.checkbox(ing_name, value=is_default, key=f"feed_{ing_name}")
                    if checked:
                        price = st.number_input(
                            f"سعر {ing_name} ($/طن)",
                            min_value=10.0,
                            max_value=2000.0,
                            value=data.get("سعر", 300.0),
                            step=10.0,
                            key=f"price_{ing_name}"
                        )
                        selected_ingredients[ing_name] = 0.0
                        ingredient_prices[ing_name] = price
    
    # تشغيل المحرك
    if st.button("🚀 تشغيل محرك التركيب", type="primary", use_container_width=True):
        with st.spinner("🔄 جاري حساب الخلطة المثلى..."):
            target_dp = needs['DP']
            target_se = needs['SE']
            
            result = optimize_horse_mixture(
                selected_ingredients,
                ingredient_prices,
                target_dp,
                target_se
            )
            
            if result["success"]:
                st.success("✅ تم حساب الخلطة المثلى بنجاح!")
                
                col1, col2 = st.columns([0.6, 0.4])
                
                with col1:
                    st.markdown("#### 📝 المقادير المعتمدة (كجم/طن):")
                    for ingredient, percent in result["formula"].items():
                        st.markdown(
                            f'<div style="background: linear-gradient(135deg, #f5f5f5, #e8f5e9); '
                            f'padding: 10px 15px; border-radius: 8px; margin-bottom: 5px; '
                            f'border-right: 4px solid #2e7d32;">'
                            f'▪️ <b>{ingredient}:</b> {percent:.2f}% ➡️ ({percent*10:.1f} كجم/طن)'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    
                    st.metric("💰 التكلفة الإجمالية للطن", f"${result['cost']:.2f}")
                    
                    # تحليل الخلطة
                    analysis = analyze_horse_mixture(result["formula"])
                    if "error" not in analysis:
                        st.markdown("#### 🔬 تحليل الخلطة:")
                        col_an1, col_an2, col_an3, col_an4 = st.columns(4)
                        with col_an1:
                            st.metric("البروتين المهضوم", f"{analysis['dp_percent']:.2f}%")
                        with col_an2:
                            st.metric("معادل النشاء", f"{analysis['se_percent']:.2f}")
                        with col_an3:
                            st.metric("النسبة الغذائية", f"{analysis['nutritive_ratio']:.2f}")
                        with col_an4:
                            st.metric("التكلفة/طن", f"${analysis['cost_per_ton']:.2f}")
                        
                        if analysis["recommendations"]:
                            st.warning("⚠️ التوصيات:")
                            for rec in analysis["recommendations"]:
                                st.markdown(f"- {rec}")
                
                with col2:
                    # رسم بياني
                    fig = px.pie(
                        values=list(result["formula"].values()),
                        names=list(result["formula"].keys()),
                        title="توزيع مكونات الخلطة",
                        color_discrete_sequence=px.colors.sequential.Greens
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.metric("حالة الخلطة", analysis.get("status", "✅ ممتاز") if "error" not in analysis else "⚠️")
                    
                    if analysis.get("nutritive_ratio", 0) > 0:
                        ratio_status = "متوازن" if 5 < analysis['nutritive_ratio'] < 7 else "غير متوازن"
                        st.metric("توازن الطاقة/البروتين", ratio_status)
            else:
                st.error(f"❌ {result['message']}")

def render_horse_analysis():
    """عرض واجهة تحليل الخلطات"""
    st.markdown("### 🔬 مختبر تحليل خلطات الخيول")
    
    st.markdown("#### 📦 أدخل نسب المكونات")
    
    ingredient_values = {}
    cols = st.columns(3)
    idx = 0
    
    for category in HORSE_FEEDS_LIBRARY.values():
        for ing_name in category.keys():
            with cols[idx % 3]:
                ingredient_values[ing_name] = st.number_input(
                    f"{ing_name} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.5,
                    key=f"analyze_{ing_name}"
                )
            idx += 1
    
    # الإضافات الإلزامية
    st.markdown("#### 🧪 الإضافات الإلزامية")
    add_cols = st.columns(3)
    add_idx = 0
    additive_values = {}
    for additive, default_pct in HORSE_FIXED_ADDITIVES.items():
        with add_cols[add_idx % 3]:
            additive_values[additive] = st.number_input(
                f"{additive} (%)",
                min_value=0.0,
                max_value=5.0,
                value=default_pct,
                step=0.1,
                key=f"analyze_add_{additive}"
            )
        add_idx += 1
    
    all_ingredients = {**ingredient_values, **additive_values}
    
    if st.button("🧪 تشغيل التحليل", type="primary", use_container_width=True):
        active = {k: v for k, v in all_ingredients.items() if v > 0}
        
        if not active:
            st.warning("⚠️ الرجاء إدخال نسب المكونات")
        else:
            total = sum(active.values())
            if abs(total - 100) > 1:
                st.warning(f"⚠️ مجموع النسب = {total:.1f}% (يجب أن يكون 100%)")
            
            normalized = {k: (v / total * 100) for k, v in active.items()}
            result = analyze_horse_mixture(normalized)
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ تم تحليل الخلطة بنجاح!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 نتائج التحليل:")
                    st.metric("البروتين الخام (CP)", f"{result['cp_percent']:.2f}%")
                    st.metric("البروتين المهضوم (DP)", f"{result['dp_percent']:.2f}%")
                    st.metric("معادل النشاء (SE)", f"{result['se_percent']:.2f}")
                    st.metric("الألياف (NDF)", f"{result['ndf_percent']:.2f}%")
                    st.metric("النسبة الغذائية", f"{result['nutritive_ratio']:.2f}")
                    st.metric("التكلفة/طن", f"${result['cost_per_ton']:.2f}")
                
                with col2:
                    st.markdown("#### 📋 تفاصيل المكونات:")
                    for ing, pct in normalized.items():
                        if pct > 0:
                            detail = result["details"].get(ing, {})
                            if "warning" in detail:
                                st.warning(f"⚠️ {ing}: {detail['warning']}")
                            else:
                                st.info(f"📌 {ing}: {pct:.1f}%")
                    
                    if result["recommendations"]:
                        st.markdown("#### 💡 التوصيات:")
                        for rec in result["recommendations"]:
                            st.markdown(f"- {rec}")
                    
                    st.metric("حالة الخلطة", result["status"])
                
                # رسم بياني
                if len(normalized) > 1:
                    fig = px.bar(
                        x=list(normalized.keys()),
                        y=list(normalized.values()),
                        labels={'x': 'المكون', 'y': 'النسبة (%)'},
                        title="توزيع المكونات",
                        color_discrete_sequence=['#2e7d32']
                    )
                    st.plotly_chart(fig, use_container_width=True)

def render_references():
    """عرض المراجع العلمية"""
    st.markdown("### 📚 المراجع العلمية لتغذية ووراثة الخيول")
    
    references = [
        {
            "title": "Nutrient Requirements of Horses",
            "authors": "NRC (National Research Council)",
            "year": 2007,
            "publisher": "National Academies Press",
            "summary": "المرجع الأساسي في تغذية الخيول ومتطلباتها الغذائية."
        },
        {
            "title": "Equine Nutrition and Feeding",
            "authors": "Frape, D.",
            "year": 2010,
            "publisher": "Wiley-Blackwell",
            "summary": "دليل شامل لتغذية الخيول في جميع مراحل الإنتاج."
        },
        {
            "title": "Horse Breeding and Genetics",
            "authors": "Cunningham, E.P.",
            "year": 2005,
            "publisher": "Equine Research Centre",
            "summary": "مرجع متخصص في وراثة وتهجين الخيول."
        },
        {
            "title": "Equine Science",
            "authors": "Parker, R.",
            "year": 2012,
            "publisher": "Cengage Learning",
            "summary": "العلوم الأساسية للخيول من تشريح إلى تغذية."
        }
    ]
    
    for ref in references:
        with st.expander(f"📖 {ref['title']} ({ref['year']})"):
            st.markdown(f"**المؤلفون:** {ref['authors']}")
            st.markdown(f"**الناشر:** {ref['publisher']}")
            st.markdown(f"**ملخص:** {ref['summary']}")

# ============================================================
# 6. الدالة الرئيسية للوحدة
# ============================================================

def render_horse_module():
    """
    الدالة الرئيسية لوحدة الخيول المتكاملة
    """
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #16213e); 
         padding: 25px; border-radius: 15px; border-right: 5px solid #e2b714; 
         margin-bottom: 30px; text-align: right;'>
        <h1 style='color: #e2b714;'>🐎 وحدة الخيول والفروسية المتكاملة</h1>
        <p style='color: #ffffff;'>نظام متقدم للوراثة والتهجين وتغذية الخيول</p>
        <p style='color: #aaaaaa; font-size: 0.9rem;'>
            المشرف: الاختصاصي م. عبد القادر إسماعيل تاور
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # تبويبات الوحدة
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧬 الوراثة والتهجين",
        "🐎 السلالات",
        "🎯 تركيب العلف",
        "🔬 تحليل الخلطات",
        "📚 المراجع"
    ])
    
    with tab1:
        render_genetics_and_breeding()
    
    with tab2:
        render_breeds_database()
    
    with tab3:
        render_horse_formulation()
    
    with tab4:
        render_horse_analysis()
    
    with tab5:
        render_references()

# ============================================================
# 7. نقطة الدخول للتطبيق المستقل
# ============================================================

def main():
    """
    نقطة الدخول الرئيسية للتطبيق المستقل
    """
    st.set_page_config(
        page_title="وحدة الخيول المتكاملة - منصة تاور",
        page_icon="🐎",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    render_horse_module()

if __name__ == "__main__":
    main()

# ============================================================
# نهاية الوحدة
# ============================================================
