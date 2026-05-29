"""
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                               ║
║                         🌾 منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف 🌾                              ║
║                                                                                                               ║
║                              الإصدار 3.0 - النظام المتكامل للبرمجة الخطية                                     ║
║                                                                                                               ║
║                                    الاختصاصي م. عبد القادر إسماعيل تاور                                       ║
║                                                                                                               ║
║                              © 2026 - جميع الحقوق محفوظة - تاور ساينتفك بلاتفورم                              ║
║                                                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 📚 المكتبات والواردات
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import sqlite3
import urllib.parse
import json
import hashlib
import hmac
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import os
import time
from functools import lru_cache, wraps
import logging
from contextlib import contextmanager

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🔧 إعدادات التسجيل والأمان
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 📊 كلاسات البيانات (Data Classes)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class UserRole(Enum):
    """صلاحيات المستخدمين"""
    OWNER = "owner"
    SPECIALIST = "specialist"
    BREEDER = "breeder"

class FeedCategory(Enum):
    """تصنيفات المواد العلفية"""
    GRAINS = "🌾 حبوب ومصادر طاقة"
    PROTEIN = "🥜 أكساب ومصادر بروتين"
    ANIMAL_PROTEIN = "🐟 بروتين حيواني"
    BYPRODUCTS = "🌾 مخلفات زراعية"
    MINERALS = "🧂 أملاح ومعادن"
    ADDITIVES = "💊 إضافات وإنزيمات"

class ProductionSector(Enum):
    """القطاعات الإنتاجية"""
    POULTRY_BROILER = "دواجن لاحم"
    POULTRY_LAYER = "دواجن بياض"
    DAIRY_CATTLE = "أبقار حلابة"
    BEEF_CATTLE = "تسمين عجول"
    SHEEP_GOAT = "أغنام وماعز"
    HORSES = "خيول"
    FISH = "أسماك"
    GENERAL = "عام"

@dataclass
class FeedIngredient:
    """بيانات المادة العلفية"""
    id: int
    name: str
    category: str
    protein: float
    lysine: float
    methionine: float
    digestibility: float
    energy: float
    price: float
    max_limit: float = 100.0
    min_limit: float = 0.0
    stock: float = 0.0
    
    @property
    def digestible_protein(self) -> float:
        """حساب البروتين المهضوم"""
        return self.protein * self.digestibility
    
    @property
    def digestible_lysine(self) -> float:
        """حساب الليسين المهضوم"""
        return self.lysine * self.digestibility
    
    @property
    def digestible_methionine(self) -> float:
        """حساب الميثيونين المهضوم"""
        return self.methionine * self.digestibility

@dataclass
class FeedFormula:
    """بيانات التركيبة العلفية"""
    id: Optional[int] = None
    name: str = ""
    ingredients: Dict[str, float] = field(default_factory=dict)
    total_cost: float = 0.0
    protein: float = 0.0
    digestible_protein: float = 0.0
    energy: float = 0.0
    lysine: float = 0.0
    methionine: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    
    def to_dict(self) -> Dict:
        """تحويل التركيبة إلى قاموس للتخزين"""
        return {
            'name': self.name,
            'ingredients': json.dumps(self.ingredients),
            'total_cost': self.total_cost,
            'protein': self.protein,
            'digestible_protein': self.digestible_protein,
            'energy': self.energy,
            'lysine': self.lysine,
            'methionine': self.methionine,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by
        }

@dataclass
class ProductionRequirement:
    """الاحتياجات الإنتاجية للحيوان"""
    sector: ProductionSector
    protein_requirement: float
    energy_requirement: float
    lysine_requirement: float
    methionine_requirement: float
    recommended_ingredients: List[str] = field(default_factory=list)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🔐 دوال الأمان والتشفير
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

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

def sanitize_input(text: str) -> str:
    """تنظيف المدخلات لمنع هجمات الحقن"""
    if not text:
        return ""
    text = re.sub(r'[<>"\']', '', text)
    text = text.strip()
    return text

def rate_limit(calls_per_minute: int = 30):
    """محدد معدل الطلبات لمنع الهجمات"""
    def decorator(func):
        last_called = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if func.__name__ in last_called:
                if now - last_called[func.__name__] < 60.0 / calls_per_minute:
                    time.sleep(0.1)
            last_called[func.__name__] = now
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🗄️ إدارة قاعدة البيانات المحسنة
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """مدير قاعدة البيانات مع دعم المعاملات والتخزين المؤقت"""
    
    def __init__(self, db_path: str = "tower_scientific.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات مع الإدارة التلقائية"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _init_database(self):
        """تهيئة قاعدة البيانات مع جميع الجداول والعلاقات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول المستخدمين مع التشفير
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
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
                max_limit REAL DEFAULT 100,
                min_limit REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # جدول المخزون
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                feed_id INTEGER PRIMARY KEY,
                quantity REAL DEFAULT 0,
                critical_level REAL DEFAULT 2,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE
            )
            ''')
            
            # جدول التركيبات
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                total_cost REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                digestible_protein REAL DEFAULT 0,
                energy REAL DEFAULT 0,
                lysine REAL DEFAULT 0,
                methionine REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                is_favorite INTEGER DEFAULT 0
            )
            ''')
            
            # جدول الإنتاج
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_id INTEGER,
                quantity REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                production_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                produced_by TEXT,
                notes TEXT,
                FOREIGN KEY (formula_id) REFERENCES formulas(id)
            )
            ''')
            
            # جدول أسعار السوق
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                price REAL NOT NULL,
                market_location TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds(id)
            )
            ''')
            
            # جدول السجل (Audit Log)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # إنشاء الفهارس لتحسين الأداء
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feeds_category ON feeds(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_formulas_created_at ON formulas(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
            
            # إضافة المستخدمين الافتراضيين
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                default_users = [
                    ("owner", "202687", UserRole.OWNER.value, "م. عبد القادر إسماعيل تاور", "abukram128@gmail.com"),
                    ("specialist", "2020", UserRole.SPECIALIST.value, "د. مختص تغذية", "specialist@tower.com"),
                    ("breeder", "2026", UserRole.BREEDER.value, "مربي نموذجي", "breeder@tower.com")
                ]
                for username, password, role, full_name, email in default_users:
                    hashed, salt = hash_password(password)
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, password_salt, role, full_name, email)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (username, hashed, salt, role, full_name, email))
            
            # إضافة المواد العلفية الافتراضية
            cursor.execute("SELECT COUNT(*) FROM feeds")
            if cursor.fetchone()[0] == 0:
                self._seed_feeds(cursor)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _seed_feeds(self, cursor):
        """إضافة المواد العلفية الافتراضية الموسعة"""
        
        feeds_data = [
            # ═══════════════════════════════════════════════════════════════════
            # 🌾 الحبوب ومصادر الطاقة (Grains & Energy Sources)
            # ═══════════════════════════════════════════════════════════════════
            ("ذرة صفراء", FeedCategory.GRAINS.value, 8.5, 0.24, 0.17, 0.85, 80.0, 230, 100, 0),
            ("ذرة بيضاء", FeedCategory.GRAINS.value, 8.8, 0.23, 0.16, 0.83, 78.0, 225, 100, 0),
            ("شعير مطحون", FeedCategory.GRAINS.value, 11.5, 0.36, 0.19, 0.80, 71.0, 210, 100, 0),
            ("سورجم (فتريتة)", FeedCategory.GRAINS.value, 10.0, 0.22, 0.15, 0.78, 70.0, 195, 100, 0),
            ("قمح محلي", FeedCategory.GRAINS.value, 12.0, 0.32, 0.21, 0.85, 75.0, 240, 100, 0),
            ("جريش أرز", FeedCategory.GRAINS.value, 7.8, 0.28, 0.20, 0.82, 82.0, 230, 100, 0),
            ("دخن", FeedCategory.GRAINS.value, 11.0, 0.30, 0.22, 0.75, 68.0, 220, 100, 0),
            ("شوفان", FeedCategory.GRAINS.value, 11.0, 0.40, 0.18, 0.76, 62.0, 230, 100, 0),
            
            # ═══════════════════════════════════════════════════════════════════
            # 🥜 الأكساب ومصادر البروتين النباتي (Protein Meals)
            # ═══════════════════════════════════════════════════════════════════
            ("كسب فول صويا 44%", FeedCategory.PROTEIN.value, 44.0, 2.70, 0.62, 0.90, 74.0, 440, 100, 0),
            ("كسب فول صويا 48%", FeedCategory.PROTEIN.value, 48.0, 2.90, 0.67, 0.91, 76.0, 480, 100, 0),
            ("كسب عباد الشمس 36%", FeedCategory.PROTEIN.value, 36.0, 1.20, 0.75, 0.76, 42.0, 310, 100, 0),
            ("أمباز الفول السوداني", FeedCategory.PROTEIN.value, 46.0, 1.60, 0.52, 0.88, 73.0, 460, 100, 0),
            ("كسب بذور القطن", FeedCategory.PROTEIN.value, 41.0, 1.75, 0.64, 0.78, 55.0, 290, 100, 0),
            ("كسب بذور الكتان", FeedCategory.PROTEIN.value, 32.0, 1.15, 0.60, 0.82, 65.0, 350, 100, 0),
            ("كسب السمسم", FeedCategory.PROTEIN.value, 42.0, 1.25, 1.10, 0.84, 70.0, 380, 100, 0),
            ("كسب جلوتين الذرة 60%", FeedCategory.PROTEIN.value, 60.0, 1.02, 1.45, 0.92, 85.0, 520, 100, 0),
            
            # ═══════════════════════════════════════════════════════════════════
            # 🐟 مصادر البروتين الحيواني (Animal Protein Sources)
            # ═══════════════════════════════════════════════════════════════════
            ("مسحوق أسماك 60%", FeedCategory.ANIMAL_PROTEIN.value, 60.0, 4.50, 1.65, 0.85, 65.0, 850, 100, 0),
            ("مسحوق أسماك 72%", FeedCategory.ANIMAL_PROTEIN.value, 72.0, 5.40, 2.10, 0.90, 72.0, 1050, 100, 0),
            ("مسحوق لحم وعظم", FeedCategory.ANIMAL_PROTEIN.value, 50.0, 2.60, 0.70, 0.75, 50.0, 650, 100, 0),
            
            # ═══════════════════════════════════════════════════════════════════
            # 🌾 المخلفات الزراعية والصناعية (Agricultural Byproducts)
            # ═══════════════════════════════════════════════════════════════════
            ("نخالة قمح (ردة)", FeedCategory.BYPRODUCTS.value, 15.0, 0.58, 0.23, 0.72, 45.0, 150, 100, 0),
            ("برسيم جاف (دريس)", FeedCategory.BYPRODUCTS.value, 16.5, 0.75, 0.28, 0.60, 35.0, 170, 100, 0),
            ("مولاس قصب السكر", FeedCategory.BYPRODUCTS.value, 4.0, 0.05, 0.02, 0.95, 50.0, 120, 100, 0),
            ("تبن قمح", FeedCategory.BYPRODUCTS.value, 3.2, 0.08, 0.04, 0.35, 18.0, 80, 100, 0),
            ("سيلاج ذرة", FeedCategory.BYPRODUCTS.value, 8.0, 0.22, 0.14, 0.68, 50.0, 180, 100, 0),
            ("تفل البنجر المجفف", FeedCategory.BYPRODUCTS.value, 8.0, 0.42, 0.12, 0.75, 58.0, 230, 100, 0),
            
            # ═══════════════════════════════════════════════════════════════════
            # 🧂 الأملاح والمعادن (Minerals & Salts)
            # ═══════════════════════════════════════════════════════════════════
            ("ملح الطعام", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 30, 5, 0.5),
            ("الحجر الجيري", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 40, 8, 0.5),
            ("فوسفات ثنائي الكالسيوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 280, 3, 0.5),
            ("بيكربونات الصوديوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 340, 2, 0.1),
            ("أكسيد المغنيسيوم", FeedCategory.MINERALS.value, 0, 0, 0, 0, 0, 230, 2, 0.1),
            
            # ═══════════════════════════════════════════════════════════════════
            # 💊 الإضافات والإنزيمات (Additives & Enzymes)
            # ═══════════════════════════════════════════════════════════════════
            ("بريمكس دواجن لاحم", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25),
            ("بريمكس دواجن بياض", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25),
            ("بريمكس مجترات", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 230, 1, 0.25),
            ("إنزيم الفايتيز", FeedCategory.ADDITIVES.value, 0, 0, 0, 0.95, 0, 230, 0.5, 0.05),
            ("إنزيم NSP", FeedCategory.ADDITIVES.value, 0, 0, 0, 0.90, 0, 230, 0.5, 0.05),
            ("مضاد سموم فطرية", FeedCategory.ADDITIVES.value, 0, 0, 0, 0, 0, 950, 0.5, 0.1),
            ("مستخلص خمائر (MOS)", FeedCategory.ADDITIVES.value, 12.0, 0.30, 0.10, 0.50, 10.0, 350, 0.5, 0.1),
            
            # ═══════════════════════════════════════════════════════════════════
            # 🧪 الأحماض الأمينية البلورية (Crystalline Amino Acids)
            # ═══════════════════════════════════════════════════════════════════
            ("ليسين نقي (L-Lysine)", FeedCategory.ADDITIVES.value, 94.0, 78.0, 0, 1.00, 0, 230, 0.5, 0.05),
            ("ميثيونين نقي (DL-Met)", FeedCategory.ADDITIVES.value, 58.0, 0, 99.0, 1.00, 0, 230, 0.5, 0.05),
            ("ثريونين نقي", FeedCategory.ADDITIVES.value, 72.0, 0, 0, 1.00, 0, 230, 0.5, 0.05),
        ]
        
        for feed in feeds_data:
            cursor.execute('''
                INSERT INTO feeds (name, category, protein, lysine, methionine, digestibility, energy, price, max_limit, min_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', feed)
            
            # إضافة المخزون الافتراضي لكل مادة
            feed_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO inventory (feed_id, quantity, critical_level)
                VALUES (?, ?, ?)
            ''', (feed_id, 10.0, 2.0))
    
    @lru_cache(maxsize=128)
    def get_all_feeds(self) -> pd.DataFrame:
        """الحصول على جميع المواد العلفية مع التخزين المؤقت"""
        with self.get_connection() as conn:
            query = '''
                SELECT f.*, i.quantity as stock, i.critical_level
                FROM feeds f
                LEFT JOIN inventory i ON f.id = i.feed_id
                WHERE f.is_active = 1
                ORDER BY f.category, f.name
            '''
            return pd.read_sql_query(query, conn)
    
    def get_feed_by_id(self, feed_id: int) -> Optional[Dict]:
        """الحصول على مادة علفية بالمعرف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_feed(self, feed_data: Dict) -> int:
        """إضافة مادة علفية جديدة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feeds (name, category, protein, lysine, methionine, digestibility, energy, price, max_limit, min_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feed_data['name'], feed_data['category'], feed_data['protein'],
                feed_data.get('lysine', 0), feed_data.get('methionine', 0),
                feed_data.get('digestibility', 0.85), feed_data.get('energy', 0),
                feed_data['price'], feed_data.get('max_limit', 100), feed_data.get('min_limit', 0)
            ))
            feed_id = cursor.lastrowid
            cursor.execute('INSERT INTO inventory (feed_id, quantity) VALUES (?, ?)', (feed_id, 0))
            conn.commit()
            self.get_all_feeds.cache_clear()
            return feed_id
    
    def update_feed(self, feed_id: int, feed_data: Dict) -> bool:
        """تحديث بيانات مادة علفية"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE feeds 
                SET name = ?, category = ?, protein = ?, lysine = ?, methionine = ?,
                    digestibility = ?, energy = ?, price = ?, max_limit = ?, min_limit = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                feed_data['name'], feed_data['category'], feed_data['protein'],
                feed_data.get('lysine', 0), feed_data.get('methionine', 0),
                feed_data.get('digestibility', 0.85), feed_data.get('energy', 0),
                feed_data['price'], feed_data.get('max_limit', 100), feed_data.get('min_limit', 0),
                feed_id
            ))
            conn.commit()
            self.get_all_feeds.cache_clear()
            return cursor.rowcount > 0
    
    def update_stock(self, feed_id: int, quantity: float, operation: str = 'set') -> bool:
        """تحديث المخزون (إضافة، خصم، تعيين)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE feed_id = ?", (feed_id,))
            row = cursor.fetchone()
            
            if not row:
                cursor.execute("INSERT INTO inventory (feed_id, quantity) VALUES (?, ?)", (feed_id, 0))
                current = 0
            else:
                current = row['quantity']
            
            if operation == 'add':
                new_quantity = current + quantity
            elif operation == 'deduct':
                new_quantity = max(0, current - quantity)
            else:
                new_quantity = max(0, quantity)
            
            cursor.execute('''
                UPDATE inventory SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                WHERE feed_id = ?
            ''', (new_quantity, feed_id))
            conn.commit()
            
            # تسجيل في سجل المراجعة
            self.log_audit(None, 'STOCK_UPDATE', 'inventory', feed_id, 
                          f"Updated stock from {current} to {new_quantity}")
            return True
    
    def save_formula(self, formula: FeedFormula) -> int:
        """حفظ التركيبة العلفية"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO formulas (name, ingredients, total_cost, protein, digestible_protein, energy, lysine, methionine, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                formula.name, json.dumps(formula.ingredients), formula.total_cost,
                formula.protein, formula.digestible_protein, formula.energy,
                formula.lysine, formula.methionine, formula.created_by
            ))
            formula_id = cursor.lastrowid
            conn.commit()
            return formula_id
    
    def get_formulas(self, limit: int = 50) -> pd.DataFrame:
        """الحصول على التركيبات السابقة"""
        with self.get_connection() as conn:
            query = '''
                SELECT * FROM formulas 
                ORDER BY created_at DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def log_audit(self, user_id: Optional[int], action: str, entity_type: str, 
                  entity_id: Optional[int], details: str = ""):
        """تسجيل حدث في سجل المراجعة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, entity_type, entity_id, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, action, entity_type, entity_id, details))
            conn.commit()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """مصادقة المستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
            user = cursor.fetchone()
            
            if user and verify_password(password, user['password_hash'], user['password_salt']):
                # تحديث آخر تسجيل دخول
                cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
                conn.commit()
                return dict(user)
            return None

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🧮 محرك الحسابات الرياضية والبرمجة الخطية
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

class OptimizationEngine:
    """محرك الاستمثال الخطي لتركيب الأعلاف بأقل تكلفة"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def calculate_nutritional_ratios(self, ingredients: List[FeedIngredient], 
                                      percentages: List[float]) -> Dict[str, float]:
        """
        حساب النسب الغذائية للتركيبة
        """
        total_percent = sum(percentages)
        if abs(total_percent - 100) > 0.01:
            raise ValueError(f"مجموع النسب يجب أن يكون 100%، ولكن هو {total_percent}%")
        
        results = {
            'protein': 0.0,
            'digestible_protein': 0.0,
            'energy': 0.0,
            'lysine': 0.0,
            'digestible_lysine': 0.0,
            'methionine': 0.0,
            'digestible_methionine': 0.0,
            'total_cost': 0.0
        }
        
        for ingredient, pct in zip(ingredients, percentages):
            ratio = pct / 100
            results['protein'] += ingredient.protein * ratio
            results['digestible_protein'] += ingredient.digestible_protein * ratio
            results['energy'] += ingredient.energy * ratio
            results['lysine'] += ingredient.lysine * ratio
            results['digestible_lysine'] += ingredient.digestible_lysine * ratio
            results['methionine'] += ingredient.methionine * ratio
            results['digestible_methionine'] += ingredient.digestible_methionine * ratio
            results['total_cost'] += ingredient.price * ratio
        
        return results
    
    def optimize_least_cost(self,
                           ingredients: List[FeedIngredient],
                           target_protein: float,
                           target_energy: Optional[float] = None,
                           target_lysine: Optional[float] = None,
                           target_methionine: Optional[float] = None,
                           use_digestible: bool = True,
                           max_iterations: int = 1000) -> Dict[str, Any]:
        """
        تحسين التركيبة بأقل تكلفة باستخدام البرمجة الخطية
        
        المعلمات:
        - ingredients: قائمة المواد العلفية
        - target_protein: نسبة البروتين المستهدفة
        - target_energy: معادل النشاء المستهدف (اختياري)
        - target_lysine: الليسين المستهدف (اختياري)
        - target_methionine: الميثيونين المستهدف (اختياري)
        - use_digestible: استخدام القيم المهضومة أم الخام
        """
        
        n = len(ingredients)
        
        # دالة الهدف: تقليل التكلفة
        c = [ing.price for ing in ingredients]
        
        # قيود المساواة
        A_eq = []
        b_eq = []
        
        # القيد الأول: مجموع النسب = 100%
        A_eq.append([1.0] * n)
        b_eq.append(100.0)
        
        # القيد الثاني: البروتين المستهدف        if use_digestible:
            protein_coeffs = [ing.digestible_protein for ing in ingredients]
        else:
            protein_coeffs = [ing.protein for ing in ingredients]
        A_eq.append(protein_coeffs)
        b_eq.append(target_protein)
        
        # القيد الثالث: الطاقة المستهدفة (إذا وجد)
        if target_energy is not None:
            A_eq.append([ing.energy for ing in ingredients])
            b_eq.append(target_energy)
        
        # قيود عدم المساواة (الحدود الدنيا والعليا)
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
        
        # حدود المكونات
        bounds = [(ing.min_limit, ing.max_limit) for ing in ingredients]
        
        # حل مشكلة البرمجة الخطية
        try:
            result = linprog(
                c,
                A_ub=A_ub if A_ub else None,
                b_ub=b_ub if b_ub else None,
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method='highs',
                options={'maxiter': max_iterations}
            )
            
            if result.success:
                percentages = result.x
                nutritional_values = self.calculate_nutritional_ratios(ingredients, percentages)
                
                return {
                    'success': True,
                    'percentages': {ing.name: pct for ing, pct in zip(ingredients, percentages) if pct > 0.01},
                    'total_cost': nutritional_values['total_cost'],
                    'protein': nutritional_values['protein'],
                    'digestible_protein': nutritional_values['digestible_protein'],
                    'energy': nutritional_values['energy'],
                    'lysine': nutritional_values['lysine'],
                    'digestible_lysine': nutritional_values['digestible_lysine'],
                    'methionine': nutritional_values['methionine'],
                    'digestible_methionine': nutritional_values['digestible_methionine'],
                    'iterations': result.nit if hasattr(result, 'nit') else 0,
                    'status': result.status
                }
            else:
                return {
                    'success': False,
                    'message': f"لم يتم إيجاد حل: {result.message}",
                    'status': result.status
                }
                
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {
                'success': False,
                'message': f"خطأ في الحسابات: {str(e)}",
                'status': -1
            }
    
    def get_production_requirements(self, sector: ProductionSector, 
                                    weight_kg: float = 0,
                                    age_days: int = 0) -> ProductionRequirement:
        """
        الحصول على الاحتياجات الإنتاجية حسب القطاع والوزن والعمر
        """
        requirements_map = {
            ProductionSector.POULTRY_BROILER: {
                'protein': 22.0,
                'energy': 75.0,
                'lysine': 1.20,
                'methionine': 0.50,
                'ingredients': ['ذرة صفراء', 'كسب فول صويا 48%', 'بريمكس دواجن لاحم', 'ملح الطعام', 'الحجر الجيري']
            },
            ProductionSector.POULTRY_LAYER: {
                'protein': 16.5,
                'energy': 70.0,
                'lysine': 0.85,
                'methionine': 0.38,
                'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'بريمكس دواجن بياض', 'ملح الطعام', 'الحجر الجيري']
            },
            ProductionSector.DAIRY_CATTLE: {
                'protein': 16.0,
                'energy': 68.0,
                'lysine': 1.10,
                'methionine': 0.35,
                'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'بريمكس مجترات', 'ملح الطعام', 'بيكربونات الصوديوم']
            },
            ProductionSector.BEEF_CATTLE: {
                'protein': 12.5,
                'energy': 65.0,
                'lysine': 0.85,
                'methionine': 0.28,
                'ingredients': ['ذرة صفراء', 'كسب عباد الشمس', 'بريمكس مجترات', 'ملح الطعام']
            },
            ProductionSector.SHEEP_GOAT: {
                'protein': 14.0,
                'energy': 62.0,
                'lysine': 0.90,
                'methionine': 0.30,
                'ingredients': ['شعير', 'كسب عباد الشمس', 'نخالة قمح', 'ملح الطعام']
            },
            ProductionSector.HORSES: {
                'protein': 12.0,
                'energy': 60.0,
                'lysine': 0.70,
                'methionine': 0.25,
                'ingredients': ['شوفان', 'شعير', 'نخالة قمح', 'ملح الطعام']
            },
            ProductionSector.FISH: {
                'protein': 28.0,
                'energy': 70.0,
                'lysine': 1.80,
                'methionine': 0.70,
                'ingredients': ['مسحوق أسماك 60%', 'كسب فول صويا 48%', 'كسب جلوتين الذرة']
            },
            ProductionSector.GENERAL: {
                'protein': 14.0,
                'energy': 65.0,
                'lysine': 0.80,
                'methionine': 0.28,
                'ingredients': ['ذرة صفراء', 'كسب فول صويا 44%', 'ملح الطعام']
            }
        }
        
        req = requirements_map.get(sector, requirements_map[ProductionSector.GENERAL])
        
        # تعديل الاحتياجات حسب الوزن والعمر
        protein_adj = req['protein']
        energy_adj = req['energy']
        
        if weight_kg > 0:
            if sector in [ProductionSector.POULTRY_BROILER, ProductionSector.POULTRY_LAYER]:
                if weight_kg < 1.0:
                    protein_adj += 2
                elif weight_kg > 2.0:
                    protein_adj -= 1
            elif sector in [ProductionSector.BEEF_CATTLE, ProductionSector.DAIRY_CATTLE]:
                if weight_kg < 200:
                    protein_adj += 1
                elif weight_kg > 500:
                    protein_adj -= 1
        
        return ProductionRequirement(
            sector=sector,
            protein_requirement=protein_adj,
            energy_requirement=energy_adj,
            lysine_requirement=req['lysine'],
            methionine_requirement=req['methionine'],
            recommended_ingredients=req['ingredients']
        )

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 📊 دوال التحليل والإحصاء
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def analyze_cost_efficiency(ingredients: List[FeedIngredient]) -> Dict[str, Any]:
    """تحليل كفاءة التكلفة للمواد العلفية"""
    
    results = {
        'protein_cost_efficiency': [],
        'energy_cost_efficiency': [],
        'recommendations': []
    }
    
    for ing in ingredients:
        if ing.protein > 0:
            protein_cost_per_kg = ing.price / (ing.protein * 10)  # تكلفة البروتين لكل كجم
            results['protein_cost_efficiency'].append({
                'name': ing.name,
                'value': protein_cost_per_kg,
                'protein': ing.protein
            })
        
        if ing.energy > 0 and ing.price > 0:
            energy_cost_per_unit = ing.price / ing.energy
            results['energy_cost_efficiency'].append({
                'name': ing.name,
                'value': energy_cost_per_unit,
                'energy': ing.energy
            })
    
    # ترتيب حسب الكفاءة
    results['protein_cost_efficiency'].sort(key=lambda x: x['value'])
    results['energy_cost_efficiency'].sort(key=lambda x: x['value'])
    
    # توصيات
    if results['protein_cost_efficiency']:
        best_protein = results['protein_cost_efficiency'][0]
        results['recommendations'].append(f"أفضل مصدر بروتين من حيث التكلفة: {best_protein['name']}")
    
    if results['energy_cost_efficiency']:
        best_energy = results['energy_cost_efficiency'][0]
        results['recommendations'].append(f"أفضل مصدر طاقة من حيث التكلفة: {best_energy['name']}")
    
    return results

