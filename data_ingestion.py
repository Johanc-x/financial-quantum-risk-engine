import sys
import os

# Para que Python pueda encontrar el paquete "core"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
import numpy as np

from core.db_connection import get_connection


def download_prices(ticker, period="5y"):
    """
    Descarga precios históricos del ticker usando yfinance.
    Devuelve un DataFrame con el precio de cierre.
    """
    data = yf.download(ticker, period=period)

    # Nos quedamos solo con la columna Close y la renombramos
    data = data[["Close"]].rename(columns={"Close": "close_price"})

    # El índice (fecha) lo llamamos igual que en Oracle: price_date
    data.index.name = "price_date"

    return data


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula retornos diarios y volatilidad de 30 días.
    """
    df["return_daily"] = df["close_price"].pct_change()
    df["vol_30d"] = df["return_daily"].rolling(window=30).std()
    df = df.dropna()
    return df


def get_or_create_asset_id(conn, ticker: str) -> int:
    """
    Busca el asset_id de un ticker en fqre_assets.
    Si no existe, lo inserta y luego lo vuelve a leer.
    """
    cur = conn.cursor()

    # 1) Intentamos buscar el asset_id
    cur.execute(
        """
        SELECT asset_id
        FROM fqre_assets
        WHERE ticker = :ticker
        """,
        {"ticker": ticker},
    )

    row = cur.fetchone()
    if row:
        asset_id = row[0]
        cur.close()
        return asset_id

    # 2) Si no existe, lo insertamos
    cur.execute(
        """
        INSERT INTO fqre_assets (ticker, asset_type, currency)
        VALUES (:ticker, 'STOCK', 'USD')
        """,
        {"ticker": ticker},
    )
    conn.commit()

    # 3) Volvemos a leer el asset_id recién creado
    cur.execute(
        """
        SELECT asset_id
        FROM fqre_assets
        WHERE ticker = :ticker
        """,
        {"ticker": ticker},
    )
    asset_id = cur.fetchone()[0]

    cur.close()
    return asset_id


def insert_prices_into_oracle(conn, df: pd.DataFrame, asset_id: int) -> None:
    """
    Inserta en Oracle todas las filas de precios para un asset_id dado
    en la tabla fqre_asset_prices.
    """
    cur = conn.cursor()

    rows = []
    for idx, row in df.iterrows():
        rows.append(
            (
                asset_id,
                idx.to_pydatetime(),             # price_date
                float(row["close_price"]),
                float(row["return_daily"]),
                float(row["vol_30d"]),
            )
        )

    cur.executemany(
        """
        INSERT INTO fqre_asset_prices (
            asset_id,
            price_date,
            close_price,
            return_daily,
            vol_30d
        )
        VALUES (:1, :2, :3, :4, :5)
        """,
        rows,
    )

    conn.commit()
    cur.close()


def run_pipeline(ticker: str) -> None:
    """
    Ejecuta el pipeline completo para un ticker:
    1) Descarga datos de yfinance
    2) Calcula retornos y volatilidad
    3) Inserta en Oracle (tablas fqre_assets y fqre_asset_prices)
    """
    print(f"Descargando precios de {ticker} desde yfinance...")
    df = download_prices(ticker)
    print("Muestra de datos descargados:")
    print(df.head())

    print("Calculando retornos y volatilidad 30d...")
    df = prepare_data(df)

    print("Conectando a Oracle...")
    conn = get_connection()

    print("Obteniendo / creando asset_id...")
    asset_id = get_or_create_asset_id(conn, ticker)
    print(f"asset_id para {ticker}: {asset_id}")

    print("Insertando precios en fqre_asset_prices...")
    insert_prices_into_oracle(conn, df, asset_id)

    conn.close()
    print(f"Pipeline completado para {ticker} ✅")


if __name__ == "__main__":
    # Ticker de prueba
    run_pipeline("AAPL")


