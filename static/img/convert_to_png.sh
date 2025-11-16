#!/bin/bash

# Recorre todos los archivos de la carpeta
for img in *; do
    # Ignorar directorios
    [ -d "$img" ] && continue

    # Obtener extensión en minúsculas
    ext="${img##*.}"
    ext_lower=$(echo "$ext" | tr 'A-Z' 'a-z')

    # Si NO es png → convertir
    if [ "$ext_lower" != "png" ]; then
        base="${img%.*}"
        echo "Convirtiendo: $img → ${base}.png"
        convert "$img" "${base}.png"
    fi
done
