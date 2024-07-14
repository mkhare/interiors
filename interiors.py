from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, login_manager
from geopy.geocoders import Nominatim, GoogleV3



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_designer = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(150))

    def __init__(self, username, email, password, is_designer=False, location=None):
        self.username = username
        self.email = email
        self.password = password
        self.is_designer = is_designer
        self.location = location


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        #is_designer = 'designer' in request.form
        is_designer = False
        #location = request.form['location']
        location = 'Chicago'
        geolocator = GoogleV3(api_key='SAMPLE')
        location = geolocator.geocode(location)
        user = User(username=username, email=email, password=password, is_designer=is_designer, location=location)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_designer:
        customers = User.query.filter_by(is_designer=False).all()
        return render_template('dashboard.html', customers=customers)
    else:
        designers = User.query.filter_by(is_designer=True).all()
        return render_template('dashboard.html', designers=designers)


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':



    # db = SQLAlchemy()
    # app = Flask("interiors")
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # db.init_app(app)
    with app.app_context():
        db.create_all()
        # Add a new user if not exists
        if User.query.filter_by(username='john_doe').first() is None:
            new_user = User(
                username='john_doe',
                email='john@example.com',
                password='securepassword',
                is_designer=True,
                location='New York'
            )
            db.session.add(new_user)
            db.session.commit()
        # Print all users to verify
        users = User.query.all()
        for user in users:
            print(user)
    app.run(debug=True)
