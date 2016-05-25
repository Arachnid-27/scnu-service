def hmget_decode(rdb, name, keys):
    results = []
    values = rdb.hmget(name, keys)
    for value in values:
        if value:
            results.append(value.decode('utf-8'))
        else:
            results.append(value)
    return results


def hget_decode(rdb, name, key):
    value = rdb.hget(name, key)
    if value:
        value = value.decode('utf-8')
    return value
