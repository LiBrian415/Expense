from app import app, db
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from app.forms import (LoginForm, RegistrationForm, EditProfileForm, ExpenseForm,
                        ResetPasswordRequestForm, ResetPasswordForm, DeleteEntryForm)
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Expense
from app.email import send_password_reset_email
from werkzeug.urls import url_parse
from sqlalchemy import func

@app.route('/', methods = ['GET','POST'])
@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    #placeholder info
    form = ExpenseForm()
    form2 = DeleteEntryForm()
    if form.validate_on_submit():
        expense = Expense(type = form.type.data, amount = form.amount.data,
                            user = current_user)
        db.session.add(expense)
        db.session.commit()
        flash('Added expenses')
        return redirect(url_for('home'))
    date = datetime.utcnow()
    #daily sum
    day_start = date.strftime("%Y-%m-%d 00:00")
    day_end = date.strftime("%Y-%m-%d 23:59")
    daily = Expense.query.filter(Expense.timestamp.between(
        day_start, day_end))
    daily_sum = daily.with_entities(func.sum(Expense.amount)).scalar()
    #monthly sum
    month_start = date.strftime("%Y-%m-01 00:00")
    if date.month == 12:
        year = int(date.year)+1
        month_end = str(year)+"-01-01 00:00"
    else:
        month = int(date.month)+1
        month_end = date.strftime("%Y-"+str(month)+"-01 00:00")
    monthly = Expense.query.filter(Expense.timestamp.between(
        month_start, month_end))
    monthly_sum = monthly.with_entities(func.sum(Expense.amount)).scalar()
    #pagination
    page = request.args.get('page', 1, type=int)
    expenses = current_user.posted_expenses().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('home', page = expenses.next_num) \
        if expenses.has_next else None
    prev_url = url_for('home', page = expenses.prev_num) \
        if expenses.has_prev else None
    return render_template('home.html', form = form, form2=form2, expenses = expenses.items,
                            next_url = next_url, prev_url = prev_url,
                            daily_sum = daily_sum, monthly_sum = monthly_sum)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first = form.first_name.data,
                    last = form.last_name.data, email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form = form)

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first = form.first_name.data
        current_user.last = form.last_name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.first_name.data = current_user.first
        form.last_name.data = current_user.last
    return render_template('edit_profile.html', form = form)

@app.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/delete/<id>', methods = ['POST'])
@login_required
def delete(id):
    expense = Expense.query.get(int(id))
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('home'))
