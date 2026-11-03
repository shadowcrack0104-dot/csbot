"""
💎 SHADOW Custom SMS Bot
Author: @King_X_vau
Version: 2.1.0
"""

import os
import sys
import asyncio
import time
import logging
import json
import aiosqlite
import aiohttp
from datetime import datetime
from typing import Optional, List, Dict, Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BOT_TOKEN = "8620671084:AAHi_Za_rDVYdPwhzH66pT-kj8E5wXD53gI"  # @BotFather থেকে নাও
ADMIN_IDS = [7986731915]  # তোমার Telegram ID দাও
SMS_API_URL = "https://apisell24.shop/sms.php"

# Fixed emoji dict - added missing keys
E = {
    "bot": "🤖", "sms": "💌", "send": "📤", "history": "📜", "profile": "👤",
    "admin": "🛡️", "stats": "📊", "users": "👥", "logs": "📋", "broadcast": "📢",
    "settings": "⚙️", "back": "◀️", "home": "🏠", "success": "✅", "error": "❌",
    "warning": "⚠️", "loading": "⏳", "lock": "🔒", "unlock": "🔓", "premium": "💎",
    "phone": "📱", "message": "💬", "check": "🔍", "shield": "🛡️", "rocket": "🚀",
    "star": "⭐", "fire": "🔥", "time": "⏰", "count": "🔢", "new": "🆕",
    "trending": "📈", "support": "🆘", "info": "ℹ️", "delete": "🗑️", "refresh": "🔄",
    "crown": "👑", "gift": "🎁", "notification": "🔔", "search": "🔎", "filter": "🔽",
    "excel": "📊", "chart": "📈", "money": "💰", "credit": "💳", "limit": "🚫",
    "ban": "🚷", "unban": "✅", "edit": "✏️", "view": "👁️", "copy": "📋",
    "share": "🔗", "download": "⬇️", "upload": "⬆️", "save": "💾", "cancel": "❌",
    "confirm": "✅", "next": "▶️", "prev": "◀️", "page": "📄", "total": "🔢",
    "today": "📅", "week": "🗓️", "month": "📆", "all": "🌍", "active": "🟢",
    "inactive": "🔴", "pending": "🟡", "processing": "🔄", "completed": "✅",
    "failed": "❌", "retry": "🔄", "speed": "⚡", "network": "🌐", "server": "🖥️",
    "database": "🗄️", "security": "🔐", "verified": "✅", "unverified": "❌",
    "vip": "💎", "normal": "👤", "upgrade": "⬆️", "downgrade": "⬇️", "promo": "🎉",
    "coupon": "🎟️", "referral": "👫", "invite": "📨", "bonus": "🎁", "rank": "🏆",
    "leaderboard": "🏅", "achievement": "🎯", "milestone": "🎖️", "streak": "🔥",
    "daily": "📅", "weekly": "🗓️", "monthly": "📆", "yearly": "📅", "custom": "🔧",
    "template": "📄", "quick": "⚡", "schedule": "⏰", "draft": "📝", "favorite": "⭐",
    "recent": "🕐", "contact": "📇", "group": "👥", "bulk": "📦", "single": "1️⃣",
    "multiple": "🔢", "import_btn": "📥", "export_btn": "📤", "backup": "💾",
    "restore": "🔄", "sync": "🔄", "connect": "🔗", "disconnect": "❌",
    "status": "📊", "health": "💚", "performance": "⚡", "uptime": "⏱️",
    "response": "📡", "latency": "⏳", "throughput": "📊", "error_rate": "❌",
    "success_rate": "✅", "queue": "📥", "rate_limit": "🚦", "timeout": "⏰",
    "reconnect": "🔄", "maintenance": "🔧", "update": "🔄", "version": "🔢",
    "changelog": "📋", "feedback": "💭", "report": "📊", "bug": "🐛", "feature": "✨",
    "request": "🙏", "donate": "💝", "sponsor": "💎", "partner": "🤝", "affiliate": "🔗",
    "api": "🔌", "webhook": "🔗", "documentation": "📚", "tutorial": "📖",
    "guide": "🗺️", "faq": "❓", "help": "❓", "about": "ℹ️", "terms": "📄",
    "privacy": "🔒", "license": "📜", "copyright": "©️", "add": "➕",
    "credit_footer": "🤖 Powered by SHADOW Custom SMS Bot | Dev: @King_X_vau"
}

BOT_NAME = "💎 SHADOW Custom SMS Bot"
DB_FILE = "sms_bot.db"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

user_states = {}
admin_states = {}

# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

