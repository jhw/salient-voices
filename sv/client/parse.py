import argparse
import logging

def matches_number(value, **kwargs):
    try:
        float(value)  # Check if value can be cast to float
        return True
    except ValueError:
        return False

def matches_int(value, **kwargs):
    return value.isdigit() or (value.startswith('-') and value[1:].isdigit())

def matches_float(value, **kwargs):
    return matches_number(value) and not matches_int(value)

def matches_str(value, **kwargs):
    return True

def matches_hexstr(value, **kwargs):
    for c in value:
        if c not in '0123456789abcdef':
            return False
    return True

def parse_number(value, **kwargs):
    return int(value) if matches_int(value) else float(value)

def parse_int(value, **kwargs):
    return int(value)

def parse_float(value, **kwargs):
    return float(value)

def parse_str(value, **kwargs):
    return value

def parse_hexstr(value, **kwargs):
    return [int(c, 16) for c in value]

def parse_line(items = []):
    def decorator(fn):
        def wrapped(self, line, **kwargs):
            try:
                args = [tok for tok in line.split(" ") if tok != '']
                if len(args) < len(items):
                    raise RuntimeError("Please enter " + ", ".join([item["name"] for item in items]))

                for item, arg_val in zip(items, args[:len(items)]):
                    matcher_fn = globals().get(f"matches_{item['type']}")
                    parser_fn = globals().get(f"parse_{item['type']}")
                    if not matcher_fn or not parser_fn:
                        raise RuntimeError(f"Unsupported type: {item['type']}")

                    if not matcher_fn(arg_val, **item):
                        raise RuntimeError(f"{item['name']} is invalid")

                    kwargs[item["name"]] = parser_fn(arg_val, **item)
                return fn(self, **kwargs)
            except RuntimeError as error:
                logging.error(str(error))
            except Exception as error:
                logging.error("Unhandled exception", exc_info = True)
        return wrapped
    return decorator

