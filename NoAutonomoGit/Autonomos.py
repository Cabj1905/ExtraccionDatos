import requests
from bs4 import BeautifulSoup
import pandas as pd


url="https://es.wikipedia.org/wiki/Territorio_no_aut%C3%B3nomo"
headers={"User-Agent": "Mozilla/5.0"}

r=requests.get(url,headers=headers)
r.raise_for_status()

soup=BeautifulSoup(r.text,"html.parser")

target=None
for h in soup.find_all(["h2"]):
    if "Miembros actuales" in h.get_text():
        target=h
        break

if target is None:
    raise ValueError("No se encontró la tabla")

table=target.find_next("table")

df=pd.read_html(str(table))[0]

df.rename(columns={"Población[nota 2]\u200b":"Población"},inplace=True)

for col in df.select_dtypes(include=["object"]).columns:
    df[col] = (
        df[col].str.replace(r"\[.*?\]", "", regex=True)  # elimina lo que está entre corchetes
        
    )

for col in ["Población", "Superficie (km²)"]:
    df[col] = (
        df[col]
        .astype(str)  # asegura que la columna sea texto
        .str.replace(r"\[.*?\]", "", regex=True)             # elimina notas tipo [nota 1]
        .str.replace(r"[\u200b-\u200d\uFEFF\xa0\s]", "", regex=True)  # elimina espacios y caracteres invisibles
        .str.replace(",", ".", regex=False)                  # cambia coma decimal a punto
        .str.strip()
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")        # convierte a float



df = df.astype({'Territorio': 'string', 'Potencia administradora': 'string', 'Fecha de inclusión en la lista de territorios no autónomos': 'string'})

print(df.dtypes)


df.to_csv("autonomos.csv",index=False)