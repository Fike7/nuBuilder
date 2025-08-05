# -*- coding: utf-8 -*-

import bcrypt
from . import database
from . import config

def hash_password(password):
    """
    Hashes a password using bcrypt.
    """
    # The salt is automatically generated and included in the hash by bcrypt.
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    """
    Verifies a password against a bcrypt hash.
    """
    if not password or not hashed_password:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def check_user_login(username, password):
    """
    Checks a standard user's login credentials against the database.
    Returns a dictionary with user information if successful, None otherwise.
    """
    sql = """
        SELECT zzzzsys_user_id AS user_id, sus_login_name AS login_name,
               sus_name AS user_name, sus_login_password as hashed_password,
               sus_change_password as change_password,
               IF(sus_expires_on < CURDATE() AND NOT sus_expires_on IS NULL, 1, 0) AS expired
        FROM zzzzsys_user
        WHERE sus_login_name = %s
    """
    user_row = database.run_query(sql, params=(username,), fetch="one")

    if not user_row:
        return None

    if user_row['expired'] == 1:
        return {'error': 'expired'}

    # The original PHP code has a fallback for MD5 passwords.
    # For this conversion, we will assume all passwords use the modern hashing.
    # If MD5 support is needed, it can be added here.

    if verify_password(password, user_row['hashed_password']):
        return {
            'error': None,
            'user_id': user_row['user_id'],
            'login_name': user_row['login_name'],
            'user_name': user_row['user_name'],
            'change_password': user_row['change_password'] == '1'
        }

    return None

def check_globeadmin_login(username, password):
    """
    Checks for the globeadmin login.
    """
    # This is a simple check against the config values, not the database.
    if (username == config.GLOBEADMIN_USERNAME and
        password == config.GLOBEADMIN_PASSWORD):
        return {
            'error': None,
            'user_id': config.GLOBEADMIN_USERNAME,
            'login_name': config.GLOBEADMIN_USERNAME,
            'user_name': 'Globe Admin',
            'is_globeadmin': True
        }

    # The original PHP code also had a demo globeadmin.
    # This can be added if needed.

    return None

def create_user_session(session, user_info):
    """
    Populates the session with all necessary user data and access rights.
    This is a complex function that replicates the logic from
    nuLoginSetupGlobeadmin and nuLoginSetupNOTGlobeadmin in the PHP code.
    """
    # This function will query the database for forms, reports, and procedures
    # that the user has access to, and store it all in the session object.
    # The session object is then saved to the zzzzsys_session table
    # by the DatabaseSessionInterface.

    # For now, we will just store the basic user info.
    # The full implementation will be done in a subsequent step.

    session['user_id'] = user_info['user_id']
    session['login_name'] = user_info['login_name']
    session['is_globeadmin'] = user_info.get('is_globeadmin', False)

    # Mark the session as modified so it gets saved.
    session.modified = True
