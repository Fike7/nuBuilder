# -*- coding: utf-8 -*-

import uuid

def generate_id():
    """
    Generates a unique ID.
    This replaces the custom nuID() function from PHP with a standard UUID,
    which is a more robust and standard way to generate unique identifiers.
    """
    return str(uuid.uuid4())
