import os
import django
import csv

# Configura la variable de entorno para el módulo de configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_ventas.settings")

# Inicializa Django
django.setup()

from sistema_2.models import departamentoCosto,categoriaCosto

todoCategorias = categoriaCosto.objects.all().order_by('id')

print(f"Se tiene {len(todoCategorias)} categorias en el año 2023")


filename = 'todoCategorias.csv'
datosCategoria = []

for categoriaInfo in todoCategorias:
    categoriaActual = [
        categoriaInfo.nombreCategoria,
        categoriaInfo.departamentoAsociado.nombreDepartamento
    ]
    datosCategoria.append(categoriaActual)

with open(filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(datosCategoria)

print(f"Archivo CSV '{filename}' exportado exitosamente.")
