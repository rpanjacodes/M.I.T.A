import sqlite3

DB_PATH = 'bot.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            nickname_toggle INTEGER DEFAULT 0,
            nickname_format TEXT DEFAULT 'User_{username}'
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS automod (
            guild_id INTEGER PRIMARY KEY,
            anti_invite INTEGER DEFAULT 0,
            anti_link INTEGER DEFAULT 0,
            anti_spam INTEGER DEFAULT 0
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS pin_messages (
            guild_id INTEGER,
            channel_id INTEGER,
            message TEXT,
            message_id INTEGER,
            enabled INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, channel_id)
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS log_settings (
            guild_id INTEGER PRIMARY KEY,
            log_channel_id INTEGER,
            log_enabled INTEGER DEFAULT 0
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_settings (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER
        )''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS regular_role (
            guild_id INTEGER PRIMARY KEY,
            role_id INTEGER,
            enabled INTEGER DEFAULT 0
        )''')

        c.execute('''
    CREATE TABLE IF NOT EXISTS giveaways (
        guild_id INTEGER,
        message_id INTEGER,
        channel_id INTEGER,
        image_url TEXT,
        end_time REAL,
        required_role TEXT,
        winner_count INTEGER,
        PRIMARY KEY (guild_id, message_id)
    )''')
# -------------------- Nickname Settings --------------------

def get_nick_setting(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT nickname_toggle, nickname_format FROM settings WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row if row else (0, "User_{username}")
    except sqlite3.Error as e:
        print(f"[DB] get_nick_setting error: {e}")
        return (0, "User_{username}")

def set_nick_setting(guild_id, value):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO settings (guild_id, nickname_toggle)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET nickname_toggle = excluded.nickname_toggle
            ''', (guild_id, value))
    except sqlite3.Error as e:
        print(f"[DB] set_nick_setting error: {e}")

def set_nick_format(guild_id, format_str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO settings (guild_id, nickname_format)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET nickname_format = excluded.nickname_format
            ''', (guild_id, format_str))
    except sqlite3.Error as e:
        print(f"[DB] set_nick_format error: {e}")

# -------------------- AutoMod Settings --------------------

def get_automod_settings(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT anti_invite, anti_link, anti_spam FROM automod WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row if row else (0, 0, 0)
    except sqlite3.Error as e:
        print(f"[DB] get_automod_settings error: {e}")
        return (0, 0, 0)

def set_automod_setting(guild_id, field, value):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(f'''
            INSERT INTO automod (guild_id, {field})
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET {field} = excluded.{field}
            ''', (guild_id, value))
    except sqlite3.Error as e:
        print(f"[DB] set_automod_setting error: {e}")

# -------------------- Persistent Pin Messages --------------------

def set_pin_message(guild_id, channel_id, message, message_id, enabled=True):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO pin_messages (guild_id, channel_id, message, message_id, enabled)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, channel_id) DO UPDATE
            SET message = excluded.message,
                message_id = excluded.message_id,
                enabled = excluded.enabled
            ''', (guild_id, channel_id, message, message_id, int(enabled)))
    except sqlite3.Error as e:
        print(f"[DB] set_pin_message error: {e}")

def get_pin_message(guild_id, channel_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT message, message_id FROM pin_messages WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
            row = c.fetchone()
            return (row[0], row[1]) if row else (None, None)
    except sqlite3.Error as e:
        print(f"[DB] get_pin_message error: {e}")
        return (None, None)

def set_pin_enabled(guild_id, channel_id, enabled):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO pin_messages (guild_id, channel_id, enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, channel_id) DO UPDATE
            SET enabled = excluded.enabled
            ''', (guild_id, channel_id, int(enabled)))
    except sqlite3.Error as e:
        print(f"[DB] set_pin_enabled error: {e}")

def is_pin_enabled(guild_id, channel_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT enabled FROM pin_messages WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
            row = c.fetchone()
            return row[0] == 1 if row else False
    except sqlite3.Error as e:
        print(f"[DB] is_pin_enabled error: {e}")
        return False

def get_full_pin_data(guild_id, channel_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT message, message_id, enabled FROM pin_messages WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
            row = c.fetchone()
            return row if row else (None, None, False)
    except sqlite3.Error as e:
        print(f"[DB] get_full_pin_data error: {e}")
        return (None, None, False)

# -------------------- Logging Settings --------------------

def set_log_settings(guild_id, channel_id=None, enabled=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            if channel_id is not None:
                c.execute('''
                INSERT INTO log_settings (guild_id, log_channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id
                ''', (guild_id, channel_id))
            if enabled is not None:
                c.execute('''
                INSERT INTO log_settings (guild_id, log_enabled)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_enabled = excluded.log_enabled
                ''', (guild_id, int(enabled)))
    except sqlite3.Error as e:
        print(f"[DB] set_log_settings error: {e}")

def get_log_channel_id(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT log_channel_id FROM log_settings WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        print(f"[DB] get_log_channel_id error: {e}")
        return None

def is_log_enabled(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT log_enabled FROM log_settings WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row[0] == 1 if row else False
    except sqlite3.Error as e:
        print(f"[DB] is_log_enabled error: {e}")
        return False

# -------------------- Anime Schedule Settings --------------------

def set_anime_schedule_settings(guild_id, channel_id, mode='instant'):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO anime_schedule (guild_id, channel_id, mode)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id, mode = excluded.mode
            ''', (guild_id, channel_id, mode))
    except sqlite3.Error as e:
        print(f"[DB] set_anime_schedule_settings error: {e}")

def get_anime_schedule_settings(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT channel_id, mode FROM anime_schedule WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row if row else (None, 'instant')
    except sqlite3.Error as e:
        print(f"[DB] get_anime_schedule_settings error: {e}")
        return (None, 'instant')

def has_posted_episode(episode_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM posted_episodes WHERE episode_id = ?', (episode_id,))
            return c.fetchone() is not None
    except sqlite3.Error as e:
        print(f"[DB] has_posted_episode error: {e}")
        return False

def mark_episode_posted(episode_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO posted_episodes (episode_id) VALUES (?)', (episode_id,))
    except sqlite3.Error as e:
        print(f"[DB] mark_episode_posted error: {e}")

# -------------------- Chatbot Settings --------------------

def set_chatbot_channel(guild_id, channel_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO chatbot_settings (guild_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
            ''', (guild_id, channel_id))
    except sqlite3.Error as e:
        print(f"[DB] set_chatbot_channel error: {e}")

def get_chatbot_channel(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT channel_id FROM chatbot_settings WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        print(f"[DB] get_chatbot_channel error: {e}")
        return None

def remove_chatbot_channel(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM chatbot_settings WHERE guild_id = ?', (guild_id,))
    except sqlite3.Error as e:
        print(f"[DB] remove_chatbot_channel error: {e}")

# -------------------- Regular Role --------------------

def set_regular_role(guild_id, role_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO regular_role (guild_id, role_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET role_id = excluded.role_id
            ''', (guild_id, role_id))
    except sqlite3.Error as e:
        print(f"[DB] set_regular_role error: {e}")

def toggle_regular_role(guild_id, enabled):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO regular_role (guild_id, enabled)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET enabled = excluded.enabled
            ''', (guild_id, int(enabled)))
    except sqlite3.Error as e:
        print(f"[DB] toggle_regular_role error: {e}")

def get_regular_role_settings(guild_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT role_id, enabled FROM regular_role WHERE guild_id = ?', (guild_id,))
            row = c.fetchone()
            return row if row else (None, 0)
    except sqlite3.Error as e:
        print(f"[DB] get_regular_role_settings error: {e}")
        return (None, 0)
    
    # -------------------- Giveaway Storage --------------------

def store_giveaway(guild_id, message_id, channel_id, image_url, end_time, required_role=None, winner_count=1):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO giveaways (guild_id, message_id, channel_id, image_url, end_time, required_role, winner_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (guild_id, message_id, channel_id, image_url, end_time, required_role, winner_count))
    except sqlite3.Error as e:
        print(f"[DB] store_giveaway error: {e}")

def get_active_giveaways():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT guild_id, message_id, channel_id, image_url, end_time, required_role, winner_count FROM giveaways
            ''')
            return c.fetchall()
    except sqlite3.Error as e:
        print(f"[DB] get_active_giveaways error: {e}")
        return []

def remove_giveaway(guild_id, message_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                DELETE FROM giveaways WHERE guild_id = ? AND message_id = ?
            ''', (guild_id, message_id))
    except sqlite3.Error as e:
        print(f"[DB] remove_giveaway error: {e}")
