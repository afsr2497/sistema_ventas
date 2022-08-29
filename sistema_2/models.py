from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.forms import CharField, FloatField
import datetime

# Create your models here.

class FileUpload(models.Model):
    file=models.FileField(upload_to='archivos')

class userProfile(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)

class clients(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64,null=True)
    apellido = models.CharField(max_length=64,null=True)
    razon_social = models.CharField(max_length=128,null=True)
    dni = models.CharField(max_length=64,null=True)
    ruc = models.CharField(max_length=64,null=True)
    email = models.CharField(max_length=64,null=True)
    contacto = models.CharField(max_length=64,null=True)
    telefono = models.CharField(max_length=64,null=True)
    direccion_fiscal = models.CharField(max_length=256,default='SinDireccion')
    direcciones = ArrayField(models.CharField(max_length=256),null=True)

class products(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=128,null=True)
    codigo = models.CharField(max_length=128,null=True)
    categoria = models.CharField(max_length=128,null=True)
    sub_categoria = models.CharField(max_length=128,null=True)
    unidad_med = models.CharField(max_length=128,null=True)
    precio_compra_sin_igv = models.FloatField(default=0,null=True)
    precio_compra_con_igv = models.FloatField(default=0,null=True)
    precio_venta_sin_igv = models.FloatField(default=0,null=True)
    precio_venta_con_igv = models.FloatField(default=0,null=True)
    codigo_sunat = models.CharField(max_length=128,null=True)
    moneda = models.CharField(max_length=128,default='SOLES')
    stock = ArrayField(ArrayField(models.CharField(max_length=20)),default=list())
    stockTotal = models.CharField(max_length=128,default='0')
    pesoProducto = models.CharField(max_length=128,default='0')

class services(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=64,null=True)
    categoria = models.CharField(max_length=64,null=True)
    sub_categoria = models.CharField(max_length=64,null=True)
    unidad_med = models.CharField(max_length=64,null=True)
    precio_venta_sin_igv = models.FloatField(default=0,null=True)
    precio_venta_con_igv = models.FloatField(default=0,null=True)

class ingresos_stock(models.Model):
    id = models.AutoField(primary_key=True)
    producto_id = models.CharField(max_length=32,null=True)
    producto_codigo = models.CharField(max_length=32,null=True)
    producto_nombre = models.CharField(max_length=256,default='')
    almacen =  models.CharField(max_length=32,null=True)
    cantidad = models.CharField(max_length=32,null=True)
    fechaIngreso = models.CharField(max_length=32,null=True)
    vendedorStock = ArrayField(models.CharField(max_length=128),null=True)

