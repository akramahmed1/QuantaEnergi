# -*- coding: utf-8 -*-
import sqlite3

def create_demo_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, token TEXT)')
    for i in range(10):
        c.execute('INSERT OR REPLACE INTO users (id, username, token) VALUES (?,?,?)', (i+1, f'demo{i}', f'token{i}'))
    conn.commit()
    conn.close()

create_demo_users()
