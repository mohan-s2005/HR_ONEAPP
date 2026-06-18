import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from flask_mail import Mail, Message
from flask_wtf import FlaskForm # type: ignore
from flask_wtf.file import FileField # type: ignore
from wtforms import StringField, EmailField, TextAreaField, FileField, SubmitField # type: ignore
from wtforms.validators import DataRequired, Email # type: ignore
from werkzeug.utils import secure_filename




app = Flask(__name__)
app.secret_key = 'super_secret_session_key_change_this_in_production'
DB_FILE = 'database.db'


#file uploading Config
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok= True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 #100MB






# grha zhrj tknt gthb
#flask mailing feature
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'nadipallisudharshan@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'grha zhrj tknt gthb')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']


mail = Mail(app)


#Form Feild setup
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    attachment = FileField('Attachment(Optional, Max 100MB)')
    submit = SubmitField('Send Message')


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'User'
        )
    ''')
    conn.commit()
   
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        admin_pass = generate_password_hash('admin123')
        user_pass = generate_password_hash('user123')
        conn.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                     ('admin', admin_pass, 'admin@example.com', 'Admin'))
        conn.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                     ('user', user_pass, 'user@example.com', 'User'))
        conn.commit()
    conn.close()


init_db()


# --- ROUTES & AUTHENTICATION ---


@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'Admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
       
        from werkzeug.security import check_password_hash
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
           
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --- ADMIN ACTIONS ---


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
       
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)


@app.route('/admin/add', methods=['POST'])
def admin_add_user():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))
       
    username = request.form['username']
    email = request.form['email']
    from werkzeug.security import generate_password_hash
    password = generate_password_hash(request.form['password'])
    role = request.form['role']
   
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
                     (username, password, email, role))
        conn.commit()
        flash('User added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Username already exists!', 'danger')
    finally:
        conn.close()
       
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/edit/<int:id>', methods=['POST'])
def admin_edit_user(id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))
       
    username = request.form['username']
    email = request.form['email']
    role = request.form['role']
   
    conn = get_db_connection()
    conn.execute('UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?', (username, email, role, id))
    conn.commit()
    conn.close()
    flash('User updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete/<int:id>')
def admin_delete_user(id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('index'))
       
    if id == session['user_id']:
        flash('You cannot delete your own session!', 'danger')
        return redirect(url_for('admin_dashboard'))
       
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# --- USER ACTIONS ---


@app.route('/user')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
       
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('user_dashboard.html', user=user)


@app.route('/user/update', methods=['POST'])
def user_update():
    if 'user_id' not in session:
        return redirect(url_for('login'))
       
    email = request.form['email']
    conn = get_db_connection()
    conn.execute('UPDATE users SET email = ? WHERE id = ?', (email, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated!', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/user/reset-password', methods=['POST'])
def user_reset_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
       
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(request.form['password'])
    conn = get_db_connection()
    conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, session['user_id']))
    conn.commit()
    conn.close()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('user_dashboard'))




@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(
            subject=f"[Contact form] {form.subject.data}",
            recipients=['nadipallisudharshan@gmail.com'], #Admin mail
            reply_to=form.email.data
        )


        body_text = f"From: {form.name.data} - {form.email.data} \n\n\nMessage: \n{form.message.data}"


        #File handling
        file = form.attachment.data
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)


            if file_size > 20 * 1024 * 1024:
                body_text = f"\n\n[SYSTEM NOTE]: A larger file named `{filename}` ({round(file_size/(1024*1024), 2)})"
            else:
                #file size is under 100MB
                with app.open_resource(file_path) as fp:
                    msg.attach(filename, file.mimetype, fp.read())
                    body_text += f"\n\n[SYSTEM NOTE:] Attached file `{filename}` successfully"
        msg.body = body_text


        try:
            mail.send(msg)
            flash(f'Your form has submitted successfully', 'success')
        except Exception as e:
            flash(f'An error occured: {e}', 'danger')


    return render_template('contact.html', form=form)


#Handle large file
@app.errorhandler(413)
def file_too_large(e):
    flash('File is too large!\nMaximum allowed size is 100MB', 'danger')
    return redirect(url_for('contact'))




if __name__ == '__main__':
    print("\n" + "═"*60)
    print(" 🚀 FIXED RUNTIME MULTI-USER ENGINE STARTING...")
    print(" 👉 ADDRESS LOCATION: http://127.0.0.1:5000")
    print("═"*60 + "\n")
   
    app.run(debug=True, port=4000)

