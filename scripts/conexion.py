
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")


def conectar_mongo():
    if not MONGO_URI:
        raise ValueError("No se encontró MONGO_URI en el archivo .env")

    if not DB_NAME:
        raise ValueError("No se encontró DB_NAME en el archivo .env")

    try:
        cliente = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000
        )

        cliente.admin.command("ping")

        db = cliente[DB_NAME]

        print("Conectado correctamente a MongoDB")
        print(f"Base de datos: {DB_NAME}")

        return cliente, db

    except Exception as e:
        raise ConnectionError(
            f"Error conectando a MongoDB: {e}"
        ) from e


def obtener_colecciones(db):
    """
    Obtener las colecciones utilizadas
    en el Dashboard de Events.
    """

    events = db["events"]
    eventguests = db["eventguests"]
    users = db["users"]

    return events, eventguests, users
