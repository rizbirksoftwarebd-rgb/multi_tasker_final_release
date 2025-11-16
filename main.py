import streamlit as st, importlib, os
from config import APP_TITLE, LOGO_PATH, SETUP_SECRET_ENV, DEFAULT_SETUP_SECRET
from auth.auth import Auth
from home.home import HomePage
from about.about import AboutPage
from admin.admin_dashboard import AdminDashboard
from utils.page_loader import discover_pages
import ensure_db
from db import add_or_update_user
import json

SETUP_FLAG = '.setup_done'

def load_css(path):
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

def is_setup_done():
    return os.path.exists(SETUP_FLAG)

def mark_setup_done():
    with open(SETUP_FLAG, 'w') as f:
        f.write('done')

class App:
    def __init__(self):
        st.set_page_config(page_title=APP_TITLE, page_icon=LOGO_PATH, layout='wide')
        try:
            ensure_db.init_db(insert_default_admin=False)
            self.db_mode = 'sql'
        except Exception:
            self.db_mode = 'json'
            st.warning('Database connection failed — running in JSON fallback mode.')
        self.auth = Auth()
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = None

    def show_setup(self):
        if is_setup_done():
            st.info('Setup has already been completed.')
            return
        st.title('Initial Setup — Create Admin')
        st.write('Enter the setup secret and create the initial admin account.')
        secret = st.text_input('Setup secret', type='password')
        expected = os.getenv(SETUP_SECRET_ENV) or DEFAULT_SETUP_SECRET
        if st.button('Verify secret'):
            if secret != expected:
                st.error('Invalid setup secret.')
            else:
                st.success('Secret verified. Create admin below.')
        st.markdown('---')
        with st.form('create_admin'):
            username = st.text_input('Admin username', value='admin')
            password = st.text_input('Admin password', type='password', value='Admin@12345')
            submitted = st.form_submit_button('Create admin')
            if submitted:
                try:
                    import binascii, secrets, hashlib
                    salt = secrets.token_bytes(16)
                    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200000)
                    h = {'algorithm':'pbkdf2_sha256','iterations':200000,'salt':binascii.hexlify(salt).decode(),'hash':binascii.hexlify(dk).decode()}
                    add_or_update_user(username, h['algorithm'], h['iterations'], h['salt'], h['hash'], role='admin')
                    mark_setup_done()
                    st.success('Admin created and setup completed. You can now log in.')
                except Exception as e:
                    st.error('Failed to create admin: ' + str(e))

    def show_login(self):
        load_css('home/home.css')
        st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:78vh'>", unsafe_allow_html=True)
        st.markdown("<div class='card' style='max-width:520px;padding:28px'>", unsafe_allow_html=True)
        st.image(LOGO_PATH, width=200)
        st.header('Sign in')
        uname = st.text_input('Username')
        pwd = st.text_input('Password', type='password')
        if st.button('Sign in'):
            ok, msg = self.auth.authenticate(uname.strip(), pwd)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = uname.strip()
                st.rerun()
            else:
                st.error(msg or 'Invalid credentials')
        st.markdown('</div></div>', unsafe_allow_html=True)

    def show_app(self):
        load_css('home/home.css')
        pages = discover_pages()
        with st.sidebar:
            st.image(LOGO_PATH, width=140)
            st.markdown('### Navigation')
            role = self.auth.get_role(st.session_state.username)
            permitted = []
            for p in pages:
                if role == 'admin':
                    permitted.append(p)
                else:
                    from db import get_permission
                    allowed = get_permission(st.session_state.username, p['name'])
                    if allowed is None or allowed:
                        permitted.append(p)
            opts = ['Home','About'] + [p['title'] for p in permitted]
            choice = st.radio('Go to', opts)
            st.markdown('---')
            if st.button('Logout'):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()

        if choice == 'Home':
            HomePage(self).run()
        elif choice == 'About':
            AboutPage(self).run()
        else:
            sel = None
            for p in pages:
                if p['title'] == choice:
                    sel = p
                    break
            if sel:
                mod = importlib.import_module(sel['module'])
                PageClass = getattr(mod, 'Page', None)
                if PageClass:
                    PageClass().run(self)

def main():
    params = st.query_params
    path_info = os.environ.get('PATH_INFO','') or os.environ.get('REQUEST_URI','')
    app = App()
    if (params.get('page', [''])[0] == 'setup') or path_info.endswith('/setup'):
        app.show_setup()
        return
    if not st.session_state.logged_in:
        app.show_login()
    else:
        app.show_app()

if __name__ == '__main__':
    main()