class Database:
    def __init__(self):
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(DB_FILE)
        await self.db.execute("PRAGMA foreign_keys = ON")
        await self.create_tables()

    async def create_tables(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                is_premium INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                daily_limit INTEGER DEFAULT 500000000000000,
                total_sent INTEGER DEFAULT 0,
                joined_at TEXT,
                last_active TEXT,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                credits INTEGER DEFAULT 0,
                language TEXT DEFAULT 'bn',
                theme TEXT DEFAULT 'dark'
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS sms_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                message TEXT,
                status TEXT,
                api_response TEXT,
                sent_at TEXT,
                processed_time REAL,
                ip_info TEXT
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action TEXT,
                target_user_id INTEGER,
                details TEXT,
                created_at TEXT
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                content TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT,
                is_public INTEGER DEFAULT 0
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                phone TEXT,
                created_at TEXT
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone_number TEXT,
                name TEXT,
                created_at TEXT
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await self.db.execute("""
            INSERT OR IGNORE INTO system_settings (key, value) VALUES 
            ('maintenance_mode', '0'),
            ('global_limit', '100'),
            ('api_status', 'active'),
            ('welcome_message', 'Welcome to SHADOW Custom SMS Bot! 💎')
        """)
        await self.db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict]:
        async with self.db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    async def create_user(self, user_id, username, first_name, last_name):
        now = datetime.now().isoformat()
        ref = f"REF{user_id}{datetime.now().strftime('%H%M%S')}"
        await self.db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_at, last_active, referral_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username or "", first_name or "", last_name or "", now, now, ref))
        await self.db.commit()

    async def update_activity(self, user_id: int):
        now = datetime.now().isoformat()
        await self.db.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
        await self.db.commit()

    async def increment_sms(self, user_id: int):
        await self.db.execute("UPDATE users SET total_sent = total_sent + 1 WHERE user_id = ?", (user_id,))
        await self.db.commit()

    async def add_sms_log(self, user_id, phone, message, status, api_response, processed_time):
        now = datetime.now().isoformat()
        await self.db.execute("""
            INSERT INTO sms_logs (user_id, phone_number, message, status, api_response, sent_at, processed_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, phone, message, status, api_response, now, processed_time))
        await self.db.commit()

    async def get_user_logs(self, user_id, limit=20, offset=0):
        async with self.db.execute("""
            SELECT * FROM sms_logs WHERE user_id = ? ORDER BY sent_at DESC LIMIT ? OFFSET ?
        """, (user_id, limit, offset)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def get_all_logs(self, limit=500, offset=0, filter_type=None):
        if filter_type == "today":
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id WHERE date(l.sent_at)=date('now') ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        elif filter_type == "week":
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id WHERE l.sent_at >= datetime('now', '-7 days') ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        elif filter_type == "month":
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id WHERE l.sent_at >= datetime('now', '-30 days') ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        elif filter_type == "success":
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id WHERE l.status='success' ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        elif filter_type == "failed":
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id WHERE l.status='failed' ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        else:
            query = "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id = u.user_id ORDER BY l.sent_at DESC LIMIT ? OFFSET ?"
        async with self.db.execute(query, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def get_stats(self):
        stats = {}
        async with self.db.execute("SELECT COUNT(*) FROM users") as c: stats['total_users'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM users WHERE date(joined_at)=date('now')") as c: stats['today_users'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs") as c: stats['total_sms'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE date(sent_at)=date('now')") as c: stats['today_sms'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE status='success'") as c: stats['success_sms'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE status='failed'") as c: stats['failed_sms'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM users WHERE is_banned=1") as c: stats['banned_users'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM users WHERE is_premium=1") as c: stats['premium_users'] = (await c.fetchone())[0]
        async with self.db.execute("""
            SELECT u.user_id, u.username, u.first_name, COUNT(l.id) as cnt
            FROM users u LEFT JOIN sms_logs l ON u.user_id=l.user_id
            GROUP BY u.user_id ORDER BY cnt DESC LIMIT 10
        """) as c: stats['top_users'] = await c.fetchall()
        return stats

    async def get_all_users(self, limit=500, offset=0):
        async with self.db.execute("SELECT * FROM users ORDER BY joined_at DESC LIMIT ? OFFSET ?", (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def ban_user(self, user_id, admin_id):
        await self.db.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
        await self.add_admin_log(admin_id, "ban_user", user_id, f"Banned user {user_id}")
        await self.db.commit()

    async def unban_user(self, user_id, admin_id):
        await self.db.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
        await self.add_admin_log(admin_id, "unban_user", user_id, f"Unbanned user {user_id}")
        await self.db.commit()

    async def add_admin_log(self, admin_id, action, target_user_id, details):
        now = datetime.now().isoformat()
        await self.db.execute("""
            INSERT INTO admin_logs (admin_id, action, target_user_id, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, action, target_user_id, details, now))
        await self.db.commit()

    async def get_contacts(self, user_id):
        async with self.db.execute("SELECT * FROM contacts WHERE user_id=? ORDER BY created_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def add_contact(self, user_id, name, phone):
        now = datetime.now().isoformat()
        await self.db.execute("INSERT INTO contacts (user_id, name, phone, created_at) VALUES (?, ?, ?, ?)", (user_id, name, phone, now))
        await self.db.commit()

    async def get_templates(self, user_id):
        async with self.db.execute("SELECT * FROM templates WHERE user_id=? OR is_public=1 ORDER BY usage_count DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def add_template(self, user_id, name, content):
        now = datetime.now().isoformat()
        await self.db.execute("INSERT INTO templates (user_id, name, content, created_at) VALUES (?, ?, ?, ?)", (user_id, name, content, now))
        await self.db.commit()

    async def get_favorites(self, user_id):
        async with self.db.execute("SELECT * FROM favorites WHERE user_id=? ORDER BY created_at DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def add_favorite(self, user_id, phone, name):
        now = datetime.now().isoformat()
        await self.db.execute("INSERT OR IGNORE INTO favorites (user_id, phone_number, name, created_at) VALUES (?, ?, ?, ?)", (user_id, phone, name, now))
        await self.db.commit()

    async def get_today_sms_count(self, user_id):
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id=? AND date(sent_at)=date('now')", (user_id,)) as c:
            return (await c.fetchone())[0]

    async def get_user_stats(self, user_id):
        stats = {}
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id=?", (user_id,)) as c: stats['total_sent'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id=? AND date(sent_at)=date('now')", (user_id,)) as c: stats['today_sent'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id=? AND status='success'", (user_id,)) as c: stats['success_count'] = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id=? AND status='failed'", (user_id,)) as c: stats['failed_count'] = (await c.fetchone())[0]
        async with self.db.execute("""
            SELECT phone_number, COUNT(*) as cnt FROM sms_logs WHERE user_id=? GROUP BY phone_number ORDER BY cnt DESC LIMIT 5
        """, (user_id,)) as c: stats['top_recipients'] = await c.fetchall()
        return stats

    async def get_analytics(self):
        analytics = {}
        # User growth last 7 days
        async with self.db.execute("""
            SELECT date(joined_at) as day, COUNT(*) as cnt
            FROM users WHERE joined_at >= datetime('now', '-7 days')
            GROUP BY day ORDER BY day
        """) as c: analytics['user_growth'] = await c.fetchall()
        # SMS volume last 7 days
        async with self.db.execute("""
            SELECT date(sent_at) as day, COUNT(*) as cnt
            FROM sms_logs WHERE sent_at >= datetime('now', '-7 days')
            GROUP BY day ORDER BY day
        """) as c: analytics['sms_volume'] = await c.fetchall()
        # Peak hours
        async with self.db.execute("""
            SELECT strftime('%H', sent_at) as hour, COUNT(*) as cnt
            FROM sms_logs GROUP BY hour ORDER BY cnt DESC LIMIT 5
        """) as c: analytics['peak_hours'] = await c.fetchall()
        # Success rate
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs") as c: total = (await c.fetchone())[0]
        async with self.db.execute("SELECT COUNT(*) FROM sms_logs WHERE status='success'") as c: success = (await c.fetchone())[0]
        analytics['success_rate'] = round(success / max(total, 1) * 100, 1)
        analytics['total_sms'] = total
        return analytics

    async def get_setting(self, key):
        async with self.db.execute("SELECT value FROM system_settings WHERE key=?", (key,)) as c:
            row = await c.fetchone()
            return row[0] if row else ""

    async def set_setting(self, key, value):
        await self.db.execute("INSERT INTO system_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        await self.db.commit()

    async def search_logs(self, query, limit=500):
        async with self.db.execute("""
            SELECT l.*, u.username, u.first_name FROM sms_logs l
            LEFT JOIN users u ON l.user_id=u.user_id
            WHERE l.phone_number LIKE ? OR l.message LIKE ? OR u.username LIKE ?
            ORDER BY l.sent_at DESC LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit)) as cursor:
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def close(self):
        if self.db: await self.db.close()

db = Database()

# ═══════════════════════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def main_menu_keyboard(is_admin=False):
    buttons = [
        [InlineKeyboardButton(f"{E['send']} Send SMS", callback_data="send_sms"),
         InlineKeyboardButton(f"{E['history']} My History", callback_data="my_history")],
        [InlineKeyboardButton(f"{E['phone']} Contacts", callback_data="contacts"),
         InlineKeyboardButton(f"{E['template']} Templates", callback_data="templates")],
        [InlineKeyboardButton(f"{E['profile']} My Profile", callback_data="my_profile"),
         InlineKeyboardButton(f"{E['favorite']} Favorites", callback_data="favorites")],
        [InlineKeyboardButton(f"{E['support']} Support", callback_data="support"),
         InlineKeyboardButton(f"{E['info']} About", callback_data="about")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(f"{E['crown']} {E['admin']} Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

def sms_options_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['single']} Single SMS", callback_data="sms_single"),
         InlineKeyboardButton(f"{E['bulk']} Bulk SMS", callback_data="sms_bulk")],
        [InlineKeyboardButton(f"{E['schedule']} Schedule SMS", callback_data="sms_schedule"),
         InlineKeyboardButton(f"{E['quick']} Quick Send", callback_data="sms_quick")],
        [InlineKeyboardButton(f"{E['template']} Use Template", callback_data="sms_template"),
         InlineKeyboardButton(f"{E['favorite']} From Favorites", callback_data="sms_favorite")],
        [InlineKeyboardButton(f"{E['back']} Back to Menu", callback_data="main_menu")]
    ])

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['stats']} Dashboard", callback_data="admin_stats"),
         InlineKeyboardButton(f"{E['logs']} All Logs", callback_data="admin_logs")],
        [InlineKeyboardButton(f"{E['users']} All Users", callback_data="admin_users"),
         InlineKeyboardButton(f"{E['search']} Search Logs", callback_data="admin_search")],
        [InlineKeyboardButton(f"{E['broadcast']} Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton(f"{E['settings']} Settings", callback_data="admin_settings")],
        [InlineKeyboardButton(f"{E['lock']} Maintenance", callback_data="admin_maintenance"),
         InlineKeyboardButton(f"{E['chart']} Analytics", callback_data="admin_analytics")],
        [InlineKeyboardButton(f"{E['back']} Back to Menu", callback_data="main_menu")]
    ])

def back_keyboard(back_to="main_menu"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"{E['back']} Back", callback_data=back_to)]])

def confirm_keyboard(confirm_data, cancel_data="main_menu"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['confirm']} Confirm", callback_data=confirm_data),
         InlineKeyboardButton(f"{E['cancel']} Cancel", callback_data=cancel_data)]
    ])

def result_keyboard(success=True):
    if success:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{E['send']} Send Another", callback_data="send_sms"),
             InlineKeyboardButton(f"{E['history']} View History", callback_data="my_history")],
            [InlineKeyboardButton(f"{E['home']} Main Menu", callback_data="main_menu")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{E['retry']} Retry", callback_data="send_sms"),
             InlineKeyboardButton(f"{E['support']} Support", callback_data="support")],
            [InlineKeyboardButton(f"{E['home']} Main Menu", callback_data="main_menu")]
        ])

def profile_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['edit']} Edit Profile", callback_data="edit_profile"),
         InlineKeyboardButton(f"{E['stats']} My Stats", callback_data="my_stats")],
        [InlineKeyboardButton(f"{E['referral']} My Referral", callback_data="my_referral"),
         InlineKeyboardButton(f"{E['upgrade']} Upgrade", callback_data="upgrade_premium")],
        [InlineKeyboardButton(f"{E['back']} Back to Menu", callback_data="main_menu")]
    ])

def logs_filter_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['today']} Today", callback_data="logs_filter_today"),
         InlineKeyboardButton(f"{E['week']} This Week", callback_data="logs_filter_week")],
        [InlineKeyboardButton(f"{E['month']} This Month", callback_data="logs_filter_month"),
         InlineKeyboardButton(f"{E['all']} All Time", callback_data="logs_filter_all")],
        [InlineKeyboardButton(f"{E['success']} Success Only", callback_data="logs_filter_success"),
         InlineKeyboardButton(f"❌ Failed Only", callback_data="logs_filter_failed")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_logs")]
    ])

def analytics_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['chart']} User Growth", callback_data="analytics_users"),
         InlineKeyboardButton(f"{E['chart']} SMS Trends", callback_data="analytics_sms")],
        [InlineKeyboardButton(f"✅ Success Rate", callback_data="analytics_success"),
         InlineKeyboardButton(f"⏰ Peak Hours", callback_data="analytics_hours")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")]
    ])

def contacts_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['add']} Add Contact", callback_data="add_contact")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")]
    ])

def templates_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{E['add']} Add Template", callback_data="add_template")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="main_menu")]
    ])

# ═══════════════════════════════════════════════════════════════
# SMS SERVICE
# ═══════════════════════════════════════════════════════════════

class SMSService:
    @staticmethod
    async def simulate_sending_process(bot, chat_id, message_id=None):
        steps = [
            ("🔍 Validating phone number format...", 1.0),
            ("🛡️ Security check in progress...", 1.2),
            ("🔐 Encrypting message content...", 0.8),
            ("🌐 Connecting to SMS gateway...", 1.5),
            ("📡 Establishing secure channel...", 1.0),
            ("💨 Sending message packet...", 1.5),
            ("✅ Verifying delivery status...", 0.8),
        ]
        text = "⏳ <b>Processing Your Request</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for step_msg, delay in steps:
            text += f"➤ {step_msg}\n"
            if message_id:
                try:
                    await bot.edit_message_text(
                        text + "\n━━━━━━━━━━━━━━━━━━━━\n<i>Please wait...</i>",
                        chat_id=chat_id, message_id=message_id, parse_mode="HTML"
                    )
                except Exception:
                    pass
            else:
                try:
                    msg = await bot.send_message(chat_id, text + "\n━━━━━━━━━━━━━━━━━━━━\n<i>Please wait...</i>", parse_mode="HTML")
                    message_id = msg.message_id
                except Exception:
                    pass
            await asyncio.sleep(delay)
        return message_id

    @staticmethod
    async def send_sms(phone, message):
        try:
            async with aiohttp.ClientSession() as session:
                params = {"num": phone, "msg": message}
                async with session.get(SMS_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response_text = await response.text()
                    status_code = response.status
                    if status_code == 200 and ("success" in response_text.lower() or "sent" in response_text.lower()):
                        return {"success": True, "status": "success", "response": response_text, "status_code": status_code}
                    else:
                        return {"success": False, "status": "failed", "response": response_text, "status_code": status_code}
        except asyncio.TimeoutError:
            return {"success": False, "status": "failed", "response": "Request timeout - gateway not responding", "status_code": 408}
        except Exception as e:
            return {"success": False, "status": "failed", "response": str(e), "status_code": 500}

    @staticmethod
    def format_phone(phone):
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("+"): phone = phone[1:]
        if phone.startswith("88"): phone = phone[2:]
        if not phone.startswith("0"): phone = "0" + phone
        return phone

    @staticmethod
    def validate_phone(phone):
        formatted = SMSService.format_phone(phone)
        if len(formatted) == 11 and formatted.startswith("01"):
            return True, formatted
        return False, formatted

# ═══════════════════════════════════════════════════════════════
# USER PANEL HANDLERS
# ═══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = await db.get_user(user.id)
    if not existing:
        await db.create_user(user.id, user.username, user.first_name, user.last_name)
    await db.update_activity(user.id)

    welcome = f"""
{E['bot']} <b>Welcome to {BOT_NAME}</b> {E['premium']}

━━━━━━━━━━━━━━━━━━━━
👋 <b>Hello, {user.first_name}!</b>

💌 Send unlimited SMS instantly
📜 Track your complete history
⭐ Save favorite contacts
📄 Use message templates
📊 View detailed analytics

{E['fire']} <b>Premium Features:</b>
• Ultra-fast delivery
• Real-time tracking
• Secure encryption
• Beautiful dashboard

━━━━━━━━━━━━━━━━━━━━
{E['crown']} <b>Dev:</b> @King_X_vau
<i>Tap a button below to get started!</i>
"""
    is_admin = user.id in ADMIN_IDS
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin))

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    await db.update_activity(user.id)
    is_admin = user.id in ADMIN_IDS
    text = f"""
{E['bot']} <b>{BOT_NAME} - Main Menu</b> {E['premium']}

━━━━━━━━━━━━━━━━━━━━
💎 <b>What would you like to do?</b>

{E['send']} <b>Send SMS</b> - Quick message delivery
{E['history']} <b>My History</b> - Past messages
{E['phone']} <b>Contacts</b> - Manage contacts
{E['template']} <b>Templates</b> - Saved messages
{E['profile']} <b>My Profile</b> - Your stats

━━━━━━━━━━━━━━━━━━━━
{E['crown']} Dev: @King_X_vau
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin))

async def send_sms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['sms']} <b>Send SMS</b> {E['rocket']}

━━━━━━━━━━━━━━━━━━━━
Choose your sending method:

{E['single']} <b>Single SMS</b> - Send to one number
{E['bulk']} <b>Bulk SMS</b> - Multiple recipients
{E['schedule']} <b>Schedule</b> - Send later
{E['quick']} <b>Quick Send</b> - Fast mode

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=sms_options_keyboard())

