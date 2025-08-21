from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Usuario, rolEnum ##importamos la clase Usuario
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.utils.auth_decorators import verificar_rol


bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

@bp.route('/', methods=['POST'])
@jwt_required()
def registrar_usuario():
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    domicilio = data.get('domicilio')
    telefono = data.get('telefono')
    contrasena = data.get('contrasena')
    rol = rolEnum[data['rol']]

    print(data)

    if not all([nombre, email, domicilio, telefono, contrasena, rol]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if Usuario.query.filter_by(email=email).first(): 
        return jsonify({"error": "El correo ya está registrado"}), 400

    nuevo_usuario = Usuario(nombre=nombre, email=email, domicilio=domicilio, telefono=telefono, rol=rol)
    nuevo_usuario.set_password(contrasena)

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "mensaje": "Usuario registrado con éxito",
        "usuario_id": nuevo_usuario.id
    }), 201

@bp.route('/registro_cliente', methods=['POST'])
def registrar_cliente():
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    domicilio = data.get('domicilio')
    telefono = data.get('telefono')
    contrasena = data.get('contrasena')
    rol = 'cliente'


    if not all([nombre, email, domicilio, telefono, contrasena]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if Usuario.query.filter_by(email=email).first(): 
        return jsonify({"error": "El correo ya está registrado"}), 400

    nuevo_usuario = Usuario(nombre=nombre, email=email, domicilio=domicilio, telefono=telefono, rol=rol)
    nuevo_usuario.set_password(contrasena)

    try:
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar usuario: {e}")
        return jsonify({"error": "Error interno al registrar usuario"}), 500
    
    return jsonify({
            "mensaje": "Usuario registrado con éxito",
            "usuario_id": nuevo_usuario.id
        }), 201

@bp.route('/login', methods=['POST'])
def login():
    print(request.content_type)
    print(request.data)
    print(request.get_json())
    data = request.get_json() #obtener data del body de la solicitud
    email = data.get('email')
    contrasena = data.get('contrasena')

    #comprobar que se igresen email y contraseña
    if not email or not contrasena:
        return jsonify({"error": "correo y contraseña son obligatorios"}), 400
    
    #Buscar usuario  por su correo 
    usuario = Usuario.query.filter_by(email=email).first()  #consulta a BD y verificar si existe 

    if not usuario:
        return jsonify({"error": "Usuario no existe"}), 400
    
    #Verificar contraseña

    if not usuario.check_password(contrasena):
        return jsonify({"error": "Contraseña incorrecta"}), 401
    

    # Si la contraseña es correcta se da acceso.

    #generar el token
    additional_claims = {"rol": usuario.rol.name}
    access_token = create_access_token(identity=str(usuario.id), additional_claims=additional_claims)
    return jsonify(access_token= access_token), 200

@bp.route('/ver_usuarios', methods=['GET'])
@jwt_required()
@verificar_rol("admin")
def ver_usuarios():
    usuarios = Usuario.query.all()
    lista = []
    for usuario in usuarios:
        lista.append({
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "contrasena": usuario.contrasena,
            "rol": usuario.rol.name    #hay que usar rol.name por que el valor en ENUM
        })
    return jsonify(lista), 200

#ver usuario por id

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@verificar_rol("admin")
def usuario_id(id):
   
    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "domicilio": usuario.domicilio,
        "telefono": usuario.telefono,
        "rol": usuario.rol.name
    })


@bp.route('/mod_usuario/<int:id>', methods=['PATCH'])
@jwt_required()
def mod_usuario(id):
    print(f"[DEBUG] PATCH recibido para usuario ID: {id}")
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    domicilio = data.get('domicilio')
    telefono = data.get('telefono')
    contrasena = data.get('contrasena')  # ← opcional
    rol_str = data.get('rol')            # ← corregido: data.get(), no data.get[]

    # Validar solo los campos obligatorios
    if not all([nombre, email, domicilio, telefono, rol_str]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        rol = rolEnum[rol_str]
    except KeyError:
        return jsonify({"error": f"Rol inválido: {rol_str}"}), 400

    usuario = Usuario.query.get(id)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verifica si ya existe otro usuario con ese email
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente and usuario_existente.id != usuario.id:
        return jsonify({"error": "El email ya está en uso por otro usuario"}), 409

    # Asignar nuevos valores
    usuario.nombre = nombre
    usuario.email = email
    usuario.domicilio = domicilio
    usuario.telefono = telefono
    usuario.rol = rol

    # Solo actualizar contraseña si fue proporcionada y no está vacía
    if contrasena:
        usuario.set_password(contrasena)

    db.session.commit()

    return jsonify({"msg": "Usuario actualizado correctamente"}), 200

@bp.route('/eliminar_usuario/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(id):
    print("Eliminando usuario", id)
    usuario = Usuario.query.get(id)

    if not usuario:  ##buscamos el usaurio en la BD, si no existe da error
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        print("Error al eliminar usuario:", e)
        return jsonify({"error": "Ocurrió un error al eliminar el usuario"}), 500



@bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil_usuario():

    user_id = get_jwt_identity()  # Esto será un string con el id
    claims = get_jwt()
    rol = claims.get("rol", "desconocido")

    usuario = Usuario.query.get(int(user_id))
    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": rol
    }), 200