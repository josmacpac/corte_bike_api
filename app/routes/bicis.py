from flask import Blueprint, request, jsonify
from app import db
from app.models import Bici, MantenimientoBici
from datetime import datetime, timedelta, date, time
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.utils.auth_decorators import verificar_rol 
from sqlalchemy import func
from zoneinfo import ZoneInfo
from sqlalchemy import or_


bp = Blueprint('bicis', __name__, url_prefix='/api/bicis')

@bp.route('/', methods=['POST'])
@jwt_required()
def agregar_bici():
    data = request.get_json()


    idUsuario = int(data.get("idUsuario"))
    marca = data.get("marca")
    modelo = data.get("modelo")
    tipo = data.get("tipo")
    talla = data.get("talla")
    rodada = data.get("rodada")
    serie = data.get("serie")
    color = data.get("color")

    if not all([idUsuario, marca, modelo, tipo, talla, rodada, serie, color]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    nueva_bici = Bici(id_usuario = idUsuario, marca=marca, modelo=modelo, tipo=tipo, talla=talla, rodada =rodada, serie=serie, color=color)

    db.session.add(nueva_bici)
    db.session.commit()

    return jsonify({
        "mensaje": "Bici registrada con éxito",
        "idBici": nueva_bici.id_bici,  ##aqui debemos devolver el id generado en la base de datos 
    
    }), 201


@bp.route('/mis_bicis', methods=["GET"])
@jwt_required()
def mis_bicis():
    usuario_actual = get_jwt_identity()
    bicis = Bici.query.filter(Bici.id_usuario == usuario_actual).all()

    if not bicis:
        return jsonify([])  # Retorna lista vacía si no hay bicis

    resultado = [{
        "bici_id": b.id_bici,
        "marca": b.marca,
        "modelo": b.modelo,
        "tipo": b.tipo,
        "talla": b.talla,
        "rodada": b.rodada,
        "serie": b.serie,
        "color": b.color
    } for b in bicis]

    return jsonify(resultado)


@bp.route('/<int:bici_id>', methods=["GET"])
@jwt_required()
def bici_por_id(bici_id):
    usuario_id = get_jwt_identity()  # ID del usuario autenticado
    bici = Bici.query.get(bici_id)

    if not bici:
        return jsonify({"error": "Bici no encontrada"}), 404

    if bici.usuario_id != usuario_id:  # Verificación de propiedad
        return jsonify({"error": "No autorizado"}), 403

    return jsonify({
        "bici_id": bici.id_bici,
        "marca": bici.marca,
        "modelo": bici.modelo,
        "tipo": bici.tipo,
        "talla": bici.talla,
        "rodada": bici.rodada,
        "color": bici.color,
        "serie": bici.serie
    })

@bp.route('/mantenimiento/<int:bici_id>', methods=["GET"])
@jwt_required()
def mantenimiento_bici_id(bici_id):
    usuario_id = get_jwt_identity()
    print(type(usuario_id))

    bici = Bici.query.get(bici_id) #verificar que la bici perteece al usuario 
    print(type(bici.id_usuario))
    if bici.id_usuario != int(usuario_id):
        return jsonify({"error": "No autorizado"}), 403
    
    mantenimientos = MantenimientoBici.query.filter_by(id_bici=bici_id).all()

    resultado = []
    for m in mantenimientos:
        resultado.append({
            "id_bici_cita": m.id_bici_cita,
            "id_cita": m.id_cita,
            "fecha": m.cita.fecha_ingreso.strftime("%Y-%m-%d"),
            "tipo": m.cita.servicio.nombre,
            "descripcion": m.cita.descripcion,
            "estado": m.cita.estado.value
        })
    
    return jsonify(resultado), 200


@bp.route('/eliminar/<int:bici_id>', methods=["DELETE"])
@jwt_required()
def eliminar_bici(bici_id):
    usuario_id = get_jwt_identity()

    bici = Bici.query.get(bici_id)
    if not bici:
        return jsonify({"error": "Bici no encontrada"}), 404

    # Verificar que la bici pertenece al usuario autenticado
    if bici.id_usuario != int(usuario_id):
        return jsonify({"error": "No autorizado"}), 403

    try:
        db.session.delete(bici)
        db.session.commit()
        return jsonify({"mensaje": "Bici eliminada correctamente"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error al eliminar bici:", e)
        return jsonify({"error": "Ocurrió un error al eliminar la bici"}), 500


@bp.route('/usuario/<int:usuario_id>', methods=["GET"])
@jwt_required()
def bicis_por_id_usuario(usuario_id):
    # Obtener todas las bicicletas del usuario
    bicis = Bici.query.filter_by(id_usuario=usuario_id).all()

    if not bicis:
        return jsonify({"error": "No se encontraron bicis para este usuario"}), 404

    # Convertir las bicis a diccionarios
    resultado = []
    for bici in bicis:
        resultado.append({
            "bici_id": bici.id_bici,
            "marca": bici.marca,
            "modelo": bici.modelo,
            "tipo": bici.tipo,
            "talla": bici.talla,
            "rodada": bici.rodada,
            "color": bici.color,
            "serie": bici.serie
        })

    return jsonify(resultado)
