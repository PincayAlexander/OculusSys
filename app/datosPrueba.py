from app.database import db
from datetime import datetime, timedelta
import random

from app.database.models import camara, tipoPlaga, ubicacion, deteccionPlaga

def generar_datos_prueba():
    admin_id = 1  # idUsuario del admin

    # 1️ Cámara
    camara1 = camara(
        nombre="Camara1",
        ubicacion_fisica="No disponible",
        idUsuario=admin_id
    )
    db.session.add(camara1)
    db.session.flush()

    # 2️ Tipos de plaga (sin grado/etiqueta aquí)
    plagas = [
        ("Broca del café", "Pequeño insecto que perfora el grano"),
        ("Roya del café", "Hongo que causa manchas amarillas en hojas"),
        ("Cochinilla", "Insecto chupador de savia que debilita la planta"),
        ("Minador de la hoja", "Larva que crea galerías en hojas"),
        ("Nematodos", "Parásitos que afectan raíces"),
        ("Planta sana", "Sin signos visibles de plaga"),
    ]
    tipos_plagas_objs = []
    for nombre, descripcion in plagas:
        tp = tipoPlaga(nombre=nombre, descripcion=descripcion)
        tipos_plagas_objs.append(tp)
        db.session.add(tp)
    db.session.flush()

    # Guardar id de planta sana
    planta_sana_id = next(tp.id for tp in tipos_plagas_objs if tp.nombre == "Planta sana")

    # 3️ Ubicaciones
    ubicaciones_objs = []
    for zona in range(1, 6):
        for parcela in ["A", "B", "C", "D"]:
            ub = ubicacion(
                parcela=parcela,
                region=str(zona),
                descripcion=f"Parcela {parcela} de la zona {zona}"
            )
            ubicaciones_objs.append(ub)
            db.session.add(ub)
    db.session.flush()

    # 4️ Detecciones
    estados_control = ["No controlada", "En control", "Erradicada"]

    for _ in range(100):
        tipo_plaga_random = random.choice(tipos_plagas_objs)
        ubicacion_random = random.choice(ubicaciones_objs)
        fecha_random = datetime.utcnow() - timedelta(days=random.randint(0, 90))

        # Si es planta sana, forzar nivel_plaga y etiqueta_gravedad
        if tipo_plaga_random.id == planta_sana_id:
            nivel = 0
            etiqueta = "Sana"
        else:
            nivel = random.randint(1, 5)
            etiqueta = (
                "Posible infección" if nivel <= 2 else
                "Infección moderada" if nivel <= 3 else
                "Infección avanzada" if nivel == 4 else
                "Muy grave"
            )

        deteccion = deteccionPlaga(
            idCamara=camara1.idCamara,
            ubicacion_id=ubicacion_random.idUbicacion,
            tipo_plaga_id=tipo_plaga_random.id,
            grado_afectacion=nivel,
            etiqueta_gravedad=etiqueta,
            fecha_deteccion=fecha_random,
            descripcion=f"Detección en {ubicacion_random.parcela}-{ubicacion_random.region}, tipo: {tipo_plaga_random.nombre}",
            estado_control=random.choice(estados_control),
            idUsuario=admin_id
        )
        db.session.add(deteccion)

    db.session.commit()
    print(" * Datos de prueba generados con éxito.")
