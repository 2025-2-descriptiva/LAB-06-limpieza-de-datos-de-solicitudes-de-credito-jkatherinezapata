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
    import pandas as pd

    in_path = Path("files/input/solicitudes_de_credito.csv")
    out_dir = Path("files/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "solicitudes_de_credito.csv"


    df = pd.read_csv(in_path, sep=";", dtype=str)


    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].str.strip()


    col_alias = {
        "linea_credito": "línea_credito",
        "linea_de_credito": "línea_credito",
        "linea de credito": "línea_credito",
    }
    df.rename(columns={k: v for k, v in col_alias.items() if k in df.columns}, inplace=True)


    text_cols = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",   
    ]

    def norm_txt(s: pd.Series) -> pd.Series:
        return (
            s.str.lower()
             .str.replace(r"[.\t\r\n]+", " ", regex=True)
             .str.replace(r"[/+]", " ", regex=True)
             .str.replace(r"[-_]+", " ", regex=True)
             .str.replace(r"\s+", " ", regex=True)
             .str.strip()
             .str.replace(" ", "_")
        )

    for c in text_cols:
        if c in df.columns:
            df[c] = norm_txt(df[c])


    if "sexo" in df.columns:
        df["sexo"] = df["sexo"].replace({
            "masculino": "m", "male": "m", "hombre": "m", "m.": "m",
            "femenino": "f", "female": "f", "mujer": "f", "f.": "f",
        })

        df["sexo"] = df["sexo"].str.replace(r"[^mf]", "", regex=True)


    if "monto_del_credito" in df.columns:
        df["monto_del_credito"] = (
            df["monto_del_credito"]
            .str.replace(r"[^0-9]", "", regex=True)
            .replace({"": pd.NA})
            .astype("Int64")
        )


    if "fecha_de_beneficio" in df.columns:
        f1 = pd.to_datetime(df["fecha_de_beneficio"], errors="coerce", dayfirst=True)
        bad = f1.isna()
        if bad.any():
            f2 = pd.to_datetime(df.loc[bad, "fecha_de_beneficio"], errors="coerce", dayfirst=False)
            f1.loc[bad] = f2
        df["fecha_de_beneficio"] = f1.dt.strftime("%Y-%m-%d")

    for num_c in ["estrato", "comuna_ciudadano"]:
        if num_c in df.columns:
            df[num_c] = pd.to_numeric(df[num_c], errors="coerce").astype("Int64")


    required = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",  
    ]
    required = [c for c in required if c in df.columns]
    if required:
        df = df.dropna(subset=required)


    df = df.drop_duplicates()


    df.to_csv(out_path, index=False, sep=";")