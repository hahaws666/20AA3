from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import json
from static.py import sendemail

app = Flask(__name__, template_folder="template")
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'dkf3sldkjfDF23fLJ3b'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'USER'
    user_name = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    total_donation = db.Column(db.Float, nullable=False)
    def __repr__(self):
        return self.user_name

class Donation(db.Model):
    __tablename__ = "donation"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20))
    amount = db.Column(db.Float)
    def __repr__(self):
        return self.user_name


with app.app_context():
    db.create_all()



def add_user(username, email, password):
    print("name: " + username + " email: " + email + " password: " + password)
    new_user = User(user_name=username, email=email, password=password, total_donation=0)
    db.session.add(new_user)
    db.session.commit()


def add_donation(username, amount):
    print("username: "+username)
    new_donation = Donation(user_name=username, amount=amount)
    donor = User.query.filter_by(user_name=username).first()
    if not donor:
        print("no such user")
        return
    print(donor.total_donation)
    donor.total_donation = donor.total_donation + float(amount)
    db.session.add(new_donation)
    db.session.commit()


@app.route('/')
def home():
    with open('static/json/visit.json') as f:
        new_visit = json.load(f) + 1
        with open('static/json/visit.json', 'w') as f:
            json.dump(new_visit, f)
        f.close()
    with open('static/json/totalFund.json') as fundFile, open('static/json/lastDonor.json', 'r') as donorFile,\
        open('static/json/lastDonation.json') as donationFile:
        totoalFund = json.load(fundFile)
        donor = donorFile.read()
        donation = json.load(donationFile)
    fundFile.close()
    donorFile.close()
    donationFile.close()

    return render_template("index.html", amount=new_visit, money=totoalFund, people=donor, number=donation)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/gallary')
def gallary():
    return render_template("gallary.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/afterlogin')
def afterlogin():
    return render_template("afterlogin.html")



@app.route('/api/register', methods=['POST', 'GET'])
def register():
    print("I'm in!")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        password_confirmation = request.form['confirmPassword']
        if password != password_confirmation:
            return render_template("register.html")
        password_hashed = bcrypt.generate_password_hash(password)
        password_hashed_str = password_hashed.decode('utf-8')
        try:
            add_user(username, email, password_hashed_str)
            return redirect(url_for('login'))
        except exc.IntegrityError:
            return render_template('register.html')
    else:
        return render_template("register.html")

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        print("start login!")
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(user_name=username).first()
        if(not user):
            print("no such user")
            return render_template("login.html")
        elif not bcrypt.check_password_hash(user.password, password):
            print("password incorrect")
            return render_template("login.html")
        else:
            print("successfully logged in")
            session["user"] = username
            session["total"] = user.total_donation
            return redirect(url_for('afterlogin', username=username))
    else:
        if "user" in session:
            return redirect(url_for('afterlogin', username=session["user"]))
        return render_template("login.html")
@app.route("/api/paying", methods=['GET', 'POST'])
def paying():
    if request.method == "POST" and session['user']:
        user = User.query.filter_by(user_name=session["user"]).first()
        donation_amount = request.form['amount']
        add_donation(session["user"], donation_amount)
        sendemail.send_mail(user.email, user.user_name)
        with open('static/json/lastDonor.json', 'w') as donorFile, open('static/json/lastDonation.json', 'w') as donationFile, open(
                'static/json/totalFund.json') as fundFile:
            total_fund = json.load(fundFile)
            new_total = float(total_fund) + float(donation_amount)
            with open('static/json/totalFund.json', 'w') as fundFile:
                json.dump(json.dumps(new_total), fundFile)
            donorFile.write(session['user'])
            json.dump(donation_amount, donationFile)
        donorFile.close()
        donationFile.close()
        fundFile.close()
        return redirect(url_for('afterpay'))
    else:
        return render_template("paying.html")

@app.route('/afterpay')
def afterpay():
    return render_template("afterpay.html")

@app.route('/api/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'GET':
        session.pop("user", None)
        return redirect(url_for('home'))
    else:
        return render_template('logout.html')

@app.route('/api/back')
def back():
    return redirect(url_for('home'))

app.run(host='0.0.0.0', port=81, debug=True)