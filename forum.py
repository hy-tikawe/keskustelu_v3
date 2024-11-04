import db

def get_threads():
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM threads t, messages m
             WHERE t.id = m.thread_id
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_thread(id):
    sql = "SELECT id, title FROM threads WHERE id = ?"
    result = db.query(sql, [id])
    return result[0] if result else None

def get_messages(thread_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, u.username
             FROM messages m, users u
             WHERE m.user_id = u.id AND m.thread_id = ?
             ORDER BY m.id"""
    return db.query(sql, [thread_id])

def get_message(id):
    sql = "SELECT id, content, user_id, thread_id FROM messages WHERE id = ?"
    result = db.query(sql, [id])
    return result[0] if result else None

def add_thread(title, content, user_id):
    sql = "INSERT INTO threads (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id

def add_message(content, user_id, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, thread_id) VALUES
             (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])

def update_message(id, content):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, id])

def remove_message(id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [id])

def search(query):
    sql = """SELECT m.id message_id,
                    m.thread_id,
                    t.title thread_title,
                    m.sent_at,
                    u.username
             FROM threads t, messages m, users u
             WHERE t.id = m.thread_id AND
                   u.id = m.user_id AND
                   m.content LIKE ?
             ORDER BY m.sent_at DESC"""
    return db.query(sql, ["%" + query + "%"])

def get_user_messages(id):
    sql = """SELECT m.id,
                    m.thread_id,
                    t.title thread_title,
                    m.sent_at
             FROM threads t, messages m
             WHERE t.id = m.thread_id AND
                   m.user_id = ?
             ORDER BY m.sent_at DESC"""
    return db.query(sql, [id])
