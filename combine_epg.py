import gzip
import requests
import xml.etree.ElementTree as ET

# Diccionario con tus fuentes corregidas y sus nombres identificadores
EPG_SOURCES = {
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
    "https://www.open-epg.com/files/spain.xml.gz": "spain.xml.gz",
    "https://www.open-epg.com/files/sports4.xml.txt": "sports4.xml.gz",
    "https://www.open-epg.com/files/unitedkingdom.xml.gz": "unitedkingdom.xml.gz",
    "https://www.open-epg.com/files/unitedstates10.xml.gz": "unitedstates10.xml.gz",
    "https://www.open-epg.com/files/unitedstates11.xml.gz": "unitedstates11.xml.gz",
    "https://www.open-epg.com/files/unitedstates2.xml.gz": "unitedstates2.xml.gz",
    "https://www.open-epg.com/files/unitedstates3.xml.gz": "unitedstates3.xml.gz",
    "https://www.open-epg.com/files/unitedstates4.xml.gz": "unitedstates4.xml.gz",
    "https://www.open-epg.com/files/unitedstates5.xml.gz": "unitedstates5.xml.gz",
    "https://www.open-epg.com/files/unitedstates6.xml.gz": "unitedstates6.xml.gz",
    "https://www.open-epg.com/files/unitedstates7.xml.gz": "unitedstates7.xml.gz",
    "https://www.open-epg.com/files/unitedstates8.xml.gz": "unitedstates8.xml.gz",
    "https://www.open-epg.com/files/unitedstates9.xml.gz": "unitedstates9.xml.gz",
    "https://www.open-epg.com/files/uruguay.xml.gz": "uruguay.xml.gz",
    "https://www.open-epg.com/files/venezuela1.xml.gz": "venezuela1.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg1.xml.gz": "Spain football&Tv",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg42.xml.gz": "latam strong8k",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg37.xml.gz": "US SPORTS"
}

def fetch_and_parse(url):
    try:
        response = requests.get(url, timeout=30)
        # Si la URL termina en .gz, descomprimimos
        if url.endswith('.gz'):
            xml_data = gzip.decompress(response.content)
        else:
            xml_data = response.content
        return ET.fromstring(xml_data)
    except Exception as e:
        print(f"[ERROR] No se pudo descargar o procesar: {url} -> {e}")
        return None

def merge_epgs():
    combined_root = ET.Element('tv')

    for url, tag in EPG_SOURCES.items():
        print(f"Procesando fuente: {tag}...")
        root = fetch_and_parse(url)
        if root is None:
            continue

        # Limpiar caracteres especiales de la etiqueta para evitar errores en los IDs
        clean_tag = tag.replace(" ", "_").replace("&", "and")

        # 1. Modificar e insertar etiquetas <channel>
        for channel in root.findall('channel'):
            old_id = channel.get('id')
            if old_id:
                new_id = f"{clean_tag}_{old_id}"
                channel.set('id', new_id)
                combined_root.append(channel)

        # 2. Modificar e insertar etiquetas <programme>
        for programme in root.findall('programme'):
            old_channel_ref = programme.get('channel')
            if old_channel_ref:
                new_channel_ref = f"{clean_tag}_{old_channel_ref}"
                programme.set('channel', new_channel_ref)
                combined_root.append(programme)

    print("Guardando y comprimiendo el resultado unificado...")
    tree = ET.ElementTree(combined_root)
    
    # Escribir archivo XML temporal
    with open('epg.xml', 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
        
    # Comprimir en epg.xml.gz final
    with open('epg.xml', 'rb') as f_in, gzip.open('epg.xml.gz', 'wb') as f_out:
        f_out.writelines(f_in)

    print("¡Proceso finalizado con éxito! Archivo generado: epg.xml.gz")

if __name__ == '__main__':
    merge_epgs()