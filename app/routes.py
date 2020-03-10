from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app import app, db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from app.models import User, Post, Comment
from app.forms import LoginForm, RegisterForm, EditProfileForm, PostForm, CommentForm
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os


# getting user last seen time( currently not in use and probably wont be cuz mainstream )
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# home page
@login_required
@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def home():
    if current_user.is_authenticated:
        form = PostForm()

        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been posted!')
            return redirect(url_for('home', post_id=post.id))

        posts = Post.query.order_by(Post.timestamp.desc()).all()
        comments = Comment.query.all()
        return render_template('home.html', title='Home', form=form, user=user, username=current_user.username,
                               posts=posts, comments=comments)
    return redirect(url_for('login'))


# posting comments button
@login_required
@app.route('/post_comment/<int:post_id>', methods=['GET', 'POST'])
def comment(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        user_comment = Comment(body=form.comment.data, commenter=current_user, post_id=post.id)
        db.session.add(user_comment)
        db.session.commit()
        flash('Comment added!')
        return redirect(url_for('home'))
    return render_template('post_comment.html', form=form, title='Post Comment', post_id=post.id)


# user page
@login_required
@app.route('/user/<username>')
def user(username):
    if current_user.is_authenticated:
        user = User.query.filter_by(username=username).first_or_404()
        posts = user.posts.order_by(Post.timestamp.desc())
        comments = Comment.query.all()
        return render_template('user.html', title='User Page', user=user, username=current_user.username,
                               posts=posts, comments=comments)
    return redirect(url_for('login'))


# logging users in
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


# registering users
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


# logging users out
@login_required
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!')
    return redirect(url_for('home'))


# editing profile
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


# following users
@login_required
@app.route('/follow/<username>')
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot follow yourself')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


# unfollowing users
@login_required
@app.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('home'))
    if user == current_user:
        flash('You cannot unfollow yourself')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}!'.format(username))
    return redirect(url_for('user', username=username))


# liking of posts
@login_required
@app.route('/like/<int:post_id>/<action>', methods=['GET', 'POST'])
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like(post)
        db.session.commit()
    elif action == 'dislike':
        current_user.dislike(post)
        db.session.commit()
    return redirect(request.referrer)


# liking of comments
@login_required
@app.route('/comment_like/<int:comment_id>/<action>', methods=['GET', 'POST'])
def comment_like_action(comment_id, action):
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if action == 'like':
        current_user.like_comment(comment)
        db.session.commit()
    elif action == 'dislike':
        current_user.dislike_comment(comment)
        db.session.commit()
    return redirect(request.referrer)


# avatar uploading
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
@app.route('/upload_avatar', methods=['POST', 'GET'])
def upload_avatar():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('user'))
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('user'))
        if file and allowed_file(file.filename):
            current_user.avatar_set = True
            db.session.commit()
            filename = secure_filename(file.filename)
            filename = current_user.username + '.' + filename.rsplit('.', 1)[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Your changes have been saved!')
            return redirect(url_for('home', filename=filename))
    return render_template('upload_avatar.html')


# Carmen
@login_required
@app.route('/carmen')
def carmen():
    return render_template('carmen.html', title='Carmen Electra')
