import streamlit as st
from db import list_users, add_or_update_user, deactivate_user, list_pages, set_permission, get_permission
import re, binascii, secrets, hashlib, json
from ensure_db import init_db, engine, users
from assets.copy_modal import open_modal, load_assets

def hash_password(password: str, salt: bytes=None, iterations: int=200000):
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return {
        "algorithm": "pbkdf2_sha256",
        "iterations": iterations,
        "salt": binascii.hexlify(salt).decode(),
        "hash": binascii.hexlify(dk).decode()
    }

def valid_password(p):
    if len(p) < 8:
        return False, "Minimum 8 characters required"
    if not re.search(r"[A-Z]", p):
        return False, "At least one uppercase letter required"
    if not re.search(r"[a-z]", p):
        return False, "At least one lowercase letter required"
    if not re.search(r"[0-9]", p):
        return False, "At least one digit required"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', p):
        return False, "At least one special character required"
    return True, ""

class AdminDashboard:
    def __init__(self, app):
        self.app = app
        init_db(insert_default_admin=True)

    def run(self):
        load_assets()
        st.title("Admin Dashboard")
        tabs = st.tabs(["Users","Permissions","System"])
        with tabs[0]:
            st.subheader("Users")
            users_list = list_users()
            for u in users_list:
                cols = st.columns([2,1,1,1,1])
                cols[0].write(u['username'])
                cols[1].write(u['role'])
                cols[2].write("Active" if u['active']==1 else "Deactivated")
                if cols[3].button(f"Deactivate##{u['username']}"):
                    deactivate_user(u['username'])
                    st.experimental_rerun()
                with cols[4]:
                    if st.button(f"Copy {u['username']}"):
                        open_modal(json.dumps(u, indent=2), theme='auto')
            st.markdown('---')
            st.subheader("Create / Update user")
            with st.form('create'):
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')
                role = st.selectbox("Role", ["user","admin"])
                submitted = st.form_submit_button("Create / Update")
                if submitted:
                    ok, msg = valid_password(password)
                    if not ok:
                        st.error(msg)
                    else:
                        h = hash_password(password)
                        add_or_update_user(username, h['algorithm'], h['iterations'], h['salt'], h['hash'], role)
                        st.success("User created/updated")
            st.markdown('---')
            st.subheader("Copy user info (click copy buttons)")
        with tabs[1]:
            st.subheader("Permissions")
            pages = list_pages()
            users_list = list_users()
            st.write("Toggle per-user permissions for each page:")
            for p in pages:
                st.markdown(f"**{p['title']}** ({p['page']})")
                for u in users_list:
                    current = get_permission(u['username'], p['page'])
                    chk = st.checkbox(f"{u['username']}", value=bool(current), key=f"perm-{p['page']}-{u['username']}")
                    if chk != bool(current):
                        set_permission(u['username'], p['page'], chk)
                        st.experimental_rerun()
            st.markdown('---')
            st.write("Permissions updated.")
        with tabs[2]:
            st.subheader("System")
            st.write(f"Database URL (detected): {engine.url}")
            st.write("Environment-based auto-init and default admin insertion is enabled.")
