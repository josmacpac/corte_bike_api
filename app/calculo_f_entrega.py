from datetime import timedelta, datetime, time

def f_entrega(fechaCita, tipoMantenimiento):
    (duracionBasico, duracionEspecial, duracionPremier, duracionInstalacion) = (24, 30, 48, 24)
    fechaCita = datetime.fromisoformat(fechaCita)
    horaCita = fechaCita.time()
    
    
    print("fecha de la cita ",fechaCita, "hora:", horaCita)
    

    ##extraer la hora, y agregar mas horas dependiendo la hora de la cita para que se pueda
    ##entregar en un horario habil

    if tipoMantenimiento == "101":
        entrega =  fechaCita + timedelta(hours=duracionBasico)
    elif tipoMantenimiento == "102":
        entrega =fechaCita + timedelta(hours=duracionEspecial)
    elif tipoMantenimiento == "103":
        entrega = fechaCita + timedelta(hours=duracionPremier)
    elif tipoMantenimiento == "104":
        entrega = fechaCita + timedelta(hours=duracionInstalacion)
    else:
         raise ValueError("Tipo de mantenimiento no valido")
    

    def ajustar_horario(entrega):
        hora_entrega = entrega.time()
        dia_semana = entrega.weekday()

        if dia_semana < 5: ##entrega de lunes a viernes
            inicio, fin = time(9,0), time(18,0)
        elif dia_semana ==5: # sabado
            inicio, fin = time(11,0), time(15,0)
        else: #Domingo esta cerrado
            return entrega.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Si la hora cae antes del inicio de operaciones, mover a la hora de apertura
        if hora_entrega < inicio:
            return entrega.replace(hour=inicio.hour, minute=0, second=0, microsecond=0)
        # Si la hora de entrega cae despues del cierre, mover al dia siguiente a primera hora
        if hora_entrega > fin:
            return ajustar_horario(
                entrega.replace(hour=inicio.hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
            )
        return entrega
    
    entrega = ajustar_horario(entrega)
    print("fecha entrega: " ,entrega)

    return entrega


    