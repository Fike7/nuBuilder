# -*- coding: utf-8 -*-

import json
import re
import requests
from . import config
from . import database

def get_table_information(table_name):
    """
    Retrieves schema information for a given table, including column names,
    types, and primary key indicators.
    """
    # WARNING: Directly inserting table_name into the query can be risky.
    # This should only be used with trusted, internally-generated table names.
    if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
        return [] # Basic validation

    columns_query = f"SHOW COLUMNS FROM `{table_name}`"
    columns = database.run_query(columns_query, fetch="all")
    if not columns:
        return []

    pk_query = f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'"
    pk_result = database.run_query(pk_query, fetch="all")
    primary_keys = [row['Column_name'] for row in pk_result] if pk_result else []

    schema_parts = []
    for col in columns:
        col_name = col.get('Field')
        col_type = col.get('Type')
        if col_name and col_type:
            is_pk = ' (PK)' if col_name in primary_keys else ''
            schema_parts.append(f"`{col_name}`: {col_type}{is_pk}")

    return schema_parts

def build_prompt_information(params):
    """
    Builds a detailed prompt string based on tables, languages, scopes, and tags.
    """
    tables = params.get('tables', [])
    languages = list(set(params.get('languages', [])))
    scopes = list(set(params.get('scopes', [])))

    lines = []

    if tables:
        lines.append('## Table Schemas')
        for table_name in tables:
            schema_parts = get_table_information(str(table_name))
            lines.append(f"- **{table_name}**: " + ", ".join(schema_parts))
        lines.append('')

    # This could be externalized to a config file
    nu_wiki_base = 'https://wiki.nubuilder.cloud/index.php?title='
    language_messages = {
        'nuphp': f"Use nuBuilder PDO PHP functions: [Documentation]({nu_wiki_base}PHP)",
        # Add other languages as needed
    }

    if any(lang in language_messages for lang in languages):
        lines.append('## Languages & Technologies')
        for lang in languages:
            if lang in language_messages:
                lines.append(f"- {language_messages[lang]}")
        lines.append('')

    return "\n".join(lines)


def get_ai_response(prompt, ai_config_override=None, post_data=None):
    """
    Sends a prompt to the configured AI service and returns the response.
    """
    post_data = post_data or {}

    # For now, we only support the default openai config
    ai_conf = config.AI_CONFIG.get('openai', {})
    api_key = ai_conf.get('api_key')
    url = ai_conf.get('base_url')

    if not api_key or not url:
        return {'error': True, 'message': 'AI configuration is missing or invalid.'}

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }

    messages = [{'role': 'user', 'content': prompt}]

    defaults = {
        'model': 'gpt-4o',
        'messages': messages,
        'max_tokens': 4000,
        'temperature': 0.7,
    }

    payload = {**defaults, **post_data}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        reply = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        return {
            'error': False,
            'reply': reply,
            'id': data.get('id'),
            'model': data.get('model'),
            'usage': data.get('usage')
        }

    except requests.exceptions.Timeout:
        return {'error': True, 'message': 'Request timed out.'}
    except requests.exceptions.HTTPError as e:
        return {'error': True, 'message': f'API Error (HTTP {e.response.status_code}): {e.response.text}'}
    except requests.exceptions.RequestException as e:
        return {'error': True, 'message': f'Request Error: {e}'}
    except (json.JSONDecodeError, KeyError):
        return {'error': True, 'message': 'Invalid response format from AI API.'}

def get_tags_from_prompt(params):
    """
    Asks the AI to identify relevant tags from a user's prompt.
    """
    tags = params.get('tags', [])
    prompt = params.get('prompt', '')

    instruction = (
        "You are given a user message and a fixed list of tags. "
        "Your job is to pick which tags best represent the topics in the message.\n\n"
        "## Rules:\n"
        "1. If the message is about a feature, include the relevant tag.\n"
        "2. Tags are case-insensitive and based on conceptual relevance.\n\n"
        "## Output format:\n"
        "- A JSON array of matching tags only.\n"
        "- No extra text or comments.\n\n"
        f"## User message:\n{prompt}\n\n"
        f"## Tags:\n{','.join(tags)}"
    )

    response = get_ai_response(instruction)

    if response['error']:
        return {
            'error': True,
            'message': f"<h3>Error</h3><p>{response['message']}</p>"
        }

    try:
        # Extract JSON from markdown if present
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', response['reply'], re.DOTALL)
        json_str = json_match.group(1) if json_match else response['reply']
        result_array = json.loads(json_str)
        return {'error': False, 'result': result_array}
    except (json.JSONDecodeError, IndexError):
        return {
            'error': True,
            'message': f"<h3>Error</h3><p>Invalid JSON in AI response: {response['reply']}</p>"
        }
