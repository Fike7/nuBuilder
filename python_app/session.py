# -*- coding: utf-8 -*-

import json
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict

from . import database

class DatabaseSession(CallbackDict, SessionMixin):
    """
    A custom session object that is dictionary-like and tracks modifications.
    """
    def __init__(self, initial=None, session_id=None, new=False):
        def on_update(self):
            self.modified = True

        super(DatabaseSession, self).__init__(initial, on_update)
        self.session_id = session_id
        self.new = new
        self.modified = False

class DatabaseSessionInterface(SessionInterface):
    """
    A custom session interface that stores session data in the database.
    This is designed to be compatible with the existing zzzzsys_session table.
    """

    def __init__(self):
        # You might want to pass a db connection or a way to get one
        pass

    def open_session(self, app, request):
        """
        This is called by Flask at the beginning of each request to open a session.
        """
        # Get session ID from the cookie
        session_cookie = request.cookies.get(app.session_cookie_name)

        if not session_cookie:
            # If there's no cookie, create a new session
            session_id = str(uuid4())
            return DatabaseSession(session_id=session_id, new=True)

        # If a cookie exists, try to load the session from the database
        rows = database.run_query(
            "SELECT sss_access FROM zzzzsys_session WHERE zzzzsys_session_id = %s",
            params=(session_cookie,),
            fetch="one"
        )

        if rows:
            try:
                # The data is stored as a JSON string in sss_access
                session_data = json.loads(rows['sss_access'])
                return DatabaseSession(session_data, session_id=session_cookie)
            except (json.JSONDecodeError, TypeError):
                # If JSON is invalid, create a new session
                session_id = str(uuid4())
                return DatabaseSession(session_id=session_id, new=True)

        # If the session ID from the cookie is not in the DB, create a new session
        session_id = str(uuid4())
        return DatabaseSession(session_id=session_id, new=True)


    def save_session(self, app, session, response):
        """
        This is called by Flask at the end of each request to save the session.
        """
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # If the session is not modified, don't do anything
        if not session.modified:
            return

        # If the session is empty, delete the session from the DB and the cookie
        if not session:
            database.run_query(
                "DELETE FROM zzzzsys_session WHERE zzzzsys_session_id = %s",
                params=(session.session_id,)
            )
            response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
            return

        # Save the session to the database
        session_data = json.dumps(dict(session))

        # Use REPLACE INTO which is a MySQL extension.
        # It's equivalent to INSERT ... ON DUPLICATE KEY UPDATE.
        # This will create a new row if the session_id doesn't exist,
        # or update the existing row if it does.
        database.run_query(
            "REPLACE INTO zzzzsys_session (zzzzsys_session_id, sss_access) VALUES (%s, %s)",
            params=(session.session_id, session_data)
        )

        # Set the session cookie on the response
        response.set_cookie(
            app.session_cookie_name,
            session.session_id,
            expires=self.get_expiration_time(app, session),
            httponly=True,
            domain=domain,
            path=path,
            secure=self.get_cookie_secure(app)
        )
