from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User
from app.forms import LoginForm, RegisterForm
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    flash("Hello and welcome to my site again usel, please enjoy nofing so fal")
    return render_template('home.html')


@app.route('/user')
def user():
    if current_user.is_authenticated:
        return render_template('user.html', username=current_user.username)
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('home'))




