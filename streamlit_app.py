import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import sqlite3
import json
import hashlib
import secrets
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
import base64
import io
import urllib.parse
from enum import Enum

# ==========================================
# إعدادات الصفحة
# ==========================================

st.set_page_config(
    page_title="منصة تاور العلمية - للانتاج الحيواني وتركيب الاعلاف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# كلاسات البيانات
# ==========================================

class UserRole(Enum):
    OWNER = "owner"
    SPECIALIST = "specialist"
    BREEDER = "breeder"

class FeedCategory(Enum):
    GRAINS = "🌾 حبوب ومصادر طاقة"
    PROTEIN = "🥜 أكساب ومصادر بروتين"
    ANIMAL_PROTEIN = "🐟 بروتين حيواني"
    BYPRODUCTS = "🌾 مخلفات زراعية"
    MINERALS = "🧂 أملاح ومعادن"
    ADDITIVES = "💊 إضافات وإنزيمات"

class ProductionSector(Enum):
    POULTRY_BROILER = "دواجن لاحم"
    POULTRY_LAYER = "دواجن بياض"
    DAIRY_CATTLE = "أبقار حلابة"
    BEEF_CATTLE = "تسمين عجول"
    SHEEP_GOAT = "أغنام وماعز"
    HORSES = "خيول"
    FISH = "أسماك"
    GENERAL = "عام"

# ==========================================
# دوال الأمان والتشفير
# ==========================================

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """تشفير كلمة المرور باستخدام SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """التحقق من صحة كلمة المرور"""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)

# ==========================================
# إعدادات المستخدمين (بالعربي)
# ==========================================

USERS_CONFIG = {
    "تاور": {
        "username": "tower",
        "password": "202687",
        "role": UserRole.OWNER.value,
        "full_name": "الاختصاصي م. عبد القادر إسماعيل تاور",
        "title": "المالك والمدير العام 👑",
        "color": "#c62828"
    },
    "مختص": {
        "username": "specialist",
        "password": "2020",
        "role": UserRole.SPECIALIST.value,
        "full_name": "الطبيب البيطري / المختص",
        "title": "مختص تغذية حيوانية 👨‍🔬",
        "color": "#1565c0"
    },
    "مربي": {
        "username": "breeder",
        "password": "2026",
        "role": UserRole.BREEDER.value,
        "full_name": "المربي / صاحب المزرعة",
        "title": "مربي منتج 🌾",
        "color": "#2e7d32"
    }
}

# ==========================================
# إعدادات قاعدة البيانات
# ==========================================

DB_NAME = "tower_scientific.db"

def init_database():
    """تهيئة قاعدة البيانات بشكل آمن"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # جدول المواد العلفية
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            protein REAL DEFAULT 0,
            lysine REAL DEFAULT 0,
            methionine REAL DEFAULT 0,
            digestibility REAL DEFAULT 0.85,
            energy REAL DEFAULT 0,
            price REAL DEFAULT 0,
            stock REAL DEFAULT 0,
            max_limit REAL DEFAULT 100,
            min_limit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # جدول التركيبات
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS formulas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sector TEXT,
            ingredients TEXT,
            total_cost REAL,
            protein REAL,
            digestible_protein REAL,
            energy REAL,
            lysine REAL,
            methionine REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
        ''')
        
        # جدول المخزون (سجل الحركات)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_name TEXT,
            quantity REAL,
            operation TEXT,
            formula_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
        ''')
        
        # جدول التقارير
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            report_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT
        )
        ''')
        
        conn.commit()
        
        # إضافة المستخدمين إذا كانت قاعدة البيانات فارغة
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            for key, user in USERS_CONFIG.items():
                hashed, salt = hash_password(user["password"])
                cursor.execute('''
                    INSERT INTO users (username, password_hash, password_salt, role, full_name, title)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user["username"], hashed, salt, user["role"], user["full_name"], user["title"]))
            conn.commit()
        
        # إضافة المواد العلفية الافتراضية
        cursor.execute("SELECT COUNT(*) FROM feeds")
        if cursor.fetchone()[0] == 0:
            seed_feeds(cursor)
            conn.commit()
        
        return conn
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e

