from flask import Blueprint, request, jsonify
from app import db
from app.models import Cita, EstadoCitaEnum ##importamos la clase Cita
from datetime import datetime, timedelta, date, time
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.utils.auth_decorators import verificar_rol 
from app import  calculo_f_entrega as calculo
from app import asignar_tecnico as tecnico 
from sqlalchemy import func
from zoneinfo import ZoneInfo
from sqlalchemy import or_



bp = Blueprint('citas', __name__, url_prefix='/api/citas')

@bp.route('/', methods=['POST'])
@jwt_required()
def crear_cita():
    data = request.get_json()

    idUsuario = int(data.get("idUsuario"))
    fechaCita = data.get("fechaHoraCita")
    cantidadBicis = int(data.get("cantidadBicis"))
    tipoMantenimiento = data.get("tipoMantenimiento")
    descripcionCita = data.get("descripcionCita")

    fechaEntrega = calculo.f_entrega(fechaCita, tipoMantenimiento)
    tecnicoAsignado = tecnico.asignar_tecnico(fechaCita)


    if not all([idUsuario, fechaCita, cantidadBicis, fechaEntrega, tecnicoAsignado, tipoMantenimiento, descripcionCita]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    nueva_cita = Cita(usuario_id = idUsuario, cantidad = cantidadBicis, descripcion = descripcionCita , fecha_ingreso = fechaCita, fecha_entrega= fechaEntrega, servicio_id = int(tipoMantenimiento), tecnico_id = tecnicoAsignado, estado = EstadoCitaEnum.pendiente)
    db.session.add(nueva_cita)
    db.session.commit()
    
    # Forzar a CDMX (America/Mexico_City) al devolver
    fecha_entrega_cdmx = nueva_cita.fecha_entrega.replace(tzinfo=ZoneInfo("America/Mexico_City"))

    return jsonify({
        "mensaje": "Cita registrada con éxito",
        "idCita": nueva_cita.id,  ##aqui debemos devolver el id generado en la base de datos 
        "fecha_entrega": fecha_entrega_cdmx.isoformat()
    }), 201



@bp.route('/', methods=['GET'])
def listar_citas():

    fecha = request.args.get('fecha')
    print(fecha)

    query = Cita.query
    if fecha:
        
        try:
            fecha_obj = date.fromisoformat(fecha)  # Convierte 'YYYY-MM-DD' a date
            print("fecha ingreso", fecha_obj)
           
            query = query.filter(func.date(Cita.fecha_ingreso) == fecha_obj)
    
           
            

        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400

    citas = query.all()

    resultado = [{
        "id_cita": c.id,
        "cliente": c.usuario.nombre,
        "tipo_mantenimiento": c.servicio.nombre,
        "fecha_ingreso": c.fecha_ingreso.isoformat(),
        "fecha_entrega_estimada": c.fecha_entrega.isoformat(),
        "estado": c.estado.name
    } for c in citas]
    return jsonify(resultado)

@bp.route('/mis_citas', methods=['GET'])
@jwt_required()
def listar_citas_usuario():
    usuario_actual = get_jwt_identity()
    citas = Cita.query.filter(Cita.usuario_id==usuario_actual, Cita.estado.in_([EstadoCitaEnum.pendiente, EstadoCitaEnum.en_proceso , EstadoCitaEnum.finalizado])).all()

   
    resultado = [{
        "id": c.id,
        "fecha_ingreso": c.fecha_ingreso.isoformat(),
        "fecha_entrega": c.fecha_entrega.isoformat(),
        "estado": c.estado.value if hasattr(c.estado, 'value') else c.estado,
        "descripcion": c.descripcion,
        "cantidad": c.cantidad,
        "tecnico": c.tecnico.nombre if c.tecnico else "No asignado",
        "tipo_mantenimiento": c.servicio.nombre if c.servicio else "Desconocido"
    } for c in citas]

    return jsonify(resultado)

@bp.route('/mis_citas_finalizadas', methods=['GET'])
@jwt_required()
def listar_citas_finalizadas():
    usuario_actual = get_jwt_identity()
    citas = Cita.query.filter(Cita.usuario_id==usuario_actual, Cita.estado.in_([EstadoCitaEnum.cancelado, EstadoCitaEnum.entregado])).all()

   
    resultado = [{
        "id": c.id,
        "fecha_ingreso": c.fecha_ingreso.isoformat(),
        "fecha_entrega": c.fecha_entrega.isoformat(),
        "estado": c.estado.value if hasattr(c.estado, 'value') else c.estado,
        "descripcion": c.descripcion,
        "cantidad": c.cantidad,
        "tecnico": c.tecnico.nombre if c.tecnico else "No asignado",
        "tipo_mantenimiento": c.servicio.nombre if c.servicio else "Desconocido"
    } for c in citas]

    return jsonify(resultado)



def generar_horarios(inicio="09:00", final="19:00", intervalo=30):
        horarios = []
        hora_actual = datetime.strptime(inicio, "%H:%M")
        hora_fin = datetime.strptime(final, "%H:%M")

        while hora_actual < hora_fin:
            horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=intervalo)

        return horarios