async def sms_single_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = {"step": "awaiting_phone", "mode": "single"}
    text = f"""
{E['phone']} <b>Enter Phone Number</b>

━━━━━━━━━━━━━━━━━━━━
Please send the recipient's phone number.

📌 <b>Format:</b> 01XXXXXXXXX
📌 <b>Example:</b> 01712345678

{E['warning']} <i>Make sure the number is correct!</i>
━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("send_sms"))

async def sms_bulk_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['bulk']} <b>Bulk SMS</b>

━━━━━━━━━━━━━━━━━━━━
{E['warning']} Bulk SMS feature coming soon!

For now, please use Single SMS to send messages one by one.

{E['info']} Future update will support:
• Multiple numbers at once
• CSV import
• Group sending

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("send_sms"))

async def sms_schedule_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['schedule']} <b>Schedule SMS</b>

━━━━━━━━━━━━━━━━━━━━
{E['warning']} Schedule SMS feature coming soon!

{E['info']} Future update will support:
• Set specific date & time
• Recurring messages
• Timezone selection

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("send_sms"))

async def sms_quick_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick Send = same as single but with faster UI"""
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = {"step": "awaiting_phone", "mode": "quick"}
    text = f"""
{E['quick']} <b>Quick Send Mode</b> {E['rocket']}

━━━━━━━━━━━━━━━━━━━━
Enter phone number to send quickly:

📌 Format: 01XXXXXXXXX
━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("send_sms"))

async def sms_from_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    templates = await db.get_templates(user_id)
    if not templates:
        await query.edit_message_text(
            f"{E['template']} <b>No Templates Found</b>\n\nAdd templates first from the Templates menu.",
            parse_mode="HTML", reply_markup=back_keyboard("send_sms")
        )
        return
    text = f"{E['template']} <b>Select a Template</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
    buttons = []
    for t in templates[:10]:
        text += f"📄 <b>{t['name']}</b>: {t['content'][:30]}...\n"
        buttons.append([InlineKeyboardButton(f"📄 {t['name'][:20]}", callback_data=f"use_template_{t['id']}")])
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="send_sms")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def sms_from_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    favs = await db.get_favorites(user_id)
    if not favs:
        await query.edit_message_text(
            f"{E['favorite']} <b>No Favorites Found</b>\n\nSave favorite contacts first.",
            parse_mode="HTML", reply_markup=back_keyboard("send_sms")
        )
        return
    text = f"{E['favorite']} <b>Select Favorite</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
    buttons = []
    for f in favs[:10]:
        text += f"⭐ {f['name']}: {f['phone_number']}\n"
        buttons.append([InlineKeyboardButton(f"⭐ {f['name'][:20]} ({f['phone_number']})", callback_data=f"fav_send_{f['phone_number']}")])
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="send_sms")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states: return
    state = user_states[user_id]
    phone = update.message.text.strip()
    valid, formatted = SMSService.validate_phone(phone)
    if not valid:
        await update.message.reply_text(
            f"{E['error']} <b>Invalid Phone Number!</b>\n\nPlease enter a valid Bangladesh number.\nExample: 01712345678",
            parse_mode="HTML", reply_markup=back_keyboard("send_sms")
        )
        return
    state["phone"] = formatted
    state["step"] = "awaiting_message"
    await update.message.reply_text(
        f"""
{E['message']} <b>Enter Your Message</b>

