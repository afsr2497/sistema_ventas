from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
import datetime
from django.utils import timezone

# Create your models here.

class FileUpload(models.Model):
    file=models.FileField(upload_to='archivos')

class userProfile(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)
    rolesUsuario = ArrayField(models.CharField(max_length=64),default=['1','1','1','1'])
    descuento_maximo = models.CharField(max_length=24,default='0')

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
    direccion_fiscal = models.CharField(max_length=512,default='SinDireccion')
    direcciones = ArrayField(models.CharField(max_length=256),null=True)
    habilitado_comisiones = models.CharField(max_length=8,default='1')
    tipo_cliente = models.CharField(max_length=8,default='S')
    max_endeudamiento = models.CharField(max_length=32,default='0')

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
    kpi_info = models.CharField(max_length=128,default='0')
    producto_kit = models.CharField(max_length=12, default='0')
    producto_A = ArrayField(models.CharField(max_length=64),default=list())
    producto_B = ArrayField(models.CharField(max_length=64),default=list())
    producto_C = ArrayField(models.CharField(max_length=64),default=list())
    producto_D = ArrayField(models.CharField(max_length=64),default=list())
    producto_E = ArrayField(models.CharField(max_length=64),default=list())

class kitsProductos(models.Model):
    productos = models.ManyToManyField(products)

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
    stock_anterior = models.CharField(max_length=32,default='0')
    nuevo_stock = models.CharField(max_length=32,default='0')
    fechaIngreso = models.CharField(max_length=32,null=True)
    fecha_emision = models.DateField(default=datetime.date.today)
    vendedorStock = ArrayField(models.CharField(max_length=128),null=True)
    operacionIngreso = models.CharField(max_length=64,default='Ingreso productos')
    referencia = models.CharField(max_length=64,default='Ingreso')

class egreso_stock(models.Model):
    id = models.AutoField(primary_key=True)
    producto_id = models.CharField(max_length=32,null=True)
    producto_codigo = models.CharField(max_length=32,null=True)
    producto_nombre = models.CharField(max_length=256,default='')
    almacen =  models.CharField(max_length=32,null=True)
    cantidad = models.CharField(max_length=32,null=True)
    stock_anterior = models.CharField(max_length=32,default='0')
    nuevo_stock = models.CharField(max_length=32,default='0')
    fechaIngreso = models.CharField(max_length=32,null=True)
    fecha_emision = models.DateField(default=datetime.date.today)
    vendedorStock = ArrayField(models.CharField(max_length=128),null=True)
    operacionIngreso = models.CharField(max_length=64,default='Egreso productos')
    referencia = models.CharField(max_length=64,default='Egreso')

