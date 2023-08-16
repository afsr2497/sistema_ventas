import os
import django
import csv

# Configura la variable de entorno para el módulo de configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_ventas.settings")

# Inicializa Django
django.setup()

from sistema_2.models import departamentoCosto,categoriaCosto, divisionCosto

todoDivisiones = divisionCosto.objects.all().order_by('id')

print(f"Se tiene {len(todoDivisiones)} categorias en el año 2023")


filename = 'todoDivisiones.csv'
datosDivisiones = []

for divisionInfo in todoDivisiones:
    divisionActual = [
        divisionInfo.nombreDivision,
        divisionInfo.tipoCosto,
        divisionInfo.comportamientoCosto,
        divisionInfo.operativoCosto,
        divisionInfo.categoriaAsociada.nombreCategoria
    ]
    datosDivisiones.append(divisionActual)

with open(filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(datosDivisiones)

print(f"Archivo CSV '{filename}' exportado exitosamente.")
