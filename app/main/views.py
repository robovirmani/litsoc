from flask import render_template, session, redirect, url_for, flash, redirect, current_app, abort, request, jsonify
from . import main
from .forms import Login, SignUp, Admin_editor, Profile_Edit, PostForm
from .. import db, login_manager, moment
from ..models.users import User, Role, Permission, Post
from werkzeug import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug import generate_password_hash
from flask_mail import Message
from ..decorators import permission_required, admin_required
from datetime import datetime
import smtplib


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
                
@main.route('/Login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user,form.remember.data)
            flash('Logged In')
            return redirect(url_for('main.home' , page = 1))
        else:
            flash('Login Failed, Incorrect Username or Password Entered')
    return render_template('Login.html', form = form)

@main.route('/SignUp', methods=['GET', 'POST'])
def sign_up():
    form = SignUp()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username = form.username.data, email = form.email.data, password= hashed_password, phone_number = form.phone_number.data)
        Role.insert_roles()
        if form.email.data == 'mankaran32@gmail.com':
            user.role = Role.query.filter_by(role_name = 'Administrator').first()
        else:
            user.role = Role.query.filter_by(role_name = 'User').first()
        user.avtar_hash = user.generate_avtar_hash()
        db.session.add(user)
        db.session.commit()
        flash('Your Acount has been successfuly registered, A confirmation E-mail been sent to your emai address. ')
        #token = user.generate_confirmation_token()
        #User.send_mail(user.email, 'Confirm Account' , 'confirmation_email'
        #            , user = user, token = token)
        return redirect(url_for('main.login'))
    return render_template('Register.html', form = form)

@main.route('/super/<name>', methods=['GET', 'POST'])
@admin_required
@login_required
def Admin_edit(name):
    user = User.query.filter_by(username = name).first()
    if not user:
        abort(404)
    form = Admin_editor()
    if form.validate_on_submit():
        if user.username!=form.username.data and User.query.filter_by(username = form.username.data).first():
            flash('Username already in use.')
            return redirect(url_for('main.Admin_edit', name = name))
        if user.email!=form.email.data and User.query.filter_by(email = form.email.data).first():
            flash('Email already in use.')
            return redirect(url_for('main.Admin_edit', name = name))
        new_role = Role.query.filter_by(role_name = form.role.data).first()
        if not new_role:
            flash('Invaid role entered.Only Administrator, User and Moderator roles available.')
            return redirect(url_for('main.Admin_edit', name = name))
        user.username = form.username.data
        user.email = form.email.data
        user.role = new_role
        db.session.commit()
        flash('Account details updated successfully.')
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role.role_name
    return render_template('Admin.html', form = form)

@main.route('/profile/<name>', methods=['GET', 'POST'])
def Profile(name):
    user = User.query.filter_by(username = name).first()
    if not user:
        abort(404)
    return render_template('Profile.html', current_time = datetime.utcnow(), user = user)

@main.route('/Edit_Profile',methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user._get_current_object()
    if not user:
        abort(404)
    form = Profile_Edit()
    if form.validate_on_submit():
        if user.username!=form.username.data and User.query.filter_by(username = form.username.data).first():
            flash('Username already in use.')
            return redirect(url_for('main.edit_profile'))
        if user.email!=form.email.data and User.query.filter_by(email = form.email.data).first():
            flash('Email already in use.')
            return redirect(url_for('main.edit_profile'))

        user.username = form.username.data
        user.email = form.email.data
        user.location = form.location.data
        user.about_me = form.about_me.data

        db.session.commit()
        flash('Account details updated successfully.')
    form.username.data = user.username
    form.email.data = user.email
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('Profile_Edit.html', form = form)



@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('Index.html')


@main.route('/confirm/<token>')
@login_required
def confirm_id(token):
    if current_user.confirmed:
        return redirect(url_for('main.home', page = 1))
    if current_user.confirm(token):
        flash('You have confirmed your account.')
    else:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.home', page = 1))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('main.index'))

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    User.generate_fake()
    Post.generate_fake()
    return "DB modifications made"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


@main.route('/Home/<int:page>', methods=['GET', 'POST'])
@login_required
def home(page):
    per_page = 10
    form = PostForm()
    if current_user.is_authenticated and form.validate_on_submit():

        post = Post(body=form.body.data)
        post.author=current_user._get_current_object()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.home', page = 1))
    

    posts = Post.query.order_by(Post.timestamp.desc()).all()
    pages = (len(posts)-1)//per_page + 1
    start = (page-1)*per_page
    end = start + per_page
    posts = posts[start:end]

    return render_template('HomePage.html', form=form, posts=posts, current_time = datetime.utcnow(), pages = pages)



@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post_viewer(id):

    post = Post.query.get_or_404(id)
    return render_template('Post.html', posts = [post])

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def post_editor(id):

    post = post = Post.query.get_or_404(id)
    if not (post.author == current_user._get_current_object() or current_user.can(Permission.MODERATE_COMMENTS)):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()
        flash('Post edited successfully.')
        return redirect(url_for('main.post_viewer', id = post.id))
    form.body.data = post.body
    return render_template('Post_Edit.html' ,form = form)










