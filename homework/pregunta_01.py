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

    # Rutas de entrada y salida
    path_in = "files/input/solicitudes_de_credito.csv"
    path_out = "files/output/solicitudes_de_credito.csv"

    # Leer archivo original
    df = pd.read_csv(path_in, sep=";")

    # 1. Eliminar columna índice basura si existe
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # 2. Normalizar texto en las columnas categóricas
    def normalizar_texto(x):
        if pd.isna(x):
            return x
        s = str(x).strip().lower()
        # reemplazar guiones/underscores por espacio
        s = s.replace("_", " ").replace("-", " ")
        # colapsar espacios múltiples
        s = " ".join(s.split())
        return s

    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]

    for c in columnas_texto:
        df[c] = df[c].apply(normalizar_texto)

    # 3. Eliminar filas duplicadas (después de normalizar)
    df = df.drop_duplicates()

    # 4. Eliminar filas con datos faltantes en columnas clave
    #    (lo usual en este ejercicio es barrio y tipo_de_emprendimiento)
    df = df.dropna(subset=["barrio", "tipo_de_emprendimiento"])

    # 5. Limpiar y convertir monto_del_credito a numérico
    #    Elimina símbolos de moneda, comas, espacios, etc.
    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.strip()
    )

    # Convertir a número (coerce pone NaN donde no pueda convertir)
    df["monto_del_credito"] = pd.to_numeric(
        df["monto_del_credito"], errors="coerce"
    )

    # Eliminar filas donde el monto quedó como NaN
    df = df.dropna(subset=["monto_del_credito"])

    # Dejarlo como entero
    df["monto_del_credito"] = df["monto_del_credito"].astype(int)

    # 6. Crear carpeta de salida si no existe
    os.makedirs(os.path.dirname(path_out), exist_ok=True)

    # 7. Guardar archivo limpio
    df.to_csv(path_out, sep=";", index=False)
