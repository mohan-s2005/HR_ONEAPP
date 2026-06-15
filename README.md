### 📝 README File Content

Here is the exact layout that has been generated and saved inside your project folder for reference:

```markdown
# HR Oneapp Matrix - Complete Workspace Operational Console

A comprehensive full-stack Human Resource management platform and live communication portal built using **Python Flask**, **SQLAlchemy ORM**, and **Socket.IO WebSockets**. The application features an organized Blueprint-driven architecture, interactive admin/employee modules, global live chat channels, and a real-time WebRTC-simulated conference room control console.

---

## 🛠️ Project Architecture & Layout

The project follows a modular, clean, scalable directory structure to segregate database management from presentation and routing engines:

```text
HR_Oneapp/
│
├── app.py                  # Main Server Configuration & WebSocket Hooks
├── models.py               # SQLAlchemy Database Schemas (User, Announcement, ChatMessage)
├── .gitignore              # Source control rules (prevents tracking db, caches, venv)
├── requirements.txt        # Python package dependencies manifest
│
├── routes/                 # Modular Blueprint Package Folder
│   ├── __init__.py         # Blank initialization file marking it as a package
│   ├── auth.py             # Login, Sign-Out, Forgot/Reset Password handlers
│   ├── admin.py            # Administrative workspace modifiers (user management)
│   └── user.py             # User profile pathways
│
└── templates/              # Jinja2 Layout View Component Templates
    ├── base.html           # Master boilerplate template with global Navbar & flash alert hooks
    ├── login.html          # Secure landing sign-in card layout
    ├── forgot_password.html# Token-generation validation request layout
    ├── reset_password.html # OTP token password overriding handler card
    └── dashboard.html      # Central interactive employee communication & configuration panel
