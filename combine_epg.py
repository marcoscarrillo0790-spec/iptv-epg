import gzip
import requests
import xml.etree.ElementTree as ET

# Diccionario con tus fuentes
EPG_SOURCES = {
    # Fuentes Personalizadas / Ferteque
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg2.xml.gz": "JAMS-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg1.xml.gz": "FERTEQUE-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg6.xml.gz": "GANJA RELEASE-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg14.xml.gz": "TROPAZ-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg52.xml.gz": "MON-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg42.xml.gz": "KOALA-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg38.xml.gz": "KOALA-EUROPA-STRONG 8K",
    
    # Fuentes Open-EPG
    "https://www.open-epg.com/files/argentina.xml.gz": "argentina.xml.gz",
    "https://www.open-epg.com/files/bolivia.xml.gz": "bolivia.xml.gz",
    "https://www.open-epg.com/files/canada.xml.gz": "canada.xml.gz",
    "https://www.open-epg.com/files/chile1.xml.gz": "chile1.xml.gz",
    "https://www.open-epg.com/files/chile2.xml.gz": "chile2.xml.gz",
    "https://www.open-epg.com/files/colombia1.xml.gz": "colombia1.xml.gz",
    "https://www.open-epg.com/files/colombia2.xml.gz": "colombia2.xml.gz",
    "https://www.open-epg.com/files/costarica1.xml.gz": "costarica1.xml.gz",
    "https://www.open-epg.com/files/dominican1.xml.gz": "dominican1.xml.gz",
    "https://www.open-epg.com/files/ecuador1.xml.gz": "ecuador1.xml.gz",
    "https://www.open-epg.com/files/elsalvador1.xml.gz": "elsalvador1.xml.gz",
    "https://www.open-epg.com/files/guatemala.xml.gz": "guatemala.xml.gz",
    "https://www.open-epg.com/files/honduras.xml.gz": "honduras.xml.gz",
    "https://www.open-epg.com/files/mexico1.xml.gz": "mexico1.xml.gz",
    "https://www.open-epg.com/files/mexico2.xml.gz": "mexico2.xml.gz",
    "https://www.open-epg.com/files/panama1.xml.gz": "panama1.xml.gz",
    "https://www.open-epg.com/files/paraguay1.xml.gz": "paraguay1.xml.gz",
    "https://www.open-epg.com/files/paraguay2.xml.gz": "paraguay2.xml.gz",
    "https://www.open-epg.com/files/peru.xml.gz": "peru.xml.gz",
    "https://www.open-epg.com/files/portugal1.xml.gz": "portugal1.xml.gz",
    "https://www.open-epg.com/files/portugal2.xml.gz": "portugal2.xml.gz",
    "https://www.open-epg.com/files/puertorico1.xml.gz": "puertorico1.xml.gz",
    "https://www.open-epg.com/files/puertorico2.xml.gz": "puertorico2.xml.gz",
    "https://www.open-epg.com/files/spain.xml.gz": "spain.xml.gz"
}

def fetch_and_parse(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # allow_redirects=True asegura que sigamos los enlaces de GitHub sin bloqueos
        response = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"[ADVERTENCIA] Código HTTP {response.status_code} para: {url}")
            return None

        # Detectar compresión GZIP mediante extensión o cabecera de bytes binarios (firma mágica \x1f\x8b)
        if url.endswith('.gz') or response.content.startswith(b'\x1f\x8b'):
            try:
                xml_data = gzip.decompress(response.content)
            except Exception as gz_err:
                print(f"[ERROR GZIP] No se pudo descomprimir {url}: {gz_err}")
                return None
        else:
            xml_data = response.content
            
        return ET.fromstring(xml_data)
    except Exception as e:
        print(f"[ERROR] No se pudo descargar o parsear XML de {url} -> {e}")
        return None

def merge_epgs():
    combined_root = ET.Element('tv')
    canales_agregados = 0
    programas_agregados = 0

    for url, tag in EPG_SOURCES.items():
        print(f"Procesando fuente: {tag}...")
        root = fetch_and_parse(url)
        if root is None:
            print(f"-> Omitida o fallida (continuando con las demás): {tag}")
            continue

        clean_tag = tag.replace(" ", "_").replace("&", "and").replace("|", "_")

        c_count = 0
        for channel in root.findall('channel'):
            old_id = channel.get('id')
            if old_id:
                new_id = f"{clean_tag}_{old_id}"
                channel.set('id', new_id)
                combined_root.append(channel)
                c_count += 1
        canales_agregados += c_count

        p_count = 0
        for programme in root.findall('programme'):
            old_channel_ref = programme.get('channel')
            if old_channel_ref:
                new_channel_ref = f"{clean_tag}_{old_channel_ref}"
                programme.set('channel', new_channel_ref)
                combined_root.append(programme)
                p_count += 1
        programas_agregados += p_count

        print(f"-> OK: {c_count} canales y {p_count} programas añadidos de {tag}.")

    print(f"\nTotal acumulado general: {canales_agregados} canales y {programas_agregados} programas.")
    print("Guardando y comprimiendo el resultado unificado...")
    
    tree = ET.ElementTree(combined_root)
    
    with open('epg.xml', 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
        
    with open('epg.xml', 'rb') as f_in, gzip.open('epg.xml.gz', 'wb') as f_out:
        f_out.writelines(f_in)

    print("¡Proceso finalizado con éxito! Archivo generado: epg.xml.gz")

if __name__ == '__main__':
    merge_epgs()