def predict_growth_rate(protein_level: float, energy_level: float, 
                        species: str = "broiler") -> float:
    """
    التنبؤ بمعدل النمو بناءً على التركيبة الغذائية
    """
    if species == "broiler":
        base_growth = 45  # جرام/يوم
        protein_factor = (protein_level - 22) * 2
        energy_factor = (energy_level - 75) * 0.5
    elif species == "layer":
        base_growth = 15
        protein_factor = (protein_level - 16.5) * 1.5
        energy_factor = (energy_level - 70) * 0.3
    elif species == "cattle":
        base_growth = 800
        protein_factor = (protein_level - 14) * 30
        energy_factor = (energy_level - 65) * 5
    else:
        base_growth = 30
        protein_factor = (protein_level - 16) * 1.5
        energy_factor = (energy_level - 65) * 0.5
    
    predicted = base_growth + max(-20, min(20, protein_factor)) + max(-10, min(10, energy_factor))
    return max(0, predicted)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🎨 واجهة المستخدم والتصورات البيانية
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def create_cost_comparison_chart(ingredients: List[FeedIngredient]) -> go.Figure:
    """إنشاء رسم بياني لمقارنة التكاليف"""
    
    fig = go.Figure()
    
    names = [ing.name for ing in ingredients[:10]]
    prices = [ing.price for ing in ingredients[:10]]
    proteins = [ing.protein for ing in ingredients[:10]]
    
    fig.add_trace(go.Bar(
        x=names,
        y=prices,
        name='السعر ($/طن)',
        marker_color='#2e7d32',
        text=prices,
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=names,
        y=proteins,
        name='البروتين (%)',
        yaxis='y2',
        marker_color='#1565c0',
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='مقارنة أسعار ومحتوى البروتين للمواد العلفية',
        xaxis_title='المادة العلفية',
        yaxis_title='السعر ($/طن)',
        yaxis2=dict(title='البروتين (%)', overlaying='y', side='right'),
        template='plotly_white',
        height=500
    )
    
    return fig

def create_formula_pie_chart(formula: Dict[str, float]) -> go.Figure:
    """إنشاء رسم بياني دائري لنسب التركيبة"""
    
    fig = go.Figure(data=[go.Pie(
        labels=list(formula.keys()),
        values=list(formula.values()),
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title='توزيع مكونات التركيبة العلفية',
        height=450,
        annotations=[dict(text='التركيبة', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

def create_nutritional_radar_chart(nutritional_values: Dict[str, float]) -> go.Figure:
    """إنشاء مخطط رادار للقيم الغذائية"""
    
    categories = ['البروتين', 'البروتين المهضوم', 'الطاقة', 'الليسين', 'الميثيونين']
    values = [
        nutritional_values.get('protein', 0),
        nutritional_values.get('digestible_protein', 0),
        nutritional_values.get('energy', 0) / 20,  # مقياس
        nutritional_values.get('lysine', 0) * 10,   # مقياس
        nutritional_values.get('methionine', 0) * 10 # مقياس
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker_color='#2e7d32'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values) * 1.2])),
        title='القيم الغذائية للتركيبة',
        height=450,
        showlegend=False
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🚀 واجهة Streamlit الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def init_session_state():
    """تهيئة حالة الجلسة"""
    defaults = {
        'logged_in': False,
        'user': None,
        'role': None,
        'user_id': None,
        'last_formula': None,
        'last_cost': 0,
        'last_protein': 0,
        'dark_mode': False,
        'language': 'ar',
        'session_id': secrets.token_hex(16)
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def apply_custom_css():
    """تطبيق تنسيقات CSS المخصصة"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #2e7d32;
        margin: 15px 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #1565c0;
        margin: 15px 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 20px;
        border-radius: 12px;
        border-right: 5px solid #ef6c00;
        margin: 15px 0;
    }
    
    .ingredient-item {
        background: #f5f5f5;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    
    .ingredient-item:hover {
        transform: translateX(-5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .formula-result {
        background: #f1f8e9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-right: 4px solid #2e7d32;
    }
    
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        text-align: center;
        font-size: 12px;
        color: #888;
        padding: 10px;
        background: transparent;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2e7d32;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    button.stButton > div {
        border-radius: 8px;
    }
    
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    hr {
        margin: 20px 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #2e7d32, transparent);
    }
    </style>
    """, unsafe_allow_html=True)

def login_screen():
    """شاشة تسجيل الدخول"""
    
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🌾 منصة تاور العلمية</h1>
        <p>للانتاج الحيواني وتركيب الاعلاف</p>
        <p style="font-size: 14px; margin-top: 10px;">الاختصاصي م. عبد القادر إسماعيل تاور</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("#### 🔐 بوابة الدخول الآمنة")
        
        username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
        password = st.text_input("🔑 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                if username and password:
                    user = db_manager.authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user['full_name']
                        st.session_state.role = user['role']
                        st.session_state.user_id = user['id']
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.warning("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # معلومات المساعدة
        with st.expander("ℹ️ معلومات الدخول"):
            st.markdown("""
            **أكواد الدخول الافتراضية:**
            - **المالك:** username: `owner` / password: `202687`
            - **المختص:** username: `specialist` / password: `2020`
            - **المربي:** username: `breeder` / password: `2026`
            """)

def main_dashboard():
    """لوحة التحكم الرئيسية"""
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 15px;">
            <div style="background: #2e7d32; width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                <span style="font-size: 30px;">🌾</span>
            </div>
            <h3 style="margin: 0; color: #2e7d32;">{st.session_state.user}</h3>
            <p style="color: #888; font-size: 12px;">{st.session_state.role}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # قائمة التنقل
        menu = {
            "home": "🏠 الرئيسية",
            "formulator": "🔬 تركيب الأعلاف",
            "inventory": "📦 إدارة المخزون",
            "history": "📊 التركيبات السابقة",
            "analysis": "📈 التحليلات",
            "help": "📚 المساعدة"
        }
        
        for key, label in menu.items():
            if st.button(label, key=f"menu_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()
        
        st.markdown("---")
        
        # إحصائيات سريعة
        feeds_df = db_manager.get_all_feeds()
        st.metric("📦 المواد العلفية", len(feeds_df))
        
        formulas_df = db_manager.get_formulas(100)
        st.metric("📝 التركيبات المحفوظة", len(formulas_df))
        
        if 'last_cost' in st.session_state and st.session_state.last_cost > 0:
            st.metric("💰 آخر تكلفة", f"${st.session_state.last_cost:.2f}")
        
        st.markdown("---")
        
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in ['logged_in', 'user', 'role', 'user_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("""
        <div class="sidebar-footer">
            © 2026 منصة تاور العلمية<br>
            الاختصاصي م. عبد القادر إسماعيل تاور
        </div>
        """, unsafe_allow_html=True)
    
    # المحتوى الرئيسي
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page == 'home':
        render_home_page()
    elif current_page == 'formulator':
        render_formulator_page()
    elif current_page == 'inventory':
        render_inventory_page()
    elif current_page == 'history':
        render_history_page()
    elif current_page == 'analysis':
        render_analysis_page()
    else:
        render_help_page()

def render_home_page():
    """صفحة الرئيسية"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);">
        <h1>🏠 لوحة التحكم الرئيسية</h1>
        <p>مرحباً بك في منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف</p>
    </div>
    """, unsafe_allow_html=True)
    
    # إحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    feeds_df = db_manager.get_all_feeds()
    formulas_df = db_manager.get_formulas(100)
    
    total_feeds = len(feeds_df)
    total_formulas = len(formulas_df)
    total_cost = formulas_df['total_cost'].sum() if not formulas_df.empty else 0
    avg_cost = formulas_df['total_cost'].mean() if not formulas_df.empty else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_feeds}</div>
            <div class="metric-label">📦 مواد علفية</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_formulas}</div>
            <div class="metric-label">📝 تركيبة محفوظة</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_cost:,.0f}</div>
            <div class="metric-label">💰 إجمالي التكاليف</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${avg_cost:.0f}</div>
            <div class="metric-label">📊 متوسط التكلفة</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # الرسم البياني لتوزيع المواد
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 توزيع المواد حسب التصنيف")
        category_counts = feeds_df['category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index, hole=0.3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.subheader("💰 أعلى 10 مواد من حيث السعر")
        top_price = feeds_df.nlargest(10, 'price')[['name', 'price']]
        fig = px.bar(top_price, x='name', y='price', color='price', color_continuous_scale='Greens')
        fig.update_layout(xaxis_title="المادة", yaxis_title="السعر ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # آخر التركيبات
    st.subheader("📋 آخر التركيبات المحفوظة")
    if not formulas_df.empty:
        display_df = formulas_df[['name', 'total_cost', 'protein', 'created_at']].head(5)
        display_df.columns = ['الاسم', 'التكلفة ($)', 'البروتين (%)', 'تاريخ الإنشاء']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("لا توجد تركيبات محفوظة بعد. قم بإنشاء تركيبة جديدة في تبويب تركيب الأعلاف.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_formulator_page():
    """صفحة تركيب الأعلاف"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🔬 محرك تركيب الأعلاف الذكي</h1>
        <p>نظام الاستمثال الخطي المتقدم (Least-Cost Formulation)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل البيانات
    feeds_df = db_manager.get_all_feeds()
    
    # إعدادات التركيب
    col_settings1, col_settings2 = st.columns(2)
    
    with col_settings1:
        sector = st.selectbox(
            "🐏 القطاع الإنتاجي",
            [s.value for s in ProductionSector]
        )
        
        target_protein = st.slider(
            "🎯 نسبة البروتين المستهدفة (%)",
            min_value=5.0, max_value=40.0, value=16.0, step=0.5
        )
        
        use_digestible = st.toggle(
            "🧬 استخدام البروتين المهضوم (DP)",
            value=True,
            help="البروتين المهضوم يعطي دقة علمية أعلى"
        )
    
    with col_settings2:
        target_energy = st.number_input(
            "⚡ معادل النشاء المستهدف (SE)",
            min_value=0.0, max_value=100.0, value=65.0, step=1.0
        ) if st.checkbox("تحديد معادل النشاء") else None
        
        target_lysine = st.number_input(
            "🧪 الليسين المستهدف (%)",
            min_value=0.0, max_value=5.0, value=0.85, step=0.05
        ) if st.checkbox("تحديد الليسين") else None
        
        target_methionine = st.number_input(
            "🧪 الميثيونين المستهدف (%)",
            min_value=0.0, max_value=3.0, value=0.35, step=0.05
        ) if st.checkbox("تحديد الميثيونين") else None
    
    st.markdown("---")
    
    # اختيار المكونات
    st.subheader("✅ اختيار المكونات العلفية")
    
    # فلترة حسب القطاع
    production_req = optimization_engine.get_production_requirements(ProductionSector(sector))
    
    with st.expander("💡 توصيات للقطاع", expanded=False):
        st.markdown(f"""
        - **البروتين الموصى به:** {production_req.protein_requirement}%
        - **معادل النشاء الموصى به:** {production_req.energy_requirement}
        - **المكونات الموصى بها:** {', '.join(production_req.recommended_ingredients)}
        """)
    
    # عرض المكونات
    selected_ingredients = []
    
    categories = feeds_df['category'].unique()
    
    for category in categories:
        with st.expander(f"📁 {category}", expanded=category in ["🌾 حبوب ومصادر طاقة", "🥜 أكساب ومصادر بروتين"]):
            category_feeds = feeds_df[feeds_df['category'] == category]
            cols = st.columns(3)
            
            for idx, (_, row) in enumerate(category_feeds.iterrows()):
                with cols[idx % 3]:
                    default_checked = row['name'] in production_req.recommended_ingredients
                    if st.checkbox(f"{row['name']} (المخزون: {row['stock']:.1f} طن)", 
                                   key=f"select_{row['id']}", value=default_checked):
                        
                        # عرض السعر مع إمكانية التعديل للمالك
                        if st.session_state.role == UserRole.OWNER.value:
                            price = st.number_input(
                                f"سعر {row['name']} ($/طن)",
                                value=float(row['price']),
                                key=f"price_{row['id']}",
                                step=5.0
                            )
                        else:
                            price = row['price']
                            st.caption(f"💰 السعر: ${price:.0f}/طن")
                        
                        selected_ingredients.append({
                            'id': row['id'],
                            'name': row['name'],
                            'protein': row['protein'],
                            'digestibility': row['digestibility'],
                            'energy': row['energy'],
                            'lysine': row['lysine'],
                            'methionine': row['methionine'],
                            'price': price,
                            'min_limit': row['min_limit'],
                            'max_limit': row['max_limit']
                        })
    
    # زر التشغيل
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 تشغيل محرك الاستمثال الخطي", type="primary", use_container_width=True):
            if len(selected_ingredients) < 2:
                st.warning("⚠️ يرجى اختيار مكونين على الأقل")
            else:
                with st.spinner("🧮 جاري حساب التركيبة المثلى..."):
                    # تحويل القائمة إلى كائنات FeedIngredient
                    ingredients = [
                        FeedIngredient(
                            id=ing['id'],
                            name=ing['name'],
                            category="",
                            protein=ing['protein'],
                            lysine=ing['lysine'],
                            methionine=ing['methionine'],
                            digestibility=ing['digestibility'],
                            energy=ing['energy'],
                            price=ing['price'],
                            max_limit=ing['max_limit'],
                            min_limit=ing['min_limit']
                        ) for ing in selected_ingredients
                    ]
                    
                    result = optimization_engine.optimize_least_cost(
                        ingredients=ingredients,
                        target_protein=target_protein,
                        target_energy=target_energy,
                        target_lysine=target_lysine,
                        target_methionine=target_methionine,
                        use_digestible=use_digestible
                    )
                    
                    if result['success']:
                        st.balloons()
                        st.markdown('<div class="success-card">', unsafe_allow_html=True)
                        st.success("✅ تم حساب التركيبة المثلى بنجاح!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # عرض النتائج
                        col_results1, col_results2 = st.columns(2)
                        
                        with col_results1:
                            st.subheader("📝 المقادير لكل طن")
                            
                            for name, pct in result['percentages'].items():
                                kg = pct * 10
                                st.markdown(f"""
                                <div class="formula-result">
                                    <strong>🌾 {name}</strong><br>
                                    <span style="font-size: 24px; font-weight: bold; color: #2e7d32;">{pct:.1f}%</span>
                                    <span style="font-size: 14px; color: #666;"> → {kg:.1f} كجم</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.session_state.last_formula = result['percentages']
                            st.session_state.last_cost = result['total_cost']
                            st.session_state.last_protein = result['protein']
                        
                        with col_results2:
                            st.subheader("💰 التكاليف والمواصفات")
                            
                            st.metric("تكلفة الطن", f"${result['total_cost']:.2f}")
                            st.metric("البروتين الكلي", f"{result['protein']:.2f}%")
                            st.metric("البروتين المهضوم", f"{result['digestible_protein']:.2f}%")
                            st.metric("معادل النشاء", f"{result['energy']:.1f}")
                            
                            # رسم بياني دائري
                            fig = create_formula_pie_chart(result['percentages'])
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # حفظ التركيبة
                        formula = FeedFormula(
                            name=f"خلطة {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            ingredients=result['percentages'],
                            total_cost=result['total_cost'],
                            protein=result['protein'],
                            digestible_protein=result['digestible_protein'],
                            energy=result['energy'],
                            lysine=result['lysine'],
                            methionine=result['methionine'],
                            created_by=st.session_state.user
                        )
                        formula_id = db_manager.save_formula(formula)
                        st.success(f"✅ تم حفظ التركيبة بنجاح (الرقم: {formula_id})")
                        
                    else:
                        st.error(f"❌ {result['message']}")
                        
                        # تقديم اقتراحات
                        st.markdown("""
                        <div class="warning-card">
                            <strong>💡 اقتراحات لحل المشكلة:</strong><br>
                            1. أضف المزيد من المكونات - خاصة مصادر البروتين<br>
                            2. خفف نسبة البروتين المستهدفة قليلاً<br>
                            3. تأكد من صحة الأسعار المدخلة<br>
                            4. أضف مكونات بديلة مثل كسب عباد الشمس
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_inventory_page():
    """صفحة إدارة المخزون"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #ef6c00 0%, #f57c00 100%);">
        <h1>📦 إدارة المخزون والمستودعات</h1>
        <p>تتبع وإدارة المواد العلفية والمخزون</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل البيانات
    feeds_df = db_manager.get_all_feeds()
    
    # خصم سريع من آخر خلطة
    if st.session_state.last_formula:
        with st.expander("🔄 خصم مكونات آخر خلطة من المخزون", expanded=False):
            col_tons, col_btn = st.columns([2, 1])
            with col_tons:
                tons = st.number_input("الكمية المنتجة (طن):", min_value=0.1, value=1.0, step=0.5, key="deduct_tons")
            with col_btn:
                if st.button("تأكيد الخصم", type="primary"):
                    for name, pct in st.session_state.last_formula.items():
                        feed_row = feeds_df[feeds_df['name'] == name]
                        if not feed_row.empty:
                            feed_id = feed_row.iloc[0]['id']
                            qty_to_deduct = (pct / 100) * tons
                            db_manager.update_stock(feed_id, qty_to_deduct, 'deduct')
                    st.success(f"✅ تم خصم {tons} طن من المخزون")
                    st.rerun()
    
    st.markdown("---")
    
    # عرض المخزون الحالي
    st.subheader("📊 الأرصدة الحالية")
    
    # إضافة فلتر
    search = st.text_input("🔍 بحث", placeholder="ابحث عن مادة علفية...")
    
    filtered_df = feeds_df
    if search:
        filtered_df = feeds_df[feeds_df['name'].str.contains(search, na=False)]
    
    # عرض المخزون
    cols = st.columns(3)
    
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with cols[idx % 3]:
            stock = row['stock']
            name = row['name']
            
            if stock <= row['critical_level']:
                status = "🔴 حرج"
                color = "#ffebee"
                border = "#c62828"
            elif stock <= row['critical_level'] * 2:
                status = "🟡 منخفض"
                color = "#fff3e0"
                border = "#ef6c00"
            else:
                status = "🟢 جيد"
                color = "#e8f5e9"
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
                    db_manager.update_stock(row['id'], new_stock, 'set')
                    st.rerun()
                st.caption(f"⚠️ الحد الحرج: {row['critical_level']} طن")
            else:
                st.markdown(f"""
                <div style="background-color: {color}; padding: 12px; margin: 5px 0; border-radius: 10px; border-right: 4px solid {border};">
                    <strong>{name}</strong><br>
                    <span style="font-size: 20px; font-weight: bold;">{stock:.1f}</span>
                    <span style="font-size: 14px;"> طن</span><br>
                    <span style="font-size: 12px;">{status}</span>
                </div>
                "", unsafe_allow_html=True)
    
    # إضافة مادة جديدة للمالك
    if st.session_state.role == UserRole.OWNER.value:
        st.markdown("---")
        with st.expander("➕ إضافة مادة علفية جديدة", expanded=False):
            col_new1, col_new2 = st.columns(2)
            with col_new1:
                new_name = st.text_input("اسم المادة")
                new_category = st.selectbox("التصنيف", [c.value for c in FeedCategory])
                new_protein = st.number_input("البروتين (%)", min_value=0.0, max_value=100.0, value=0.0)
            
            with col_new2:
                new_price = st.number_input("السعر ($/طن)", min_value=0.0, value=100.0)
                new_energy = st.number_input("معادل النشاء (SE)", min_value=0.0, value=50.0)
                new_digestibility = st.slider("معامل الهضم", 0.0, 1.0, 0.85)
            
            if st.button("💾 إضافة المادة", type="primary"):
                if new_name:
                    feed_data = {
                        'name': new_name,
                        'category': new_category,
                        'protein': new_protein,
                        'lysine': 0,
                        'methionine': 0,
                        'digestibility': new_digestibility,
                        'energy': new_energy,
                        'price': new_price,
                        'max_limit': 100,
                        'min_limit': 0
                    }
                    db_manager.add_feed(feed_data)
                    st.success(f"✅ تم إضافة {new_name} بنجاح")
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_history_page():
    """صفحة التركيبات السابقة"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #6a1b9a 0%, #7b1fa2 100%);">
        <h1>📊 تاريخ التركيبات العلفية</h1>
        <p>جميع التركيبات المحفوظة سابقاً</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل التركيبات
    formulas_df = db_manager.get_formulas(100)
    
    if formulas_df.empty:
        st.info("ℹ️ لا توجد تركيبات محفوظة. قم بإنشاء تركيبة جديدة في تبويب تركيب الأعلاف.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # إضافة فلتر
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        date_filter = st.date_input("📅 تصفية حسب التاريخ", value=[])
    with col_filter2:
        cost_filter = st.slider("💰 تصفية حسب التكلفة", 0.0, float(formulas_df['total_cost'].max()), (0.0, float(formulas_df['total_cost'].max())))
    
    # تطبيق الفلاتر
    filtered_df = formulas_df.copy()
    if date_filter:
        filtered_df = filtered_df[pd.to_datetime(filtered_df['created_at']).dt.date.isin(date_filter)]
    filtered_df = filtered_df[(filtered_df['total_cost'] >= cost_filter[0]) & (filtered_df['total_cost'] <= cost_filter[1])]
    
    st.markdown(f"**📋 عدد التركيبات:** {len(filtered_df)}")
    
    # عرض التركيبات
    for _, row in filtered_df.iterrows():
        with st.expander(f"📅 {row['created_at']} - {row['name']} - ${row['total_cost']:.2f}"):
            ingredients = json.loads(row['ingredients'])
            
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.markdown("**المكونات:**")
                for name, pct in ingredients.items():
                    st.write(f"• {name}: {pct:.1f}% ({pct*10:.1f} كجم)")
            
            with col_exp2:
                st.markdown("**المواصفات:**")
                st.write(f"💰 التكلفة: ${row['total_cost']:.2f}/طن")
                st.write(f"🧬 البروتين: {row['protein']:.2f}%")
                st.write(f"⚡ الطاقة: {row['energy']:.1f} SE")
                st.write(f"🧪 الليسين: {row['lysine']:.2f}%")
                st.write(f"🧪 الميثيونين: {row['methionine']:.2f}%")
            
            # زر إعادة الاستخدام
            if st.button(f"🔄 استخدام هذه التركيبة", key=f"reuse_{row['id']}"):
                st.session_state.last_formula = ingredients
                st.session_state.last_cost = row['total_cost']
                st.session_state.last_protein = row['protein']
                st.session_state.current_page = 'formulator'
                st.success("تم تحميل التركيبة بنجاح!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analysis_page():
    """صفحة التحليلات والتقارير"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #00838f 0%, #0097a7 100%);">
        <h1>📈 التحليلات والتقارير المتقدمة</h1>
        <p>تحليل البيانات وإحصائيات المنصة</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تحميل البيانات
    feeds_df = db_manager.get_all_feeds()
    formulas_df = db_manager.get_formulas(500)
    
    # تحليل كفاءة التكلفة
    if not feeds_df.empty:
        ingredients = []
        for _, row in feeds_df.iterrows():
            ingredients.append(FeedIngredient(
                id=row['id'], name=row['name'], category=row['category'],
                protein=row['protein'], lysine=row['lysine'], methionine=row['methionine'],
                digestibility=row['digestibility'], energy=row['energy'],
                price=row['price'], max_limit=row['max_limit'], min_limit=row['min_limit'],
                stock=row['stock']
            ))
        
        efficiency = analyze_cost_efficiency(ingredients)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💵 كفاءة تكلفة البروتين")
            if efficiency['protein_cost_efficiency']:
                top_protein = efficiency['protein_cost_efficiency'][:5]
                for item in top_protein:
                    st.write(f"**{item['name']}:** ${item['value']:.2f} / كجم بروتين")
        
        with col2:
            st.subheader("⚡ كفاءة تكلفة الطاقة")
            if efficiency['energy_cost_efficiency']:
                top_energy = efficiency['energy_cost_efficiency'][:5]
                for item in top_energy:
                    st.write(f"**{item['name']}:** ${item['value']:.2f} / وحدة طاقة")
        
        if efficiency['recommendations']:
            st.markdown("---")
            st.subheader("💡 التوصيات")
            for rec in efficiency['recommendations']:
                st.info(rec)
    
    # تحليل التركيبات
    if not formulas_df.empty:
        st.markdown("---")
        st.subheader("📊 تحليل التركيبات السابقة")
        
        col_trend1, col_trend2 = st.columns(2)
        
        with col_trend1:
            # اتجاه التكاليف
            fig = px.line(formulas_df, x='created_at', y='total_cost', 
                         title='اتجاه تكاليف التركيبات', markers=True)
            fig.update_layout(xaxis_title="التاريخ", yaxis_title="التكلفة ($)", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_trend2:
            # توزيع البروتين
            fig = px.histogram(formulas_df, x='protein', nbins=20,
                              title='توزيع نسب البروتين في التركيبات')
            fig.update_layout(xaxis_title="البروتين (%)", yaxis_title="العدد", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # العلاقة بين التكلفة والبروتين
        st.subheader("🔬 العلاقة بين التكلفة ونسبة البروتين")
        fig = px.scatter(formulas_df, x='protein', y='total_cost',
                        title='التكلفة مقابل البروتين',
                        labels={'protein': 'البروتين (%)', 'total_cost': 'التكلفة ($)'},
                        trendline="ols")
        st.plotly_chart(fig, use_container_width=True)
        
        # إحصائيات إضافية
        st.markdown("---")
        st.subheader("📋 الإحصائيات الموجزة")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("متوسط التكلفة", f"${formulas_df['total_cost'].mean():.2f}")
        with stat_col2:
            st.metric("أقل تكلفة", f"${formulas_df['total_cost'].min():.2f}")
        with stat_col3:
            st.metric("أعلى تكلفة", f"${formulas_df['total_cost'].max():.2f}")
        with stat_col4:
            st.metric("متوسط البروتين", f"{formulas_df['protein'].mean():.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_help_page():
    """صفحة المساعدة والدليل"""
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(135deg, #37474f 0%, #455a64 100%);">
        <h1>📚 المساعدة والدليل الشامل</h1>
        <p>دليل استخدام المنصة والمصطلحات العلمية</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📖 دليل الاستخدام", "🔑 الصلاحيات", "🧬 المصطلحات العلمية", "❓ الأسئلة الشائعة"])
    
    with tabs[0]:
        st.markdown("""
        ### 🎯 كيفية استخدام منصة تاور العلمية
        
        #### الخطوة 1: تسجيل الدخول
        - استخدم اسم المستخدم وكلمة المرور المخصصين لك
        - تتوفر ثلاث صلاحيات: مالك، مختص، مربي
        
        #### الخطوة 2: اختيار القطاع الإنتاجي
        - اختر نوع الحيوان (دواجن، أبقار، أغنام، خيول، أسماك)
        - سيتم عرض التوصيات المناسبة لكل قطاع
        
        #### الخطوة 3: اختيار المكونات
        - اختر المواد العلفية المتوفرة لديك
        - يمكن تعديل الأسعار حسب السوق المحلي
        
        #### الخطوة 4: تحديد المواصفات
        - حدد نسبة البروتين المستهدفة
        - يمكن تحديد معادل النشاء والأحماض الأمينية
        
        #### الخطوة 5: تشغيل المحرك
        - اضغط على زر "تشغيل محرك الاستمثال الخطي"
        - ستظهر التركيبة المثلى بأقل تكلفة
        
        #### الخطوة 6: حفظ وتطبيق النتيجة
        - يمكن حفظ التركيبة للاستخدام المستقبلي
        - يمكن خصم المكونات من المخزون تلقائياً
        """)
    
    with tabs[1]:
        st.markdown("""
        ### 🔐 نظام الصلاحيات والأمان
        
        | الصلاحية | المالك 👑 | المختص 👨‍🔬 | المربي 🌾 |
        |----------|----------|------------|----------|
        | تركيب الأعلاف | ✅ | ✅ | ✅ |
        | مشاهدة المخزون | ✅ | ✅ | ✅ |
        | تعديل المخزون | ✅ | ❌ | ❌ |
        | إضافة مواد جديدة | ✅ | ❌ | ❌ |
        | تعديل الأسعار | ✅ | ❌ | ❌ |
        | إدارة المستخدمين | ✅ | ❌ | ❌ |
        | عرض التقارير | ✅ | ✅ | ❌ |
        
        #### أكواد الدخول الافتراضية:
        - **المالك:** username: `owner` / password: `202687`
        - **المختص:** username: `specialist` / password: `2020`
        - **المربي:** username: `breeder` / password: `2026`
        
        #### نصائح أمنية:
        - يرجى تغيير كلمة المرور الافتراضية بعد أول تسجيل دخول
        - لا تشارك كلمة المرور مع أي شخص
        - يتم تشفير جميع كلمات المرور باستخدام SHA-256
        """)
    
    with tabs[2]:
        st.markdown("""
        ### 🧬 المصطلحات العلمية المستخدمة
        
        #### البروتين المهضوم (Digestible Protein - DP)
        - هو البروتين الفعلي الذي يستطيع الحيوان هضمه وامتصاصه
        - يتم حسابه بضرب البروتين الخام في معامل الهضم
        - يعطي دقة أكبر من البروتين الخام في التغذية
        
        #### معادل النشاء (Starch Equivalent - SE)
        - مقياس لطاقة العلف مقارنة بالنشاء
        - يستخدم لتقييم كفاءة الطاقة في العلائق
        
        #### البرمجة الخطية (Linear Programming)
        - تقنية رياضية لإيجاد الحل الأمثل
        - تستخدم لتقليل التكلفة مع تحقيق المواصفات المطلوبة
        
        #### معامل الهضم (Digestibility Coefficient)
        - نسبة المادة الغذائية التي يهضمها الحيوان
        - تتراوح بين 0 و 1 (أو 0% إلى 100%)
        
        #### الأحماض الأمينية الأساسية
        - **الليسين (Lysine):** أول حمض أميني محدود في تغذية الدواجن
        - **الميثيونين (Methionine):** حمض أميني يحتوي على كبريت، مهم للنمو والريش
        """)
    
    with tabs[3]:
        st.markdown("""
        ### ❓ الأسئلة الشائعة
        
        **س: ماذا أفعل إذا لم يتم إيجاد حل للتركيبة؟**
        
        ج: حاول إضافة المزيد من المكونات، خاصة مصادر البروتين، أو خفض نسبة البروتين المستهدفة قليلاً.
        
        **س: كيف يمكنني تحديث أسعار المواد؟**
        
        ج: إذا كنت تملك صلاحية المالك، يمكنك تعديل السعر مباشرة عند اختيار المكون.
        
        **س: هل يمكن حفظ التركيبات للاستخدام المستقبلي؟**
        
        ج: نعم، يتم حفظ جميع التركيبات تلقائياً ويمكنك الوصول إليها من تبويب "التركيبات السابقة".
        
        **س: كيف يتم حساب البروتين المهضوم؟**
        
        ج: البروتين المهضوم = البروتين الخام × معامل الهضم الخاص بكل مادة.
        
        **س: ماذا تعني الألوان في المخزون؟**
        
        ج: 🟢 أخضر = مخزون جيد، 🟡 أصفر = مخزون منخفض، 🔴 أحمر = مخزون حرج.
        
        **س: كيف يمكنني التواصل للاستشارات الفنية؟**
        
        ج: يمكنك التواصل مع الاختصاصي م. عبد القادر إسماعيل تاور عبر البريد الإلكتروني أو واتساب.
        """)
    
    st.markdown("---")
    st.caption("© 2026 - الاختصاصي م. عبد القادر إسماعيل تاور - جميع الحقوق محفوظة")
    st.caption("منصة تاور العلمية للانتاج الحيواني وتركيب الاعلاف - الإصدار 3.0")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# 🚀 تشغيل التطبيق
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    
    # تهيئة
    init_session_state()
    apply_custom_css()
    
    # تهيئة مدير قاعدة البيانات ومحرك التحسين
    global db_manager, optimization_engine
    db_manager = DatabaseManager()
    optimization_engine = OptimizationEngine(db_manager)
    
    # عرض الشاشة المناسبة
    if not st.session_state.logged_in:
        login_screen()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
