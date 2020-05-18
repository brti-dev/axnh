from config import config
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from forms import SearchForm
import os, time, json
from pprint import pprint

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

    def getTable(self, table):
        with open('./data/fish_'+self.hemisphere+'.json') as json_file:
            data = json.load(json_file)
        return data

    def findAll(self, table, filter={}):
        data = self.getTable(table)
        if filter:
            for name, info in data.copy().items():
                print(name, '***********')
                found = 0
                for key, val in info.items():
                    print(key, ':', type(val))
                    if key in filter:
                        print('check', filter, key, filter[key])
                        if type(val) is list:
                            if filter[key] in val:
                                found += 1
                                print('found', filter[key], 'in', key)
                        else:
                            if filter[key] == val:
                                found += 1
                                print('found', filter[key], 'in', key)
                if found < 2:
                    del data[name]
        return data

    def findByName(self, name, table):
        data = self.getTable(table)
        return data.get(name)

@app.route('/')
def index():
    flash('foo')
    flash('bar')
    db = DB()
    data = db.findAll('fish', {'months':5, 'times':23})
    return render_template(
        'index.html',
        current_time = datetime.utcnow(),
        data = data
    )

""" Establishes the user's time via frontend
    If different from server time, refresh the page to reflect current stuffs"""
@app.route("/getTime", methods=['GET'])
def getTime():
    client_time = request.args.get("time")
    print("Client time: ", client_time)
    print("Server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'))
    month, day, hour, timezone = client_time.split(' ')
    #set session for hemisphere
    response_json = {'response':'OK', 'html':'<time datetime="{}-{}T{}:00{}">fuuu</time>'.format(month, day, hour, timezone)}
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
    return render_template('404.html', name=name)

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
    if form.validate_on_submit():
        query = form.query.data
        print('form valid... redirect to', url_for('search', query=query))
        """This doesn't work. Why?! expect /search/foo actual /search/?query=foo
        return redirect(url_for('search', query=query))"""
        return redirect('/search/' + query)
    return render_template('search.html', query=query)

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
