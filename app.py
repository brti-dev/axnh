from config import config
from flask import Flask, abort, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

bootstrap = Bootstrap()
moment = Moment()

config_name = os.getenv('FLASK_CONFIG') or 'default'

app = Flask(__name__)
app.config.from_object(config[config_name])
config[config_name].init_app(app)

bootstrap.init_app(app)
moment.init_app(app)

@app.route('/')
def index():
    flash('fuuu')
    flash('baaa')
    return render_template(
        'index.html',
        current_time = datetime.utcnow(), 
    )

class SearchNameForm(FlaskForm):
    name = StringField('Search Users', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/user/<string:name>", methods=['GET', 'POST'])
def user(name):
    form = SearchNameForm()
    if form.validate_on_submit():
        name = form.name.data
        return redirect(url_for('user', name=name))
    return render_template(
        'user.html', 
        name = name,
        form = form,
    )

users = {1:'bob', 2:'foo', 3:'bar'}

@app.route("/user/id/<int:id>")
def userId(id):
    if id not in users:
        abort(404)
    else:
        return redirect(url_for('user', name=users.get(id)))
    return 'Get USERID:{}'.format(id)

@app.route("/bugs/<name>")
def bugs(name):
    return render_template('item.html', name=name)

@app.route("/fish/<name>")
def fish(name):
    return render_template('item.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500