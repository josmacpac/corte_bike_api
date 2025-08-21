from collections import Counter
from app.models import Cita  # Asegúrate de importar tu modelo
from sqlalchemy import func
from app.models import Tecnico
import random
from datetime import datetime


def asignar_tecnico(fecha_ingreso_date):
    print("fecha a verificar para asignar tecnico..")

    
    
    tecnicos = Tecnico.query.filter_by(activo=True).all()
    print("verificando tecnicos disponibles")
    if not tecnicos:
        raise ValueError("No hay técnicos disponibles")
    
    citasTecnico = {}
    for tecnico in tecnicos:
        cantidad_citas = Cita.query.filter_by(tecnico_id=tecnico.id)\
            .filter(func.date(Cita.fecha_ingreso) == fecha_ingreso_date)\
            .count()
        citasTecnico[tecnico.id] = cantidad_citas

    menor_carga = min(citasTecnico.values())
    tecnicos_menor_carga = [tec_id for tec_id, citasTecnico in citasTecnico.items() if citasTecnico == menor_carga]  
    tecnico_asignado = random.choice(tecnicos_menor_carga)

    return tecnico_asignado




    