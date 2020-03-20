from sqlalchemy.orm import class_mapper
from base64 import b64encode
from arrow import utcnow


def to_dict(obj):
    d = {}
    for col in class_mapper(obj.__class__).persist_selectable.c:
        a = getattr(obj, col.name)
        if a is None or a == 'None' or a == '':
            continue

        d[col.name] = a
        if d[col.name] and (col.name.endswith('time') or
                            col.name.endswith('_at')):
            d[col.name] = getattr(obj, col.name) \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    try:
        d['tags'] = [t.tag for t in obj.tags]
    except AttributeError:
        pass

    try:
        d['message'] = [b64encode(m.message) for m in obj.messages]
    except AttributeError:
        pass

    try:
        d['groups'] = [g.group for g in obj.groups]
    except AttributeError:
        pass

    d.pop('id')
    if d.get('confidence'):
        d['confidence'] = int(d['confidence'])
    else:
        d['confidence'] = 0

    return d


def normalize_data(data):
    for d in data:
        _normalize_rdata(d)
        d = _clean_timestamps(d)
        d['tags'] = _normalize_tags(d)


def _clean_timestamps(i):
    if not i.get('last_at'):
        i['last_at'] = utcnow().datetime.replace(tzinfo=None)

    if not i.get('reported_at'):
        i['reported_at'] = utcnow().datetime.replace(tzinfo=None)

    if not i.get('first_at'):
        i['first_at'] = i['last_at']

    return i


def _normalize_tags(i):
    tags = i.get("tags", [])
    if len(tags) == 0:
        return tags

    if isinstance(tags, str):
        tags = tags.split(',')

    del i['tags']

    return tags


def _normalize_rdata(d):
    if d.get('rdata', '') != '' and isinstance(d['rdata'], list):
        d['rdata'] = ','.join(d['rdata'])
