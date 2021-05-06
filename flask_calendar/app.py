#!/usr/bin/python3
import logging
logging.basicConfig(filename='/home/Lii544/Projects/LTScal-pythonanywhere.log',level=logging.DEBUG)
from datetime import datetime
import locale
import os
import git # CD/CI with GitHub
import hmac # Securing the webhook
import hashlib # Securing the webhook
from typing import Dict
import config  # noqa: F401
logging.debug( ': loaded config')
logging.debug('now trying to load flask')
import flask
logging.debug('imported flask')
from flask_calendar.actions import (
    delete_task_action,
    do_login_action,
    edit_task_action,
    hide_repetition_task_instance_action,
    index_action,
    login_action,
    main_calendar_action,
    new_task_action,
    save_task_action,
    update_task_action,
    update_task_day_action,
    calendar_view_action,
)

from flask_calendar.app_utils import task_details_for_markup

def create_app(config_overrides: Dict = None):
    logging.debug(": function create_app running...")
    app = flask.Flask(__name__)
    app.config.from_object("config")

    logging.debug(": setting config")

    if config_overrides is not None:
        app.config.from_mapping(config_overrides)

    if app.config["LOCALE"] is not None:
        try:
            locale.setlocale(locale.LC_ALL, app.config["LOCALE"])
        except locale.Error as e:
            app.logger.warning("{} ({})".format(str(e), app.config["LOCALE"]))

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # route configuration for receiving information from GitHub
    def is_valid_signature(x_hub_signature, data, private_key):
        # x_hub_signature and data are from the webhook payload
        # private key is your webhook secret
        hash_algorithm, github_signature = x_hub_signature.split('=', 1)
        algorithm = hashlib.__dict__.get(hash_algorithm)
        encoded_key = bytes(private_key, 'latin-1')
        mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
        return hmac.compare_digest(mac.hexdigest(), github_signature)
    
    def webhook():
        logging.debug("starting webhook()")
        abort_code = 418
        if flask.request.method in ['POST', 'GET']:
            logging.debug("webhook method = POST")
            repo = git.Repo('/home/Lii544/Projects/LTScal')
            
            x_hub_signature = flask.request.headers.get('X-Hub-Signature')
            w_secret = os.environ['SECRET_TOKEN']
            if not is_valid_signature(x_hub_signature, flask.request.data, w_secret):
                print('Deploy signature failed:{sig}'.format(sig=x_hub_signature))
                flask.abort(abort_code)
            
            origin = repo.remotes.origin
            origin.pull()
            return 'Updated PythonAnywhere successfully by POST', 200
        else:
            logging.debug("webhook method <> POST")
            return 'Wrong event type', 400

    def index():
        return 'Updated automatically!!! :-)', 200
    # To avoid main_calendar_action below shallowing favicon requests and generating error logs
    @app.route("/favicon.ico")
    def favicon():
        return flask.send_from_directory(
            os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon",
        )
    app.add_url_rule("/server/update", "webhook", webhook, methods=["POST", "GET"])
    app.add_url_rule("/", "index", index, methods=["GET"])
    #app.add_url_rule("/", "index_action", index_action, methods=["GET"])
    #app.add_url_rule("/login", "login_action", login_action, methods=["GET"])
    #app.add_url_rule("/do_login", "do_login_action", do_login_action, methods=["POST"])
    #app.add_url_rule("/<calendar_id>/<view>", "calendar_view_action", calendar_view_action, methods=["GET"])

    #app.add_url_rule("/<calendar_id>/", "main_calendar_action", main_calendar_action, methods=["GET"])
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/new_task", "new_task_action", new_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "edit_task_action", edit_task_action, methods=["GET"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/task/<task_id>",
        "update_task_action",
        update_task_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/new_task", "save_task_action", save_task_action, methods=["POST"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/", "delete_task_action", delete_task_action, methods=["DELETE"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/",
        "update_task_day_action",
        update_task_day_action,
        methods=["PUT"],
    )
    app.add_url_rule(
        "/<calendar_id>/<year>/<month>/<day>/<task_id>/hide/",
        "hide_repetition_task_instance_action",
        hide_repetition_task_instance_action,
        methods=["POST"],
    )
    logging.debug(": before app.jinja_env")
    app.jinja_env.filters["task_details_for_markup"] = task_details_for_markup
    logging.debug(": before return")
    return app

logging.debug('creating app')
app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"], host=app.config["HOST_IP"])
