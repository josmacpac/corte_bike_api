from app import db
from datetime import datetime, timedelta, date, time
from app.models import Cita



def generar_horarios(inicio="09:00", final="19:00", intervalo=30):
    horarios = []
    hora_actual = datetime.strptime(inicio, "%H:%M")
    hora_fin = datetime.strptime(final, "%H:%M")

    while hora_actual < hora_fin:
        horarios.append(hora_actual.strftime("%H:%M"))
        hora_actual += timedelta(minutes=intervalo)

    return horarios

horarios_disponibles = []
capacidad = 1
fecha_consulta_str = "2025-08-06" #esta fecha viene del frontend
fecha_consulta_obj = date.fromisoformat(fecha_consulta_str) 
horarios_posibles = generar_horarios()

for h in horarios_posibles:
    hora_obj = time.fromisoformat(h)
    conteo = db.session.query(Cita).filter(Cita.fecha == fecha_consulta_obj).filter(Cita.hora == hora_obj).count()

    if conteo < capacidad:
        horarios_disponibles.append(h)


print(horarios_disponibles)