━━━━━━━━━━━━━━━━━━━━
📱 <b>To:</b> <code>{formatted}</code>

Now type your message below.
You can also send emojis! 😊

{E['info']} <i>Max 500 characters</i>
━━━━━━━━━━━━━━━━━━━━
""", parse_mode="HTML", reply_markup=back_keyboard("send_sms"))

async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states: return
    state = user_states[user_id]
    message_text = update.message.text.strip()
    if len(message_text) > 500:
        await update.message.reply_text(f"{E['warning']} Message too long! Max 500 characters.", reply_markup=back_keyboard("send_sms"))
        return
    state["message"] = message_text
    state["step"] = "confirm"
    preview = f"""
{E['sms']} <b>Message Preview</b>

━━━━━━━━━━━━━━━━━━━━
📱 <b>To:</b> <code>{state['phone']}</code>
💬 <b>Message:</b>
<code>{message_text}</code>

{E['check']} <b>Ready to send?</b>
━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(preview, parse_mode="HTML", reply_markup=confirm_keyboard("confirm_send", "send_sms"))

async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in user_states:
        await query.edit_message_text(f"{E['error']} Session expired. Please start again.", reply_markup=back_keyboard("main_menu"))
        return
    state = user_states[user_id]
    phone = state["phone"]
    message = state["message"]

    msg = await query.edit_message_text(
        f"{E['loading']} <b>Initializing...</b>\n\n<i>Preparing your request...</i>", parse_mode="HTML"
    )

    start_time = time.time()
    msg_id = await SMSService.simulate_sending_process(context.bot, query.message.chat_id, msg.message_id if msg else None)
    result = await SMSService.send_sms(phone, message)
    processed_time = round(time.time() - start_time, 2)

    await db.add_sms_log(user_id, phone, message, result["status"], result["response"], processed_time)
    await db.increment_sms(user_id)

    if result["success"]:
        success_text = f"""
{E['success']} <b>SMS Sent Successfully!</b> {E['rocket']}

━━━━━━━━━━━━━━━━━━━━
📱 <b>To:</b> <code>{phone}</code>
💬 <b>Message:</b> <code>{message[:50]}{'...' if len(message) > 50 else ''}</code>
⏱️ <b>Time:</b> {processed_time}s
📡 <b>Status:</b> Delivered

{E['star']} <i>Your message has been delivered!</i>
━━━━━━━━━━━━━━━━━━━━
"""
        try:
            await context.bot.edit_message_text(success_text, chat_id=query.message.chat_id, message_id=msg_id or msg.message_id, parse_mode="HTML", reply_markup=result_keyboard(success=True))
        except Exception:
            await context.bot.send_message(query.message.chat_id, success_text, parse_mode="HTML", reply_markup=result_keyboard(success=True))
    else:
        fail_text = f"""
{E['error']} <b>SMS Failed!</b> {E['warning']}

━━━━━━━━━━━━━━━━━━━━
📱 <b>To:</b> <code>{phone}</code>
❌ <b>Error:</b> <code>{result['response'][:100]}</code>
⏱️ <b>Time:</b> {processed_time}s

{E['retry']} <i>You can retry or contact support.</i>
━━━━━━━━━━━━━━━━━━━━
"""
        try:
            await context.bot.edit_message_text(fail_text, chat_id=query.message.chat_id, message_id=msg_id or msg.message_id, parse_mode="HTML", reply_markup=result_keyboard(success=False))
        except Exception:
            await context.bot.send_message(query.message.chat_id, fail_text, parse_mode="HTML", reply_markup=result_keyboard(success=False))

    del user_states[user_id]

async def my_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    logs = await db.get_user_logs(user_id, limit=5)
    if not logs:
        text = f"""
{E['history']} <b>Your SMS History</b>

━━━━━━━━━━━━━━━━━━━━
{E['info']} No messages sent yet.

Start sending SMS now!
━━━━━━━━━━━━━━━━━━━━
"""
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("main_menu"))
        return
    text = f"{E['history']} <b>Your Recent Messages</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, log in enumerate(logs, 1):
        status_emoji = E['success'] if log['status'] == 'success' else E['error']
        msg_preview = log['message'][:30] + '...' if len(log['message']) > 30 else log['message']
        time_str = log['sent_at'][:16] if log['sent_at'] else 'Unknown'
        text += f"{i}. {status_emoji} <code>{log['phone_number']}</code>\n   💬 {msg_preview}\n   🕐 {time_str}\n\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n<i>Showing last 5 messages</i>"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("main_menu"))

async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user_data = await db.get_user(user_id)
    stats = await db.get_user_stats(user_id)
    today_count = await db.get_today_sms_count(user_id)
    premium_badge = f"{E['crown']} PREMIUM" if user_data.get('is_premium') else f"{E['normal']} FREE"
    text = f"""
{E['profile']} <b>Your Profile</b> {E['premium']}

━━━━━━━━━━━━━━━━━━━━
👤 <b>Name:</b> {user_data.get('first_name', 'N/A')}
🆔 <b>ID:</b> <code>{user_id}</code>
📛 <b>Username:</b> @{user_data.get('username', 'N/A')}
{E['crown']} <b>Status:</b> {premium_badge}

📊 <b>Statistics:</b>
{E['send']} Total Sent: <b>{stats['total_sent']}</b>
📅 Today: <b>{today_count}</b> / {user_data.get('daily_limit', 50)}
{E['success']} Success: <b>{stats['success_count']}</b>
{E['error']} Failed: <b>{stats['failed_count']}</b>

📅 <b>Joined:</b> {user_data.get('joined_at', 'N/A')[:10] if user_data.get('joined_at') else 'N/A'}
━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=profile_keyboard())

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    stats = await db.get_user_stats(user_id)
    text = f"""
{E['stats']} <b>Your Detailed Stats</b> {E['chart']}

