import os
import django
import csv

# Configura la variable de entorno para el módulo de configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_ventas.settings")

# Inicializa Django
django.setup()

from sistema_2.models import abonosOperacion

abonosActuales = abonosOperacion.objects.all().order_by('codigo_comprobante')

print(f"Se tiene {len(abonosActuales)} abonos en el año 2023")


filename = 'abonosActuales.csv'
dataAbonos = []

for abonoInfo in abonosActuales:
    if abonoInfo.abono_comisionable == '1':
        enabledComission = 'ON'
    else:
        enabledComission = 'OFF'

    if abonoInfo.codigo_comprobante[0] == 'F':
        tipoComprobante = 'BILL'
    else:
        tipoComprobante = 'INVOICE'
    abonoActual = [
        abonoInfo.fechaAbono,
        abonoInfo.codigo_comprobante,
        abonoInfo.codigo_guia,
        abonoInfo.codigo_coti,
        abonoInfo.codigo_vendedor,
        enabledComission,
        abonoInfo.comprobanteCancelado,
        abonoInfo.datos_banco[1],
        abonoInfo.datos_banco[2],
        tipoComprobante,
        abonoInfo.nro_operacion,
        abonoInfo.nro_operacion_2,
        abonoInfo.datos_cliente[1],
    ]
    dataAbonos.append(abonoActual)


with open(filename, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(dataAbonos)

print(f"Archivo CSV '{filename}' exportado exitosamente.")