import pandas as pd
import os


# URL directa de la página de Wikipedia con la tabla
url = "https://es.wikipedia.org/wiki/Anexo:Partidos_de_la_provincia_de_Buenos_Aires"

# Leer todas las tablas de la página
dfs = pd.read_html(url)

# Mostrar las primeras 5 filas de la primera tabla (la que nos interesa)
df = dfs[2]
print(df.head())

# (Opcional) Guardar como CSV
df.to_csv("partidos_pba.csv", index=False, encoding="utf-8-sig")

ruta_csv = os.path.abspath("partidos_pba.csv")
print(f"Archivo CSV guardado en:\n{ruta_csv}")
