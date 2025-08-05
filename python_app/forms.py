# -*- coding: utf-8 -*-

from . import database

import re

def get_form_properties(form_id, columns='*'):
    """
    Fetches properties for a given form from the zzzzsys_form table.
    Equivalent to nuFormProperties in nuform.php.
    """
    # Basic validation to prevent injection in column names
    if columns != '*' and not all(re.match(r'^[a-zA-Z0-9_]+$', col.strip()) for col in columns.split(',')):
        print(f"Error: Invalid column names requested: {columns}")
        return None

    sql = f"SELECT {columns} FROM zzzzsys_form WHERE zzzzsys_form_id = %s"
    params = (form_id,)

    return database.run_query(sql, params, fetch="one")


def get_form_data(table, primary_key, record_id):
    """
    Fetches the data for a single record from the form's table.
    Equivalent to nuGetFormData in nuform.php.
    """
    if not table or not primary_key or not record_id:
        return None

    # Basic validation to prevent SQL injection in table/key names
    if not re.match(r'^[a-zA-Z0-9_]+$', table) or not re.match(r'^[a-zA-Z0-9_]+$', primary_key):
        print(f"Error: Invalid table or primary key name.")
        return None

    sql = f"SELECT * FROM `{table}` WHERE `{primary_key}` = %s"
    params = (record_id,)
    return database.run_query(sql, params, fetch="one")


def get_form_object(form_id, record_id):
    """
    This will be the main function to construct the complete form object,
    similar to nuGetFormObject in nuform.php.

    For now, it will be a placeholder.
    """

    # 1. Get basic form properties
    form_props = get_form_properties(form_id)
    if not form_props:
        return {'error': 'Form not found'}

    # In Python, we'll build up a dictionary that will be returned as JSON.
    form_obj = {
        'id': form_props['zzzzsys_form_id'],
        'form_code': form_props['sfo_code'],
        'form_description': form_props['sfo_description'],
        'table': form_props['sfo_table'],
        'primary_key': form_props['sfo_primary_key'],
        'record_id': record_id,
        'objects': [], # This will be populated later
        'browse_columns': [], # This will be populated later
        'tabs': [], # This will be populated later
    }

    # 2. Get the record data if a record_id is provided
    record_data = None
    if record_id and record_id != '-1':
        record_data = get_form_data(
            form_obj['table'],
            form_obj['primary_key'],
            record_id
        )

    form_obj['data'] = record_data

    # 3. Get all the UI objects for this form
    sql_objects = """
        SELECT *
        FROM zzzzsys_object
        JOIN zzzzsys_tab ON zzzzsys_tab_id = sob_all_zzzzsys_tab_id
        WHERE sob_all_zzzzsys_form_id = %s
        ORDER BY
            IF(sob_all_type = 'contentbox', -1, sob_all_order),
            syt_order,
            (sob_all_type = 'run'),
            sob_all_zzzzsys_tab_id
    """
    params = (form_id,)
    db_objects = database.run_query(sql_objects, params, fetch="all")

    if db_objects:
        for db_obj in db_objects:
            # This is where the complex logic of nuGetFormModifyObject will go.
            # For now, we'll just add a simplified object.
            ui_object = {
                'object_id': db_obj['zzzzsys_object_id'],
                'id': db_obj['sob_all_id'],
                'type': db_obj['sob_all_type'],
                'label': db_obj['sob_all_label'],
                'top': db_obj['sob_all_top'],
                'left': db_obj['sob_all_left'],
                'width': db_obj['sob_all_width'],
                'height': db_obj['sob_all_height'],
                'value': record_data.get(db_obj['sob_all_id']) if record_data else None
            }
            form_obj['objects'].append(ui_object)

    return form_obj
