# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, session

# Import the core components that will be used by the application routes.
from . import config
from . import database
from . import common
from . import auth
from . import forms
from .session import DatabaseSessionInterface

def create_app():
    """
    Create and configure an instance of the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object('python_app.config')
    app.session_interface = DatabaseSessionInterface()
    app.session_cookie_name = app.config.get('DB_NAME', 'nubuilder4')

    @app.route('/')
    def index():
        return "<h1>nuBuilder Forte (Python Conversion)</h1><p>The web application skeleton is running.</p>"

    @app.route('/api/login', methods=['POST'])
    def login():
        params = request.get_json()
        if not params or 'username' not in params or 'password' not in params:
            return jsonify({'error': 'Username and password required'}), 400

        username = params['username']
        password = params['password']

        user = auth.check_globeadmin_login(username, password)
        if not user:
            user = auth.check_user_login(username, password)

        if user and not user.get('error'):
            session.clear()
            auth.create_user_session(session, user)
            return jsonify({'success': True, 'user_id': user['user_id']})
        elif user and user.get('error') == 'expired':
            return jsonify({'error': 'Account expired'}), 401
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    @app.route('/api/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'success': True})

    # --- Form API Routes ---
    @app.route('/api/getform', methods=['GET'])
    def get_form():
        form_id = request.args.get('form_id')
        record_id = request.args.get('record_id')

        if not form_id:
            return jsonify({'error': 'form_id parameter is required'}), 400

        form_data = forms.get_form_object(form_id, record_id)

        if 'error' in form_data:
            return jsonify(form_data), 404

        return jsonify(form_data)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
