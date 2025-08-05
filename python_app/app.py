# -*- coding: utf-8 -*-

from flask import Flask

# Import the core components that will be used by the application routes.
from . import config
from . import database
from . import common

def create_app():
    """
    Create and configure an instance of the Flask application.
    This uses the application factory pattern, which is a good practice.
    """
    app = Flask(__name__)

    # Load configuration from the config.py file.
    # Flask uses uppercase keys for its configuration variables.
    app.config.from_object('python_app.config')

    @app.route('/')
    def index():
        """
        A simple root route to verify that the Flask application is running.
        """
        return "<h1>nuBuilder Forte (Python Conversion)</h1><p>The web application skeleton is running.</p>"

    # --- AI API Routes ---

    # Import necessary modules for these routes
    from flask import request, jsonify
    from . import ai

    @app.route('/api/ai/prompt-info', methods=['POST'])
    def ai_prompt_info():
        params = request.get_json()
        if not params:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        prompt_info = ai.build_prompt_information(params)
        return jsonify({'error': False, 'prompt': prompt_info})

    @app.route('/api/ai/tags-from-prompt', methods=['POST'])
    def ai_tags_from_prompt():
        params = request.get_json()
        if not params:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        result = ai.get_tags_from_prompt(params)
        return jsonify(result)

    @app.route('/api/ai/response', methods=['POST'])
    def ai_response():
        params = request.get_json()
        if not params:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        prompt = params.get('prompt', '')
        post_data = params.get('post_data', {})

        result = ai.get_ai_response(prompt, post_data=post_data)
        return jsonify(result)


    # More routes will be added here as PHP files are converted.

    return app

# This block allows the app to be run directly for development purposes.
# e.g., `python -m python_app.app`
# In a production environment, a WSGI server like Gunicorn would be used.
if __name__ == '__main__':
    app = create_app()
    # Running in debug mode provides helpful error pages and auto-reloading.
    app.run(debug=True)
