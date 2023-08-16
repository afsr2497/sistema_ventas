import os
import django
import csv

# Configura la variable de entorno para el módulo de configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_ventas.settings")

# Inicializa Django
django.setup()

from sistema_2.models import departamentoCosto

allDepartments = departamentoCosto.objects.all().order_by('id')

print(f"Se tiene {len(allDepartments)} departamentos en el año 2023")


filename = 'allDepartments.csv'
datosDepartment = []

for departmentInfo in allDepartments:
    thisDepartment = [
        departmentInfo.nombreDepartamento
    ]
    datosDepartment.append(thisDepartment)

with open(filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(datosDepartment)

print(f"Archivo CSV '{filename}' exportado exitosamente.")
