from email.policy import default
import nturl2path
from pyexpat import model
from signal import default_int_handler
from typing_extensions import Required
from unittest.mock import DEFAULT
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.forms import FloatField

# Create your models here.

class Perfiles(User):
    usr_tipo = models.CharField(max_length=64)
    usr_telefono = models.CharField(max_length=64)


class Usuarios(models.Model):
    id = models.AutoField(primary_key=True)
    usr_usuario = models.CharField(max_length=64)
    usr_password = models.CharField(max_length=64)
    usr_email = models.CharField(max_length=64,null=True)
    usr_celular = models.CharField(max_length=64,null=True)
    usr_tipo = models.CharField(max_length=64,null=True)

class Clientes(models.Model):
    id = models.AutoField(primary_key=True)
    cli_nombre = models.CharField(max_length=64,null=True)
    cli_apellido = models.CharField(max_length=64,null=True)
    cli_razon_social = models.CharField(max_length=128,null=True)
    cli_dni = models.CharField(max_length=64,null=True)
    cli_ruc = models.CharField(max_length=64,null=True)
    cli_email = models.CharField(max_length=64,null=True)
    cli_contacto = models.CharField(max_length=64,null=True)
    cli_telefono = models.CharField(max_length=64,null=True)
    cli_department = models.CharField(max_length=64,null=True)
    cli_provincia = models.CharField(max_length=64,null=True)
    cli_distrito = models.CharField(max_length=64,null=True)

class Productos(models.Model):
    id = models.AutoField(primary_key=True)
    pro_nombre = models.CharField(max_length=128,null=True)
    pro_codigo = models.CharField(max_length=128,null=True)
    pro_categoria = models.CharField(max_length=128,null=True)
    pro_sub_categoria = models.CharField(max_length=128,null=True)
    pro_unidad_med = models.CharField(max_length=128,null=True)
    pro_precio_compra_sin_igv = models.FloatField(default=0,null=True)
    pro_precio_compra_con_igv = models.FloatField(default=0,null=True)
    pro_precio_venta_sin_igv = models.FloatField(default=0,null=True)
    pro_precio_venta_con_igv = models.FloatField(default=0,null=True)
    pro_codigo_sunat = models.CharField(max_length=128,null=True)
    pro_moneda = models.CharField(max_length=128,null=True)
    pro_stock = models.IntegerField(null=True,default=0)
    pro_almacen = models.CharField(null=True,max_length=64)

class Servicios(models.Model):
    id = models.AutoField(primary_key=True)
    ser_nombre = models.CharField(max_length=64,null=True)
    ser_categoria = models.CharField(max_length=64,null=True)
    ser_sub_categoria = models.CharField(max_length=64,null=True)
    ser_unidad_med = models.CharField(max_length=64,null=True)
    ser_precio_venta_sin_igv = models.FloatField(default=0,null=True)
    ser_precio_venta_con_igv = models.FloatField(default=0,null=True)

class Proformas(models.Model):
    id = models.AutoField(primary_key=True)
    prof_cliente = ArrayField(models.CharField(max_length=64),null=True)
    prof_fecha = models.CharField(max_length=64,null=True)
    prof_valor_total = models.FloatField(default=0,null=True)
    prof_estado = models.CharField(max_length=64,default='NoGenerada',null=True)
    prof_productos = ArrayField(ArrayField(models.CharField(max_length=64)),null=True)
    prof_descuentos = ArrayField(models.FloatField(default=0),null=True)
    prof_vendedor = ArrayField(models.CharField(max_length=64),null=True)
    prof_tipo_cambio = models.FloatField(default=0,null=True)

class Guias(models.Model):
    id = models.AutoField(primary_key=True)
    gui_cliente = ArrayField(models.CharField(max_length=64))
    gui_codigo = models.CharField(max_length=64,null=True)
    gui_fecha = models.CharField(max_length=64,null=True)
    gui_valor_total = models.FloatField()
    gui_estado = models.CharField(max_length=64,null=True)
    gui_descuentos = ArrayField(models.FloatField(default=0),null=True)
    gui_productos = ArrayField(ArrayField(models.CharField(max_length=64)))
    gui_tipo_cambio = models.FloatField(default=0,null=True)

class Facturas(models.Model):
    id = models.AutoField(primary_key=True)
    fac_cliente = ArrayField(models.CharField(max_length=64))
    fac_fecha = models.CharField(max_length=64)
    fac_valor_total = models.FloatField()
    fac_estado = models.CharField(max_length=64)
    fac_productos = ArrayField(ArrayField(models.CharField(max_length=64)))
    fac_descuentos = ArrayField(models.CharField(max_length=64),null=True)
    fac_condi_pago = models.CharField(max_length=64,null=True)
    fac_fecha_vencimiento = models.CharField(max_length=64,null=True)
    fac_gui_codigo = models.CharField(max_length=64,null=True)
    fac_codigo = models.CharField(max_length=64,null=True)
    fac_tipo_cambio = models.FloatField(default=0,null=True)

class FileUpload(models.Model):
    file=models.FileField(upload_to='archivos')