class cotizaciones(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
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
    fecha_emision = models.DateField(default=datetime.date.today)
    fecha_vencReg = models.DateField(default=datetime.date.today)
    registroCoti = models.CharField(max_length=64,default='0')
    cred_dias = models.CharField(max_length=64,default='0')
    validez_dias = models.CharField(max_length=64,default='7')
    mostrarCabos = models.CharField(max_length=64,default='0')
    mostrarPanhos = models.CharField(max_length=64,default='0')
    nombresColumnas = ArrayField(models.CharField(max_length=64,default=''),default=list())

class guias(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
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
    cotiRelacionada = models.CharField(max_length=128,default='')
    origenGuia = ArrayField(models.CharField(max_length=512,default=''),default=list())
    

class facturas(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
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
    codigosGuias = ArrayField(models.CharField(max_length=128),default=list())
    nroDocumento = models.CharField(max_length=128,null=True)
    estadoSunat = models.CharField(max_length=128,default='')
    fecha_emision = models.DateField(null=True)
    registroFactura = models.CharField(max_length=64,default='0')
    codigosCotis = ArrayField(models.CharField(max_length=128),default=list())
    facturaPagada = models.CharField(max_length=64,default='0')
    stockAct = models.CharField(max_length=64,default='0')
    observacionFactura = models.CharField(max_length=512,default='Sin Observacion')

class boletas(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
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
    registroBoleta = models.CharField(max_length=64,default='0')
    stockAct = models.CharField(max_length=64,default='0')
    codigosCotis = ArrayField(models.CharField(max_length=128),default=list())
    boletaPagada = models.CharField(max_length=64,default='0')

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
    almacenesSistema = ArrayField(models.CharField(max_length=256),default=list())
    almacenesDescuento = ArrayField(models.CharField(max_length=256),default=list())
    tipoCambio = models.CharField(max_length=8, default='0')

class notaCredito(models.Model):
    cliente = ArrayField(models.CharField(max_length=256),null=True)
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    servicios = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    vendedor = ArrayField(models.CharField(max_length=30),null=True)
    tipoComprobante = models.CharField(max_length=64,null=True)
    serieComprobante = models.CharField(max_length=64,null=True)
    nroComprobante = models.CharField(max_length=64,null=True)
    fechaComprobante = models.CharField(max_length=64,null=True)
    fechaEmision = models.DateField(default=datetime.date.today)
    codigoComprobante = models.CharField(max_length=64,null=True)
    codigoNotaCredito = models.CharField(max_length=64,null=True)
    estadoNotaCredito = models.CharField(max_length=64,null=True)
    serieNota = models.CharField(max_length=64,null=True)
    nroNota = models.CharField(max_length=64,null=True)
    tipoCambio = ArrayField(models.CharField(max_length=64),null=True)
    monedaNota = models.CharField(max_length=30,null=True)
    imprimirDescuento = models.CharField(max_length=20,null=True)
    tipoItemsNota = models.CharField(max_length=32,null=True)
    modoNota = models.CharField(max_length=64,default='DEVOLUCION_TOTAL')
    estadoSunat = models.CharField(max_length=32,default='SinComprobar')
    stockAct = models.CharField(max_length=32,default="0")

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
    clienteExcel = models.CharField(max_length=256,default='')
    referencia2 = models.CharField(max_length=256,default='')
    conectado_abono = models.CharField(max_length=64,default='0')

class abonosOperacion(models.Model):
    datos_banco = ArrayField(models.CharField(max_length=128),default=list())
    datos_cliente = ArrayField(models.CharField(max_length=128),default=list())
    nro_operacion = models.CharField(max_length=64,default='')
    nro_operacion_2 = models.CharField(max_length=64,default='')
    codigo_comprobante = models.CharField(max_length=64,default='')
    codigo_guia = models.CharField(max_length=64,default='')
    codigo_coti = models.CharField(max_length=64,default='')
    codigo_vendedor = models.CharField(max_length=64,default='')
    conectado = models.CharField(max_length=64,default='0')
    idRegistroOp = models.CharField(max_length=64,default='0')
    comprobanteCancelado = models.CharField(max_length=64,default='PENDIENTE')
    fechaAbono = models.DateField(default=datetime.date.today)
    abono_comisionable = models.CharField(max_length=12,default='1')

class inventariosProductos(models.Model):
    fechaInventario = models.DateField(default=timezone.now)
    usuarioInventario = ArrayField(models.CharField(max_length=64),default=list())
    estadoInventario = models.CharField(max_length=128,default='Revision')
    ubicacionArchivo = models.FileField(upload_to='media/')
    codigoInventario = models.CharField(max_length=64,default='INV-0000')
    almacenInventario = models.CharField(max_length=64,default='Chimbote')

class ubigeoDistrito(models.Model):
    distritoUbigeo = models.CharField(max_length=256,default='')
    codigoUbigeo = models.CharField(max_length=256,default='')

class ordenCompra(models.Model):
    fechaOrden = models.DateField(default=datetime.date.today)
    proveedorCodigo = models.CharField(max_length=64,default='000000')
    proveedorNombre = models.CharField(max_length=64,default='')
    usuarioOrden = models.CharField(max_length=64,default='')
    monedaOrden = models.CharField(max_length=64,default='SOLES')
    productos = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    direccion = models.CharField(max_length=64,default='')
    destino = models.CharField(max_length=64,default='')
    ruc_proveedor = models.CharField(max_length=64,default='')
    codigo_orden = models.CharField(max_length=64,default='')
    estado_orden = models.CharField(max_length=64,default='')

class ordenCompraMetalprotec(models.Model):
    rucProveedor = models.CharField(default='',max_length=32)
    fechaEmision = models.DateField(default=datetime.date.today)
    condicionOrden = models.CharField(default='',max_length=32)
    codigoOrden = models.CharField(default='',max_length=32)
    direccionProveedor = models.CharField(default='',max_length=128)
    nombreProveedor = models.CharField(default='',max_length=64)
    ciudadCliente = models.CharField(default='',max_length=32)
    destinoCliente = models.CharField(default='',max_length=128)
    atencionCliente = models.CharField(default='',max_length=64)
    monedaOrden = models.CharField(default='SOLES',max_length=24)
    productosOrden = ArrayField(ArrayField(models.CharField(max_length=64)),default=list())
    tcCompraOrden = models.CharField(max_length=8,default='0.000')
    tcVentaOrden = models.CharField(max_length=8,default='0.000')
    mostrarDescuento = models.CharField(max_length=8,default='0')
    mostrarVU = models.CharField(max_length=8,default='0')

class configurarComisiones(models.Model):
    porcentajeComision = models.CharField(max_length=8,default='0')
    incluyeIgv = models.CharField(max_length=8,default='0')
    usuarioRelacionado = models.ForeignKey(User,on_delete=models.CASCADE)
    fechaRegistro = models.DateField(default=datetime.datetime.today)
    tipoComision = models.CharField(max_length=32,default='PARCIAL')
    usuariosComision = ArrayField(ArrayField(models.CharField(max_length=32)),default=list())
    codigoComision = models.CharField(max_length=32,default='COM-0000')

class departamentoCosto(models.Model):
    nombreDepartamento = models.CharField(max_length=64,default='')

    def __str__(self):
        return self.nombreDepartamento

class categoriaCosto(models.Model):
    nombreCategoria = models.CharField(max_length=64, default='')
    departamentoAsociado = models.ForeignKey(departamentoCosto, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombreCategoria

class divisionCosto(models.Model):
    categoriaAsociada = models.ForeignKey(categoriaCosto, on_delete=models.CASCADE)
    nombreDivision = models.CharField(max_length=64, default='')
    tipoCosto = models.CharField(max_length=16, default='')
    comportamientoCosto = models.CharField(max_length=16, default='')
    operativoCosto = models.CharField(max_length=8, default='')

    def __str__(self):
        return self.nombreDivision


class cajaChica(models.Model):
    conceptoCaja = models.CharField(max_length=32, default='')
    valorRegistrado = models.CharField(max_length=32,default='0')
    fechaCreacion = models.DateField(default=datetime.datetime.today)
    monedaCaja = models.CharField(default='SOLES',max_length=16)

def get_default_caja():
        return cajaChica.objects.get(conceptoCaja='Caja-0').id

class registroCosto(models.Model):    
    divisionRelacionada = models.ForeignKey(divisionCosto, on_delete=models.CASCADE)
    cajaRelacionada = models.ForeignKey(cajaChica, on_delete=models.SET_NULL,null=True,default=get_default_caja)
    fechaCosto = models.DateField(default=datetime.date.today)
    documentoCosto = models.CharField(max_length=16, default='')
    rucCosto = models.CharField(max_length=16, default='')
    razonCosto = models.CharField(max_length=64, default='')
    conceptoCosto = models.CharField(max_length=64, default='')
    importeCosto = models.CharField(max_length=16, default='')
    monedaCosto = models.CharField(max_length=16, default='')

class ingresosCaja(models.Model):
    fechaIngreso = models.DateField(default=datetime.datetime.today)
    valorIngresado = models.CharField(max_length=32,default='0')
    conceptoIngreso = models.CharField(max_length=64,default='')
    cajaRelacionada = models.ForeignKey(cajaChica,on_delete=models.CASCADE)