@bp.route("/horarios_disponibles", methods=["GET"])
@jwt_required()
def horarios_disponibles(): 

    fecha_consulta_str = request.args.get("fecha") #esta fecha viene del frontend
    if not fecha_consulta_str:
        return {"error": "Falta la fecha"}, 400
    

    try:
        fecha_consulta_obj = date.fromisoformat(fecha_consulta_str)
    except ValueError:
        return {"error": "Formato de fecha inválido"}, 400
    
    fecha_actual = (datetime.now()).date()
    hora_actual = datetime.now().replace(minute=0, second=0, microsecond=0)

    #definir horarios segun el dia de la semana 
    dia_semana = fecha_consulta_obj.weekday()

    if dia_semana == 6: #si cae en domingo
        return {"disponibles": [] }
    elif dia_semana == 5:
        hora_inicio, hora_final = "11:00", "16:00"
    else:
        hora_inicio, hora_final = "09:00", "19:00"    

    # ajustar horarios si la fecha es hoy
    if fecha_actual == fecha_consulta_obj: # validar si el dia a consultar es el dia en curso

        if hora_actual.time() < time(9,0): # validar si la hora en la que se consulta es menor a la hora de apertura
            hora_actual = hora_actual.replace(hour=9, minute=0, second=0, microsecond=0) #sustituir por hora de apertura
        if hora_actual.time() >= time(9,0): # si es mayor a la hora de apertura, sumar 2 horas para que no sea tan inmediata la cita
            hora_inicio = (hora_actual + timedelta(hours=2)).strftime("%H:%M")
    else:
        hora_inicio = "09:00" 
    
    horarios_posibles = generar_horarios(inicio=hora_inicio, final=hora_final, intervalo=30)

    horarios_disponibles = []
    capacidad = 1  ## capacidad para recibir clientes en cada horario
    

    for h in horarios_posibles:
        
        hora_obj = time.fromisoformat(h)
        conteo = db.session.query(Cita).filter(func.date(Cita.fecha_ingreso) == fecha_consulta_obj).filter(func.time(Cita.fecha_ingreso) == hora_obj).count()

        if conteo < capacidad:
            horarios_disponibles.append(h)

    return {"disponibles": horarios_disponibles}

## Editar cita


@bp.route('/editar_cita/<int:id>', methods=['PATCH'])
@jwt_required()
def editar_cita(id):
    print("editando cita...")
    data = request.get_json()
    
    cita = Cita.query.get(id)
    if not cita:
        return jsonify({"error": "La cita no existe"}), 404

    if "tipoMantenimiento" in data:
         cita.servicio_id = data["tipoMantenimiento"]

    if "tecnico" in data:
        cita.tecnico = data["tecnico"]

    if "fechaEntrega" in data:
        cita.fecha_entrega = datetime.fromisoformat(data["fechaEntrega"])

    if "estado" in data:
        cita.estado = data["estado"]

    if "descripcion" in data:
        cita.descripcion = data["descripcion"]

    if "fechaRecibo" in data:
        cita.fecha_recibo = datetime.fromisoformat(data["fechaRecibo"])

    if "cantidad" in data:
        cita.cantidad = data["cantidad"]

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar la cita", "detalle": str(e)}), 500

    return jsonify({"msg": "Cita actualizada correctamente"}), 200

    

