from flask import Blueprint, request, jsonify
from app import db
from app.models import Cita, EstadoCitaEnum, MantenimientoBici, Tecnico, Usuario, Servicio ##importamos la clase Cita
from datetime import datetime, timedelta, date, time
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.utils.auth_decorators import verificar_rol 
from app import  calculo_f_entrega as calculo
from app import asignar_tecnico as tecnico 
from sqlalchemy import func, text
from zoneinfo import ZoneInfo
from sqlalchemy import or_


bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


@bp.route('/tiempos', methods=['GET'])
@jwt_required()
def tiempo_por_cita():
    print("Reporte de tiempos por cita")

    # Obtener parámetros desde query string
    fecha_inicio_str = request.args.get("fecha_inicio")
    fecha_final_str = request.args.get("fecha_final")

    if not fecha_inicio_str or not fecha_final_str:
        return jsonify({"error": "Debes enviar fecha_inicio y fecha_final en formato YYYY-MM-DD"}), 400

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_final_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido, usa YYYY-MM-DD"}), 400

    citas = db.session.query(
        Cita.id,
        Cita.usuario_id,
        Usuario.nombre.label('cliente'),
        Tecnico.nombre.label('tecnico'),
        Servicio.nombre.label('servicio'),
        Cita.fecha_recibo,
        Cita.fecha_finalizado,
        func.timestampdiff(text('SECOND'), Cita.fecha_recibo, Cita.fecha_finalizado).label('tiempo_segundos')
    ).join(Usuario).join(Tecnico, isouter=True).join(Servicio).filter(
        Cita.estado == 'finalizado',
        or_(
            Cita.fecha_recibo >= fecha_inicio,
            Cita.fecha_finalizado >= fecha_inicio
        ),
        or_(
            Cita.fecha_recibo <= fecha_fin,
            Cita.fecha_finalizado <= fecha_fin
        )
    ).all()

    if not citas:
        return jsonify({"mensaje": "No se encontraron citas en el rango de fechas especificado"}), 404

    resultado = []
    for cita in citas:
    # Si alguna fecha falta, tiempo = 0
        if cita.fecha_recibo and cita.fecha_finalizado:
            tiempo_segundos = (cita.fecha_finalizado - cita.fecha_recibo).total_seconds()
        else:
            tiempo_segundos = 0

        tiempo_horas = tiempo_segundos / 3600

        resultado.append({
            "id": cita.id,
            "usuario_id": cita.usuario_id,
            "cliente": cita.cliente,
            "tecnico": cita.tecnico,
            "servicio": cita.servicio,
            "fecha_recibo": cita.fecha_recibo.strftime("%Y-%m-%d %H:%M") if cita.fecha_recibo else None,
            "fecha_finalizado": cita.fecha_finalizado.strftime("%Y-%m-%d %H:%M") if cita.fecha_finalizado else None,
            "tiempo_horas": round(tiempo_horas, 2)
        })

    return jsonify(resultado), 200