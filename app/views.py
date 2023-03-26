# _*_ encoding: utf-8 _*_

from flask import request, current_app, abort, make_response

from app import app
from .http_probe import probe


@app.route('/probe', methods=['GET'])
def perform_probe():
    if 'target' not in request.args:
        current_app.logger.warning(f"No target specified with request args: {dict(request.args)}")
        abort(400, "Required argument - target missed in request")
    _target = request.args.get('target')
    probe_result = probe(_target)
    if not probe_result:
        abort(400, "Incorrect URL provided for probe")
    metrics = probe_result.decode()
    response = make_response(metrics, 200)
    response.mimetype = "text/plain"
    return response
