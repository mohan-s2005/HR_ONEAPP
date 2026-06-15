# 🎓 HR Oneapp System

A full-stack human resource management and operational portal web application built with **Python Flask**, **SQLAlchemy (SQLite)**, and clean **HTML5/CSS3** utilizing Jinja2 template inheritance and real-time WebSockets.

## 🚀 Key Features Built

* **Secure Password Hashing:** Leverages `werkzeug.security` (PBKDF2 SHA256) to ensure credentials are never stored as plain text.
* **Session Protection:** Prevents unauthorized URL access via structural backend blueprint route verification.
* **Dynamic Flash Alerts:** Utilizes Flask's native message flashing engine to handle real-time form validation and authentication feedback.
* **Role-Based Routing:** Differentiates administrative and employee dashboard panels seamlessly based on user access levels.
* **Live Dynamic Interactions:** Implements `Flask-SocketIO` to manage real-time global messaging channels and simulated interactive video feeds instantly.

## 🛠️ Tech Stack Used

* **Backend:** Python 3, Flask
* **Database:** SQLAlchemy, SQLite3
* **Real-time Engine:** Flask-SocketIO (WebSockets)
* **Frontend:** Jinja2 Templates, HTML5, Custom CSS, JavaScript (DOM Manipulation)

## 🔑 Login Credentials

* **Admin Email:** `admin@company.org`
* **Admin Password:** `admin123`
* **Default OTP:** `000000`

## 💻 How to Run Locally

1. Clone the repository or navigate to the directory
2. Run `python3 app.py`
3. Open `http://127.0.0.1:5000/` in your browser to explore the HR dashboard.
