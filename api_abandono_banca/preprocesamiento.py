import numpy as np
import pandas as pd


def preparar_datos_crudos(df_entrada: pd.DataFrame) -> pd.DataFrame:
    """Aplica reglas deterministas y prepara las variables derivadas del modelo."""
    df = df_entrada.copy()

    columnas_descarte = [
        "id_cliente",
        "salario_mensual_aprox",
        "comentarios_cliente",
        "motivo_cancelacion",
    ]
    df = df.drop(columns=columnas_descarte, errors="ignore")

    if "edad" in df.columns:
        df.loc[(df["edad"] <= 0) | (df["edad"] > 120), "edad"] = np.nan
    if "ingresos_anuales" in df.columns:
        df.loc[df["ingresos_anuales"] <= 0, "ingresos_anuales"] = np.nan
    if "saldo_cuenta" in df.columns:
        df["saldo_cuenta"] = df["saldo_cuenta"].replace(-999, np.nan)

    if "tipo_cuenta" in df.columns:
        df["tipo_cuenta"] = df["tipo_cuenta"].astype(str).str.strip().str.capitalize()
        df["tipo_cuenta"] = df["tipo_cuenta"].replace(
            {"Desconocido": np.nan, "?": np.nan, "Nan": np.nan, "None": np.nan}
        )

    if "canal_preferido" in df.columns:
        df["canal_preferido"] = df["canal_preferido"].astype(str).str.strip()
        df["canal_preferido"] = df["canal_preferido"].replace(
            {"???": np.nan, "Nan": np.nan, "None": np.nan}
        )

    if "nivel_estudios" in df.columns:
        df["nivel_estudios"] = df["nivel_estudios"].astype(str).str.strip()
        df["nivel_estudios"] = df["nivel_estudios"].replace(
            {"Nan": np.nan, "nan": np.nan, "None": np.nan}
        )

    if "saldo_cuenta" in df.columns and "ingresos_anuales" in df.columns:
        df["ratio_saldo_ingresos"] = df["saldo_cuenta"] / (df["ingresos_anuales"] + 1)

    if "saldo_cuenta" in df.columns and "num_productos" in df.columns:
        df["saldo_por_producto"] = df["saldo_cuenta"] / df["num_productos"].replace(0, np.nan)

    if "edad" in df.columns:
        limites_edad = [0, 30, 55, 120]
        etiquetas_edad = ["Joven", "Adulto", "Senior"]
        df["grupo_edad"] = pd.cut(
            df["edad"], bins=limites_edad, labels=etiquetas_edad
        ).astype(str)

    if "antiguedad_meses" in df.columns:
        df["antiguedad_anios"] = df["antiguedad_meses"] / 12.0
        df = df.drop(columns=["antiguedad_meses"])

    return df
