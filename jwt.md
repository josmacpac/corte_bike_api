# Autenticación con JWT en el Backend (Flask)

## ✅ Lo que **sí debes saber** de JWT en el backend

---

### 1. **Cómo generar el token**

Usas `create_access_token` y puedes pasarle lo que quieras como identidad (aunque **debe ser string**, recuerda eso):

```python
from flask_jwt_extended import create_access_token

token = create_access_token(identity=str(usuario.id))
```

---

### 2. **Cómo proteger rutas**

Simple: decoras con `@jwt_required()` y dentro puedes recuperar el usuario así:

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    user_id = get_jwt_identity()
    # puedes consultar la base de datos con ese ID
```

---

### 3. **Configurar tiempos de expiración**

Puedes configurar cuánto tiempo dura un token:

```python
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
```

Así puedes obligar a re-logearse después de cierto tiempo.

---

### 4. **Manejo de errores JWT**

Muy importante manejar errores si el token está mal, caducado o no está:

```python
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized_callback(err):
    return jsonify({"error": "Token faltante"}), 401

@jwt.invalid_token_loader
def invalid_callback(err):
    return jsonify({"error": "Token inválido"}), 422

@jwt.expired_token_loader
def expired_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token expirado"}), 401
```

---

### 5. **Revocar tokens (opcional, para más adelante)**

Si después quieres revocar tokens (por ejemplo al cerrar sesión), puedes llevar una lista negra (blacklist) y verificarla en cada request.

---

### 6. **Guardar más datos en el token (opcional)**

Puedes meter el rol del usuario o email dentro del token:

```python
access_token = create_access_token(
    identity=str(usuario.id),
    additional_claims={"rol": usuario.rol}
)
```

Y luego recuperarlo así:

```python
from flask_jwt_extended import get_jwt

claims = get_jwt()
rol = claims["rol"]
```

---

### 7. **Nunca almacenes contraseñas en el token**

Los tokens se pueden ver si no usas HTTPS, así que **no metas datos sensibles como contraseñas** en el JWT. Solo IDs o roles.

---

### 8. **Usa siempre HTTPS en producción**

Si no usas HTTPS, alguien podría robar el token con un ataque de red (sniffing).

---

## 🧱 En resumen:

| Tema                          | Qué aprender                                            |
| ----------------------------- | ------------------------------------------------------- |
| Generación del token          | `create_access_token()`                                 |
| Protección de rutas           | `@jwt_required()`                                       |
| Obtener identidad             | `get_jwt_identity()`                                    |
| Manejo de errores JWT         | Decoradores de error (`@jwt.unauthorized_loader`, etc.) |
| Configuración de expiración   | `JWT_ACCESS_TOKEN_EXPIRES`                              |
| Claims personalizados         | `additional_claims={...}`                               |
| Buenas prácticas de seguridad | HTTPS, tokens cortos, sin info sensible                 |
