# -*- coding: utf-8 -*-

# --- Database Settings ---
# Database Host / IP. You may try localhost if 127.0.0.1 does not work.
DB_HOST = "127.0.0.1"
# Database Name. You can change the name, if desired.
DB_NAME = "nubuilder4"
# Database port.
DB_PORT = 3306
# Database User. It is strongly recommended to use a different user than root.
DB_USER = "root"
# Database Password. We strongly recommend you to use any strong password.
DB_PASSWORD = ""
# InnoDB or MyISAM
DB_ENGINE = "InnoDB"
# Or utf8_general_ci etc.
DB_COLLATE = "utf8mb4_unicode_ci"
# Or utf8 etc.
DB_CHARACTER_SET = "utf8mb4"
# PDO Options equivalent for mysql-connector-python
DB_OPTIONS = {}

# --- Administrator Login ---
# Administrator username. You can choose any username you like.
GLOBEADMIN_USERNAME = "globeadmin"
# Administrator password. Please choose a stronger password!
GLOBEADMIN_PASSWORD = "nu"

# --- SSO ---
# normal/sso/both->Leave as 'normal' unless you want to enable SSO.
LOGON_MODE = 'normal'
# If LOGON_MODE=='both', only the SSO login option is displayed *unless* the last user
# to log in (from this browser) matches one of the listed users in this setting.
SSO_ONLY_EXCEPT = ['globeadmin']

# --- Includes ---
# These will be handled by the web framework's template system.
INCLUDE_JS = ''
INCLUDE_CSS = ''

# --- Settings ---
# Use settings from setup->settings if set to true (default)
SETTINGS_FROM_DB = True

# --- AI Config & Credentials ---
AI_CONFIG = {
    'openai': {
        'api_key': 'sk-proj-xxxxxxxxxx',
        'base_url': 'https://api.openai.com/v1/chat/completions',
    }
}

# --- 2FA: Bypass check for defined IPs ---
# Example structure, logic will need to be implemented in the application.
TWO_FA_SAFE_IP_ADDRESSES = {
    'globeadmin': [
        '192.168.0.1',
        '::1'
    ],
    'user': {
        '*': [
            '192.168.0.1',
            '::1'
        ]
    }
}
