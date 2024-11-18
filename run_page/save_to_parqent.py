import duckdb

with duckdb.connect() as conn:
    conn.install_extension("sqlite")
    conn.load_extension("sqlite")
    conn.sql("ATTACH 'run_page/data.db' (TYPE SQLITE);USE data;")
    conn.sql(
        "COPY (SELECT * FROM activities) TO 'run_page/data.parquet' (FORMAT PARQUET);"
    )
