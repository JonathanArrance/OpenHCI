def floatORzero(val):
    try:
        return float(val)
    except Exception:
        return 0.0


def val_or_blank(val):
    if val is None: return '&nbsp;'
    return val


def make_table(ob):
    ret = []
    #for k in ob._meta.get_all_field_names():
    for _k in ob._meta.fields:
        k = _k.name
        try:
            v = getattr(ob, k)
        except AttributeError:
            v = '<None>'
        ret.append((k, v))

    return ret

def hide_table_columns(table, viewmode):
    # Based on the current viewmode of a table (which defaults to 'additional_mode').
    # Iterate through the column_priorities, and for each tuple, grab the list and
    # add it to showcolumns. Return hidecolumns, which is a tuple of columns to
    # exclude.
    viewmode_info = table.column_priorities()[viewmode]
    showcolumns = []
    for x in viewmode_info:
        for y in x[1]:
            showcolumns.append(y)

    hidecolumns = []
    for x in table.column_priorities()['all_mode']:
        for y in x[1]:
            hidecolumns.append(y)

    for item in showcolumns:
        hidecolumns.remove(item)
    return tuple(hidecolumns)


def show_table_columns(table, viewmode):
    # Based on the current viewmode of a table (which defaults to 'additional_mode').
    # Iterate through the column_priorities, and for each tuple, grab the list and
    # add it to showcolumns.
    viewmode_info = table.column_priorities()[viewmode]
    showcolumns = []
    for x in viewmode_info:
        for y in x[1]:
            showcolumns.append(y)
    return tuple(showcolumns)


def col_group_info(table, viewmode):
    #collate column group info based on table viewmode which is passed to colgroup_list in extratags.py
    viewmode_info = table.column_priorities()[viewmode]

    colgroups = []
    for tup in viewmode_info:
        col = []
        col.append(len(tup[1]))
        col.append(tup[0])
        colgroups.append(tuple(col))

    return tuple(colgroups)

def blank_if_zero(v):
    if v == 0:
        return ''
    else:
        return v



def instance_dict(instance, key_format=None):
    "Returns a dictionary containing field names and values for the given instance"
    from django.db.models.fields.related import ForeignKey
    if key_format:
        assert '%s' in key_format, 'key_format must contain a %s'
    key = lambda key: key_format and key_format % key or key

    d = {}
    d['pk']=instance.pk
    for field in instance._meta.fields:
        attr = field.name
        value = getattr(instance, attr)

        d[key(attr)] = value

    return d

