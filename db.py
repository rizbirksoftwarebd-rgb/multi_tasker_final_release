from ensure_db import users, pages, user_permissions, engine
from sqlalchemy import select, insert, update, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError

def add_or_update_user(username, algorithm, iterations, salt, hashhex, role="user", active=1):
    backend = engine.url.get_backend_name()
    try:
        if backend == "postgresql":
            stmt = pg_insert(users).values(
                username=username, algorithm=algorithm, iterations=iterations, salt=salt, hash=hashhex, role=role, active=active
            ).on_conflict_do_update(
                index_elements=[users.c.username],
                set_={"algorithm": algorithm, "iterations": iterations, "salt": salt, "hash": hashhex, "role": role, "active": active}
            )
            with engine.begin() as conn:
                conn.execute(stmt)
        else:
            stmt = text("""
                INSERT INTO users (username, algorithm, iterations, salt, hash, role, active)
                VALUES (:username, :algorithm, :iterations, :salt, :hash, :role, :active)
                ON CONFLICT(username) DO UPDATE SET
                    algorithm = excluded.algorithm,
                    iterations = excluded.iterations,
                    salt = excluded.salt,
                    hash = excluded.hash,
                    role = excluded.role,
                    active = excluded.active
            """)
            with engine.begin() as conn:
                conn.execute(stmt, {"username":username, "algorithm":algorithm, "iterations":iterations, "salt":salt, "hash":hashhex, "role":role, "active":active})
    except SQLAlchemyError as e:
        print('DB error', e)
        raise

def get_user(username):
    stmt = select(users).where(users.c.username == username)
    with engine.connect() as conn:
        r = conn.execute(stmt).mappings().fetchone()
        return dict(r) if r else None

def list_users():
    stmt = select(users.c.username, users.c.role, users.c.active)
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().fetchall()
        return [dict(r) for r in rows]

def deactivate_user(username):
    stmt = update(users).where(users.c.username==username).values(active=0)
    with engine.begin() as conn:
        conn.execute(stmt)

def register_page(page, title):
    backend = engine.url.get_backend_name()
    try:
        if backend == 'postgresql':
            stmt = pg_insert(pages).values(page=page, title=title).on_conflict_do_update(index_elements=[pages.c.page], set_={'title':title})
            with engine.begin() as conn:
                conn.execute(stmt)
        else:
            stmt = text("""
                INSERT INTO pages (page, title) VALUES (:page, :title)
                ON CONFLICT(page) DO UPDATE SET title = excluded.title
            """)
            with engine.begin() as conn:
                conn.execute(stmt, {'page':page, 'title':title})
    except SQLAlchemyError as e:
        print('Page register error', e)

def list_pages():
    stmt = select(pages.c.page, pages.c.title)
    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().fetchall()
        return [dict(r) for r in rows]

def set_permission(username, page, allowed):
    stmt = insert(user_permissions).values(username=username, page=page, allowed=1 if allowed else 0)
    backend = engine.url.get_backend_name()
    try:
        if backend == 'postgresql':
            stmt = pg_insert(user_permissions).values(username=username, page=page, allowed=1 if allowed else 0).on_conflict_do_update(index_elements=[user_permissions.c.username, user_permissions.c.page], set_={'allowed':1 if allowed else 0})
            with engine.begin() as conn:
                conn.execute(stmt)
        else:
            stmt = text("""
                INSERT INTO user_permissions (username, page, allowed)
                VALUES (:username, :page, :allowed)
                ON CONFLICT(username, page) DO UPDATE SET allowed = excluded.allowed
            """)
            with engine.begin() as conn:
                conn.execute(stmt, {'username':username, 'page':page, 'allowed':1 if allowed else 0})
    except SQLAlchemyError as e:
        print('Permission error', e)

def get_permission(username, page):
    stmt = select(user_permissions.c.allowed).where(user_permissions.c.username==username).where(user_permissions.c.page==page)
    with engine.connect() as conn:
        r = conn.execute(stmt).scalar()
        return bool(r) if r is not None else None
