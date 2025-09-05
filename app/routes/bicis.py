from flask import Blueprint, request, jsonify
from app import db
from app.models import Bici
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

