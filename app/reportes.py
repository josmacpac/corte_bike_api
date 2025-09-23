from sqlalchemy.orm import Session
from datetime import datetime
from models import Cita, Servicio, Tecnico

def tiempos_entrega(session: Session, fecha_inicio_str: str, fecha_fin_str: str):
    fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
    fecha_fin = datetime.fromisoformat(fecha_fin_str)

    query = (
        session.query(
            Cita.id.label("folio"),
            Cita.fecha_recibo,
            Cita.fecha_finalizado,
            Tecnico.nombre.label("tecnico"),
            Servicio.nombre.label("tipo_servicio")
        )
        .join(Servicio, Cita.servicio_id == Servicio.id)
        .join(Tecnico, Cita.tecnico_id == Tecnico.id, isouter=True)
        .filter(Cita.fecha_ingreso >= fecha_inicio, Cita.fecha_recibo <= fecha_fin)
        .order_by(Cita.fecha_recibo)
    )

    resultados = query.all()

    reporte = []

    for folio, fecha_recibo, fecha_finalizado, tipo_servicio, tecnico in resultados:
        duracion_horas = (fecha_finalizado - fecha_recibo).total_seconds() / 3600 if fecha_finalizado else None
        reporte.append({
            "folio": folio,
            "tipo_servicio": tipo_servicio,
            "tecnico": tecnico if tecnico else "Sin asignar" ,
            "fecha_recibo": fecha_recibo.isoformat(),
            "fecha_finalizado": fecha_finalizado.isoformat() if fecha_finalizado else None,
            "duracion_horas": round(duracion_horas, 2) if duracion_horas else None
        })

    return reporte
