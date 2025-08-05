# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
# Use a relative import to access modules in the parent package (python_app)
from .. import ai
from .. import forms

# Create a Blueprint. The first argument is the blueprint's name,
# the second is the import name, and url_prefix will be prepended to all routes.
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- AI API Routes (moved from app.py) ---

@api_bp.route('/ai/prompt-info', methods=['POST'])
def ai_prompt_info():
    """
    Endpoint to build a detailed prompt based on tables, languages, etc.
    """
    params = request.get_json()
    if not params:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    prompt_info = ai.build_prompt_information(params)
    return jsonify({'error': False, 'prompt': prompt_info})

@api_bp.route('/ai/tags-from-prompt', methods=['POST'])
def ai_tags_from_prompt():
    """
    Endpoint to get relevant tags from a prompt using the AI service.
    """
    params = request.get_json()
    if not params:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    result = ai.get_tags_from_prompt(params)
    return jsonify(result)

@api_bp.route('/ai/response', methods=['POST'])
def ai_response():
    """
    A general-purpose endpoint to get a response from the AI service.
    """
    params = request.get_json()
    if not params:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    prompt = params.get('prompt', '')
    post_data = params.get('post_data', {})

    result = ai.get_ai_response(prompt, post_data=post_data)
    return jsonify(result)


# --- Form API Routes ---

@api_bp.route('/form', methods=['POST'])
def get_form():
    """
    The main endpoint for fetching a form definition and its data.
    This will replace the 'getform' call_type from nuapi.php.
    """
    state = request.get_json()
    if not state:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    form_id = state.get('form_id')
    record_id = state.get('record_id')

    if not form_id:
        return jsonify({'error': 'form_id is required'}), 400

    form_object = forms.get_form_object(form_id, record_id)

    # The original nuapi.php wrapped the form object in a list `f->forms[0]`.
    # We should do the same for compatibility.
    response_data = [form_object]

    return jsonify(response_data)


# --- Email API Route ---
from .. import emailer

@api_bp.route('/email/send', methods=['POST'])
def send_email_route():
    """
    Endpoint to send an email. This replaces the email functionality
    that would have been called from various parts of the PHP application.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    # Extract required parameters from the request data
    to_list = data.get('to_list')
    subject = data.get('subject')
    body = data.get('body')

    if not all([to_list, subject, body]):
        return jsonify({'error': 'Missing required fields: to_list, subject, body'}), 400

    # Optional parameters
    success, message = emailer.send_email(
        to_list=to_list,
        subject=subject,
        body=body,
        from_address=data.get('from_address'),
        from_name=data.get('from_name'),
        is_html=data.get('is_html', False),
        attachments=data.get('attachments'),
        cc_list=data.get('cc_list'),
        bcc_list=data.get('bcc_list')
    )

    return jsonify({'success': success, 'message': message})
