from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from wtforms_helper import *
from elephantsql import *
from flask_socketio import SocketIO, send
from passlib.hash import pbkdf2_sha256
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template
import secrets
from sqlalchemy.exc import SQLAlchemyError
from flask_session import Session

app = Flask(__name__, template_folder='templates')

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.secret_key = secrets.token_hex(16) 
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://omeakqpt:xUUfVIvuZMNPUookJJXGiq4vFAwcShil@flora.db.elephantsql.com/omeakqpt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login=LoginManager(app)
login.init_app(app)

@login.user_loader  #add the logined user
def load_user(id):
  return db.session.query(User).get(int(id))   #= User.query.filter_by(id=id).first()

@app.route('/')
def index():
    form = RegistrationForm()
    return render_template('index.html', form=form)

@app.route('/form1')
@login_required
def filltheform():
    
    return render_template('fillinform.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
      login_form = LoginForm(request.form)
      email = login_form.email.data
      password = login_form.password.data 
      print("Email:", email)
      print("Password:", password)


      if login_form.validate_on_submit(): # it automatically check if post method was used, and the form was used
        user_object=User.query.filter_by(email=login_form.email.data).first()
        login_user(user_object)
        print(current_user.email)
        if current_user.is_authenticated:
         flash("OK")
         return redirect(url_for('filltheform'))
    return render_template("index.html", form=login_form)



@app.route('/signup', methods=['POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        #confirm_password = form.confirm_password.data

        user_object = User.query.filter_by(email=email).first()
        if user_object:
            flash("Someone else has taken this username!", 'error')
            return redirect(url_for('index'))

        hashed_pswd=pbkdf2_sha256.hash(password)  #automaticall salt and iteration added
        user=User(email=email, password=hashed_pswd)

        db.session.add(user)
        db.session.commit()


        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Registration failed. Please check your information and try again.', 'error')
        return redirect(url_for('index'))


@app.route('/submitForm', methods=['POST'])
def submitForm():
    try:
      customer = request.form.get('customer')
      customernumber = request.form.get('customernumber')
      orderitem = request.form.get('order')
      orderstatus = request.form.get('orderstatus')
      print(customer, customernumber, orderitem, orderstatus)

      user=Orders(customer=customer, customernumber=customernumber, orderitem=orderitem, orderstatus=orderstatus)

      db.session.add(user)
      db.session.commit()  

      return redirect(url_for('display_orders'))

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return redirect(url_for('filltheform')) 

@app.route("/logout", methods=['GET'])
def logout():
  logout_user()

  return "Logged out"


@app.route('/display_orders')
def display_orders():
    try:
        orders = Orders.query.all()  
        return render_template('display_orders.html', orders=orders)
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return render_template('error.html')  


  


if __name__=="__main__":
  app.run(debug=True)

  