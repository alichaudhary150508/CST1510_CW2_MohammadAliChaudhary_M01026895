import streamlit as st
import hashlib
import os

from database import init_db, add_user_to_db, get_user_from_db
from models.user import User

# Page title and icon
st.set_page_config(
    page_title="Home",
    page_icon="🗝️",
)

# Initialize DB
init_db()

USER_DATA_PATH = "users.txt"


# -------- Helpers --------
def load_users():
    """Load users from the text file."""
    users = {}
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "r") as f:
            for line in f:
                if ":" in line:
                    user, pw = line.strip().split(":", 1)
                    users[user] = pw
    return users


def save_user_to_text(user: User):
    """Save a User object to users.txt"""
    with open(USER_DATA_PATH, "a") as f:
        f.write(user.to_text_line())


def hash_password(password):
    """Hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


# -------- Init Session --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


# -------- Modern Button CSS --------
st.markdown("""
    <style>
    .title-center {
        text-align: center;
        font-weight: 800;
        font-size: 40px;
        margin-bottom: 1rem;
    }
    .btn-modern {
        width: 260px !important;
        padding: 18px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
    }
    .logout-button button {
        width: 100%;
        padding: 10px 0;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        background-color: #e53935;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


# Title
st.markdown('<h1 class="title-center">Welcome!</h1>', unsafe_allow_html=True)

users = load_users()

# LOGGED-IN AREA
if st.session_state.logged_in:
    st.success(f"Logged in as **{st.session_state.username}**")
    st.write("")

    colA, colB, colC = st.columns([2, 1, 2])
    with colB:
        st.markdown('<div class="logout-button">', unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>Choose an Area:</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.5])

    with col2:
        cyber_btn = st.button("Cyber Incidents", key="cyber_btn")
        dash_btn = st.button("Dashboard", key="dash_btn")
        it_btn = st.button("IT Operations", key="it_btn")
        data_btn = st.button("Data Science", key="data_btn")

        st.markdown("""
            <script>
                const btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
                if (btns[0]) btns[0].classList.add('btn-modern');
                if (btns[1]) btns[1].classList.add('btn-modern');
                if (btns[2]) btns[1].classList.add('btn-modern');
                if (btns[3]) btns[1].classList.add('btn-modern');
            </script>
        """, unsafe_allow_html=True)

    if cyber_btn:
        st.switch_page("pages/Cyber Incidents.py")

    if dash_btn:
        st.switch_page("pages/Dashboard.py")

    if it_btn:
        st.switch_page("pages/IT Operations.py")

    if data_btn:
        st.switch_page("pages/Data Science.py")

    st.stop()

# LOGIN + REGISTER SECTION
tab_login, tab_register = st.tabs(["Login", "Register"])

# ---------------- LOGIN ----------------
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_user_input")
    login_password = st.text_input("Password", type="password", key="login_pw_input")

    if st.button("Log in", key="login_btn"):
        hashed_pw = hash_password(login_password)
        db_user = get_user_from_db(login_username)

        if db_user:
            if db_user.password == hashed_pw:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error("Invalid password")
        else:
            st.error("User does not exist")

# REGISTER
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("New Username", key="reg_user_input")
    email = st.text_input("Email", key="reg_email_input")
    first_name = st.text_input("First Name", key="reg_first_input")
    last_name = st.text_input("Last Name", key="reg_last_input")
    pw = st.text_input("Password", type="password", key="reg_pw_input")
    cpw = st.text_input("Confirm Password", type="password", key="reg_cpw_input")

    if st.button("Create Account", key="reg_btn_create"):
        if not new_username or not pw:
            st.warning("Fill everything in.")
        elif pw != cpw:
            st.error("Passwords do not match.")
        elif new_username in users:
            st.error("User already exists.")
        else:
            hashed_pw = hash_password(pw)

            # Create the User object
            new_user = User(
                username=new_username,
                email=email,
                password=hashed_pw,
                first_name=first_name,
                last_name=last_name
            )

            # Save to database and text file
            add_user_to_db(new_user)
            save_user_to_text(new_user)

            st.success("Account created. You can now log in.")