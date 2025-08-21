from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Tecnico


bp = Blueprint('tecnicos', __name__, url_prefix='/api/tecnicos')

@bp.route('/', methods=['POST'])
def registrar_tecnico():
    data = request.get_json()

    nombre = data.get('nombre')
    especialidad = data.get('especialidad')
    # Validar campo activo como 0 o 1
    try:
        activo = int(data.get('activo'))
        if activo not in [0, 1]:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "El campo 'activo' debe ser 0 o 1"}), 400

    if nombre is None or especialidad is None or activo is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    if Tecnico.query.filter_by(nombre=nombre).first(): 
        return jsonify({"error": "El tecnico ya está registrado"}), 400

    
    try:
        nuevo_tecnico = Tecnico(nombre=nombre, activo=activo, especialidad=especialidad)
        db.session.add(nuevo_tecnico)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al guardar técnico", "detalle": str(e)}), 500
    
    return jsonify({
        "mensaje": "Técnico registrado con éxito",
        "tecnico_id": nuevo_tecnico.id
    }), 201

@bp.route('/', methods=['GET'])
def listar_tecnicos():
     # Obtener parámetro opcional ?activo=1 o ?activo=0
    activo_param = request.args.get('activo')

    try:
        if activo_param is not None:
            activo = int(activo_param)
            if activo not in [0, 1]:
                raise ValueError
            tecnicos = Tecnico.query.filter_by(activo=activo).all()
        else:
            tecnicos = Tecnico.query.all()
    except ValueError:
        return jsonify({"error": "El parámetro 'activo' debe ser 0 o 1"}), 400

    resultado = []
    for t in tecnicos:
        resultado.append({
            "id": t.id,
            "nombre": t.nombre,
            "especialidad": t.especialidad,
            "activo": t.activo
        })

    return jsonify(resultado), 200

