from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def obtener_html_renderizado(url):
    """
    Obtiene el HTML renderizado (con JS ejecutado) desde una URL usando Selenium.

    Args:
        url (str): URL de la página

    Returns:
        str: HTML completo con JavaScript ejecutado
    """
    opciones = Options()
    opciones.add_argument("--headless")  # Ejecutar en segundo plano
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument("--disable-extensions")
    opciones.add_argument('--user-agent=Mozilla/5.0')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opciones)
    try:
        driver.get(url)
        time.sleep(5)  # Esperar a que cargue JS (ajustar si es necesario)
        html = driver.page_source
    finally:
        driver.quit()

    return html






def extraer_titulos_noticias(html):
    """
    Extrae los textos 'alt' de imágenes dentro de <body> que provienen de Cointelegraph.

    Args:
        html: HTML completo renderizado

    Returns:
        list: Lista de 'alt' relevantes
    """
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    if not body:
        return []

    alt_textos = []

    for img in body.find_all('img', alt=True):
        alt = img['alt'].strip()
        atributos_img = dict(img.attrs)

        # Verificar si alguno de los atributos contiene 'images.cointelegraph.com'
        contiene_imagen_valida = any(
            'images.cointelegraph.com' in str(valor)
            for clave, valor in atributos_img.items()
            if isinstance(valor, str)
        )

        if contiene_imagen_valida and alt:
            alt_textos.append(alt)

    return alt_textos





html = obtener_html_renderizado('https://es.cointelegraph.com/search?query=solana')
print(extraer_titulos_noticias(html))
