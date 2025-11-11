"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

from pathlib import Path
def pregunta_01():
    """
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"

    """
    import re
    import unicodedata
    import pandas as pd

    in_path = Path("files/input/solicitudes_de_credito.csv")
    out_dir = Path("files/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "solicitudes_de_credito.csv"

    # --- lectura tolerante (autodetección del separador) ---
    df = pd.read_csv(in_path, sep=None, engine="python")

    # --- helper: quitar tildes y normalizar texto ---
    def _strip_accents(s: str) -> str:
        if pd.isna(s):
            return s
        s = str(s)
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        return s

    def _clean_text(s: pd.Series) -> pd.Series:
        return (
            s.astype(str)
             .map(_strip_accents)
             .str.lower()
             .str.strip()
             # homogeniza separadores y basura común
             .str.replace(r"[.$/\\|]", " ", regex=True)
             .str.replace(r"[-_]+", " ", regex=True)
             .str.replace(r"\s+", " ", regex=True)
             .str.replace(r"\s", "_", regex=True)
        )

    # --- normaliza encabezados (por si vienen "raros") ---
    df.columns = (
        pd.Series(df.columns)
          .map(_strip_accents)
          .str.lower()
          .str.strip()
          .str.replace(r"\s+", "_", regex=True)
    )

    # Campos esperados (si existen en el archivo)
    text_cols = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "linea_credito",          # algunas copias usan 'linea_credito'
        "línea_credito",          # otras usan acento
        "linea_de_credito",       # alias frecuente
        "ciudad",
        "departamento",
        "empresa",
    ]
    money_cols = ["monto_del_credito", "monto_credito"]
    date_cols  = ["fecha_de_beneficio", "fecha_del_beneficio", "fecha_beneficio"]
    int_like   = ["estrato", "comuna_ciudadano", "antiguedad", "score"]

    # --- limpia texto en columnas tipo string si existen ---
    for c in text_cols:
        if c in df.columns:
            df[c] = _clean_text(df[c])

    # Unifica nombre de columna de línea de crédito
    if "línea_credito" in df.columns and "linea_credito" not in df.columns:
        df.rename(columns={"línea_credito": "linea_credito"}, inplace=True)
    if "linea_de_credito" in df.columns and "linea_credito" not in df.columns:
        df.rename(columns={"linea_de_credito": "linea_credito"}, inplace=True)

    # --- normaliza 'sexo' si existe ---
    if "sexo" in df.columns:
        map_sexo = {
            "m": "m", "masculino": "m", "male": "m", "hombre": "m",
            "f": "f", "femenino": "f", "female": "f", "mujer": "f",
        }
        df["sexo"] = df["sexo"].replace(map_sexo)

    # --- monto: elimina $, puntos, comas, espacios y lo convierte a número ---
    target_money_col = None
    for c in money_cols:
        if c in df.columns:
            target_money_col = c
            break
    if target_money_col:
        df[target_money_col] = (
            df[target_money_col]
              .astype(str)
              .str.replace(r"[\s$.,]", "", regex=True)
              .replace({"": None})
              .astype("Int64")
        )
        # Homologar nombre final
        if target_money_col != "monto_del_credito":
            df.rename(columns={target_money_col: "monto_del_credito"}, inplace=True)

    # --- fechas: intenta múltiples formatos comunes (día/mes/año y mes/día/año) ---
    target_date_col = None
    for c in date_cols:
        if c in df.columns:
            target_date_col = c
            break
    if target_date_col:
        # intentos con dayfirst y sin, usando infer_datetime_format tolerante
        parsed = pd.to_datetime(df[target_date_col], errors="coerce", dayfirst=True)
        bad = parsed.isna()
        if bad.any():
            parsed2 = pd.to_datetime(df.loc[bad, target_date_col], errors="coerce", dayfirst=False)
            parsed.loc[bad] = parsed2
        df[target_date_col] = parsed.dt.date  # almacenar solo fecha
        if target_date_col != "fecha_de_beneficio":
            df.rename(columns={target_date_col: "fecha_de_beneficio"}, inplace=True)

    # --- enteros suaves ---
    for c in int_like:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    # --- columnas clave para validar faltantes (usa las que existan) ---
    required = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "linea_credito",
    ]
    required = [c for c in required if c in df.columns]

    # --- elimina registros con faltantes en campos clave ---
    if required:
        df = df.dropna(subset=required)

    # --- elimina duplicados tras la limpieza (sobre todas las columnas presentes) ---
    df = df.drop_duplicates()

    # --- guarda resultado ---
    df.to_csv(out_path, index=False)