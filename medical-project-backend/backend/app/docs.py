from flask import Blueprint, send_from_directory, render_template
import os

docs_bp = Blueprint('docs', __name__, template_folder='templates')


@docs_bp.route('/openapi.yaml')
def openapi_spec():
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), 'static'),
        path='openapi.yaml',
        mimetype='application/x-yaml'
    )


@docs_bp.route('/')
def swagger_ui():
    return render_template('swagger_ui.html')
