from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify
from functools import wraps

def verificar_rol(rol_esperado):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs ):
            claims = get_jwt()
            if claims.get("rol") != rol_esperado:
                return jsonify(msg="Acceso denegado: permisos insuficientes"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
