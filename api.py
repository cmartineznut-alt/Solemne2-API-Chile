"""
Módulo cliente para la API REST del Portal de Datos Públicos de Chile.
Encapsula el acceso a https://datos.gob.cl usando el estándar CKAN.
"""
import requests
import pandas as pd


class ClienteDatosGob:
    """
    Cliente para consumir la API de datos.gob.cl (CKAN 2.10).

    Esta clase encapsula la lógica de conexión, paginación y conversión
    de los datos JSON a DataFrame de pandas, dejando a la capa de
    presentación (app.py) sin detalles técnicos.
    """

    URL_BASE = "https://datos.gob.cl/api/3/action"

    def __init__(self, timeout=30):
        """
        Inicializa el cliente.

        Parámetros:
            timeout (int): segundos máximos a esperar por la respuesta.
        """
        self.timeout = timeout

    def _consultar(self, accion, parametros):
        """
        Método privado: realiza la consulta GET a un endpoint de la API.
        El guion bajo inicial indica por convención que es interno.

        Parámetros:
            accion (str): endpoint, por ej. 'datastore_search'.
            parametros (dict): parámetros de la consulta.

        Retorna:
            dict: el contenido del campo 'result' de la respuesta JSON.

        Lanza:
            requests.HTTPError si la API responde con error.
        """
        url = f"{self.URL_BASE}/{accion}"
        respuesta = requests.get(url, params=parametros, timeout=self.timeout)
        respuesta.raise_for_status()
        return respuesta.json()["result"]

    def obtener_recurso_completo(self, resource_id, tamano_pagina=1000):
        """
        Descarga TODAS las filas de un recurso usando paginación.
        La API limita cada consulta a unos pocos miles de filas, así
        que iteramos con 'offset' hasta traer todo.

        Parámetros:
            resource_id (str): ID del recurso en datos.gob.cl.
            tamano_pagina (int): filas por consulta (máx 32000 según CKAN).

        Retorna:
            pandas.DataFrame con todas las filas del recurso.
        """
        todas_las_filas = []
        offset = 0

        while True:
            parametros = {
                "resource_id": resource_id,
                "limit": tamano_pagina,
                "offset": offset,
            }
            resultado = self._consultar("datastore_search", parametros)
            filas = resultado["records"]

            if not filas:
                break  # no llegaron más datos, terminamos

            todas_las_filas.extend(filas)
            offset += len(filas)

            # Si la API nos dijo cuántas filas totales hay y ya las tenemos, salimos
            total = resultado.get("total", 0)
            if offset >= total:
                break

        return pd.DataFrame(todas_las_filas)


# Bloque de prueba: solo se ejecuta si corres este archivo directamente
# (no se ejecuta cuando lo importas desde app.py)
if __name__ == "__main__":
    print("Probando ClienteDatosGob...")
    cliente = ClienteDatosGob()
    RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"  # Establecimientos de Salud
    df = cliente.obtener_recurso_completo(RESOURCE_ID)
    print(f"Filas descargadas: {len(df)}")
    print(f"Columnas: {list(df.columns)[:5]} ...")
    print("\nPrimeras filas:")
    print(df.head(3))