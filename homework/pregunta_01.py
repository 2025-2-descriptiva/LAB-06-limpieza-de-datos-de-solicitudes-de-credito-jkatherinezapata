"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

import os
import pandas as pd


def pregunta_01():
    """
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"
    """

    ruta_entrada = "files/input/solicitudes_de_credito.csv"
    ruta_salida = "files/output/solicitudes_de_credito.csv"

    # --- 1. Leer datos originales (la primera columna es solo índice) ---
    df = pd.read_csv(ruta_entrada, sep=";", index_col=0)

    # --- 2. Filtrar registros claramente malos ---
    #    a) Eliminar filas con valores faltantes en cualquier columna
    df = df.dropna()

    #    b) Quitar registros duplicados
    df = df.drop_duplicates()

    # --- 3. Normalizar la columna de fecha_de_beneficio ---
    # Intentamos primero con formato día/mes/año y luego año/mes/día
    fecha_1 = pd.to_datetime(
        df["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce"
    )
    fecha_2 = pd.to_datetime(
        df["fecha_de_beneficio"], format="%Y/%m/%d", errors="coerce"
    )
    df["fecha_de_beneficio"] = fecha_1.combine_first(fecha_2)

    # --- 4. Limpieza de columnas categóricas de texto ---

    def limpiar_texto_columna(serie: pd.Series) -> pd.Series:
        """Pasa a minúsculas, reemplaza '-', '_' por espacios y recorta espacios."""
        return (
            serie.str.lower()
            .replace(["-", "_"], " ", regex=True)
            .str.strip()
        )

    # columnas con la misma lógica de limpieza
    df["sexo"] = limpiar_texto_columna(df["sexo"])
    df["tipo_de_emprendimiento"] = limpiar_texto_columna(df["tipo_de_emprendimiento"])
    df["idea_negocio"] = limpiar_texto_columna(df["idea_negocio"])
    df["línea_credito"] = limpiar_texto_columna(df["línea_credito"])

    # barrio tiene un tratamiento ligeramente diferente (sin usar regex)
    df["barrio"] = (
        df["barrio"]
        .str.lower()
        .str.replace("-", " ", regex=False)
        .str.replace("_", " ", regex=False)
    )

    # --- 5. Conversión de columnas numéricas discretas ---
    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype(int)

    # --- 6. Limpieza y conversión de monto_del_credito ---
    monto_limpio = (
        df["monto_del_credito"]
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace(".00", "", regex=False)
    )

    df["monto_del_credito"] = pd.to_numeric(monto_limpio, errors="coerce")

    # --- 7. Revisión final: quitar duplicados y filas con datos faltantes ---
    df = df.drop_duplicates()
    df = df.dropna()

    # --- 8. Guardar resultado limpio ---
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df.to_csv(ruta_salida, sep=";", index=False)


if __name__ == "__main__":
    pregunta_01()
