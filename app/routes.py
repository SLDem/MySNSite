from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User
from app.forms import LoginForm, RegisterForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    flash("Welcome to my site!")
    return render_template('home.html', title='Home')


@login_required
@app.route('/user')
def user():
    user = User.query.filter_by(username=current_user.username)
    return render_template('user.html', title=current_user.username, user=user)


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
    return render_template('login.html', form=form, title='Login')


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
    return render_template('register.html', form=form, title='Register')


@login_required
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('home'))


@login_required
@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved!')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title='Edit Profile')




