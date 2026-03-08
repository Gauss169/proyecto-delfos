import requests
from bs4 import BeautifulSoup

# URL de la página de la que quieres obtener datos
url = "https://es.cointelegraph.com/"

# Agregamos un encabezado con un User-Agent simulado
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Realizamos la solicitud HTTP con el encabezado
response = requests.get(url, headers=headers)

# Verificamos si la solicitud fue exitosa
if response.status_code == 200:
    print("Página cargada correctamente.")
else:
    print("Hubo un problema al cargar la página.")
    print(response.status_code)

# Parseamos el contenido HTML de la respuesta
soup = BeautifulSoup(response.text, 'html.parser')

# Buscamos todos los títulos <h2>
titulos = soup.find_all('h1')

print(type(titulos))

# Imprimimos todos los títulos encontrados
for titulo in titulos:
    print(titulo.text)
