from flask import Flask, request, abort, g
from functools import wraps
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)


def get_payload_name():
    if request.args:
        return 'args'
    elif request.form:
        return 'form'
    elif request.json:
        return 'json'
    else:
        return 'args'


def parse_class_string(cls):
    return str(cls)[8:str(cls).rfind("'")]  # get "bool" from "<class 'bool'>" etc


def arguments_required(required_args, override_namespace=False, use_json=False):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            payload_name = get_payload_name()
            err = []
            new_payload = getattr(request, payload_name).to_dict(flat=True)

            for argname, argtype in required_args.items():
                arg = new_payload.get(argname)
                print(arg)
                parsed_class_string = parse_class_string(argtype)
                if arg is None:
                    err.append('must supply {} as a parameter with type {}'.format(argname, parsed_class_string))
                else:
                    try:
                        new_payload[argname] = argtype(arg)
                    except Exception as e:
                        err.append('{} must be convertible to {}: {}'.format(argname, parsed_class_string, e))
            if err:
                abort(400, ', '.join(err))

            # Preserve original datatype, whether dict or ImmutableMultiDict
            setattr(request,
                    payload_name if override_namespace else 'parsed_data',
                    ImmutableMultiDict(new_payload) if not use_json else new_payload)

            return func(*args, **kwargs)
        return decorated_function
    return decorator


# Usage
@app.route('/', methods=['GET', 'POST'])
@arguments_required({'baby': bool, 'adult': float}, override_namespace=True)
def hello_world():
    print(request.json, request.form, request.args)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