def seed_feeds(cursor):
    """إضافة المواد العلفية الافتراضية"""
    
    feeds_data = [
        # 🌾 الحبوب ومصادر الطاقة
        ("ذرة صفراء", FeedCategory.GRAINS.value, 8.5, 0.24, 0.17, 0.85, 80.0, 230, 100, 0, 25),
        ("ذرة بيضاء", FeedCategory.GRAINS.value, 8.8, 0.23, 0.16, 0.83, 78.0, 225, 100, 0, 25),
        ("شعير مطحون", FeedCategory.GRAINS.value, 11.5, 0.36, 0.19, 0.80, 71.0, 210, 100, 0, 25),
        ("سورجم (فتريتة)", FeedCategory.GRAINS.value, 10.0, 0.22, 0.15, 0.78, 70.0, 195, 100, 0, 25),
        ("قمح محلي", FeedCategory.GRAINS.value, 12.0, 0.32, 0.21, 0.85, 75.0, 240, 100, 0, 25),
        ("جريش أرز", FeedCategory.GRAINS.value, 7.8, 0.28, 0.20, 0.82, 82.0, 230, 100, 0, 25),
        ("دخن", FeedCategory.GRAINS.value, 11.0, 0.30, 0.22, 0.75, 68.0, 220, 100, 0, 25),
        ("شوفان", FeedCategory.GRAINS.value, 11.0, 0.40, 0.18, 0.76, 62.0, 230, 100, 0, 25),
        
        # 🥜 الأكساب ومصادر البروتين
        ("كسب فول صويا 44%", FeedCategory.PROTEIN.value, 44.0, 2.70, 0.62, 0.90, 74.0, 440, 100, 0, 20),
        ("كسب فول صويا 48%", FeedCategory.PROTEIN.value, 48.0, 2.90, 0.67, 0.91, 76.0, 480, 100, 0, 20),
        ("كسب عباد الشمس 36%", FeedCategory.PROTEIN.value, 36.0, 1.20, 0.75, 0.76, 42.0, 310, 100, 0, 20),
        ("أمباز الفول السوداني", FeedCategory.PROTEIN.value, 46.0, 1.60, 0.52, 0.88, 73.0, 460, 100, 0, 20),
        ("كسب بذور القطن", FeedCategory.PROTEIN.value, 41.0, 1.75, 0.64, 0.78, 55.0, 290, 100, 0, 20),
        ("كسب بذور الكتان", FeedCategory.PROTEIN.value, 32.0, 1.15, 0.60, 0.82, 65.0, 350, 100, 0, 20),
        ("كسب السمسم", FeedCategory.PROTEIN.value, 42.0, 1.25, 1.10, 0.84, 70.0, 380, 100, 0, 20),
        ("كسب جلوتين الذرة 60%", FeedCategory.PROTEIN.value, 60.0, 1.02, 1.45, 0.92, 85.0, 520, 100, 0, 20),
        
        # 🐟 بروتين حيواني
        ("مسحوق أسماك 60%", FeedCategory.ANIMAL_PROTEIN.value, 60.0, 4.50, 1.65, 0.85, 65.0, 850, 100, 0, 10),
        ("مسحوق أسماك 72%", FeedCategory.ANIMAL_PROTEIN.value, 72.0, 5.40, 2.10, 0.90, 72.0, 1050, 100, 0, 10),
        ("مسحوق لحم وعظم", FeedCategory.ANIMAL_PROTEIN.value, 50.0, 2.60, 0.70, 0.75, 50.0, 650, 100, 0, 10),
        
        # 🌾 مخلفات زراعية
        ("نخالة قمح (ردة)", FeedCategory.BYPRODUCTS.value, 15.0, 0.58, 0.23, 0.72, 45.0, 150, 100, 0, 15),
        ("برسيم جاف (دريس)", FeedCategory.BYPRODUCTS.value, 16.5, 0.75, 0.28, 0.60, 35.0, 170, 100, 0, 15),
        ("مولاس قصب السكر", FeedCategory.BYPRODUCTS.value, 4.0, 0.05, 0.02, 0.95, 50.0, 120, 100, 0, 15),
        ("تبن قمح", FeedCategory.BYPRODUCTS.value, 3.2, 0.08, 0.04, 0.35, 18.0, 80, 100, 0, 15),
        ("سيلاج ذرة", FeedCategory.BYPRODUCTS.value, 8.0, 0.22, 0.14, 0.68, 50.0, 180, 100, 0, 15),
        ("تفل البنجر المجفف", FeedCategory.BYPRODUCTS.value, 8.0, 0.42, 0.12, 0.75, 58.0, 230, 100, 0, 15),
        
        # 🧂 أملاح ومعادن
        ("ملح الطعام", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 30, 5, 0.5, 20),
        ("الحجر الجيري", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 40, 8, 0.5, 20),
        ("فوسفات ثنائي الكالسيوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 280, 3, 0.5, 20),
        ("بيكربونات الصوديوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 340, 2, 0.1, 20),
        ("أكسيد المغنيسيوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 230, 2, 0.1, 20),
        
        # 💊 إضافات وإنزيمات
        ("بريمكس دواجن لاحم", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25, 10),
        ("بريمكس دواجن بياض", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25, 10),
        ("بريمكس مجترات", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25, 10),
        ("إنزيم الفايتيز", FeedCategory.ADDITIVES.value, 0, 0, 0, 0.95, 0, 230, 0.5, 0.05, 10),
        ("إنزيم NSP", FeedCategory.ADDITIVES.value, 0, 0, 0, 0.90, 0, 230, 0.5, 0.05, 10),
        ("مضاد سموم فطرية", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 950, 0.5, 0.1, 10),
        ("مستخلص خمائر (MOS)", FeedCategory.ADDITIVES.value, 12.0, 0.30, 0.10, 0.50, 10.0, 350, 0.5, 0.1, 10),
        
        # 🧪 أحماض أمينية
        ("ليسين نقي (L-Lysine)", FeedCategory.ADDITIVES.value, 94.0, 78.0, 0, 1.00, 0, 230, 0.5, 0.05, 10),
        ("ميثيونين نقي (DL-Met)", FeedCategory.ADDITIVES.value, 58.0, 0, 99.0, 1.00, 0, 230, 0.5, 0.05, 10),
        ("ثريونين نقي", FeedCategory.ADDITIVES.value, 72.0, 0, 0, 1.00, 0, 230, 0.5, 0.05, 10),
    ]
    
    for feed in feeds_data:
        cursor.execute('''
            INSERT INTO feeds (name, category, protein, lysine, methionine, 
                             digestibility, energy, price, max_limit, min_limit, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', feed)

def get_all_feeds():
    """الحصول على جميع المواد العلفية"""
    conn = init_database()
    df = pd.read_sql_query("SELECT * FROM feeds ORDER BY category, name", conn)
    conn.close()
    return df

def update_stock(feed_name, quantity, operation="set", formula_name="", user=""):
    """تحديث المخزون مع تسجيل الحركة"""
    conn = init_database()
    cursor = conn.cursor()
    
    if operation == "set":
        cursor.execute("UPDATE feeds SET stock = ? WHERE name = ?", (quantity, feed_name))
    elif operation == "add":
        cursor.execute("UPDATE feeds SET stock = stock + ? WHERE name = ?", (quantity, feed_name))
    elif operation == "deduct":
        cursor.execute("UPDATE feeds SET stock = MAX(0, stock - ?) WHERE name = ?", (quantity, feed_name))
    
    # تسجيل الحركة
    cursor.execute('''
        INSERT INTO inventory_log (feed_name, quantity, operation, formula_name, created_by)
        VALUES (?, ?, ?, ?, ?)
    ''', (feed_name, quantity, operation, formula_name, user))
    
    conn.commit()
    conn.close()

def save_formula(name, sector, ingredients, cost, protein, digestible_protein, energy, lysine, methionine, user):
    """حفظ التركيبة"""
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO formulas (name, sector, ingredients, total_cost, protein, digestible_protein, energy, lysine, methionine, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, sector, json.dumps(ingredients), cost, protein, digestible_protein, energy, lysine, methionine, user))
    conn.commit()
    formula_id = cursor.lastrowid
    conn.close()
    return formula_id

def get_formulas(limit=100):
    """الحصول على التركيبات السابقة"""
    conn = init_database()
    df = pd.read_sql_query(f"SELECT * FROM formulas ORDER BY created_at DESC LIMIT {limit}", conn)
    conn.close()
    return df

def authenticate_user(username, password):
    """مصادقة المستخدم"""
    conn = None
    try:
        conn = init_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2], user[3]):
            # تحديث آخر تسجيل دخول
            conn2 = init_database()
            cursor2 = conn2.cursor()
            cursor2.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
            conn2.commit()
            conn2.close()
            
            return {
                'id': user[0],
                'username': user[1],
                'role': user[4],
                'full_name': user[5],
                'title': user[6]
            }
        return None
    except Exception as e:
        return None

# ==========================================
# محرك التحسين الرياضي
# ==========================================

class FeedIngredient:
    def __init__(self, name, protein, digestibility, energy, price, lysine=0, methionine=0, min_limit=0, max_limit=100):
        self.name = name
        self.protein = protein
        self.digestibility = digestibility
        self.energy = energy
        self.price = price
        self.lysine = lysine
        self.methionine = methionine
        self.min_limit = min_limit
        self.max_limit = max_limit
    
    @property
    def digestible_protein(self):
        return self.protein * self.digestibility
    
    @property
    def digestible_lysine(self):
        return self.lysine * self.digestibility
    
    @property
    def digestible_methionine(self):
        return self.methionine * self.digestibility

def optimize_formula(ingredients, target_protein, target_energy=None, target_lysine=None, target_methionine=None, use_digestible=True):
    """
    حساب التركيبة المثلى باستخدام البرمجة الخطية
    """
    n = len(ingredients)
    
    if n < 2:
        return {'success': False, 'message': 'يجب اختيار مكونين على الأقل'}
    
    # دالة الهدف (تقليل التكلفة)
    c = [ing.price for ing in ingredients]
    
    # قيود المساواة
    A_eq = []
    b_eq = []
    
    # القيد الأول: مجموع النسب = 100%
    A_eq.append([1.0] * n)
    b_eq.append(100.0)
    
    # القيد الثاني: البروتين المستهدف
    if use_digestible:
        protein_coeffs = [ing.digestible_protein for ing in ingredients]
    else:
        protein_coeffs = [ing.protein for ing in ingredients]
    A_eq.append(protein_coeffs)
    b_eq.append(target_protein)
    
    # قيود عدم المساواة
    A_ub = []
    b_ub = []
    
    # الليسين (حد أدنى)
    if target_lysine is not None:
        if use_digestible:
            lysine_coeffs = [-ing.digestible_lysine for ing in ingredients]
        else:
            lysine_coeffs = [-ing.lysine for ing in ingredients]
        A_ub.append(lysine_coeffs)
        b_ub.append(-target_lysine)
    
    # الميثيونين (حد أدنى)
    if target_methionine is not None:
        if use_digestible:
            methionine_coeffs = [-ing.digestible_methionine for ing in ingredients]
        else:
            methionine_coeffs = [-ing.methionine for ing in ingredients]
        A_ub.append(methionine_coeffs)
        b_ub.append(-target_methionine)
    
    # الطاقة (حد أدنى)
    if target_energy is not None:
        energy_coeffs = [-ing.energy for ing in ingredients]
        A_ub.append(energy_coeffs)
        b_ub.append(-target_energy)
    
    # حدود المكونات
    bounds = [(ing.min_limit, ing.max_limit) for ing in ingredients]
    
    try:
        result = linprog(c, A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                        A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if result.success:
            # حساب التكلفة الإجمالية
            total_cost = sum(result.x[i] * ingredients[i].price for i in range(n)) / 100
            
            # حساب القيم الغذائية
            protein_total = sum(result.x[i] * (ingredients[i].digestible_protein if use_digestible else ingredients[i].protein) 
                               for i in range(n)) / 100
            digestible_protein_total = sum(result.x[i] * ingredients[i].digestible_protein for i in range(n)) / 100
            energy_total = sum(result.x[i] * ingredients[i].energy for i in range(n)) / 100
            lysine_total = sum(result.x[i] * (ingredients[i].digestible_lysine if use_digestible else ingredients[i].lysine) 
                              for i in range(n)) / 100
            methionine_total = sum(result.x[i] * (ingredients[i].digestible_methionine if use_digestible else ingredients[i].methionine) 
                                  for i in range(n)) / 100
            
            # تجميع النتائج
            percentages = {}
            for i, ing in enumerate(ingredients):
                if result.x[i] > 0.01:
                    percentages[ing.name] = result.x[i]
            
            return {
                'success': True,
                'percentages': percentages,
                'total_cost': total_cost,
                'protein': protein_total,
                'digestible_protein': digestible_protein_total,
                'energy': energy_total,
                'lysine': lysine_total,
                'methionine': methionine_total,
                'message': "تم الحل بنجاح"
            }
        else:
            return {
                'success': False,
                'message': f"لم يتم إيجاد حل: {result.message}"
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"خطأ في الحساب: {str(e)}"
        }

# ==========================================
# دوال التوصيات
# ==========================================

def get_sector_recommendations(sector: ProductionSector):
    """الحصول على توصيات للقطاع الإنتاجي"""
    
    recommendations = {
        ProductionSector.POULTRY_BROILER: {
            'protein': 22.0,
            'energy': 75.0,
            'lysine': 1.20,
            'methionine': 0.50,
            'ingredients': ['ذرة صفراء', 'كسب فول صويا 48%', 'بريمكس دواجن لاحم', 'ملح الطعام', 'الحجر الجيري'],
            'notes': 'تسمين دواجن - فترة النمو السريع'
        },
        ProductionSector.POULTRY_LAYER: {
            'protein': 16.5,
            'energy': 70.0,
            'lysine': 0.85,
            'methionine': 0.38,
            'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'بريمكس دواجن بياض', 'ملح الطعام', 'الحجر الجيري'],
            'notes': 'بياض - إنتاج البيض'
        },
        ProductionSector.DAIRY_CATTLE: {
            'protein': 16.0,
            'energy': 68.0,
            'lysine': 1.10,
            'methionine': 0.35,
            'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'بريمكس مجترات', 'ملح الطعام', 'بيكربونات الصوديوم'],
            'notes': 'أبقار حلابة - إنتاج الحليب'
        },
        ProductionSector.BEEF_CATTLE: {
            'protein': 12.5,
            'energy': 65.0,
            'lysine': 0.85,
            'methionine': 0.28,
            'ingredients': ['ذرة صفراء', 'كسب عباد الشمس', 'بريمكس مجترات', 'ملح الطعام'],
            'notes': 'تسمين عجول - نمو سريع'
        },
        ProductionSector.SHEEP_GOAT: {
            'protein': 14.0,
            'energy': 62.0,
            'lysine': 0.90,
            'methionine': 0.30,
            'ingredients': ['شعير', 'كسب عباد الشمس', 'نخالة قمح', 'ملح الطعام'],
            'notes': 'أغنام وماعز - تسمين وإنتاج حليب'
        },
        ProductionSector.HORSES: {
            'protein': 12.0,
            'energy': 60.0,
            'lysine': 0.70,
            'methionine': 0.25,
            'ingredients': ['شوفان', 'شعير', 'نخالة قمح', 'ملح الطعام'],
            'notes': 'خيول - رياضة ونشاط'
        },
        ProductionSector.FISH: {
            'protein': 28.0,
            'energy': 70.0,
            'lysine': 1.80,
            'methionine': 0.70,
            'ingredients': ['مسحوق أسماك 60%', 'كسب فول صويا 48%', 'كسب جلوتين الذرة'],
            'notes': 'أسماك - نمو سريع'
        },
        ProductionSector.GENERAL: {
            'protein': 14.0,
            'energy': 65.0,
            'lysine': 0.80,
            'methionine': 0.28,
            'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'ملح الطعام'],
            'notes': 'تركيبة عامة لمعظم الحيوانات'
        }
    }
    
    return recommendations.get(sector, recommendations[ProductionSector.GENERAL])

# ==========================================
# دوال واجهة المستخدم
# ==========================================

def apply_custom_css():
    """تطبيق التنسيقات"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 28px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 10px 0 0;
    }
    
    .main-header .subtitle {
        color: #ffd54f;
        font-size: 16px;
        margin-top: 8px;
    }
    
    .formula-result {
        background: linear-gradient(135deg, #f1f8e9 0%, #c8e6c9 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-right: 5px solid #2e7d32;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #2e7d32;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 8px;
    }
    
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        text-align: center;
        font-size: 11px;
        color: #888;
        padding: 10px;
    }
    
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white;
        border: none;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .user-badge {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-right: 5px solid #ef6c00;
    }
    
    hr {
        margin: 25px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2e7d32, transparent);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

def login_screen():
    """شاشة تسجيل الدخول"""
    
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</h1>
        <p>النسخة المتقدمة - نظام الاستمثال الخطي الذكي</p>
        <p class="subtitle">الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("#### 🔐 بوابة الدخول الآمنة")
        st.markdown("يرجى إدخال بيانات الدخول الخاصة بك")
        
        username = st.text_input("👤 اسم المستخدم", placeholder="تاور / مختص / مربي", key="login_username")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور", key="login_password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user['role']
                        st.session_state.user_name = user['full_name']
                        st.session_state.user_title = user['title']
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("ℹ️ معلومات الدخول"):
            st.markdown("""
            **أكواد الدخول المتاحة:**
            
            | الاسم | اسم المستخدم | كلمة المرور | الصلاحية |
            |-------|--------------|-------------|----------|
            | تاور | `tower` | `202687` | 👑 مالك المنصة |
            | مختص | `specialist` | `2020` | 👨‍🔬 مختص تغذية |
            | مربي | `breeder` | `2026` | 🌾 مربي منتج |
            """)

# ==========================================
# الصفحات الرئيسية
# ==========================================

def render_home_page():
    """صفحة الرئيسية"""
    
    feeds_df = get_all_feeds()
    formulas_df = get_formulas(100)
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(feeds_df)}</div>
            <div class="metric-label">📦 مواد علفية</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(formulas_df)}</div>
            <div class="metric-label">📝 تركيبة محفوظة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_cost = formulas_df['total_cost'].mean() if not formulas_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_cost:.0f}</div>
            <div class="metric-label">📊 متوسط التكلفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        low_stock = len(feeds_df[feeds_df['stock'] < 5])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{low_stock}</div>
            <div class="metric-label">⚠️ مواد منخفضة</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # رسم بياني لتوزيع المواد
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 توزيع المواد حسب التصنيف")
        category_counts = feeds_df['category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index, hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("💰 أعلى 10 مواد سعراً")
        top_price = feeds_df.nlargest(10, 'price')[['name', 'price', 'category']]
        fig = px.bar(top_price, x='name', y='price', color='category',
                    title="أسعار المواد العلفية",
                    labels={'name': 'المادة', 'price': 'السعر ($/طن)'})
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # آخر التركيبات
    st.subheader("📋 آخر التركيبات المحفوظة")
    if not formulas_df.empty:
        display_df = formulas_df[['name', 'sector', 'total_cost', 'protein', 'created_at']].head(10]
        display_df.columns = ['اسم التركيبة', 'القطاع', 'التكلفة ($)', 'البروتين (%)', 'التاريخ']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("📌 لا توجد تركيبات محفوظة بعد. قم بإنشاء تركيبة جديدة في تبويب تركيب الأعلاف.")

def render_formulator_page():
    """صفحة تركيب الأعلاف"""
    
    st.markdown("""
    <div class="main-header">
        <h1>🔬 محرك تركيب الأعلاف الذكي</h1>
        <p>نظام الاستمثال الخطي المتقدم (Least-Cost Formulation)</p>
        <p class="subtitle">يعتمد على البرمجة الخطية لإيجاد أقل تكلفة مع تحقيق المواصفات</p>
    </div>
    """, unsafe_allow_html=True)
    
    feeds_df = get_all_feeds()
    
    # إعدادات التركيب
    col_settings1, col_settings2 = st.columns(2)
    
    with col_settings1:
        sector = st.selectbox(
            "🐏 القطاع الإنتاجي",
            [s.value for s in ProductionSector],
            help="اختر القطاع لتحصل على توصيات مناسبة"
        )
        
        sector_enum = ProductionSector(sector)
        recommendations = get_sector_recommendations(sector_enum)
        
        st.info(f"💡 **توصيات للقطاع:** {recommendations['notes']}")
        
        target_protein = st.slider(
            "🎯 نسبة البروتين المستهدفة (%)",
            min_value=5.0, max_value=40.0,
            value=recommendations['protein'],
            step=0.5,
            help="النسبة المئوية للبروتين في العلف النهائي"
        )
        
        use_digestible = st.toggle(
            "🧬 استخدام البروتين المهضوم (DP)",
            value=True,
            help="البروتين المهضوم يعطي دقة علمية أعلى"
        )
    
    with col_settings2:
        formula_name = st.text_input(
            "📝 اسم التركيبة",
            value=f"خلطة {sector} - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        target_energy = st.number_input(
            "⚡ معادل النشاء المستهدف (SE)",
            min_value=0.0, max_value=100.0,
            value=recommendations['energy'],
            step=1.0,
            help="وحدة قياس طاقة العلف"
        ) if st.checkbox("تحديد معادل النشاء") else None
        
        target_lysine = st.number_input(
            "🧪 الليسين المستهدف (%)",
            min_value=0.0, max_value=5.0,
            value=recommendations['lysine'],
            step=0.05,
            help="حمض أميني أساسي مهم للنمو"
        ) if st.checkbox("تحديد الليسين") else None
        
        target_methionine = st.number_input(
            "🧪 الميثيونين المستهدف (%)",
            min_value=0.0, max_value=3.0,
            value=recommendations['methionine'],
            step=0.05,
            help="حمض أميني أساسي يحتوي على كبريت"
        ) if st.checkbox("تحديد الميثيونين") else None
    
    st.markdown("---")
    
    # المكونات الموصى بها
    with st.expander("⭐ المكونات الموصى بها لهذا القطاع", expanded=False):
        st.markdown(f"**المكونات:** {', '.join(recommendations['ingredients'])}")
        st.markdown(f"**البروتين الموصى به:** {recommendations['protein']}%")
        st.markdown(f"**معادل النشاء:** {recommendations['energy']} SE")
    
    st.markdown("---")
    st.subheader("✅ اختر مكونات العلف")
    st.caption("💡 نصيحة: اختر 4-6 مكونات للحصول على أفضل نتيجة")
    
    # اختيار المكونات
    selected_ingredients = []
    
    for category in feeds_df['category'].unique():
        with st.expander(f"📁 {category}", expanded=category in ["🌾 حبوب ومصادر طاقة", "🥜 أكساب ومصادر بروتين"]):
            category_feeds = feeds_df[feeds_df['category'] == category]
            cols = st.columns(3)
            
            for idx, (_, row) in enumerate(category_feeds.iterrows()):
                with cols[idx % 3]:
                    is_recommended = row['name'] in recommendations['ingredients']
                    default_checked = is_recommended
                    
                    if st.checkbox(f"{row['name']} 🏷️", value=default_checked, key=f"select_{row['id']}"):
                        # عرض معلومات المادة
                        st.caption(f"🥩 بروتين: {row['protein']}% | ⚡ طاقة: {row['energy']} SE")
                        
                        # تعديل السعر (للمالك فقط)
                        if st.session_state.role == UserRole.OWNER.value:
                            price = st.number_input(
                                f"سعر {row['name']}",
                                value=float(row['price']),
                                key=f"price_{row['id']}",
                                step=5.0
                            )
                        else:
                            price = row['price']
                            st.caption(f"💰 السعر: ${price:.0f}/طن")
                        
                        # عرض المخزون المتوفر
                        if row['stock'] < 5:
                            st.warning(f"⚠️ المخزون منخفض: {row['stock']:.1f} طن")
                        
                        selected_ingredients.append(FeedIngredient(
                            name=row['name'],
                            protein=row['protein'],
                            digestibility=row['digestibility'],
                            energy=row['energy'],
                            price=price,
                            lysine=row['lysine'],
                            methionine=row['methionine'],
                            min_limit=row['min_limit'],
                            max_limit=row['max_limit']
                        ))
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
            if len(selected_ingredients) < 2:
                st.warning("⚠️ يرجى اختيار مكونين على الأقل (مثال: ذرة + كسب صويا)")
            else:
                with st.spinner("🧮 جاري حساب التركيبة المثلى..."):
                    result = optimize_formula(
                        selected_ingredients,
                        target_protein,
                        target_energy,
                        target_lysine,
                        target_methionine,
                        use_digestible
                    )
                    
                    if result['success']:
                        st.balloons()
                        st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                        
                        # عرض النتائج
                        col_r1, col_r2 = st.columns(2)
                        
                        with col_r1:
                            st.subheader("📝 المقادير لكل طن")
                            
                            total_percent = 0
                            for name, pct in result['percentages'].items():
                                kg = pct * 10
                                total_percent += pct
                                st.markdown(f"""
                                <div class="formula-result">
                                    <strong>🌾 {name}</strong><br>
                                    <span style="font-size: 22px; font-weight: bold; color: #2e7d32;">{pct:.1f}%</span>
                                    <span style="font-size: 14px;"> → {kg:.1f} كجم لكل طن</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.caption(f"✅ مجموع النسب: {total_percent:.1f}%")
                            
                            # حفظ التركيبة في session state
                            st.session_state.last_formula = result['percentages']
                            st.session_state.last_cost = result['total_cost']
                            st.session_state.last_protein = result['protein']
                            st.session_state.last_energy = result['energy']
                        
                        with col_r2:
                            st.subheader("💰 التكاليف والمواصفات")
                            
                            st.metric("💵 تكلفة الطن الواحد", f"${result['total_cost']:.2f}")
                            st.metric("🥩 البروتين الكلي", f"{result['protein']:.2f}%")
                            st.metric("🧬 البروتين المهضوم", f"{result['digestible_protein']:.2f}%")
                            st.metric("⚡ معادل النشاء", f"{result['energy']:.1f} SE")
                            
                            if result.get('lysine', 0) > 0:
                                st.metric("🧪 الليسين", f"{result['lysine']:.2f}%")
                            if result.get('methionine', 0) > 0:
                                st.metric("🧪 الميثيونين", f"{result['methionine']:.2f}%")
                            
                            st.markdown("---")
                            
                            # رسم بياني دائري
                            fig = go.Figure(data=[go.Pie(
                                labels=list(result['percentages'].keys()),
                                values=list(result['percentages'].values()),
                                hole=0.4,
                                marker=dict(colors=px.colors.qualitative.Set3)
                            )])
                            fig.update_layout(title="توزيع مكونات التركيبة", height=350)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # حفظ التركيبة
                        st.markdown("---")
                        col_save1, col_save2 = st.columns(2)
                        
                        with col_save1:
                            if st.button("💾 حفظ التركيبة", use_container_width=True):
                                formula_id = save_formula(
                                    name=formula_name,
                                    sector=sector,
                                    ingredients=result['percentages'],
                                    cost=result['total_cost'],
                                    protein=result['protein'],
                                    digestible_protein=result['digestible_protein'],
                                    energy=result['energy'],
                                    lysine=result.get('lysine', 0),
                                    methionine=result.get('methionine', 0),
                                    user=st.session_state.user_name
                                )
                                st.success(f"✅ تم حفظ التركيبة بنجاح (الرقم: {formula_id})")
                        
                        with col_save2:
                            # خصم من المخزون
                            tons = st.number_input("الكمية المنتجة (طن)", min_value=0.1, value=1.0, step=0.5)
                            if st.button("📦 خصم من المخزون", use_container_width=True):
                                for name, pct in result['percentages'].items():
                                    qty_to_deduct = (pct / 100) * tons
                                    update_stock(name, qty_to_deduct, "deduct", formula_name, st.session_state.user_name)
                                st.success(f"✅ تم خصم {tons} طن من المخزون")
                                st.rerun()
                        
                        # مشاركة النتيجة
                        st.markdown("---")
                        share_text = f"🌾 منصة تاور العلمية - خلطة {sector} بتكلفة ${result['total_cost']:.2f}/طن، بروتين {result['protein']:.1f}%"
                        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
                        st.link_button("📱 مشاركة النتيجة عبر واتساب", whatsapp_url, use_container_width=True)
                        
                    else:
                        st.error(f"❌ {result['message']}")
                        st.markdown("""
                        <div class="warning-card">
                            <strong>💡 اقتراحات لحل المشكلة:</strong><br>
                            1. أضف المزيد من المكونات - خاصة مصادر البروتين (كسب صويا، أمباز فول)<br>
                            2. خفف نسبة البروتين المستهدفة قليلاً (جرب خفضها بمقدار 1-2%)<br>
                            3. تأكد من صحة الأسعار المدخلة<br>
                            4. أضف مكونات بديلة مثل كسب عباد الشمس أو كسب بذور القطن<br>
                            5. تأكد من أن الحدود الدنيا والعليا للمكونات منطقية
                        </div>
                        """, unsafe_allow_html=True)

def render_inventory_page():
    """صفحة إدارة المخزون"""
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #ef6c00 0%, #f57c00 100%);">
        <h1>📦 إدارة المخزون والمستودعات</h1>
        <p>تتبع وإدارة المواد العلفية والمخزون</p>
    </div>
    """, unsafe_allow_html=True)
    
    feeds_df = get_all_feeds()
    
    # خصم سريع من آخر خلطة
    if 'last_formula' in st.session_state and st.session_state.last_formula:
        with st.expander("🔄 خصم مكونات آخر خلطة من المخزون", expanded=False):
            col_tons, col_btn = st.columns([2, 1])
            with col_tons:
                tons = st.number_input("الكمية المنتجة (طن):", min_value=0.1, value=1.0, step=0.5, key="deduct_tons")
            with col_btn:
                if st.button("تأكيد الخصم", type="primary"):
                    for name, pct in st.session_state.last_formula.items():
                        qty_to_deduct = (pct / 100) * tons
                        update_stock(name, qty_to_deduct, "deduct", "خصم سريع", st.session_state.user_name)
                    st.success(f"✅ تم خصم {tons} طن من المخزون")
                    st.rerun()
    
    st.markdown("---")
    st.subheader("📊 الأرصدة الحالية")
    
    # بحث
    search = st.text_input("🔍 بحث", placeholder="ابحث عن مادة علفية...")
    filtered_df = feeds_df
    if search:
        filtered_df = feeds_df[feeds_df['name'].str.contains(search, na=False)]
    
    # إحصائيات المخزون
    total_stock = filtered_df['stock'].sum()
    low_stock_count = len(filtered_df[filtered_df['stock'] < 5])
    critical_count = len(filtered_df[filtered_df['stock'] < 2])
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("📦 إجمالي المخزون", f"{total_stock:.1f} طن")
    with col_stat2:
        st.metric("⚠️ مواد منخفضة (<5 طن)", low_stock_count)
    with col_stat3:
        st.metric("🔴 مواد حرجة (<2 طن)", critical_count)
    
    st.markdown("---")
    
    # عرض المخزون
    cols = st.columns(3)
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with cols[idx % 3]:
            stock = row['stock']
            name = row['name']
            category = row['category']
            
            if stock <= 2:
                color = "#ffebee"
                status = "🔴 حرج - يرجى التوريد"
                border = "#c62828"
            elif stock <= 5:
                color = "#fff3e0"
                status = "🟡 منخفض - يفضل التوريد"
                border = "#ef6c00"
            else:
                color = "#e8f5e9"
                status = "🟢 جيد"
                border = "#2e7d32"
            
            if st.session_state.role == UserRole.OWNER.value:
                new_stock = st.number_input(
                    f"{name}",
                    value=float(stock),
                    key=f"stock_{row['id']}",
                    step=0.5,
                    label_visibility="collapsed"
                )
                if new_stock != stock:
                    update_stock(name, new_stock, "set", "تعديل يدوي", st.session_state.user_name)
                    st.rerun()
                st.caption(f"📂 {category}")
            else:
                st.markdown(f"""
                <div style="background-color: {color}; padding: 15px; margin: 8px 0; border-radius: 12px; border-right: 4px solid {border};">
                    <strong style="font-size: 16px;">{name}</strong><br>
                    <span style="font-size: 24px; font-weight: bold;">{stock:.1f}</span>
                    <span style="font-size: 14px;"> طن</span><br>
                    <span style="font-size: 12px; color: #666;">{status}</span><br>
                    <span style="font-size: 11px; color: #999;">{category}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # إضافة مادة جديدة (للمالك فقط)
    if st.session_state.role == UserRole.OWNER.value:
        st.markdown("---")
        with st.expander("➕ إضافة مادة علفية جديدة", expanded=False):
            col_new1, col_new2 = st.columns(2)
            with col_new1:
                new_name = st.text_input("اسم المادة")
                new_category = st.selectbox("التصنيف", [c.value for c in FeedCategory])
                new_protein = st.number_input("البروتين (%)", min_value=0.0, max_value=100.0, value=0.0)
                new_energy = st.number_input("معادل النشاء (SE)", min_value=0.0, value=50.0)
            
            with col_new2:
                new_price = st.number_input("السعر ($/طن)", min_value=0.0, value=100.0)
                new_stock = st.number_input("المخزون الابتدائي (طن)", min_value=0.0, value=10.0)
                new_digestibility = st.slider("معامل الهضم", 0.0, 1.0, 0.85)
                new_lysine = st.number_input("الليسين (%)", min_value=0.0, value=0.0)
                new_methionine = st.number_input("الميثيونين (%)", min_value=0.0, value=0.0)
            
            if st.button("💾 إضافة المادة", type="primary"):
                if new_name:
                    conn = init_database()
                    cursor = conn.cursor()
                    try:
                        cursor.execute('''
                            INSERT INTO feeds (name, category, protein, lysine, methionine, digestibility, energy, price, stock, max_limit, min_limit)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 100, 0)
                        ''', (new_name, new_category, new_protein, new_lysine, new_methionine, new_digestibility, new_energy, new_price, new_stock))
                        conn.commit()
                        st.success(f"✅ تم إضافة {new_name} بنجاح")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")
                    finally:
                        conn.close()

def render_history_page():
    """صفحة التركيبات السابقة"""
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #6a1b9a 0%, #7b1fa2 100%);">
        <h1>📊 تاريخ التركيبات العلفية</h1>
        <p>جميع التركيبات المحفوظة سابقاً</p>
    </div>
    """, unsafe_allow_html=True)
    
    formulas_df = get_formulas(100)
    
    if formulas_df.empty:
        st.info("📌 لا توجد تركيبات محفوظة. قم بإنشاء تركيبة جديدة في تبويب تركيب الأعلاف.")
        return
    
    # فلترة وبحث
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        sector_filter = st.selectbox("تصفية حسب القطاع", ["الكل"] + list(formulas_df['sector'].unique()))
    with col_filter2:
        search = st.text_input("🔍 بحث", placeholder="ابحث عن تركيبة...")
    with col_filter3:
        sort_by = st.selectbox("ترتيب حسب", ["التاريخ", "التكلفة", "البروتين"])
    
    # تطبيق الفلاتر
    filtered_df = formulas_df.copy()
    if sector_filter != "الكل":
        filtered_df = filtered_df[filtered_df['sector'] == sector_filter]
    if search:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search, na=False)]
    
    st.markdown(f"**📋 عدد التركيبات:** {len(filtered_df)}")
    
    # عرض التركيبات
    for _, row in filtered_df.iterrows():
        with st.expander(f"📅 {row['created_at'][:16]} - {row['name']} - 💰 ${row['total_cost']:.2f}/طن"):
            ingredients = json.loads(row['ingredients'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🌾 المكونات:**")
                for name, pct in ingredients.items():
                    st.write(f"• {name}: {pct:.1f}% ({pct*10:.1f} كجم/طن)")
            
            with col2:
                st.markdown("**📊 المواصفات:**")
                st.write(f"💰 التكلفة: ${row['total_cost']:.2f}/طن")
                st.write(f"🥩 البروتين: {row['protein']:.1f}%")
                st.write(f"🧬 البروتين المهضوم: {row['digestible_protein']:.1f}%")
                st.write(f"⚡ الطاقة: {row['energy']:.1f} SE")
                if row['lysine'] > 0:
                    st.write(f"🧪 الليسين: {row['lysine']:.2f}%")
                if row['methionine'] > 0:
                    st.write(f"🧪 الميثيونين: {row['methionine']:.2f}%")
                st.write(f"👤 بواسطة: {row['created_by']}")
            
            # أزرار الإجراءات
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button(f"🔄 استخدام هذه التركيبة", key=f"use_{row['id']}"):
                    st.session_state.last_formula = ingredients
                    st.session_state.last_cost = row['total_cost']
                    st.session_state.last_protein = row['protein']
                    st.session_state.current_page = 'formulator'
                    st.success("تم تحميل التركيبة بنجاح")
                    st.rerun()
            
            with col_btn2:
                if st.button(f"📦 خصم من المخزون", key=f"deduct_{row['id']}"):
                    tons = st.number_input("الكمية (طن)", min_value=0.1, value=1.0, step=0.5, key=f"tons_{row['id']}")
                    if st.button("تأكيد", key=f"confirm_{row['id']}"):
                        for name, pct in ingredients.items():
                            qty = (pct / 100) * tons
                            update_stock(name, qty, "deduct", row['name'], st.session_state.user_name)
                        st.success(f"✅ تم خصم {tons} طن")
                        st.rerun()

def render_help_page():
    """صفحة المساعدة"""
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #37474f 0%, #455a64 100%);">
        <h1>📚 المساعدة والدليل الشامل</h1>
        <p>دليل استخدام المنصة والمصطلحات العلمية</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 دليل الاستخدام", "🔑 الصلاحيات", "🧬 المصطلحات العلمية", "❓ الأسئلة الشائعة"])
    
    with tab1:
        st.markdown("""
        ### 🎯 كيفية استخدام منصة تاور العلمية
        
        #### الخطوة 1: تسجيل الدخول
        - استخدم اسم المستخدم وكلمة المرور المخصصين لك
        - تتوفر ثلاث صلاحيات: **تاور (مالك)**، **مختص**، **مربي**
        
        #### الخطوة 2: اختيار القطاع الإنتاجي
        - اختر نوع الحيوان (دواجن، أبقار، أغنام، خيول، أسماك)
        - سيتم عرض التوصيات المناسبة لكل قطاع
        
        #### الخطوة 3: اختيار المكونات
        - اختر المواد العلفية المتوفرة لديك
        - يُفضل اختيار 4-6 مكونات للحصول على أفضل نتيجة
        - المكونات الأساسية الموصى بها: ذرة + كسب صويا + نخالة + أملاح
        
        #### الخطوة 4: تحديد المواصفات
        - حدد نسبة البروتين المستهدفة
        - يمكن تحديد معادل النشاء والأحماض الأمينية
        
        #### الخطوة 5: تشغيل المحرك
        - اضغط على زر "تشغيل محرك الاستمثال الخطي"
        - ستظهر التركيبة المثلى بأقل تكلفة
        
        #### الخطوة 6: حفظ وتطبيق النتيجة
        - يمكن حفظ التركيبة للاستخدام المستقبلي
        - يمكن خصم المكونات من المخزون تلقائياً
        - يمكن مشاركة النتيجة عبر واتساب
        """)
    
    with tab2:
        st.markdown("""
        ### 🔐 نظام الصلاحيات والأمان
        
        | الصلاحية | تاور (مالك) 👑 | مختص 👨‍🔬 | مربي 🌾 |
        |----------|---------------|----------|--------|
        | تركيب الأعلاف | ✅ | ✅ | ✅ |
        | مشاهدة المخزون | ✅ | ✅ | ✅ |
        | تعديل المخزون | ✅ | ❌ | ❌ |
        | إضافة مواد جديدة | ✅ | ❌ | ❌ |
        | تعديل الأسعار | ✅ | ❌ | ❌ |
        | إدارة المستخدمين | ✅ | ❌ | ❌ |
        | عرض التقارير | ✅ | ✅ | ❌ |
        | تصدير البيانات | ✅ | ✅ | ❌ |
        
        #### أكواد الدخول:
        
        | الاسم | اسم المستخدم | كلمة المرور |
        |-------|--------------|-------------|
        | **تاور (مالك)** | `tower` | `202687` |
        | **مختص** | `specialist` | `2020` |
        | **مربي** | `breeder` | `2026` |
        
        #### نصائح أمنية:
        - يرجى تغيير كلمة المرور الافتراضية بعد أول تسجيل دخول
        - لا تشارك كلمة المرور مع أي شخص
        - يتم تشفير جميع كلمات المرور باستخدام SHA-256
        """)
    
    with tab3:
        st.markdown("""
        ### 🧬 المصطلحات العلمية المستخدمة
        
        #### البروتين المهضوم (Digestible Protein - DP)
        - هو البروتين الفعلي الذي يستطيع الحيوان هضمه وامتصاصه
        - يتم حسابه بضرب البروتين الخام في معامل الهضم
        - يعطي دقة أكبر من البروتين الخام في التغذية
        
        #### معادل النشاء (Starch Equivalent - SE)
        - مقياس لطاقة العلف مقارنة بالنشاء
        - يستخدم لتقييم كفاءة الطاقة في العلائق
        - وحدة قياس طاقة العلف
        
        #### البرمجة الخطية (Linear Programming)
        - تقنية رياضية لإيجاد الحل الأمثل
        - تستخدم لتقليل التكلفة مع تحقيق المواصفات المطلوبة
        - تعتبر المعيار الذهبي في صناعة الأعلاف
        
        #### معامل الهضم (Digestibility Coefficient)
        - نسبة المادة الغذائية التي يهضمها الحيوان
        - تتراوح بين 0 و 1 (أو 0% إلى 100%)
        - يختلف حسب نوع المادة ونوع الحيوان
        
        #### الأحماض الأمينية الأساسية
        - **الليسين (Lysine):** أول حمض أميني محدود في تغذية الدواجن
        - **الميثيونين (Methionine):** حمض أميني يحتوي على كبريت، مهم للنمو والريش
        - **الثريونين (Threonine):** مهم لصحة الأمعاء والجهاز المناعي
        
        #### المصطلحات الإضافية
        - **العلائق (Rations):** الخلطات العلفية المتوازنة
        - **الأكساب (Meals):** المنتجات الثانوية لاستخلاص الزيوت
        - **البريمكس (Premix):** خليط من الفيتامينات والمعادن
        """)
    
    with tab4:
        st.markdown("""
        ### ❓ الأسئلة الشائعة
        
        **س: ماذا أفعل إذا لم يتم إيجاد حل للتركيبة؟**
        
        ج: حاول إضافة المزيد من المكونات، خاصة مصادر البروتين (كسب صويا، أمباز فول)، أو خفض نسبة البروتين المستهدفة قليلاً بمقدار 1-2%.
        
        **س: كيف يمكنني تحديث أسعار المواد؟**
        
        ج: إذا كنت تملك صلاحية المالك (تاور)، يمكنك تعديل السعر مباشرة عند اختيار المكون في تبويب تركيب الأعلاف.
        
        **س: هل يمكن حفظ التركيبات للاستخدام المستقبلي؟**
        
        ج: نعم، يتم حفظ جميع التركيبات تلقائياً ويمكنك الوصول إليها من تبويب "التركيبات السابقة".
        
        **س: كيف يتم حساب البروتين المهضوم؟**
        
        ج: البروتين المهضوم = البروتين الخام × معامل الهضم الخاص بكل مادة. هذه الطريقة أكثر دقة علمياً.
        
        **س: ماذا تعني الألوان في المخزون؟**
        
        ج: 🟢 أخضر = مخزون جيد (>5 طن)، 🟡 أصفر = مخزون منخفض (2-5 طن)، 🔴 أحمر = مخزون حرج (<2 طن).
        
        **س: كيف يمكنني التواصل للاستشارات الفنية؟**
        
        ج: يمكنك التواصل مع الاختصاصي م. عبد القادر إسماعيل تاور عبر البريد الإلكتروني أو واتساب.
        
        **س: ما هو الفرق بين البروتين الخام والبروتين المهضوم؟**
        
        ج: البروتين الخام هو القيمة المختبرية الكلية، بينما البروتين المهضوم هو الجزء الفعلي الذي يمتصه الحيوان ويستفيد منه.
        
        **س: كيف أعرف أن التركيبة مناسبة لحيواني؟**
        
        ج: المنصة تقدم توصيات حسب القطاع الإنتاجي الذي تختاره، ويمكنك تعديل البروتين والطاقة حسب احتياجاتك الخاصة.
        """)
    
    st.markdown("---")
    st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور - جميع الحقوق محفوظة")
    st.caption("منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - الإصدار 3.0")

# ==========================================
# تشغيل التطبيق
# ==========================================

def main():
    """الدالة الرئيسية"""
    
    # تهيئة حالة الجلسة
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.user_name = None
        st.session_state.user_title = None
        st.session_state.current_page = "home"
    
    # تطبيق التنسيقات
    apply_custom_css()
    
    # شاشة تسجيل الدخول
    if not st.session_state.logged_in:
        login_screen()
        return
    
    # تهيئة قاعدة البيانات
    init_database()
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
            <span style="font-size: 24px;">🌾</span>
            <h3 style="margin: 5px 0; color: white;">{st.session_state.user_name}</h3>
            <p style="margin: 0; font-size: 12px; opacity: 0.9;">{st.session_state.user_title}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # قائمة التنقل
        menu = {
            "home": "🏠 الرئيسية",
            "formulator": "🔬 تركيب الأعلاف",
            "inventory": "📦 إدارة المخزون",
            "history": "📊 التركيبات السابقة",
            "help": "📚 المساعدة والدليل"
        }
        
        for key, label in menu.items():
            if st.button(label, key=f"menu_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        
        st.markdown("---")
        
        # إحصائيات سريعة
        feeds_df = get_all_feeds()
        formulas_df = get_formulas(100)
        
        st.metric("📦 المواد العلفية", len(feeds_df))
        st.metric("📝 التركيبات المحفوظة", len(formulas_df))
        
        if 'last_cost' in st.session_state and st.session_state.last_cost > 0:
            st.metric("💰 آخر تكلفة", f"${st.session_state.last_cost:.2f}/طن")
        
        st.markdown("---")
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in ['logged_in', 'user', 'role', 'user_name', 'user_title', 'current_page']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("""
        <div class="sidebar-footer">
            © 2026 منصة تاور العلمية<br>
            الاختصاصي م. عبد القادر إسماعيل تاور
        </div>
        """, unsafe_allow_html=True)
    
    # عرض الصفحة المختارة
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page == 'home':
        render_home_page()
    elif current_page == 'formulator':
        render_formulator_page()
    elif current_page == 'inventory':
        render_inventory_page()
    elif current_page == 'history':
        render_history_page()
    else:
        render_help_page()

if __name__ == "__main__":
    main()
