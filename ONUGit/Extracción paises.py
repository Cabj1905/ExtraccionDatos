import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url="https://es.wikipedia.org/wiki/Anexo:Pa%C3%ADses#Pa%C3%ADses_reconocidos_por_las_Naciones_Unidas"
headers = {"User-Agent": "Mozilla/5.0"}

r=requests.get (url,headers=headers)
r.raise_for_status()

soup=BeautifulSoup(r.text, "html.parser")


#busco el encabezado por texto
target_header=None
for h in soup.find_all(["h2","h3","h4"]):
   if "Países reconocidos por las Naciones Unidas" in h.get_text():
       target_header=h
       break    
   
if target_header is None:
    raise ValueError("No se encontró el encacabezado en la página")

table=target_header.find_next("table")


df = pd.read_html(str(table))[0]

# Nos quedamos solo con las filas donde 'Capital(es)' no sea igual a 'Forma de gobierno'
#hago esto ya que estaba tomando las descripciones de los paises como una nueva columna duplicando así todos los datos.
df_filtrado = df[df["Capital(es)"] != df["Forma de gobierno"]]

# Resetear índice
df_filtrado = df_filtrado.reset_index(drop=True)

df_filtrado.drop(columns=["Ubicación"],inplace=True)
df_filtrado.drop(columns=["Estado soberano (nombre común).1"],inplace=True)
df_filtrado.rename(columns={"Estado soberano (nombre común)":"Nombre país"},inplace=True)


df_filtrado["Año_reconocimiento"] = df_filtrado["Estatus ONU"].str.extract(r"(\d{4})")

#\( y \) → buscan los paréntesis literal.
#(.*?) → captura cualquier carácter (.), de forma no codiciosa (?), hasta encontrar el paréntesis de cierre.
df_filtrado["Nombre_comun"] = df_filtrado["Nombre país"].str.extract(r"\((.*?)\)")

#reemplazo el nombre común del país de la columna del país oficial
#\(.*?\) → busca cualquier texto entre paréntesis.
#.str.strip() → quita espacios sobrantes que pueden quedar al final.
df_filtrado["Nombre país"] = df_filtrado["Nombre país"].str.replace(r"\(.*?\)", "", regex=True).str.strip()


# Opcional: convertir a número (int)
df_filtrado["Año_reconocimiento"] = pd.to_numeric(df_filtrado["Año_reconocimiento"], errors="coerce")

#Evito que los años queden con un .0 (1983.0,1920.0, etc.)
df_filtrado["Año_reconocimiento"] = df_filtrado["Año_reconocimiento"].astype("Int64")


# Limpiar todas las columnas de texto
for col in df_filtrado.select_dtypes(include=["object"]).columns:
    df_filtrado[col] = (
        df_filtrado[col]
        .str.replace(r"\[.*?\]", "", regex=True)  # elimina lo que está entre corchetes
        .str.replace(r"[\u200b-\u200d\uFEFF]", "", regex=True)  # elimina caracteres invisibles
        .str.strip()  # quita espacios extra
    )

#Elimino el duplicado de Azerbayan que estaba vacio
df_filtrado=df_filtrado.dropna(subset=["Forma de gobierno"])

df_filtrado.to_csv("paises_reconocidos.csv", index=False)