━━━━━━━━━━━━━━━━━━━━
{E['send']} <b>Total Messages:</b> {stats['total_sent']}
{E['success']} <b>Successful:</b> {stats['success_count']}
{E['error']} <b>Failed:</b> {stats['failed_count']}

📈 <b>Success Rate:</b> {stats['success_count'] / max(stats['total_sent'], 1) * 100:.1f}%

🏆 <b>Top Recipients:</b>
"""
    for recipient in stats.get('top_recipients', []):
        text += f"\n📱 {recipient[0]} - {recipient[1]} msgs"
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("my_profile"))

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['edit']} <b>Edit Profile</b>

━━━━━━━━━━━━━━━━━━━━
{E['info']} Profile editing coming soon!

You will be able to:
• Change display name
• Set profile picture
• Update contact info

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("my_profile"))

async def my_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user_data = await db.get_user(user_id)
    ref_code = user_data.get('referral_code', 'N/A') if user_data else 'N/A'
    text = f"""
{E['referral']} <b>Your Referral</b>

━━━━━━━━━━━━━━━━━━━━
🎟️ <b>Your Code:</b> <code>{ref_code}</code>

Share this code with friends!
Each referral earns you bonus credits.

{E['info']} Referral rewards coming soon!
━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("my_profile"))

async def upgrade_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['crown']} <b>Upgrade to Premium</b> {E['premium']}

━━━━━━━━━━━━━━━━━━━━
{E['fire']} <b>Premium Benefits:</b>
• Unlimited daily SMS
• Priority delivery
• Advanced analytics
• Custom templates
• Priority support

💰 <b>Contact Admin for pricing:</b>
👤 @King_X_vau

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("my_profile"))

async def contacts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    contacts = await db.get_contacts(user_id)
    text = f"{E['phone']} <b>Your Contacts</b>\n\n"
    if not contacts:
        text += f"{E['info']} No contacts saved yet.\n\nTap Add Contact to save one!"
    else:
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for contact in contacts:
            text += f"👤 <b>{contact['name']}</b>\n📱 <code>{contact['phone']}</code>\n\n"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=contacts_keyboard())

async def add_contact_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = {"step": "add_contact_name"}
    await query.edit_message_text(
        f"{E['add']} <b>Add Contact</b>\n\n━━━━━━━━━━━━━━━━━━━━\nEnter the contact name:",
        parse_mode="HTML", reply_markup=back_keyboard("contacts")
    )

async def templates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    templates = await db.get_templates(user_id)
    text = f"{E['template']} <b>Your Templates</b>\n\n"
    if not templates:
        text += f"{E['info']} No templates saved yet.\n\nTap Add Template to create one!"
    else:
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for t in templates:
            content_preview = t['content'][:40] + '...' if len(t['content']) > 40 else t['content']
            text += f"📄 <b>{t['name']}</b>\n💬 {content_preview}\n\n"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=templates_keyboard())

async def add_template_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_states[update.effective_user.id] = {"step": "add_template_name"}
    await query.edit_message_text(
        f"{E['add']} <b>Add Template</b>\n\n━━━━━━━━━━━━━━━━━━━━\nEnter the template name:",
        parse_mode="HTML", reply_markup=back_keyboard("templates")
    )

async def favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    favorites = await db.get_favorites(user_id)
    text = f"{E['favorite']} <b>Your Favorites</b>\n\n"
    if not favorites:
        text += f"{E['info']} No favorites saved yet."
    else:
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for f in favorites:
            text += f"⭐ <b>{f['name']}</b>\n📱 <code>{f['phone_number']}</code>\n\n"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("main_menu"))

async def support_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['support']} <b>Support Center</b>

━━━━━━━━━━━━━━━━━━━━
{E['info']} <b>Need Help?</b>

👤 <b>Developer:</b> @King_X_vau
📱 Contact via Telegram

{E['warning']} <b>Common Issues:</b>
• Invalid phone format → Use 01XXXXXXXXX
• Message failed → Check API status
• Limit reached → Wait or upgrade

━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("main_menu"))

async def about_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = f"""
{E['bot']} <b>About {BOT_NAME}</b> {E['premium']}

━━━━━━━━━━━━━━━━━━━━
🤖 <b>Version:</b> 2.1.0
💎 <b>Type:</b> SHADOW Custom SMS Bot
🌐 <b>API:</b> Custom Gateway

{E['fire']} <b>Features:</b>
• Unlimited SMS Sending
• Real-time Delivery
• Secure Encryption
• Beautiful UI
• Admin Dashboard
• Contact Management
• Message Templates
• Detailed Analytics

━━━━━━━━━━━━━━━━━━━━
{E['crown']} <b>Developer:</b> @King_X_vau
{E['api']} <b>API Credit:</b> @King_X_vau
{E['rocket']} <b>Bot Credit:</b> @King_X_vau
━━━━━━━━━━━━━━━━━━━━
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("main_menu"))

# ═══════════════════════════════════════════════════════════════
# ADMIN PANEL HANDLERS
# ═══════════════════════════════════════════════════════════════

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await query.answer("⛔ Unauthorized!", show_alert=True)
        return
    text = f"""
{E['crown']} <b>ADMIN PANEL</b> {E['shield']}

━━━━━━━━━━━━━━━━━━━━
👑 <b>Welcome, Admin!</b>

{E['stats']} Dashboard Overview
{E['logs']} View All Logs
{E['users']} Manage Users
{E['broadcast']} Send Broadcast
{E['settings']} System Settings

━━━━━━━━━━━━━━━━━━━━
{E['crown']} Dev: @King_X_vau
<i>Select an option below</i>
"""
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    stats = await db.get_stats()
    text = f"""
{E['stats']} <b>Admin Dashboard</b> {E['chart']}

━━━━━━━━━━━━━━━━━━━━
👥 <b>Users:</b>
   Total: <code>{stats['total_users']}</code>
   Today: <code>{stats['today_users']}</code>
   Premium: <code>{stats['premium_users']}</code>
   Banned: <code>{stats['banned_users']}</code>

💌 <b>SMS Stats:</b>
   Total: <code>{stats['total_sms']}</code>
   Today: <code>{stats['today_sms']}</code>
   Success: <code>{stats['success_sms']}</code>
   Failed: <code>{stats['failed_sms']}</code>

📈 <b>Success Rate:</b> <code>{stats['success_sms'] / max(stats['total_sms'], 1) * 100:.1f}%</code>

🏆 <b>Top Users:</b>
"""
    for user in stats.get('top_users', []):
        name = user[2] or user[1] or f"User_{user[0]}"
        text += f"\n   {name[:15]}: {user[3]} msgs"
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("admin_panel"))

async def admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    logs = await db.get_all_logs(limit=10)
    text = f"{E['logs']} <b>All SMS Logs</b> (Recent 10)\n\n"
    buttons = []
    if not logs:
        text += "No logs found."
    else:
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for log in logs:
            status_emoji = E['success'] if log['status'] == 'success' else E['error']
            name = log.get('first_name') or log.get('username') or f"User_{log['user_id']}"
            msg_preview = log['message'][:25] + '...' if len(log['message']) > 25 else log['message']
            time_str = log['sent_at'][:16] if log['sent_at'] else 'N/A'
            text += f"{status_emoji} <b>{name[:15]}</b> | 📱 {log['phone_number']}\n   💬 {msg_preview}\n   🕐 {time_str}\n"
            if len(log['message']) > 5:
                buttons.append([InlineKeyboardButton(f"👁️ Full Msg #{log['id']} ({name[:10]}...)", callback_data=f"view_log_{log['id']}")])
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    buttons.append([InlineKeyboardButton(f"{E['filter']} Filter Logs", callback_data="logs_filter_menu")])
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def view_log_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show full message content for a specific log entry"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    log_id = int(query.data.replace("view_log_", ""))
    # Fetch this specific log
    async with db.db.execute(
        "SELECT l.*, u.username, u.first_name FROM sms_logs l LEFT JOIN users u ON l.user_id=u.user_id WHERE l.id=?",
        (log_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            await query.answer("Log not found!", show_alert=True)
            return
        columns = [desc[0] for desc in cursor.description]
        log = dict(zip(columns, row))

    name = log.get('first_name') or log.get('username') or f"User_{log['user_id']}"
    status_emoji = E['success'] if log['status'] == 'success' else E['error']
    time_str = log['sent_at'][:19] if log['sent_at'] else 'N/A'

    text = f"""👁️ <b>Full Log Details</b> #{log_id}

