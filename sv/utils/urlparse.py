import re

def parse_value(value):
    if re.search("^\\-?\\d+$", value):
        return int(value)
    elif re.search("^\\-?\\d+\\.\\d+$", value):
        return float(value)
    else:
        return value

def parse_querystring(qs):
    params = {}
    for tok in qs.split("&"):
        key, value = tok.split("=")
        params[key] = parse_value(value)
    return params

"""
NB sorted for indexation consistency
"""

def format_querystring(params):
    return "&".join([f"{k}={params[k]}" for k in sorted(params.keys())])

def parse_url(url):
    tokens = url.split("?")
    if len(tokens) == 2:
        path, qs = tokens
        params = parse_querystring(qs)
    else:
        path, params = tokens[0], {}
    return path, params

if __name__ == "__main__":
    pass
