import os, json, binascii
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.exc import OperationalError
from db_connection import get_engine
from json_loader import load_json

engine = get_engine(prefer_manual=True)
metadata = MetaData()

users = Table(
    "users", metadata,
    Column("username", String, primary_key=True),
    Column("algorithm", String, nullable=False),
    Column("iterations", Integer, nullable=False),
    Column("salt", String, nullable=False),
    Column("hash", String, nullable=False),
    Column("role", String, nullable=False, server_default="user"),
    Column("active", Integer, nullable=False, server_default="1")
)

pages = Table(
    "pages", metadata,
    Column("page", String, primary_key=True),
    Column("title", String, nullable=False)
)

user_permissions = Table(
    "user_permissions", metadata,
    Column("username", String, primary_key=True),
    Column("page", String, primary_key=True),
    Column("allowed", Integer, nullable=False, server_default="0")
)

def init_db(insert_default_admin=False, backup_json_path='backup_auth.json'):
    try:
        metadata.create_all(engine)
    except OperationalError as e:
        print('DB init failed', e)
        raise
    if insert_default_admin:
        with engine.connect() as conn:
            r = conn.execute("SELECT username FROM users WHERE role='admin' LIMIT 1").fetchone()
            if not r:
                data = load_json(backup_json_path, default=None)
                if data and 'admin' in data:
                    admin = data['admin']
                    try:
                        ins = users.insert().values(
                            username='admin',
                            algorithm=admin['algorithm'],
                            iterations=int(admin.get('iterations',100000)),
                            salt=admin['salt'],
                            hash=admin['hash'],
                            role='admin',
                            active=1
                        )
                        conn.execute(ins)
                        conn.commit()
                    except Exception as e:
                        print('Failed to seed admin from JSON', e)