━━━━━━━━━━━━━━━━━━━━
{status_emoji} <b>Status:</b> {log['status'].upper()}
👤 <b>User:</b> {name} (<code>{log['user_id']}</code>)
📱 <b>Phone:</b> <code>{log['phone_number']}</code>
🕐 <b>Time:</b> {time_str}
⏱️ <b>Processed:</b> {log.get('processed_time', 'N/A')}s

💬 <b>Full Message:</b>
━━━━━━━━━━━━━━━━━━━━
<code>{log['message']}</code>
━━━━━━━━━━━━━━━━━━━━"""

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_keyboard("admin_logs"))

async def logs_filter_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show filter options for logs"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    await query.edit_message_text(
        f"{E['filter']} <b>Filter Logs</b>\n\nকোন ধরনের লগ দেখতে চাও?",
        parse_mode="HTML", reply_markup=logs_filter_keyboard()
    )

async def admin_logs_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all logs_filter_* callbacks"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    data = query.data  # e.g. "logs_filter_today"
    filter_type = data.replace("logs_filter_", "")
    label_map = {
        "today": "Today", "week": "This Week", "month": "This Month",
        "all": "All Time", "success": "Success Only", "failed": "Failed Only"
    }
    label = label_map.get(filter_type, "Filtered")
    logs = await db.get_all_logs(limit=150999, filter_type=filter_type if filter_type != "all" else None)
    text = f"{E['filter']} <b>Logs: {label}</b>\n\n"
    if not logs:
        text += f"{E['info']} No logs found for this filter."
    else:
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        for log in logs:
            status_emoji = E['success'] if log['status'] == 'success' else E['error']
            name = log.get('first_name') or log.get('username') or f"User_{log['user_id']}"
            msg_preview = log['message'][:25] + '...' if len(log['message']) > 25 else log['message']
            time_str = log['sent_at'][:16] if log['sent_at'] else 'N/A'
            text += f"{status_emoji} <b>{name[:15]}</b>\n   📱 {log['phone_number']}\n   💬 {msg_preview}\n   🕐 {time_str}\n\n"
    text += "━━━━━━━━━━━━━━━━━━━━"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=logs_filter_keyboard())

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    users = await db.get_all_users(limit=155555)
    text = f"{E['users']} <b>All Users</b> (Recent 15)\n\n━━━━━━━━━━━━━━━━━━━━\n"
    buttons = []
    for user in users:
        status = f"{E['ban']} BANNED" if user['is_banned'] else f"{E['active']} Active"
        premium = f"{E['crown']} VIP" if user['is_premium'] else ""
        name = user['first_name'] or user['username'] or f"User_{user['user_id']}"
        text += f"👤 <b>{name[:15]}</b> {premium}\n   🆔 <code>{user['user_id']}</code> | {status}\n   📅 Joined: {user['joined_at'][:10] if user['joined_at'] else 'N/A'}\n   💌 Sent: {user['total_sent']}\n"
        buttons.append([InlineKeyboardButton(f"📜 {name[:18]} এর হিস্ট্রি", callback_data=f"user_logs_{user['user_id']}")])
    text += "━━━━━━━━━━━━━━━━━━━━"
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def admin_user_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """নির্দিষ্ট ইউজারের সব মেসেজ হিস্ট্রি দেখাও"""
    query = update.callback_query
    await query.answer()
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS: return

    target_uid = int(query.data.replace("user_logs_", ""))
    target_user = await db.get_user(target_uid)
    name = target_user.get('first_name') or target_user.get('username') or f"User_{target_uid}" if target_user else f"User_{target_uid}"

    logs = await db.get_user_logs(target_uid, limit=155555)

    text = f"📜 <b>{name} এর মেসেজ হিস্ট্রি</b>\n🆔 <code>{target_uid}</code>\n\n━━━━━━━━━━━━━━━━━━━━\n"
    buttons = []

    if not logs:
        text += f"{E['info']} কোনো মেসেজ পাওয়া যায়নি।"
    else:
        for log in logs:
            status_emoji = E['success'] if log['status'] == 'success' else E['error']
            msg_preview = log['message'][:20] + '...' if len(log['message']) > 20 else log['message']
            time_str = log['sent_at'][:16] if log['sent_at'] else 'N/A'
            text += f"{status_emoji} 📱 <code>{log['phone_number']}</code>\n   💬 {msg_preview}\n   🕐 {time_str}\n"
            buttons.append([InlineKeyboardButton(
                f"👁️ Full Msg #{log['id']} → {log['phone_number']}",
                callback_data=f"view_log_{log['id']}"
            )])

    text += "\n━━━━━━━━━━━━━━━━━━━━"
    buttons.append([InlineKeyboardButton(f"{E['back']} ইউজার লিস্টে ফিরে যাও", callback_data="admin_users")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def admin_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    admin_states[user_id] = {"step": "admin_search"}
    await query.edit_message_text(
        f"{E['search']} <b>Search Logs</b>\n\nEnter search query (phone, message, or username):",
        parse_mode="HTML", reply_markup=back_keyboard("admin_panel")
    )

async def handle_admin_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_states or admin_states[user_id].get("step") != "admin_search": return
    query_text = update.message.text.strip()
    logs = await db.search_logs(query_text, limit=20)
    text = f"{E['search']} <b>Search Results for:</b> <code>{query_text}</code>\n\n"
    buttons = []
    if not logs:
        text += f"{E['info']} No results found."
    else:
        text += f"Found {len(logs)} results:\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for log in logs:
            status_emoji = E['success'] if log['status'] == 'success' else E['error']
            name = log.get('first_name') or log.get('username') or f"User_{log['user_id']}"
            msg_preview = log['message'][:30] + '...' if len(log['message']) > 30 else log['message']
            time_str = log['sent_at'][:16] if log['sent_at'] else 'N/A'
            text += f"{status_emoji} <b>{name[:15]}</b>\n   📱 {log['phone_number']}\n   💬 {msg_preview}\n   🕐 {time_str}\n"
            buttons.append([InlineKeyboardButton(
                f"👁️ Full Msg #{log['id']} ({name[:10]})",
                callback_data=f"view_log_{log['id']}"
            )])
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    del admin_states[user_id]

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    broadcast_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📢 Broadcast to ALL Users", callback_data="broadcast_all")],
        [InlineKeyboardButton(f"🎯 Send to Specific User", callback_data="broadcast_target")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")]
    ])
    await query.edit_message_text(
        f"{E['broadcast']} <b>Broadcast Menu</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 <b>Broadcast to ALL</b> - সবাইকে মেসেজ পাঠাও\n"
        f"🎯 <b>Specific User</b> - নির্দিষ্ট ইউজারকে মেসেজ পাঠাও\n\n"
        f"{E['warning']} Text, Photo, Video, File, Voice সব পাঠানো যাবে!",
        parse_mode="HTML", reply_markup=broadcast_kb
    )

async def broadcast_all_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    admin_states[user_id] = {"step": "admin_broadcast", "target": "all"}
    await query.edit_message_text(
        f"📢 <b>Broadcast to ALL Users</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"এখন যেকোনো মেসেজ পাঠাও:\n"
        f"✅ Text  ✅ Photo  ✅ Video\n✅ File  ✅ Voice  ✅ Sticker\n\n"
        f"{E['warning']} এটি সকল ইউজারকে পাঠানো হবে!",
        parse_mode="HTML", reply_markup=back_keyboard("admin_broadcast")
    )

async def broadcast_target_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    admin_states[user_id] = {"step": "broadcast_target_id"}
    # Show list of users to pick from
    users = await db.get_all_users(limit=20)
    text = f"🎯 <b>Select Target User</b>\n\n━━━━━━━━━━━━━━━━━━━━\nUser ID টাইপ করো অথবা নিচের বাটন থেকে বেছে নাও:\n\n"
    buttons = []
    for u in users:
        name = u['first_name'] or u['username'] or f"User_{u['user_id']}"
        uname = f"@{u['username']}" if u['username'] else ""
        buttons.append([InlineKeyboardButton(
            f"👤 {name[:20]} {uname} | ID: {u['user_id']}",
            callback_data=f"bt_select_{u['user_id']}"
        )])
    buttons.append([InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_broadcast")])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def broadcast_select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called when admin picks a user from button list"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    target_id = int(query.data.replace("bt_select_", ""))
    target_user = await db.get_user(target_id)
    name = target_user.get('first_name') or target_user.get('username') or f"User_{target_id}" if target_user else f"User_{target_id}"
    admin_states[user_id] = {"step": "admin_broadcast", "target": "single", "target_id": target_id, "target_name": name}
    await query.edit_message_text(
        f"🎯 <b>Send to: {name}</b>\n<code>ID: {target_id}</code>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"এখন মেসেজ পাঠাও:\n"
        f"✅ Text  ✅ Photo  ✅ Video\n✅ File  ✅ Voice  ✅ Sticker\n\n"
        f"যেকোনো ধরনের কন্টেন্ট পাঠাতে পারবে!",
        parse_mode="HTML", reply_markup=back_keyboard("admin_broadcast")
    )

async def handle_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admin_states: return
    state = admin_states[user_id]
    if state.get("step") != "admin_broadcast": return

    message = update.message
    target = state.get("target", "all")

    async def forward_message(target_chat_id):
        """Send any type of message to target"""
        if message.text:
            await context.bot.send_message(target_chat_id, message.text)
        elif message.photo:
            await context.bot.send_photo(target_chat_id, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            await context.bot.send_video(target_chat_id, message.video.file_id, caption=message.caption)
        elif message.document:
            await context.bot.send_document(target_chat_id, message.document.file_id, caption=message.caption)
        elif message.voice:
            await context.bot.send_voice(target_chat_id, message.voice.file_id, caption=message.caption)
        elif message.audio:
            await context.bot.send_audio(target_chat_id, message.audio.file_id, caption=message.caption)
        elif message.sticker:
            await context.bot.send_sticker(target_chat_id, message.sticker.file_id)
        elif message.video_note:
            await context.bot.send_video_note(target_chat_id, message.video_note.file_id)
        elif message.animation:
            await context.bot.send_animation(target_chat_id, message.animation.file_id, caption=message.caption)
        else:
            await context.bot.forward_message(target_chat_id, from_chat_id=message.chat_id, message_id=message.message_id)

    if target == "single":
        target_id = state.get("target_id")
        target_name = state.get("target_name", str(target_id))
        try:
            await forward_message(target_id)
            await message.reply_text(
                f"{E['success']} <b>Sent Successfully!</b>\n\n🎯 To: <b>{target_name}</b>\n🆔 ID: <code>{target_id}</code>",
                parse_mode="HTML", reply_markup=back_keyboard("admin_panel")
            )
        except Exception as ex:
            await message.reply_text(
                f"{E['error']} <b>Failed to send!</b>\n\n🎯 To: {target_name}\n❌ Error: <code>{str(ex)[:100]}</code>",
                parse_mode="HTML", reply_markup=back_keyboard("admin_panel")
            )
    else:
        users = await db.get_all_users(limit=10000)
        status_msg = await message.reply_text(f"{E['loading']} Broadcasting to {len(users)} users...")
        success = 0
        failed = 0
        for u in users:
            try:
                await forward_message(u['user_id'])
                success += 1
            except Exception:
                failed += 1
        await status_msg.edit_text(
            f"{E['success']} <b>Broadcast Complete!</b>\n\n✅ Sent: {success}\n❌ Failed: {failed}\n📊 Total: {len(users)}",
            parse_mode="HTML", reply_markup=back_keyboard("admin_panel")
        )
    del admin_states[user_id]

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    maintenance = await db.get_setting("maintenance_mode")
    global_limit = await db.get_setting("global_limit")
    text = f"""
{E['settings']} <b>System Settings</b>

