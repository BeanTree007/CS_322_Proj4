"""Flask application for the ACP brevet control time calculator."""

import flask
from flask import request
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration(proxied=__name__ != "__main__")
app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculate control times from kilometers, brevet distance, and start time.
    Expects URL-encoded km, brevet_dist_km, and start_time arguments.
    """
    km = request.args.get("km")
    brevet_distance = request.args.get("brevet_dist_km")
    start_time = request.args.get("start_time")
    if not km or not brevet_distance or not start_time:
        response = flask.jsonify(
            error="km, brevet_dist_km, and start_time are required"
        )
        return response, 400

    try:
        result = {
            "open": acp_times.open_time(km, brevet_distance, start_time),
            "close": acp_times.close_time(km, brevet_distance, start_time),
        }
    except ValueError as error:
        return flask.jsonify(error=str(error)), 400
    return flask.jsonify(result=result)


#############

app.debug = getattr(CONFIG, "DEBUG", False)
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