class cotizaciones(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    pagoProforma = models.CharField(max_length=30,null=True)
    monedaProforma = models.CharField(max_length=30,null=True)
    fechaProforma = models.CharField(max_length=30,null=True)
    fechaVencProforma = models.CharField(max_length=64,null=True)
    tipoProforma = models.CharField(max_length=32,null=True)
    codigoProforma = models.CharField(max_length=30,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    estadoProforma = models.CharField(max_length=20,null=True)
    imprimirDescuento = models.CharField(max_length=20,null=True)
    imprimirPU = models.CharField(max_length=128,null=True)
    imprimirVU = models.CharField(max_length=128,null=True)
    cantidadCuotas = models.CharField(max_length=64,null=True)
    observacionesCot = models.CharField(max_length=512,null=True)
    nroDocumento = models.CharField(max_length=128,null=True)
    nroCotizacion = models.CharField(max_length=128,null=True)
    serieCotizacion = models.CharField(max_length=128,null=True)
    fecha_emision = models.DateField(null=True)

class guias(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    pagoGuia = models.CharField(max_length=30,null=True)
    monedaGuia = models.CharField(max_length=30,null=True)
    fechaGuia = models.CharField(max_length=30,null=True)
    fechaVencGuia = models.CharField(max_length=30,null=True)
    tipoGuia = models.CharField(max_length=32,null=True)
    codigoGuia = models.CharField(max_length=30,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    estadoGuia = models.CharField(max_length=20,null=True)
    datosTraslado = ArrayField(models.CharField(max_length=64,null=True),null=True)
    datosTransportista = ArrayField(models.CharField(max_length=64,null=True),null=True)
    serieGuia = models.CharField(max_length=64,null=True)
    nroGuia = models.CharField(max_length=64,null=True)
    ubigeoGuia = models.CharField(max_length=64,null=True)
    codigoFactura = models.CharField(max_length=64,null=True)
    idFactura = models.CharField(max_length=64,null=True)
    datosVehiculo = ArrayField(models.CharField(max_length=64),null=True)
    cantidadCuotas = models.CharField(max_length=64,null=True)
    observacionesGuia = models.CharField(max_length=512,null=True)
    nroDocumento = models.CharField(max_length=128,null=True)
    estadoSunat = models.CharField(max_length=128,null=True)
    fecha_emision = models.DateField(null=True)
    

class facturas(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    pagoFactura = models.CharField(max_length=30,null=True)
    monedaFactura = models.CharField(max_length=30,null=True)
    fechaFactura = models.CharField(max_length=30,null=True)
    tipoFactura = models.CharField(max_length=32,null=True)
    codigoFactura = models.CharField(max_length=30,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    estadoFactura = models.CharField(max_length=20,null=True)
    codigoGuia = models.CharField(max_length=32,null=True)
    fechaVencFactura = models.CharField(max_length=32,null=True)
    imprimirDescuento = models.CharField(max_length=20,null=True)
    serieFactura = models.CharField(max_length=64,null=True)
    nroFactura = models.CharField(max_length=64,null=True)
    cuotasFactura = models.CharField(max_length=64,null=True)
    fechasCuotas = ArrayField(models.CharField(max_length=64,null=True),null=True)
    codigosGuias = ArrayField(models.CharField(max_length=128),null=True)
    nroDocumento = models.CharField(max_length=128,null=True)
    estadoSunat = models.CharField(max_length=128,default='')
    fecha_emision = models.DateField(null=True)

class boletas(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    pagoBoleta = models.CharField(max_length=30,null=True)
    monedaBoleta = models.CharField(max_length=30,null=True)
    fechaBoleta = models.CharField(max_length=30,null=True)
    tipoBoleta = models.CharField(max_length=32,null=True)
    codigoBoleta = models.CharField(max_length=30,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    estadoBoleta = models.CharField(max_length=20,null=True)
    codigoGuia = models.CharField(max_length=32,null=True)
    fechaVencBoleta = models.CharField(max_length=32,null=True)
    imprimirDescuento = models.CharField(max_length=20,null=True)
    serieBoleta = models.CharField(max_length=64,null=True)
    nroBoleta = models.CharField(max_length=64,null=True)
    codigosGuias = ArrayField(models.CharField(max_length=128),null=True)
    nroDocumento = models.CharField(max_length=128,null=True)
    estadoSunat = models.CharField(max_length=128,default='')
    fecha_emision = models.DateField(null=True)

class config_docs(models.Model):
    boletaSerie = models.CharField(max_length=128,null=True)
    boletaNro = models.CharField(max_length=128,null=True)
    facturaSerie = models.CharField(max_length=128,null=True)
    facturaNro = models.CharField(max_length=128,null=True)
    guiaSerie = models.CharField(max_length=128,null=True)
    guiaNro = models.CharField(max_length=128,null=True)
    notaSerie = models.CharField(max_length=128,null=True)
    notaNro = models.CharField(max_length=128,null=True)
    notaFactSerie = models.CharField(max_length=128,null=True)
    notaFactNro = models.CharField(max_length=128,null=True)
    cotiSerie = models.CharField(max_length=128,null=True)
    cotiNro = models.CharField(max_length=128,null=True)    
    tokenDoc = models.CharField(max_length=128,default='')

class notaCredito(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    tipoComprobante = models.CharField(max_length=64,null=True)
    serieComprobante = models.CharField(max_length=64,null=True)
    nroComprobante = models.CharField(max_length=64,null=True)
    fechaComprobante = models.CharField(max_length=64,null=True)
    fechaEmision = models.CharField(max_length=64,null=True)
    codigoComprobante = models.CharField(max_length=64,null=True)
    codigoNotaCredito = models.CharField(max_length=64,null=True)
    estadoNotaCredito = models.CharField(max_length=64,null=True)
    serieNota = models.CharField(max_length=64,null=True)
    nroNota = models.CharField(max_length=64,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    monedaNota = models.CharField(max_length=30,null=True)
    imprimirDescuento = models.CharField(max_length=20,null=True)
    tipoItemsNota = models.CharField(max_length=32,null=True)

class regCuenta(models.Model):
    bancoCuenta = models.CharField(max_length=256,default='')
    monedaCuenta = models.CharField(max_length=256,default='SOLES')
    nroCuenta = models.CharField(max_length=256,default='')
    saldoCuenta = models.CharField(max_length=256,default='0')

class regOperacion(models.Model):
    idCuentaBank = models.CharField(max_length=64,default='0')
    fechaOperacion = models.DateField(default=datetime.date.today)
    fechaValuta = models.CharField(max_length=64,default='')
    monedaOperacion = models.CharField(max_length=128,default='SOLES')
    detalleOperacion = models.CharField(max_length=256,default='')
    montoOperacion = models.CharField(max_length=256,default='0')
    saldoOperacion = models.CharField(max_length=256,default='0')
    lugarOperacion = models.CharField(max_length=128,default='0')
    nroOperacion = models.CharField(max_length=64,default='0')
    horaOperacion = models.CharField(max_length=64,default='')
    tipoOperacion = models.CharField(max_length=64,default='EGRESO')
    estadoOperacion = models.CharField(max_length=128,default='IMCOMPLETO')
    clienteOperacion = ArrayField(models.CharField(max_length=256),default=list())
    comprobanteOperacion = ArrayField(models.CharField(max_length=256),default=list())
    guiaOperacion = ArrayField(models.CharField(max_length=256),default=list())
    vendedorOperacion = ArrayField(models.CharField(max_length=256),default=list())
    cotizacionOperacion = ArrayField(models.CharField(max_length=256),default=list())
    usuarioOperacion = models.CharField(max_length=128,default='')
    utcOperacion = models.CharField(max_length=128,default='')
    itfOperacion = models.CharField(max_length=128,default='0')
    cargoOperacion = models.CharField(max_length=128,default='0')