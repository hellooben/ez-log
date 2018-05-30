import os

from flask import Flask
# from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # when not testing, load the instance config
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # the index page
    # @app.route('/')
    # def index():
    #     # print('Welcome to the index page! :D')
    #     return 'Welcome to the index page! :D'

    # a simple hello page
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # register the db functions
    from . import db
    db.init_app(app)

    # register the prompt blueprint, setting it as the default
    from . import prompt
    app.register_blueprint(prompt.bp)
    app.add_url_rule('/', endpoint='verify')

    # register the login blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    app.add_url_rule('/login', endpoint='login')

    # register the blog blueprint
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/home', endpoint='home')

    # register the 'my logs' blueprint
    from . import mine
    app.register_blueprint(mine.bp)
    app.add_url_rule('/my_logs', endpoint='mine')

    # Bootstrap(app)

    return app
