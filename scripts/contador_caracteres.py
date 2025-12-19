import os

def contar_caracteres_md(ruta_base):
    total_caracteres = 0

    for raiz, _, archivos in os.walk(ruta_base):
        for archivo in archivos:
            if archivo.lower().endswith(".md"):
                ruta_archivo = os.path.join(raiz, archivo)
                try:
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        contenido = f.read()
                        total_caracteres += len(contenido)
                except Exception as e:
                    print(f"Error leyendo {ruta_archivo}: {e}")

    return total_caracteres


# Uso
#directorio = "ruta/al/directorio"
directorio = "C:/ruta/al/directorio/louis"
total = contar_caracteres_md(directorio)
print(f"Total de caracteres en archivos .md: {total}")
