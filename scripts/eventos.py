
import pandas as pd
from scripts.conexion import conectar_mongo


# =====================================================
# 1. CONFIGURACIÓN DE CAMPOS
# =====================================================

CAMPOS_EVENTS = [
    "_id",
    "title",
    "date",
    "createdAt",
    "publishedAt",
    "isActive",
    "status",
    "modality",
    "spots",
    "isFree",
    "price",
    "organizer",
    "hasCertificate",

    # Campos recientemente implementados
    "category",
    "type",
    "companyId",
    "companyName",
    "registrationType",
    "certificatePrice",
]

CAMPOS_GUESTS = [
    "_id",
    "event",
    "userEmail",
    "status",
    "registrationDate",
    "isCertificatePaid",
    "entityType",
    "entityRole",
    "discoveryInterest",
]

CAMPOS_USERS = [
    "_id",
    "email",
    "createdAt",
    "profession",
]


# =====================================================
# 2. FUNCIONES DE LIMPIEZA
# =====================================================

def normalizar_correo(serie):
    return (
        serie.astype("string")
        .str.strip()
        .str.lower()
        .replace("", pd.NA)
    )


def normalizar_id(serie):
    return (
        serie.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


def normalizar_texto(serie, mayusculas=False):
    resultado = (
        serie.astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    if mayusculas:
        resultado = resultado.str.upper()

    return resultado


def normalizar_booleano(serie):
    texto = (
        serie.astype("string")
        .str.strip()
        .str.lower()
    )

    return texto.map({
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
        "si": True,
        "sí": True,
    }).astype("boolean")


def normalizar_fecha(serie):
    return pd.to_datetime(
        serie,
        errors="coerce",
        utc=True
    )


def preparar_columnas(df, campos):
    """
    Garantiza que todas las columnas existan,
    incluso si MongoDB aún no tiene valores
    para los campos nuevos.
    """
    return df.reindex(columns=campos)


def proyeccion(campos):
    return {campo: 1 for campo in campos}


# =====================================================
# 3. CARGAR Y LIMPIAR DATOS
# =====================================================

def cargar_eventos():

    cliente, db = conectar_mongo()

    try:
        eventos = list(
            db["events"].find(
                {},
                proyeccion(CAMPOS_EVENTS)
            )
        )

        invitados = list(
            db["eventguests"].find(
                {},
                proyeccion(CAMPOS_GUESTS)
            )
        )

        usuarios = list(
            db["users"].find(
                {},
                proyeccion(CAMPOS_USERS)
            )
        )

    finally:
        cliente.close()

    # =================================================
    # 4. DATAFRAMES
    # =================================================

    df_events = preparar_columnas(
        pd.DataFrame(eventos),
        CAMPOS_EVENTS
    )

    df_guests = preparar_columnas(
        pd.DataFrame(invitados),
        CAMPOS_GUESTS
    )

    df_users = preparar_columnas(
        pd.DataFrame(usuarios),
        CAMPOS_USERS
    )

    total_eventos_original = len(df_events)
    total_inscripciones_original = len(df_guests)

    print("\n===== DATOS ORIGINALES =====")
    print("Eventos:", total_eventos_original)
    print("Inscripciones:", total_inscripciones_original)
    print("Usuarios:", len(df_users))

    if df_events.empty:
        raise ValueError(
            "La colección events no contiene registros."
        )

    # Si todavía no existen inscripciones,
    # continuamos con un DataFrame vacío.
    # El dashboard deberá mostrar indicadores en 0.
    #
    # if df_guests.empty:
    #     raise ValueError(
    #         "La colección eventguests no contiene registros."
    #     )

    # =================================================
    # 5. IDENTIFICADORES
    # =================================================

    df_events = df_events.rename(
        columns={"_id": "event_id"}
    )

    df_guests = df_guests.rename(
        columns={"_id": "eventguest_id"}
    )

    df_events["event_id"] = normalizar_id(
        df_events["event_id"]
    )

    df_guests["event_id"] = normalizar_id(
        df_guests["event"]
    )

    df_guests["eventguest_id"] = normalizar_id(
        df_guests["eventguest_id"]
    )

    if df_events["event_id"].isna().any():
        raise ValueError(
            "Hay eventos sin identificador."
        )

    if df_events["event_id"].duplicated().any():
        raise ValueError(
            "Hay identificadores duplicados en events."
        )

    if df_guests["eventguest_id"].isna().any():
        raise ValueError(
            "Hay inscripciones sin identificador."
        )

    if df_guests["eventguest_id"].duplicated().any():
        raise ValueError(
            "Hay identificadores duplicados en eventguests."
        )

    # =================================================
    # 6. LIMPIEZA DE EVENTS
    # =================================================

    fechas_eventos = [
        "date",
        "createdAt",
        "publishedAt",
    ]

    for columna in fechas_eventos:
        df_events[columna] = normalizar_fecha(
            df_events[columna]
        )

    textos_eventos = [
        "title",
        "status",
        "modality",
        "organizer",
        "category",
        "type",
        "companyId",
        "companyName",
        "registrationType",
    ]

    for columna in textos_eventos:
        df_events[columna] = normalizar_texto(
            df_events[columna]
        )

    # Normalizar identificador de empresa.
    df_events["companyId"] = normalizar_id(
        df_events["companyId"]
    )

    # Unificar estados y modalidades para agrupar.
    df_events["status"] = normalizar_texto(
        df_events["status"],
        mayusculas=True
    )

    df_events["modality"] = (
        df_events["modality"]
        .str.lower()
        .replace({
            "presencial": "Presencial",
            "virtual": "Virtual",
            "híbrido": "Híbrido",
            "hibrido": "Híbrido",
        })
    )

    # Booleanos: conservar nulos como desconocidos.
    for columna in [
        "isActive",
        "isFree",
        "hasCertificate",
    ]:
        df_events[columna] = normalizar_booleano(
            df_events[columna]
        )

    # Valores numéricos.
    for columna in [
        "spots",
        "price",
        "certificatePrice",
    ]:
        df_events[columna] = pd.to_numeric(
            df_events[columna],
            errors="coerce"
        )

    # Etiquetas para gráficos.
    # No modifican el valor original normalizado.
    df_events["categoria_dashboard"] = (
        df_events["category"]
        .fillna("No informado")
    )

    df_events["tipo_evento_dashboard"] = (
        df_events["type"]
        .fillna("No informado")
    )

    df_events["empresa_dashboard"] = (
        df_events["companyName"]
        .fillna("No informado")
    )

    df_events["registro_dashboard"] = (
        df_events["registrationType"]
        .fillna("No informado")
    )

    # =================================================
    # 7. LIMPIEZA DE EVENTGUESTS
    # =================================================

    df_guests["registrationDate"] = normalizar_fecha(
        df_guests["registrationDate"]
    )

    df_guests["email_key"] = normalizar_correo(
        df_guests["userEmail"]
    )

    df_guests["status"] = (
        normalizar_texto(
            df_guests["status"],
            mayusculas=True
        )
        .fillna("SIN INFORMACIÓN")
    )

    df_guests["isCertificatePaid"] = (
        normalizar_booleano(
            df_guests["isCertificatePaid"]
        )
    )

    for columna in [
        "entityType",
        "entityRole",
        "discoveryInterest",
    ]:
        df_guests[columna] = normalizar_texto(
            df_guests[columna]
        )

    # Campos preparados para análisis del perfil.
    for columna in [
        "entityType",
        "entityRole",
        "discoveryInterest",
    ]:
        df_guests[f"{columna}_dashboard"] = (
            df_guests[columna]
            .fillna("No informado")
        )

    # =================================================
    # 8. LIMPIEZA DE USERS
    # =================================================

    df_users["email_key"] = normalizar_correo(
        df_users["email"]
    )

    df_users["createdAt"] = normalizar_fecha(
        df_users["createdAt"]
    )

    df_users["profession"] = normalizar_texto(
        df_users["profession"]
    )

    df_users = df_users.rename(
        columns={
            "createdAt": "fecha_creacion_usuario"
        }
    )

    # Excluir solo cuentas sin correo del cruce,
    # nunca inscripciones.
    df_users = df_users.dropna(
        subset=["email_key"]
    ).copy()

    # Una fila por correo para evitar multiplicar
    # inscripciones en el merge.
    #
    # Regla: conservar la cuenta con fecha de
    # creación más antigua. No fusionar cuentas.
    df_users = (
        df_users.sort_values(
            "fecha_creacion_usuario",
            na_position="last",
            kind="stable"
        )
        .drop_duplicates(
            subset=["email_key"],
            keep="first"
        )
    )

    # =================================================
    # 9. RELACIONAR GUESTS CON USERS
    # =================================================

    usuarios_cruce = df_users[
        [
            "email_key",
            "fecha_creacion_usuario",
            "profession",
        ]
    ].copy()

    invitados_con_correo = df_guests[
        df_guests["email_key"].notna()
    ].copy()

    invitados_sin_correo = df_guests[
        df_guests["email_key"].isna()
    ].copy()

    inscritos_con_correo = (
        invitados_con_correo.merge(
            usuarios_cruce,
            on="email_key",
            how="left",
            validate="many_to_one",
            indicator=True
        )
    )

    inscritos_con_correo["cuenta_identificada"] = (
        inscritos_con_correo["_merge"].eq("both")
    )

    inscritos_con_correo = (
        inscritos_con_correo.drop(
            columns=["_merge"]
        )
    )

    # Conservar también inscripciones sin correo.
    invitados_sin_correo["fecha_creacion_usuario"] = (
        pd.NaT
    )

    invitados_sin_correo["profession"] = pd.NA

    invitados_sin_correo["cuenta_identificada"] = False

    df_inscripciones = pd.concat(
        [
            inscritos_con_correo,
            invitados_sin_correo,
        ],
        ignore_index=True
    )

    df_inscripciones["profesion_dashboard"] = (
        normalizar_texto(
            df_inscripciones["profession"]
        )
        .fillna("No informado")
    )

    # =================================================
    # 10. CLASIFICAR USUARIOS
    # =================================================

    def clasificar_usuario(fila):

        if pd.isna(fila["email_key"]):
            return "No determinado"

        if not fila["cuenta_identificada"]:
            return "Sin cuenta identificada"

        fecha_cuenta = fila["fecha_creacion_usuario"]
        fecha_registro = fila["registrationDate"]

        if pd.isna(fecha_cuenta) or pd.isna(fecha_registro):
            return "No determinado"

        if fecha_cuenta <= fecha_registro:
            return "Usuario Laboral.AI"

        return "Cuenta creada después"

    df_inscripciones["tipo_usuario"] = (
        df_inscripciones.apply(
            clasificar_usuario,
            axis=1
        )
    )

    # =================================================
    # 11. RELACIONAR INSCRIPCIONES CON EVENTS
    # =================================================

    campos_evento_para_cruce = [
        "event_id",
        "title",
        "date",
        "modality",
        "category",
        "type",
        "companyId",
        "companyName",
        "registrationType",
        "certificatePrice",
        "isFree",
        "hasCertificate",
        "price",
        "categoria_dashboard",
        "tipo_evento_dashboard",
        "empresa_dashboard",
        "registro_dashboard",
    ]

    df_inscripciones = df_inscripciones.merge(
        df_events[campos_evento_para_cruce],
        on="event_id",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    df_inscripciones["evento_identificado"] = (
        df_inscripciones["_merge"].eq("both")
    )

    df_inscripciones = df_inscripciones.drop(
        columns=["_merge"]
    )

    # =================================================
    # 12. CAMPOS PARA ANÁLISIS DE CERTIFICADOS
    # =================================================

    # True únicamente cuando está marcado como
    # pagado. Los nulos no se convierten en pagos.
    df_inscripciones["certificado_pagado"] = (
        df_inscripciones["isCertificatePaid"]
        .eq(True)
        .fillna(False)
        .astype(bool)
    )

    # Precio unitario asociado a cada inscripción
    # marcada como certificado pagado.
    #
    # No equivale necesariamente a dinero cobrado.
    # No se fuerza un precio desconocido a cero.
    precio_valido = (
        df_inscripciones["certificatePrice"].notna()
        & df_inscripciones["certificatePrice"].ge(0)
    )

    condicion_importe = (
        df_inscripciones["certificado_pagado"]
        & precio_valido
        & df_inscripciones["evento_identificado"]
    )

    df_inscripciones["importe_certificado_estimado"] = (
        df_inscripciones["certificatePrice"]
        .where(condicion_importe)
    )

    # =================================================
    # 13. VALIDACIONES
    # =================================================

    if len(df_events) != total_eventos_original:
        raise ValueError(
            "Cambió el número de eventos tras la limpieza."
        )

    if len(df_inscripciones) != total_inscripciones_original:
        raise ValueError(
            "El cruce alteró el número de inscripciones."
        )

    if df_inscripciones["eventguest_id"].duplicated().any():
        raise ValueError(
            "El cruce generó inscripciones duplicadas."
        )

    sin_evento = int(
        (~df_inscripciones["evento_identificado"]).sum()
    )

    certificados_pagados = int(
        df_inscripciones["certificado_pagado"].sum()
    )

    certificados_sin_precio = int(
        (
            df_inscripciones["certificado_pagado"]
            & ~precio_valido
        ).sum()
    )

    certificados_sin_evento = int(
        (
            df_inscripciones["certificado_pagado"]
            & ~df_inscripciones["evento_identificado"]
        ).sum()
    )

    # =================================================
    # 14. RESUMEN FINAL
    # =================================================

    print("\n===== DATOS LIMPIOS =====")

    print(
        "Eventos:",
        len(df_events)
    )

    print(
        "Inscripciones:",
        len(df_inscripciones)
    )

    print(
        "Participantes únicos con correo:",
        df_inscripciones["email_key"].nunique()
    )

    print(
        "Inscripciones sin evento asociado:",
        sin_evento
    )

    print(
        "Certificados marcados como pagados:",
        certificados_pagados
    )

    print(
        "Certificados pagados sin precio válido:",
        certificados_sin_precio
    )

    print(
        "Certificados pagados sin evento asociado:",
        certificados_sin_evento
    )

    print(
        "Inscripciones con profesión informada:",
        df_inscripciones["profession"].notna().sum()
    )

    print("\nClasificación de usuarios:")
    print(
        df_inscripciones["tipo_usuario"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nCobertura de campos nuevos en events:")

    for columna in [
        "category",
        "type",
        "companyId",
        "companyName",
        "registrationType",
        "certificatePrice",
    ]:
        completos = df_events[columna].notna().sum()

        print(
            f"{columna}: "
            f"{completos}/{len(df_events)}"
        )

    print("==========================\n")

    return df_events, df_inscripciones