━━━━━━━━━━━━━━━━━━━━
🔧 <b>Maintenance Mode:</b> {'🔴 ON' if maintenance == '1' else '🟢 OFF'}
📊 <b>Global Limit:</b> {global_limit}
📡 <b>API Status:</b> Active
{E['crown']} <b>Dev:</b> @King_X_vau

━━━━━━━━━━━━━━━━━━━━
"""
    settings_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{'🔴 Disable' if maintenance == '1' else '🟢 Enable'} Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton(f"{E['back']} Back", callback_data="admin_panel")]
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=settings_kb)

async def admin_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    current = await db.get_setting("maintenance_mode")
    new_val = "0" if current == "1" else "1"
    await db.set_setting("maintenance_mode", new_val)
    status = "ENABLED" if new_val == "1" else "DISABLED"
    await query.answer(f"Maintenance mode {status}!", show_alert=True)
    await admin_settings(update, context)

async def admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    analytics = await db.get_analytics()
    text = f"""
{E['chart']} <b>Analytics Dashboard</b>

━━━━━━━━━━━━━━━━━━━━
📈 <b>Overview:</b>
   Total SMS: {analytics['total_sms']}
   Success Rate: {analytics['success_rate']}%

📊 <b>SMS (Last 7 days):</b>
"""
    for row in analytics.get('sms_volume', []):
        text += f"   {row[0]}: {row[1]} msgs\n"
    text += "\n⏰ <b>Peak Hours:</b>\n"
    for row in analytics.get('peak_hours', []):
        text += f"   {row[0]}:00 → {row[1]} msgs\n"
    text += "\n━━━━━━━━━━━━━━━━━━━━"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=analytics_keyboard())

async def analytics_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle analytics_users, analytics_sms, analytics_success, analytics_hours"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS: return
    data = query.data
    analytics = await db.get_analytics()

    if data == "analytics_users":
        text = f"{E['users']} <b>User Growth (Last 7 Days)</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        rows = analytics.get('user_growth', [])
        if rows:
            for row in rows:
                text += f"📅 {row[0]}: +{row[1]} users\n"
        else:
            text += f"{E['info']} No data available."
    elif data == "analytics_sms":
        text = f"{E['sms']} <b>SMS Volume (Last 7 Days)</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        rows = analytics.get('sms_volume', [])
        if rows:
            for row in rows:
                text += f"📅 {row[0]}: {row[1]} SMS\n"
        else:
            text += f"{E['info']} No data available."
    elif data == "analytics_success":
        text = f"✅ <b>Success Rate Analysis</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📊 Overall Rate: <b>{analytics['success_rate']}%</b>\n"
        text += f"📩 Total SMS: {analytics['total_sms']}\n"
    elif data == "analytics_hours":
        text = f"⏰ <b>Peak Usage Hours</b>\n\n━━━━━━━━━━━━━━━━━━━━\n"
        rows = analytics.get('peak_hours', [])
        if rows:
            for i, row in enumerate(rows, 1):
                text += f"{i}. {row[0]}:00 - {row[1]} messages\n"
        else:
            text += f"{E['info']} No data available."
    else:
        text = f"{E['info']} Unknown analytics view."

    text += "\n━━━━━━━━━━━━━━━━━━━━"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=analytics_keyboard())

# ═══════════════════════════════════════════════════════════════
# MULTI-STEP TEXT HANDLER
# ═══════════════════════════════════════════════════════════════

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_states:
        state = user_states[user_id]
        step = state.get("step")
        if step == "awaiting_phone":
            await handle_phone_input(update, context)
            return
        elif step == "awaiting_message":
            await handle_message_input(update, context)
            return
        elif step == "add_contact_name":
            state["contact_name"] = update.message.text.strip()
            state["step"] = "add_contact_phone"
            await update.message.reply_text(
                f"{E['phone']} Now enter the phone number for <b>{state['contact_name']}</b>:",
                parse_mode="HTML", reply_markup=back_keyboard("contacts")
            )
            return
        elif step == "add_contact_phone":
            phone_text = update.message.text.strip()
            valid, formatted = SMSService.validate_phone(phone_text)
            if not valid:
                await update.message.reply_text(f"{E['error']} Invalid number. Use 01XXXXXXXXX format.", reply_markup=back_keyboard("contacts"))
                return
            await db.add_contact(user_id, state["contact_name"], formatted)
            del user_states[user_id]
            await update.message.reply_text(
                f"{E['success']} Contact <b>{state['contact_name']}</b> saved!\n📱 {formatted}",
                parse_mode="HTML", reply_markup=back_keyboard("contacts")
            )
            return
        elif step == "add_template_name":
            state["template_name"] = update.message.text.strip()
            state["step"] = "add_template_content"
            await update.message.reply_text(
                f"{E['template']} Now enter the message content for template <b>{state['template_name']}</b>:",
                parse_mode="HTML", reply_markup=back_keyboard("templates")
            )
            return
        elif step == "add_template_content":
            content = update.message.text.strip()
            await db.add_template(user_id, state["template_name"], content)
            del user_states[user_id]
            await update.message.reply_text(
                f"{E['success']} Template <b>{state['template_name']}</b> saved!",
                parse_mode="HTML", reply_markup=back_keyboard("templates")
            )
            return

    if user_id in admin_states:
        admin_state = admin_states[user_id]
        step = admin_state.get("step")
        if step == "admin_search":
            await handle_admin_search(update, context)
            return
        elif step == "admin_broadcast":
            await handle_admin_broadcast(update, context)
            return
        elif step == "broadcast_target_id":
            # Admin typed a user ID manually
            try:
                target_id = int(update.message.text.strip())
                target_user = await db.get_user(target_id)
                if target_user:
                    name = target_user.get('first_name') or target_user.get('username') or f"User_{target_id}"
                else:
                    name = f"User_{target_id}"
                admin_states[user_id] = {"step": "admin_broadcast", "target": "single", "target_id": target_id, "target_name": name}
                await update.message.reply_text(
                    f"🎯 <b>Target Set: {name}</b>\n<code>ID: {target_id}</code>\n\nএখন মেসেজ পাঠাও (Text/Photo/Video/File/Voice):",
                    parse_mode="HTML", reply_markup=back_keyboard("admin_broadcast")
                )
            except ValueError:
                await update.message.reply_text(f"{E['error']} Invalid User ID! শুধু নাম্বার দাও।", reply_markup=back_keyboard("admin_broadcast"))
            return

    is_admin = user_id in ADMIN_IDS
    await update.message.reply_text("Please use the buttons below 👇", reply_markup=main_menu_keyboard(is_admin))

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle media messages for broadcast"""
    user_id = update.effective_user.id
    if user_id not in admin_states: return
    state = admin_states[user_id]
    if state.get("step") == "admin_broadcast":
        await handle_admin_broadcast(update, context)

