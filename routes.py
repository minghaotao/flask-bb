# / Some of code has been copied from Corey Shaffer's flask application
# https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
# /
from flask import request, render_template, url_for, flash, redirect
from flaskbb import app, db, bcrypt, mail
from flaskbb.forms import RegistrationFrom, LoginFrom, RequestRestForm, ResetPasswordForm, Coursecopy, Coursemerge
from flaskbb.Bb_API.Bb_production import Blackboard
from flaskbb.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import json


@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template('home.html', title='Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationFrom()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are not able to log in', 'Success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/create_course", methods=['GET', 'POST'])
@login_required
def create_course():
    try:
        if request.method == 'POST':
            bb = Blackboard()
            course_id = request.form['course_id']
            course_name = request.form['course_name']
            course_type = request.form['type']
            username = request.form['userName']

            bb.create_course(course_id, course_name, course_type)
            bb.create_course_memberships('courseId:{}'.format(course_id.strip()), 'userName:{}'.format(username),
                                         'Instructor')

            # Add to the Post Database table
            post = Post(title='Create_course',
                        content=f'{course_id} has been created for {username}', author=current_user)
            db.session.add(post)
            db.session.commit()

            return render_template('results.html', title='Create Course', course_id=course_id, username=username)

        else:
            return render_template('create_course.html')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route("/batch_enroll", methods=['GET', 'POST'])
@login_required
def batch_enroll():
    try:
        if request.method == 'POST':
            bb = Blackboard()
            course_role = request.form['role']
            userName = request.form['username']
            courses = request.form['course_id']
            # courses = [course.strip() for course in courses.split('\r')]

            for course in courses.split('\r'):
                bb.create_course_memberships('courseId:{}'.format(course.strip()), 'userName:{}'.format(userName),
                                             course_role)

            post = Post(title='Batch_enroll_courses',
                        content=f'{userName} has been added to {courses} as {course_role}', author=current_user)
            db.session.add(post)
            db.session.commit()

            return render_template('results.html', userName=userName, courses=courses)

        else:
            return render_template('batch_enroll.html')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route("/add_students", methods=['GET', 'POST'])
@login_required
def add_students():
    try:
        if request.method == 'POST':
            bb = Blackboard()
            course_role = request.form['role']
            course = request.form['course_id']
            userName = request.form['username']

            for user in userName.split('\r'):
                bb.create_course_memberships('courseId:{}'.format(course.strip()), 'userName:{}'.format(user.strip()),
                                             course_role)

            post = Post(title='Batch_enroll_users', content=f'{userName} has been added to {course} as {course_role}',
                        author=current_user)
            db.session.add(post)
            db.session.commit()

            return render_template('results.html', userName=userName, course=course)
        else:
            return render_template('add_students.html')
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route("/course_copy", methods=['GET', 'POST'])
@login_required
def course_copy():
    form = Coursecopy()
    try:
        if form.validate_on_submit():
            bb = Blackboard()
            status = form.Copy_type.data
            Origin_course = form.Orig_courseId.data
            Dest_course = form.Dest_courseId.data
            if int(status) == 0:
                for or_course in Dest_course.split('\r'):
                    r = bb.get_courseid(f'{or_course.strip()}')
                    r = json.loads(r)
                    bb.course_copy(Origin_course, f"{r['id']}", 0)
                return render_template('results.html', status=status, or_course=or_course, Origin_course=Origin_course,
                                       Dest_course=Dest_course)
            elif int(status) == 1:
                for or_course in Dest_course.split('\r'):
                    bb.course_copy(Origin_course, or_course, 1)
                return render_template('results.html', status=status, or_course=or_course,
                                       Origin_course=Origin_course,
                                       Dest_course=Dest_course)
            else:
                flash('Something went wrong')
                return render_template('error.html', error=str(Exception))
        else:
            return render_template('course_copy.html', form=form)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route("/course_merge", methods=['GET', 'POST'])
@login_required
def course_merge():
    form = Coursemerge()
    try:
        if form.validate_on_submit():
            bb = Blackboard()
            course_id = form.Course_id.data
            course_name = form.Course_name.data
            child_course = form.Child_courses.data

            partial_course = course_id.rsplit('_', 1)
            Term = partial_course[1]
            new_courseName = Term + '_' + partial_course[0] + '_' + course_name

            bb.create_course(course_id.strip(), new_courseName, 'False', Term)

            for child_id in child_course.split('\r'):
                bb.course_merge(course_id.strip(), child_id.strip())

            post = Post(title="Course_merge", content=f"{child_course} has been merged to {course_id}",
                        author=current_user)
            db.session.add(post)
            db.session.commit()

            return render_template('results.html', master_id=course_id, child_course=child_course)
        else:
            return render_template('course_merge.html', form=form)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/log")
@login_required
def log():
    try:
        post = Post()
        return render_template('log.html', Post=post)
    except Exception as e:
        return render_template('error.html', error=str(e))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f''' To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    
    If you didn't make this request then simply ingore this email and no change  
    '''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with Instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or experied token', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated!', 'Success')
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
