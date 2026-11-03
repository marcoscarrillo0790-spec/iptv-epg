import urllib.request
import xml.etree.ElementTree as ET
import gzip
import io

# Definición de tus fuentes externas para strong8k / ferteque / KOALA-STRONG 8K
# (Puedes agregar o ajustar las URLs directas de tus listas aquí)
FUENTES_STRONG8K = [
    # Ejemplo de enlace de ferteque / strong8k (reemplaza o añade los tuyos reales)
    "https://raw.githubusercontent.com/ferteque/epg/main/strong8k.xml", 
    # Agrega más URLs si lo requieres
]

def limpiar_y_filtrar_elemento(elem):
    """Verifica si el elemento o sus atributos contienen referencias a open-epg.com"""
    # Revisar atributos comunes donde suele aparecer la fuente
    for key, val in elem.attrib.items():
        if val and "open-epg.com" in val.lower():
        # Si prefieres comprobar texto interno o IDs, puedes añadirlo aquí
            return False
    return True

def procesar_xml_desde_fuente(url_o_archivo, es_url=True):
    """Descarga (o lee) un XML/GZ, filtra open-epg y retorna una lista de elementos <channel> y <programme>"""
    elementos_validos = []
    try:
        if es_url:
            print(f"Descargando fuente: {url_o_archivo}")
            req = urllib.request.urlopen(url_o_archivo, timeout=30)
            contenido = req.read()
            
            # Si el archivo descargado está comprimido en gzip
            if url_o_archivo.endswith('.gz') or contenido[:2] == b'\x1f\x8b':
                with gzip.GzipFile(fileobj=io.BytesIO(contenido)) as f:
                    contenido = f.read()
            
            root = ET.fromstring(contenido)
        else:
            # Para archivos locales como latam.xml
            tree = ET.parse(url_o_archivo)
            root = tree.getroot()

        # Filtrar canales y programas descartando open-epg.com
        for child in root:
            # Validar si el canal/programa menciona open-epg
            texto_elemento = ET.tostring(child, encoding='utf-8').decode('utf-8').lower()
            if "open-epg.com" in texto_elemento:
                continue # Se descarta
            
            elementos_validos.append(child)
            
    except Exception as e:
        print(f"Error procesando la fuente {url_o_archivo}: {e}")
        
    return elementos_validos

def main():
    print("--- INICIANDO FUSIÓN Y FILTRADO INTELIGENTE DE EPG ---")

    # ==========================================
    # 1. GENERAR epg-elgato.xml (Basado en iptv-org / latam.xml)
    # ==========================================
    print("Procesando fuentes de iptv-org (latam.xml)...")
    elementos_iptv = procesar_xml_desde_fuente("latam.xml", es_url=False)
    
    root_elgato = ET.Element("tv")
    for elem in elementos_iptv:
        root_elgato.append(elem)
        
    tree_elgato = ET.ElementTree(root_elgato)
    tree_elgato.write("guia_final_unificada.xml", encoding="utf-8", xml_declaration=True)
    # Nota: El workflow actual se encarga de renombrarlo/comprimirlo a epg-elgato.xml.gz a partir de latam.xml o este archivo.


    # ==========================================
    # 2. GENERAR strong8k.xml (Ferteque + Strong8k + Koala-Strong, sin open-epg)
    # ==========================================
    print("Procesando fuentes de strong8k / ferteque...")
    root_strong = ET.Element("tv")
    
    for url in FUENTES_STRONG8K:
        elementos_fuente = procesar_xml_desde_fuente(url, es_url=True)
        for elem in elementos_fuente:
            root_strong.append(elem)
            
    tree_strong = ET.ElementTree(root_strong)
    tree_strong.write("strong8k.xml", encoding="utf-8", xml_declaration=True)
    print("Archivo strong8k.xml generado y filtrado con éxito.")

if __name__ == "__main__":
    main()