# ═══════════════════════════════════════════════════════════════
# CALLBACK ROUTER
# ═══════════════════════════════════════════════════════════════

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # User Panel
    if data == "main_menu": await main_menu_callback(update, context)
    elif data == "send_sms": await send_sms_menu(update, context)
    elif data == "sms_single": await sms_single_start(update, context)
    elif data == "sms_bulk": await sms_bulk_info(update, context)
    elif data == "sms_schedule": await sms_schedule_info(update, context)
    elif data == "sms_quick": await sms_quick_start(update, context)
    elif data == "sms_template": await sms_from_template(update, context)
    elif data == "sms_favorite": await sms_from_favorites(update, context)
    elif data == "confirm_send": await confirm_send(update, context)
    elif data == "my_history": await my_history(update, context)
    elif data == "my_profile": await my_profile(update, context)
    elif data == "my_stats": await my_stats(update, context)
    elif data == "edit_profile": await edit_profile(update, context)
    elif data == "my_referral": await my_referral(update, context)
    elif data == "upgrade_premium": await upgrade_premium(update, context)
    elif data == "contacts": await contacts_menu(update, context)
    elif data == "add_contact": await add_contact_start(update, context)
    elif data == "templates": await templates_menu(update, context)
    elif data == "add_template": await add_template_start(update, context)
    elif data == "favorites": await favorites_menu(update, context)
    elif data == "support": await support_menu(update, context)
    elif data == "about": await about_menu(update, context)

    # Admin Panel
    elif data == "admin_panel": await admin_panel(update, context)
    elif data == "admin_stats": await admin_stats(update, context)
    elif data == "admin_logs": await admin_logs(update, context)
    elif data == "admin_users": await admin_users(update, context)
    elif data == "admin_search": await admin_search(update, context)
    elif data == "admin_broadcast": await admin_broadcast(update, context)
    elif data == "broadcast_all": await broadcast_all_start(update, context)
    elif data == "broadcast_target": await broadcast_target_start(update, context)
    elif data == "admin_settings": await admin_settings(update, context)
    elif data == "admin_maintenance": await admin_maintenance(update, context)
    elif data == "admin_analytics": await admin_analytics(update, context)

    # View full log
    elif data.startswith("view_log_"): await view_log_detail(update, context)

    # Specific user message history
    elif data.startswith("user_logs_"): await admin_user_logs(update, context)

    # Broadcast target select
    elif data.startswith("bt_select_"): await broadcast_select_user(update, context)

    # Logs filter menu
    elif data == "logs_filter_menu": await logs_filter_menu(update, context)

    # Logs filters
    elif data.startswith("logs_filter_"): await admin_logs_filter(update, context)

    # Analytics detail
    elif data.startswith("analytics_"): await analytics_detail(update, context)

    # Favorites quick send
    elif data.startswith("fav_send_"):
        phone = data.replace("fav_send_", "")
        user_states[update.effective_user.id] = {"step": "awaiting_message", "phone": phone, "mode": "single"}
        await query.answer()
        await query.edit_message_text(
            f"{E['message']} <b>Enter message for</b> <code>{phone}</code>:\n\nType your message below.",
            parse_mode="HTML", reply_markup=back_keyboard("send_sms")
        )

    # Template use
    elif data.startswith("use_template_"):
        template_id = int(data.replace("use_template_", ""))
        user_id = update.effective_user.id
        templates = await db.get_templates(user_id)
        tmpl = next((t for t in templates if t['id'] == template_id), None)
        if tmpl:
            user_states[user_id] = {"step": "awaiting_phone", "mode": "template", "template_msg": tmpl['content']}
            await query.answer()
            await query.edit_message_text(
                f"{E['template']} Template: <b>{tmpl['name']}</b>\n\nNow enter the phone number:",
                parse_mode="HTML", reply_markup=back_keyboard("sms_template")
            )
        else:
            await query.answer("Template not found!", show_alert=True)

    elif data == "noop":
        await query.answer()
    else:
        await query.answer("Coming soon! 🚧")

# ═══════════════════════════════════════════════════════════════
# BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════

async def post_init(application: Application):
    await db.connect()
    application.bot_data["admin_ids"] = ADMIN_IDS
    logger.info("✅ Bot started! Database connected.")

async def post_shutdown(application: Application):
    await db.close()
    logger.info("🛑 Bot stopped! Database closed.")

def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Media handler for broadcast (photo, video, document, voice, audio, sticker, animation)
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.Document.ALL |
         filters.VOICE | filters.AUDIO | filters.Sticker.ALL |
         filters.ANIMATION | filters.VIDEO_NOTE) & ~filters.COMMAND,
        handle_media
    ))

    logger.info("🚀 Starting SHADOW Custom SMS Bot by @King_X_vau ...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
