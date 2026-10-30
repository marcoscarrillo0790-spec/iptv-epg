import os
import gzip
import shutil
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = {
    # Si descargamos latam.xml previamente en el workflow, lo leemos localmente:
    "latam.xml": "LATAM",
    
    # Fuentes Personalizadas / Ferteque
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg2.xml.gz": "JAMS-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg1.xml.gz": "FERTEQUE-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg6.xml.gz": "GANJA RELEASE-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg14.xml.gz": "TROPAZ-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg52.xml.gz": "MON-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg42.xml.gz": "KOALA-STRONG 8K",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg38.xml.gz": "KOALA-EUROPA-STRONG 8K",
    
    # Fuentes Open-EPG
    "https://www.open-epg.com/files/argentina.xml.gz": "argentina",
    "https://www.open-epg.com/files/mexico1.xml.gz": "mexico1",
    "https://www.open-epg.com/files/mexico2.xml.gz": "mexico2",
    "https://www.open-epg.com/files/peru.xml.gz": "peru",
    "https://www.open-epg.com/files/colombia1.xml.gz": "colombia1",
    "https://www.open-epg.com/files/colombia2.xml.gz": "colombia2",
    "https://www.open-epg.com/files/elsalvador1.xml.gz": "elsalvador1",
    "https://www.open-epg.com/files/guatemala.xml.gz": "guatemala",
    "https://www.open-epg.com/files/honduras.xml.gz": "honduras",
    "https://www.open-epg.com/files/bolivia.xml.gz": "bolivia",
    "https://www.open-epg.com/files/canada.xml.gz": "canada",
    "https://www.open-epg.com/files/chile1.xml.gz": "chile1",
    "https://www.open-epg.com/files/chile2.xml.gz": "chile2",
    "https://www.open-epg.com/files/costarica1.xml.gz": "costarica1",
    "https://www.open-epg.com/files/dominican1.xml.gz": "dominican1",
    "https://www.open-epg.com/files/ecuador1.xml.gz": "ecuador1",
    "https://www.open-epg.com/files/panama1.xml.gz": "panama1",
    "https://www.open-epg.com/files/paraguay1.xml.gz": "paraguay1",
    "https://www.open-epg.com/files/paraguay2.xml.gz": "paraguay2",
    "https://www.open-epg.com/files/portugal1.xml.gz": "portugal1",
    "https://www.open-epg.com/files/portugal2.xml.gz": "portugal2",
    "https://www.open-epg.com/files/puertorico1.xml.gz": "puertorico1",
    "https://www.open-epg.com/files/puertorico2.xml.gz": "puertorico2",
    "https://www.open-epg.com/files/spain.xml.gz": "spain"
}

TEMP_DIR = "epg_temp"
OUTPUT_FILE = "guia_final_unificada.xml"

def preparar_entorno():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def descargar_y_descomprimir():
    archivos_xml = []
    for path_or_url, nombre_id in SOURCES.items():
        safe_filename = nombre_id.lower().replace(" ", "_").replace("&", "and") + ".xml.gz"
        compressed_path = os.path.join(TEMP_DIR, safe_filename)
        xml_name = safe_filename.replace(".gz", "")
        xml_path = os.path.join(TEMP_DIR, xml_name)
        
        try:
            if not path_or_url.startswith("http"):
                if os.path.exists(path_or_url):
                    shutil.copyfile(path_or_url, xml_path)
                    archivos_xml.append((xml_path, nombre_id))
                    print(f"📁 Usando archivo local [{nombre_id}]")
                else:
                    print(f"⚠️ Archivo local no encontrado (omitido): {path_or_url}")
                continue

            print(f"📥 Descargando [{nombre_id}]...")
            urllib.request.urlretrieve(path_or_url, compressed_path)
            
            if safe_filename.endswith(".gz"):
                with gzip.open(compressed_path, "rb") as f_in:
                    with open(xml_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                archivos_xml.append((xml_path, nombre_id))
            else:
                archivos_xml.append((compressed_path, nombre_id))
                
        except Exception as e:
            print(f"⚠️ Error al procesar {nombre_id} ({path_or_url}): {e}")
            
    return archivos_xml

def fusionar_xmltv_inteligente(archivos_xml, output_path):
    print("🔄 Analizando y fusionando inteligentemente los archivos EPG...")
    
    channels_dict = {}  
    programmes_list = []
    
    priority_sources = [
        'argentina', 'mexico', 'peru', 
        'colombia', 'elsalvador', 'guatemala', 
        'honduras', 'koala-strong_8k', 'latam'
    ]

    for archivo, nombre_id in archivos_xml:
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            is_priority = any(p in nombre_id.lower().replace(" ", "_") for p in priority_sources)

            channels_with_programs = set()
            source_programmes = root.findall("programme")
            for prog in source_programmes:
                ch_ref = prog.get("channel")
                if ch_ref:
                    channels_with_programs.add(ch_ref)

            for channel in root.findall("channel"):
                channel_id = channel.get("id")
                if not channel_id:
                    continue

                has_logo = channel.find("icon") is not None
                has_prog = channel_id in channels_with_programs

                if channel_id not in channels_dict:
                    channels_dict[channel_id] = {
                        'element': channel,
                        'has_prog': has_prog,
                        'has_logo': has_logo,
                        'is_priority': is_priority
                    }
                else:
                    existing = channels_dict[channel_id]
                    if is_priority and not existing['is_priority']:
                        channels_dict[channel_id] = {
                            'element': channel,
                            'has_prog': has_prog or existing['has_prog'],
                            'has_logo': has_logo or existing['has_logo'],
                            'is_priority': True
                        }
                    else:
                        if not existing['has_logo'] and has_logo:
                            existing['element'] = channel
                            existing['has_logo'] = True
                        if not existing['has_prog'] and has_prog:
                            existing['has_prog'] = True

            for programme in source_programmes:
                ch_ref = programme.get("channel")
                if ch_ref in channels_dict:
                    programmes_list.append(programme)

        except Exception as e:
            print(f"⚠️ Error al parsear {archivo}: {e}")

    root_final = ET.Element("tv")
    for channel_id, data in channels_dict.items():
        root_final.append(data['element'])
        
    for programme in programmes_list:
        root_final.append(programme)

    tree_final = ET.ElementTree(root_final)
    tree_final.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ ¡Guía unificada inteligente generada con éxito en: {output_path}!")
    print(f"📊 Total resultante: {len(channels_dict)} canales y {len(programmes_list)} programas.")

def limpiar_temporales():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    preparar_entorno()
    xmls = descargar_y_descomprimir()
    if xmls:
        fusionar_xmltv_inteligente(xmls, OUTPUT_FILE)
        limpiar_temporales()
    else:
        print("❌ No se pudieron descargar fuentes EPG válidas.")
