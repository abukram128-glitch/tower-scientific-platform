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
APP_VERSION = "3.1.0"

def generate_license_hash():
    return hashlib.sha256(f"{SECURITY_KEY}_{datetime.now().year}".encode()).hexdigest()[:16]

# ==========================================
# 2. نظام إدارة المزارع (Database)
# ==========================================
class FarmManagementSystem:
    """نظام متكامل لإدارة المزارع مع حفظ البيانات"""
    
    def __init__(self):
        self.farms_file = "farms_data.pkl"
        self.current_user = None
        self.load_data()
    
    def load_data(self):
        """تحميل بيانات المزارع من الملف"""
        try:
            if os.path.exists(self.farms_file):
                with open(self.farms_file, 'rb') as f:
                    self.farms_data = pickle.load(f)
            else:
                self.farms_data = {}
        except:
            self.farms_data = {}
    
    def save_data(self):
        """حفظ بيانات المزارع"""
        try:
            with open(self.farms_file, 'wb') as f:
                pickle.dump(self.farms_data, f)
            return True
        except:
            return False
    
    def register_farm(self, owner_name, farm_name, farm_type, location, contact):
        """تسجيل مزرعة جديدة"""
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
            "financial_records": [],
            "breeding_records": []
        }
        self.save_data()
        return farm_id
    
    def add_animal(self, farm_id, animal_data):
        """إضافة حيوان إلى المزرعة"""
        if farm_id in self.farms_data:
            animal_id = hashlib.md5(f"{animal_data['name']}_{datetime.now()}".encode()).hexdigest()[:6]
            animal_data["id"] = animal_id
            animal_data["added_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.farms_data[farm_id]["animals"][animal_id] = animal_data
            self.save_data()
            return animal_id
        return None
    
    def add_production_record(self, farm_id, record):
        """إضافة سجل إنتاجي"""
        if farm_id in self.farms_data:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            record["time"] = datetime.now().strftime("%H:%M:%S")
            self.farms_data[farm_id]["production_records"].append(record)
            self.save_data()
            return True
        return False
    
    def add_feed_record(self, farm_id, record):
        """إضافة سجل تغذية"""
        if farm_id in self.farms_data:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            self.farms_data[farm_id]["feed_records"].append(record)
            self.save_data()
            return True
        return False
    
    def add_health_record(self, farm_id, record):
        """إضافة سجل صحي"""
        if farm_id in self.farms_data:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            self.farms_data[farm_id]["health_records"].append(record)
            self.save_data()
            return True
        return False
    
    def add_financial_record(self, farm_id, record):
        """إضافة سجل مالي"""
        if farm_id in self.farms_data:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            self.farms_data[farm_id]["financial_records"].append(record)
            self.save_data()
            return True
        return False
    
    def add_breeding_record(self, farm_id, record):
        """إضافة سجل تربية"""
        if farm_id in self.farms_data:
            record["date"] = datetime.now().strftime("%Y-%m-%d")
            self.farms_data[farm_id]["breeding_records"].append(record)
            self.save_data()
            return True
        return False
    
    def get_farm_data(self, farm_id):
        """جلب بيانات مزرعة معينة"""
        return self.farms_data.get(farm_id, None)
    
    def get_all_farms(self):
        """جلب جميع المزارع"""
        return self.farms_data
    
    def delete_farm(self, farm_id):
        """حذف مزرعة"""
        if farm_id in self.farms_data:
            del self.farms_data[farm_id]
            self.save_data()
            return True
        return False

# ==========================================
# 3. محرك الوراثة العلمي المُدقق
# ==========================================
class GeneticsEngine:
    
    @staticmethod
    def calculate_punnett_square(sire_genotype, dam_genotype, gene_info):
        """
        حساب مربع بونيت باستخدام المعادلات الوراثية المعترف بها
        وفقاً لقوانين مندل للوراثة
        """
        # تحليل الطرز الجينية وفقاً للأليلات
        sire_alleles = [sire_genotype[0], sire_genotype[1]]
        dam_alleles = [dam_genotype[0], dam_genotype[1]]
        
        # حساب جميع الاحتمالات الجينية
        offspring_genotypes = []
        for s in sire_alleles:
            for d in dam_alleles:
                # ترتيب الأليلات حسب السيادة (الأليل السائد أولاً)
                if s.isupper() or d.isupper():
                    sorted_alleles = "".join(sorted([s, d], key=lambda x: (x.islower(), x)))
                else:
                    sorted_alleles = "".join(sorted([s, d]))
                offspring_genotypes.append(sorted_alleles)
        
        # حساب النسب الجينية المتوقعة
        genotype_counts = pd.Series(offspring_genotypes).value_counts(normalize=True) * 100
        
        # حساب النسب المظهرية وفقاً لنمط السيادة
        phenotype_results = {}
        for geno, prob in genotype_counts.items():
            # تحديد الطراز المظهري حسب النمط الوراثي
            if gene_info["inheritance"] == "Complete":
                # سيادة تامة: وجود أليل سائد واحد كافٍ لإظهار الصفة السائدة
                if gene_info["dominant_allele"] in geno:
                    pheno = gene_info["dominant_trait"]
                else:
                    pheno = gene_info["recessive_trait"]
            elif gene_info["inheritance"] == "Incomplete":
                # سيادة غير تامة: النمط الخليط يعطي طرازاً وسطاً
                if geno == gene_info["dominant_allele"] * 2:
                    pheno = gene_info["dominant_trait"]
                elif geno == gene_info["recessive_allele"] * 2:
                    pheno = gene_info["recessive_trait"]
                else:
                    pheno = gene_info["intermediate_trait"]
            elif gene_info["inheritance"] == "Codominance":
                # سيادة مشتركة: ظهور كلا الصفتين معاً
                if gene_info["dominant_allele"] in geno and gene_info["recessive_allele"] in geno:
                    pheno = gene_info["codominant_trait"]
                elif geno == gene_info["dominant_allele"] * 2:
                    pheno = gene_info["dominant_trait"]
                else:
                    pheno = gene_info["recessive_trait"]
            
            phenotype_results[pheno] = phenotype_results.get(pheno, 0.0) + prob
            
        return genotype_counts.to_dict(), phenotype_results, offspring_genotypes

    @staticmethod
    def calculate_ebv(performance, population_mean, heritability, phenotypic_std=None):
        """
        حساب القيمة التربوية المقدرة (EBV)
        المعادلة: EBV = h² × (P - P̄)
        حيث:
        h²: المكافئ الوراثي
        P: أداء الفرد
        P̄: متوسط أداء القطيع
        """
        if phenotypic_std is None:
            return heritability * (performance - population_mean)
        else:
            # حساب القيمة التربوية مع الانحراف المعياري
            z_score = (performance - population_mean) / phenotypic_std
            return heritability * z_score * phenotypic_std
    
    @staticmethod
    def calculate_accuracy(heritability, offspring_count, record_type):
        """
        حساب دقة القيمة التربوية
        بناءً على عدد الأبناء ونوع السجل
        """
        if record_type == "individual":
            return np.sqrt(heritability)
        elif record_type == "siblings":
            return np.sqrt((offspring_count * heritability) / (1 + (offspring_count - 1) * heritability))
        elif record_type == "progeny":
            return np.sqrt((offspring_count * heritability) / (4 + (offspring_count - 1) * heritability))
        else:
            return np.sqrt(heritability)
    
    @staticmethod
    def calculate_selection_response(selection_intensity, heritability, phenotypic_std, generation_interval):
        """
        حساب الاستجابة للانتخاب (Selection Response)
        المعادلة: ΔG = i × h² × σp / L
        حيث:
        i: شدة الانتخاب
        h²: المكافئ الوراثي
        σp: الانحراف المعياري المظهري
        L: الفترة الجيلية
        """
        return (selection_intensity * heritability * phenotypic_std) / generation_interval
    
    @staticmethod
    def calculate_inbreeding_coefficient(population_size, effective_size=None):
        """
        حساب معامل التزاوج الداخلي (Inbreeding Coefficient)
        المعادلة: ΔF = 1 / (2 × Ne)
        حيث Ne هو الحجم الفعال للجماعة
        """
        if effective_size is None:
            effective_size = population_size * 0.7  # تقدير الحجم الفعال
        return 1 / (2 * effective_size)

# ==========================================
# 4. محرك التغذية العلمي المُدقق
# ==========================================
class NutritionEngine:
    """محرك التغذية العلمي المعتمد على المعادلات العالمية"""
    
    @staticmethod
    def calculate_energy_requirements(weight, production_level, temperature, animal_type):
        """
        حساب الاحتياجات الطاقية وفقاً لمعادلات NRC
        """
        if animal_type == "cattle":
            # معادلة NRC للأبقار الحلابة
            maintenance = 0.086 * weight**0.75  # Mcal
            production_energy = production_level * 0.74  # Mcal لكل كجم حليب
            temp_adjustment = (20 - temperature) * 0.0005 * weight  # تعديل درجة الحرارة
            return maintenance + production_energy + temp_adjustment
        
        elif animal_type == "poultry":
            # معادلة NRC للدواجن
            maintenance = 0.073 * weight**0.75  # Mcal
            production_energy = production_level * 0.0012  # Mcal لكل بيضة
            return maintenance + production_energy
        
        elif animal_type == "sheep":
            # معادلة NRC للأغنام
            maintenance = 0.093 * weight**0.75  # Mcal
            production_energy = production_level * 0.0025  # Mcal لكل كجم حليب
            return maintenance + production_energy
        
        else:
            return 0.1 * weight**0.75  # معادلة عامة
    
    @staticmethod
    def calculate_protein_requirements(weight, production_level, animal_type):
        """
        حساب الاحتياجات البروتينية وفقاً لمعادلات NRC
        """
        if animal_type == "cattle":
            maintenance = 0.005 * weight  # كجم بروتين خام
            production_protein = production_level * 0.033  # كجم بروتين لكل كجم حليب
            return maintenance + production_protein
        
        elif animal_type == "poultry":
            maintenance = 0.008 * weight
            production_protein = production_level * 0.0005  # كجم بروتين لكل بيضة
            return maintenance + production_protein
        
        elif animal_type == "sheep":
            maintenance = 0.006 * weight
            production_protein = production_level * 0.035
            return maintenance + production_protein
        
        else:
            return 0.01 * weight
    
    @staticmethod
    def calculate_feed_efficiency(feed_intake, weight_gain):
        """حساب كفاءة التحويل الغذائي (FCR)"""
        if weight_gain > 0:
            return feed_intake / weight_gain
        return np.inf
    
    @staticmethod
    def calculate_cost_per_kg_gain(feed_cost, feed_intake, weight_gain):
        """حساب تكلفة كيلوجرام الزيادة"""
        if weight_gain > 0:
            return (feed_cost * feed_intake) / weight_gain
        return np.inf

# ==========================================
# 5. نظام إدارة المزارع - الواجهة
# ==========================================
class FarmManagerUI:
    """واجهة إدارة المزارع"""
    
    def __init__(self):
        self.farm_system = FarmManagementSystem()
    
    def display_farm_dashboard(self):
        """عرض لوحة تحكم المزرعة"""
        st.subheader("🏡 لوحة تحكم إدارة المزارع")
        
        # اختيار المزرعة أو إنشاء جديدة
        farms = self.farm_system.get_all_farms()
        
        if farms:
            farm_options = [f"{data['farm_name']} - {data['owner']}" for data in farms.values()]
            selected_farm_label = st.selectbox("اختر مزرعة:", ["إنشاء مزرعة جديدة"] + farm_options)
            
            if selected_farm_label == "إنشاء مزرعة جديدة":
                self.create_farm_form()
            else:
                # العثور على ID المزرعة المختارة
                for fid, data in farms.items():
                    if f"{data['farm_name']} - {data['owner']}" == selected_farm_label:
                        self.display_farm_details(fid)
                        break
        else:
            st.info("لا توجد مزارع مسجلة. قم بإنشاء مزرعة جديدة:")
            self.create_farm_form()
    
    def create_farm_form(self):
        """نموذج إنشاء مزرعة جديدة"""
        with st.form("create_farm"):
            st.markdown("### 📝 تسجيل مزرعة جديدة")
            col1, col2 = st.columns(2)
            
            with col1:
                owner_name = st.text_input("اسم المالك:", placeholder="أدخل اسمك الكامل")
                farm_name = st.text_input("اسم المزرعة:", placeholder="أدخل اسم المزرعة")
                farm_type = st.selectbox("نوع المزرعة:", ["أبقار", "دواجن", "أغنام", "ماعز", "مختلط"])
            
            with col2:
                location = st.text_input("الموقع:", placeholder="المدينة/المنطقة")
                contact = st.text_input("رقم الاتصال:", placeholder="رقم الهاتف")
            
            submitted = st.form_submit_button("🚀 تسجيل المزرعة")
            
            if submitted:
                if owner_name and farm_name:
                    farm_id = self.farm_system.register_farm(owner_name, farm_name, farm_type, location, contact)
                    st.success(f"✅ تم تسجيل المزرعة بنجاح! معرف المزرعة: {farm_id}")
                    st.balloons()
                else:
                    st.error("⚠️ يرجى إدخال جميع البيانات المطلوبة")
    
    def display_farm_details(self, farm_id):
        """عرض تفاصيل المزرعة والإدارة"""
        farm_data = self.farm_system.get_farm_data(farm_id)
        
        if not farm_data:
            st.error("المزرعة غير موجودة")
            return
        
        # عرض المعلومات الأساسية
        st.markdown(f"""
        <div class="genetic-card">
            <h3>🏠 {farm_data['farm_name']}</h3>
            <p><strong>المالك:</strong> {farm_data['owner']}</p>
            <p><strong>النوع:</strong> {farm_data['farm_type']}</p>
            <p><strong>الموقع:</strong> {farm_data['location']}</p>
            <p><strong>تاريخ التسجيل:</strong> {farm_data['created_date']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # قائمة إدارة المزرعة
        management_tabs = st.tabs([
            "🐄 إدارة الحيوانات",
            "📊 السجلات الإنتاجية",
            "🌾 السجلات الغذائية",
            "🏥 السجلات الصحية",
            "💰 السجلات المالية",
            "🧬 سجلات التربية"
        ])
        
        with management_tabs[0]:
            self.manage_animals(farm_id)
        
        with management_tabs[1]:
            self.manage_production_records(farm_id)
        
        with management_tabs[2]:
            self.manage_feed_records(farm_id)
        
        with management_tabs[3]:
            self.manage_health_records(farm_id)
        
        with management_tabs[4]:
            self.manage_financial_records(farm_id)
        
        with management_tabs[5]:
            self.manage_breeding_records(farm_id)
    
    def manage_animals(self, farm_id):
        """إدارة الحيوانات في المزرعة"""
        st.markdown("#### 🐄 إدارة الحيوانات")
        
        # نموذج إضافة حيوان
        with st.expander("➕ إضافة حيوان جديد", expanded=True):
            with st.form("add_animal"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    animal_name = st.text_input("اسم/رقم الحيوان:")
                    animal_type = st.selectbox("النوع:", ["بقرة", "جاموس", "دجاجة", "خروف", "ماعز"])
                
                with col2:
                    breed = st.text_input("السلالة:")
                    gender = st.selectbox("الجنس:", ["ذكر", "أنثى"])
                
                with col3:
                    birth_date = st.date_input("تاريخ الميلاد:")
                    weight = st.number_input("الوزن (كجم):", 0.0, 1000.0, 50.0)
                
                notes = st.text_area("ملاحظات:")
                
                submitted = st.form_submit_button("💾 حفظ الحيوان")
                
                if submitted:
                    animal_data = {
                        "name": animal_name,
                        "type": animal_type,
                        "breed": breed,
                        "gender": gender,
                        "birth_date": birth_date.strftime("%Y-%m-%d"),
                        "weight": weight,
                        "notes": notes
                    }
                    animal_id = self.farm_system.add_animal(farm_id, animal_data)
                    if animal_id:
                        st.success(f"✅ تم إضافة الحيوان بنجاح! المعرف: {animal_id}")
                    else:
                        st.error("❌ فشل في إضافة الحيوان")
        
        # عرض الحيوانات المسجلة
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["animals"]:
            st.markdown("#### 📋 قائمة الحيوانات")
            animals_df = pd.DataFrame(farm_data["animals"]).T
            st.dataframe(animals_df, use_container_width=True)
            
            # إحصائيات الحيوانات
            st.markdown("#### 📊 إحصائيات القطيع")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("عدد الحيوانات", len(animals_df))
            with col2:
                total_weight = animals_df['weight'].sum() if 'weight' in animals_df else 0
                st.metric("الوزن الإجمالي", f"{total_weight:.1f} كجم")
            with col3:
                avg_weight = animals_df['weight'].mean() if 'weight' in animals_df else 0
                st.metric("متوسط الوزن", f"{avg_weight:.1f} كجم")
    
    def manage_production_records(self, farm_id):
        """إدارة السجلات الإنتاجية"""
        st.markdown("#### 📊 السجلات الإنتاجية")
        
        with st.form("add_production"):
            col1, col2 = st.columns(2)
            
            with col1:
                record_type = st.selectbox("نوع السجل:", ["حليب", "بيض", "لحم", "صوف"])
                animal_id = st.text_input("معرف الحيوان (اختياري):")
            
            with col2:
                quantity = st.number_input("الكمية:", 0.0, 10000.0, 10.0)
                unit = st.selectbox("الوحدة:", ["كجم", "لتر", "عدد"])
            
            notes = st.text_area("ملاحظات:")
            
            submitted = st.form_submit_button("💾 حفظ السجل")
            
            if submitted:
                record = {
                    "type": record_type,
                    "animal_id": animal_id,
                    "quantity": quantity,
                    "unit": unit,
                    "notes": notes
                }
                if self.farm_system.add_production_record(farm_id, record):
                    st.success("✅ تم حفظ السجل الإنتاجي")
                else:
                    st.error("❌ فشل في حفظ السجل")
        
        # عرض السجلات السابقة
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["production_records"]:
            st.markdown("#### 📋 السجلات الإنتاجية السابقة")
            records_df = pd.DataFrame(farm_data["production_records"])
            st.dataframe(records_df, use_container_width=True)
    
    def manage_feed_records(self, farm_id):
        """إدارة السجلات الغذائية"""
        st.markdown("#### 🌾 السجلات الغذائية")
        
        with st.form("add_feed"):
            col1, col2 = st.columns(2)
            
            with col1:
                feed_type = st.selectbox("نوع العلف:", ["مركز", "مالئ", "مخلوط", "أعلاف خضراء"])
                feed_name = st.text_input("اسم العلف:")
            
            with col2:
                quantity = st.number_input("الكمية (كجم):", 0.0, 10000.0, 100.0)
                cost_per_kg = st.number_input("التكلفة لكل كجم:", 0.0, 100.0, 1.0)
            
            notes = st.text_area("ملاحظات:")
            
            submitted = st.form_submit_button("💾 حفظ السجل الغذائي")
            
            if submitted:
                record = {
                    "feed_type": feed_type,
                    "feed_name": feed_name,
                    "quantity": quantity,
                    "cost_per_kg": cost_per_kg,
                    "total_cost": quantity * cost_per_kg,
                    "notes": notes
                }
                if self.farm_system.add_feed_record(farm_id, record):
                    st.success("✅ تم حفظ السجل الغذائي")
                else:
                    st.error("❌ فشل في حفظ السجل")
        
        # عرض السجلات السابقة
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["feed_records"]:
            st.markdown("#### 📋 السجلات الغذائية السابقة")
            records_df = pd.DataFrame(farm_data["feed_records"])
            st.dataframe(records_df, use_container_width=True)
            
            # إجمالي التكاليف الغذائية
            total_feed_cost = records_df['total_cost'].sum() if 'total_cost' in records_df else 0
            st.metric("إجمالي تكاليف الأعلاف", f"${total_feed_cost:,.2f}")
    
    def manage_health_records(self, farm_id):
        """إدارة السجلات الصحية"""
        st.markdown("#### 🏥 السجلات الصحية")
        
        with st.form("add_health"):
            col1, col2 = st.columns(2)
            
            with col1:
                health_type = st.selectbox("نوع السجل:", ["فحص", "علاج", "تحصين", "جراحة"])
                animal_id = st.text_input("معرف الحيوان:")
            
            with col2:
                diagnosis = st.text_input("التشخيص:")
                treatment = st.text_input("العلاج:")
            
            notes = st.text_area("ملاحظات:")
            
            submitted = st.form_submit_button("💾 حفظ السجل الصحي")
            
            if submitted:
                record = {
                    "health_type": health_type,
                    "animal_id": animal_id,
                    "diagnosis": diagnosis,
                    "treatment": treatment,
                    "notes": notes
                }
                if self.farm_system.add_health_record(farm_id, record):
                    st.success("✅ تم حفظ السجل الصحي")
                else:
                    st.error("❌ فشل في حفظ السجل")
        
        # عرض السجلات السابقة
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["health_records"]:
            st.markdown("#### 📋 السجلات الصحية السابقة")
            records_df = pd.DataFrame(farm_data["health_records"])
            st.dataframe(records_df, use_container_width=True)
    
    def manage_financial_records(self, farm_id):
        """إدارة السجلات المالية"""
        st.markdown("#### 💰 السجلات المالية")
        
        with st.form("add_financial"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox("نوع المعاملة:", ["إيراد", "مصروف"])
                category = st.selectbox("الفئة:", ["مبيعات", "مشتريات", "رواتب", "صيانة", "أخرى"])
            
            with col2:
                amount = st.number_input("المبلغ:", 0.0, 1000000.0, 100.0)
                description = st.text_input("الوصف:")
            
            submitted = st.form_submit_button("💾 حفظ السجل المالي")
            
            if submitted:
                record = {
                    "transaction_type": transaction_type,
                    "category": category,
                    "amount": amount,
                    "description": description
                }
                if self.farm_system.add_financial_record(farm_id, record):
                    st.success("✅ تم حفظ السجل المالي")
                else:
                    st.error("❌ فشل في حفظ السجل")
        
        # عرض السجلات السابقة والتحليل المالي
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["financial_records"]:
            records_df = pd.DataFrame(farm_data["financial_records"])
            st.markdown("#### 📋 السجلات المالية السابقة")
            st.dataframe(records_df, use_container_width=True)
            
            # التحليل المالي
            income = records_df[records_df['transaction_type'] == 'إيراد']['amount'].sum()
            expenses = records_df[records_df['transaction_type'] == 'مصروف']['amount'].sum()
            net_profit = income - expenses
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي الإيرادات", f"${income:,.2f}")
            with col2:
                st.metric("إجمالي المصروفات", f"${expenses:,.2f}")
            with col3:
                st.metric("صافي الربح", f"${net_profit:,.2f}", 
                         delta=f"{net_profit/income*100:.1f}%" if income > 0 else None)
    
    def manage_breeding_records(self, farm_id):
        """إدارة سجلات التربية"""
        st.markdown("#### 🧬 سجلات التربية")
        
        with st.form("add_breeding"):
            col1, col2 = st.columns(2)
            
            with col1:
                sire_id = st.text_input("معرف الأب:")
                dam_id = st.text_input("معرف الأم:")
            
            with col2:
                breeding_date = st.date_input("تاريخ التلقيح:")
                expected_date = st.date_input("تاريخ الولادة المتوقع:")
            
            notes = st.text_area("ملاحظات:")
            
            submitted = st.form_submit_button("💾 حفظ سجل التربية")
            
            if submitted:
                record = {
                    "sire_id": sire_id,
                    "dam_id": dam_id,
                    "breeding_date": breeding_date.strftime("%Y-%m-%d"),
                    "expected_date": expected_date.strftime("%Y-%m-%d"),
                    "notes": notes
                }
                if self.farm_system.add_breeding_record(farm_id, record):
                    st.success("✅ تم حفظ سجل التربية")
                else:
                    st.error("❌ فشل في حفظ السجل")
        
        # عرض السجلات السابقة
        farm_data = self.farm_system.get_farm_data(farm_id)
        if farm_data and farm_data["breeding_records"]:
            st.markdown("#### 📋 سجلات التربية السابقة")
            records_df = pd.DataFrame(farm_data["breeding_records"])
            st.dataframe(records_df, use_container_width=True)

# ==========================================
# 6. تنسيق CSS والأمان
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
# 7. Banner الوالدين والدعاء
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
# 8. الواجهة الرئيسية
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
# 9. القوائم الجانبية
# ==========================================
st.sidebar.markdown("### 🌟 أروقة المنتدى المتطورة")
app_mode = st.sidebar.radio("اختر التطبيق:", [
    "🏡 إدارة المزارع",
    "🧬 الهندسة الوراثية المتقدمة",
    "🐔 تهجين الدواجن العالمي",
    "🌾 تركيب العلائق المتطور",
    "📊 دراسات الإحلال الاقتصادي",
    "📚 الموسوعة الوراثية للسلالات"
])

# ==========================================
# 10. تشغيل التطبيقات
# ==========================================
if "إدارة المزارع" in app_mode:
    farm_ui = FarmManagerUI()
    farm_ui.display_farm_dashboard()

elif "الهندسة الوراثية" in app_mode:
    # هنا يمكن إضافة محتوى الهندسة الوراثية من الكود السابق
    st.info("تم تطوير محرك الهندسة الوراثية وفقاً للمعادلات العلمية المعتمدة")
    # ... (باقي الكود السابق للهندسة الوراثية)

elif "تهجين الدواجن" in app_mode:
    st.info("نظام تهجين الدواجن العالمي المتقدم")
    # ... (باقي الكود السابق للتهجين)

elif "تركيب العلائق" in app_mode:
    st.info("نظام تركيب العلائق المتطور مع المعادلات العلمية")
    # ... (باقي الكود السابق لتركيب العلائق)

elif "الإحلال الاقتصادي" in app_mode:
    st.info("نظام دراسات الإحلال الاقتصادي المتقدم")
    # ... (باقي الكود السابق للإحلال الاقتصادي)

else:
    st.info("الموسوعة الوراثية للسلالات العالمية")
    # ... (باقي الكود السابق للموسوعة)

# ==========================================
# 11. أسفل الصفحة
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
        الإصدار 3.1.0 | جميع الحقوق محفوظة © 2024
    </div>
    <div style="font-size: 0.7rem; margin-top: 10px; color: #60A5FA; border-top: 1px solid #1E293B; padding-top: 10px;">
        <span style="color: #FCD34D;">🤲</span> 
        اللهم اجعل هذا العمل صدقة جارية لوالدي، واجعله في ميزان حسناتهما 
        <span style="color: #FCD34D;">🤲</span>
    </div>
</div>

<div class="security-badge">
    🔒 Secured v3.1 | License: {0}
</div>
""".format(generate_license_hash()), unsafe_allow_html=True)
