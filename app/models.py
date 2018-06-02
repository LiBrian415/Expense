from app import app, db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), index = True, unique = True)
    first = db.Column(db.String(120))
    last = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.first, self.last)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def posted_expenses(self):
        return Expense.query.filter_by(user_id = self.id).order_by(
                                    Expense.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(64))
    amount = db.Column(db.Numeric(10,2))
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Expense {}>'.format(self.amount)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
