import os
import django
import csv

# Configura la variable de entorno para el módulo de configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_ventas.settings")

# Inicializa Django
django.setup()

from sistema_2.models import abonosOperacion, cajaChica

cajasTotales = cajaChica.objects.all().order_by('id')

print(f"Se tiene {len(cajasTotales)} cajas en el año 2023")


filename = 'cajasActuales.csv'
dataCajas = []

for cajaInfo in cajasTotales:
    cajaActual = [
        cajaInfo.conceptoCaja,
        cajaInfo.valorRegistrado,
        cajaInfo.fechaCreacion.strftime('%d-%m-%Y'),
        cajaInfo.monedaCaja,
    ]

    dataCajas.append(cajaActual)


with open(filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(dataCajas)

print(f"Archivo CSV '{filename}' exportado exitosamente.")