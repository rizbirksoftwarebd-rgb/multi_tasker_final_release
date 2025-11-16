import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
load_dotenv()

def get_engine(prefer_manual=True):
    manual = os.getenv('MANUAL_DATABASE_URL','').strip()
    auto = os.getenv('DATABASE_URL','').strip() or os.getenv('RENDER_DATABASE_URL','').strip() or os.getenv('RENDER_EXTERNAL_POSTGRES_URL','').strip()

    if prefer_manual and manual:
        try:
            eng = create_engine(manual, future=True, pool_pre_ping=True)
            with eng.connect() as conn:
                conn.execute('SELECT 1')
            print('Connected using MANUAL_DATABASE_URL')
            return eng
        except Exception as e:
            print('Manual DB connect failed:', e)

    if auto:
        try:
            eng = create_engine(auto, future=True, pool_pre_ping=True)
            with eng.connect() as conn:
                conn.execute('SELECT 1')
            print('Connected using DATABASE_URL/Render DB')
            return eng
        except Exception as e:
            print('Auto DB connect failed:', e)

    sqlite_url = 'sqlite:///app.db'
    eng = create_engine(sqlite_url, future=True)
    print('Using sqlite fallback at', sqlite_url)
    return eng
