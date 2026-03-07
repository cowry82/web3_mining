import mysql.connector
from datetime import datetime
from config import config

# 数据库连接配置
db_config = {
    'host': config['database']['host'],
    'port': config['database']['port'],
    'user': config['database']['user'],
    'password': config['database']['password'],
    'database': config['database']['db']
}

def get_db():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        # 如果MySQL连接失败，尝试使用SQLite作为后备
        import sqlite3
        conn = sqlite3.connect('mining.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查是否是MySQL连接
    is_mysql = hasattr(conn, 'is_connected')
    
    # 用户表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL UNIQUE,
                tokens DECIMAL(20,6) DEFAULT 0,
                power DECIMAL(20,6) DEFAULT 0,
                referral_code VARCHAR(255) UNIQUE,
                referrer_id VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                tokens REAL DEFAULT 0,
                power REAL DEFAULT 0,
                referral_code TEXT UNIQUE,
                referrer_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # 节点购买记录表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_purchases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                node_type VARCHAR(50) NOT NULL,
                price DECIMAL(20,6) NOT NULL,
                purchase_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                referrer_id VARCHAR(255),
                status VARCHAR(20) DEFAULT 'active'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS node_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                node_type TEXT NOT NULL,
                price REAL NOT NULL,
                purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrer_id TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
    
    # 解锁记录表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unlock_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                amount DECIMAL(20,6) NOT NULL,
                unlock_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'unlocked'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unlock_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                unlock_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'unlocked'
            )
        ''')
    
    # 节点表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type VARCHAR(50) NOT NULL UNIQUE,
                total_supply INT NOT NULL,
                remaining INT NOT NULL,
                price DECIMAL(20,6) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT UNIQUE NOT NULL,
                total_supply INTEGER NOT NULL,
                remaining INTEGER NOT NULL,
                price REAL NOT NULL
            )
        ''')
    
    # 挖矿记录表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                amount DECIMAL(20,6) NOT NULL,
                power DECIMAL(20,6) NOT NULL,
                total_power DECIMAL(20,6) NOT NULL,
                daily_output DECIMAL(20,6) NOT NULL,
                mining_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mining_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                power REAL NOT NULL,
                total_power REAL NOT NULL,
                daily_output REAL NOT NULL,
                mining_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # 全网算力表
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_power (
                id INT AUTO_INCREMENT PRIMARY KEY,
                total_power DECIMAL(20,6) DEFAULT 0,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_power (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_power REAL DEFAULT 0,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # 币种表 (fa_app_currency)
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fa_app_currency (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL DEFAULT '',
                full_name VARCHAR(255) DEFAULT NULL,
                exchange DECIMAL(30,10) DEFAULT 0.0,
                suffix VARCHAR(32) NOT NULL DEFAULT '',
                thumb_image VARCHAR(255) DEFAULT NULL,
                process DECIMAL(30,10) DEFAULT 0.0,
                is_reg TINYINT DEFAULT 1,
                min_recharge INT DEFAULT 1,
                is_wid TINYINT DEFAULT 1,
                min_widthdraw DECIMAL(12,2) DEFAULT 0.0,
                max_widthdraw DECIMAL(12,2) DEFAULT 0.0,
                is_tran TINYINT DEFAULT 0,
                is_otc TINYINT DEFAULT 0,
                min_hang DECIMAL(30,10) DEFAULT 0.0,
                max_hang DECIMAL(30,10) DEFAULT 0.0,
                status ENUM('0','1') DEFAULT '1',
                createtime INT DEFAULT NULL,
                updatetime INT DEFAULT NULL,
                weigh INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fa_app_currency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT '',
                full_name TEXT DEFAULT NULL,
                exchange REAL DEFAULT 0.0,
                suffix TEXT NOT NULL DEFAULT '',
                thumb_image TEXT DEFAULT NULL,
                process REAL DEFAULT 0.0,
                is_reg INTEGER DEFAULT 1,
                min_recharge INTEGER DEFAULT 1,
                is_wid INTEGER DEFAULT 1,
                min_widthdraw REAL DEFAULT 0.0,
                max_widthdraw REAL DEFAULT 0.0,
                is_tran INTEGER DEFAULT 0,
                is_otc INTEGER DEFAULT 0,
                min_hang REAL DEFAULT 0.0,
                max_hang REAL DEFAULT 0.0,
                status TEXT DEFAULT '1',
                createtime INTEGER DEFAULT NULL,
                updatetime INTEGER DEFAULT NULL,
                weigh INTEGER DEFAULT 0
            )
        ''')
    
    # 用户币种表 (fa_app_currency_user)
    if is_mysql:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fa_app_currency_user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL DEFAULT 0,
                curr_id INT NOT NULL DEFAULT 0,
                num DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_hy DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_fb DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_lh DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_dj DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_hy_dj DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_fb_dj DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                num_lh_dj DECIMAL(20,6) NOT NULL DEFAULT 0.0,
                address VARCHAR(255) NOT NULL DEFAULT '',
                password VARCHAR(255) NOT NULL DEFAULT '',
                tron_address VARCHAR(255) DEFAULT NULL,
                tron_address_hex VARCHAR(1000) DEFAULT NULL,
                tron_private_key VARCHAR(1000) DEFAULT NULL,
                tron_public_key VARCHAR(1000) DEFAULT NULL,
                trxnum DECIMAL(20,6) DEFAULT 0.0,
                trxusdt DECIMAL(20,6) DEFAULT 0.0,
                ethnum DECIMAL(20,6) DEFAULT 0.0,
                usdtnum DECIMAL(20,6) DEFAULT 0.0,
                updatetime INT DEFAULT NULL,
                listentime INT DEFAULT NULL,
                listentimes INT DEFAULT NULL,
                version INT DEFAULT NULL,
                jtupdatetime INT DEFAULT 0,
                regtime INT NOT NULL DEFAULT 0,
                INDEX idx_user_id (user_id),
                INDEX idx_curr_id (curr_id),
                INDEX idx_user_curr (user_id, curr_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fa_app_currency_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 0,
                curr_id INTEGER NOT NULL DEFAULT 0,
                num REAL NOT NULL DEFAULT 0.0,
                num_hy REAL NOT NULL DEFAULT 0.0,
                num_fb REAL NOT NULL DEFAULT 0.0,
                num_lh REAL NOT NULL DEFAULT 0.0,
                num_dj REAL NOT NULL DEFAULT 0.0,
                num_hy_dj REAL NOT NULL DEFAULT 0.0,
                num_fb_dj REAL NOT NULL DEFAULT 0.0,
                num_lh_dj REAL NOT NULL DEFAULT 0.0,
                address TEXT NOT NULL DEFAULT '',
                password TEXT NOT NULL DEFAULT '',
                tron_address TEXT DEFAULT NULL,
                tron_address_hex TEXT DEFAULT NULL,
                tron_private_key TEXT DEFAULT NULL,
                tron_public_key TEXT DEFAULT NULL,
                trxnum REAL DEFAULT 0.0,
                trxusdt REAL DEFAULT 0.0,
                ethnum REAL DEFAULT 0.0,
                usdtnum REAL DEFAULT 0.0,
                updatetime INTEGER DEFAULT NULL,
                listentime INTEGER DEFAULT NULL,
                listentimes INTEGER DEFAULT NULL,
                version INTEGER DEFAULT NULL,
                jtupdatetime INTEGER DEFAULT 0,
                regtime INTEGER NOT NULL DEFAULT 0
            )
        ''')
    
    # 初始化power币种
    try:
        if is_mysql:
            cursor.execute('''
                INSERT IGNORE INTO fa_app_currency (id, name, full_name, suffix, status)
                VALUES (1, 'power', '算力币', 'POWER', '1')
            ''')
        else:
            cursor.execute('''
                INSERT OR IGNORE INTO fa_app_currency (id, name, full_name, suffix, status)
                VALUES (1, 'power', '算力币', 'POWER', '1')
            ''')
    except Exception as e:
        print(f"初始化power币种失败: {e}")
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()