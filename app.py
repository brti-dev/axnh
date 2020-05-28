from config import config
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from forms import SearchForm
from pprint import pprint
import os, time, json

bootstrap = Bootstrap()
moment = Moment()

config_name = os.getenv('FLASK_CONFIG') or 'default'

app = Flask(__name__)
app.config.from_object(config[config_name])
config[config_name].init_app(app)

bootstrap.init_app(app)
moment.init_app(app)

class DB:
    hemisphere = 'north'

    def __init(self, hemisphere='north'):
        self.hemisphere = hemisphere

    """Get a whole data set"""
    def getTable(self, table):
        with open('./data/{}_{}.json'.format(table, self.hemisphere)) as json_file:
            data = json.load(json_file)
        return data

    """Return a data set filtered by properties"""
    def findAll(self, table, filterer=None):
        data = self.getTable(table)
        if filterer:
            data = dict(filter(filterer, data.items()))
        return data

    def findByName(self, name, table):
        data = self.getTable(table)
        return data.get(name)

@app.route('/')
def index():
    month = int(time.strftime('%m'))
    hour = int(time.strftime('%H'))
    print('Server time', month, hour)
    db = DB()
    # ????????????????
    data_bugs = db.findAll('bugs', lambda item: month in item[1]['months'] and hour in item[1]['times'])
    print(data_bugs)
    data_fish = db.findAll('fish', lambda item: month in item[1]['months'] and hour in item[1]['times'])
    return render_template(
        'index.html',
        current_time = datetime.utcnow(),
        bugs = data_bugs,
        fish = data_fish,
    )

""" Establishes the user's time via frontend
    If different from server time, refresh the page to reflect current stuffs"""
@app.route("/getTime", methods=['GET'])
def getTime():
    client_time = request.args.get("time")
    client_timezone = request.args.get("timezone")
    month, day, hour = client_time.split(' ')
    print("Client time:", client_time, client_timezone)

    server_time = '{} {} {}'.format(time.strftime('%m').lstrip(
        '0'), time.strftime('%d').lstrip('0'), time.strftime('%H').lstrip('0'))
    server_timezone = time.strftime('%Z')
    print("Server time:", server_time, server_timezone)

    if client_time != server_time:
        #set session for hemisphere
        db = DB()
        data_fish, data_bugs = {}, {}
        data_fish = db.findAll('fish', lambda item: int(month) in item[1]['months'] and int(hour) in item[1]['times'])
        data_bugs = db.findAll('bugs', lambda item: int(month) in item[1]['months'] and int(hour) in item[1]['times'])
        response_json = {
            # 'response':'Information updated based on your local time', 
            'html': render_template('bugs_render.html', bugs=data_bugs) + render_template('fish_render.html', fish=data_fish)
        }
    else:
        response_json = {'ok':'ok'}

    return jsonify(response_json)

@app.route("/fish")
@app.route("/fish/<name>")
def fish(name=None):
    db = DB()
    data = db.getTable('fish')
    if (name == None):
        flash('Work in progress')
        return render_template(
            'fish.html',
            data = data
        )
    else:
        return render_template('fish.html', name=name, data=db.findByName(name, 'fish'))

@app.route("/bugs")
@app.route("/bugs/<name>")
def bugs(name=None):
    db = DB()
    data = db.getTable('bugs')
    if (name == None):
        flash('Work in progress')
        return render_template(
            'bugs.html',
            data = data
        )
    else:
        return render_template('bugs.html', name=name, data=db.findByName(name, 'bugs'))

@app.route("/events")
@app.route("/events/<name>")
def events(name=None):
    return render_template('404.html', name=name)

users = {1:'bob', 2:'foo', 3:'bar'}

@app.route("/user/id/<int:id>")
def userId(id):
    if id not in users:
        abort(404)
    else:
        return redirect(url_for('user', name=users.get(id)))
    return 'Get USERID:{}'.format(id)

@app.route('/search/', methods=['GET', 'POST'])
@app.route('/search/<string:query>')
def search(query=None):
    form = SearchForm()
    results_bugs, results_fish = {}, {}
    num_results, num_results_bugs, num_results_fish = 0, 0, 0

    if form.validate_on_submit():
        query = form.query.data
        db = DB()
        results_fish = db.findAll('fish', lambda item: query.lower() in item[0].lower())
        results_bugs = db.findAll('bugs', lambda item: query.lower() in item[0].lower())
        num_results_bugs = len(results_bugs)
        num_results_fish = len(results_fish)
        num_results = num_results_bugs + num_results_fish

        print('form valid... redirect to', url_for('search', query=query))
        """This doesn't work. Why?! expect /search/foo actual /search/?query=foo
        return redirect(url_for('search', query=query))"""
        # return redirect('/search/' + query)
    return render_template('search.html', query=query, fish=results_fish, bugs=results_bugs, num_results=num_results, num_results_bugs=num_results_bugs, num_results_fish=num_results_fish)

@app.route("/user/<string:name>", methods=['GET', 'POST'])
def user(name):
    form = SearchForm()
    if form.validate_on_submit():
        name = form.name.data
        return redirect(url_for('user', name=name))
    return render_template(
        'user.html', 
        name = name,
        form = form,
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

"""Use Context Processor to inject variables into templates"""
@app.context_processor
def inject():
    return dict(search_form=SearchForm())
