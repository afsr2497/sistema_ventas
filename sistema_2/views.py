from distutils.log import info
from itertools import product
import math
from datetime import datetime,timedelta
from optparse import AmbiguousOptionError
from tokenize import Number
from dateutil.relativedelta import relativedelta
from distutils.command.config import config
from django.contrib.auth.models import User
from django.db.models import F
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django import forms
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from .models import clients, products, services, userProfile, cotizaciones, ingresos_stock, guias, facturas, boletas, config_docs, notaCredito, regOperacion, regCuenta, abonosOperacion
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from django.db.models import Q
from reportlab.lib.pagesizes import A4
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
from django.views.decorators.csrf import csrf_exempt
import time
from base64 import b64decode
from django.contrib.auth.decorators import login_required
from decimal import Decimal,getcontext
from dateutil.parser import parse
import random
import requests
import traceback
import sys
from apis_net_pe import ApisNetPe
import openpyxl

APIS_TOKEN = "apis-token-1.aTSI1U7KEuT-6bbbCguH-4Y8TI6KS73N"
api_consultas = ApisNetPe(APIS_TOKEN)
getcontext().prec = 10

null = None


class authen_form(forms.Form):
    user = forms.CharField(label='Username',required=True)
    user_psw = forms.CharField(label='Password',widget=forms.PasswordInput(),required=True)

# Create your views here.
@login_required(login_url='/sistema_2')
@csrf_exempt
def ingresos(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ing = ingresos_stock.objects.all()
    return render(request,'sistema_2/ingresos.html',{
        'ing': ing.order_by('-id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def dashboard(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    return render(request,'sistema_2/dashboard.html',{
        'usr_rol': user_logued,
    })

def login_view(request):
    if request.method == "POST":
        usuario_sistema = request.POST.get("user")
        password_sistema = request.POST.get("user_psw")
        usuario = authenticate(request,username=usuario_sistema,password=password_sistema)
        if usuario is not None:
            login(request, usuario)
            return HttpResponseRedirect("dashboard")
        else:
            return render(request,'sistema_2/log_in.html',{
                "message": "DATOS INVALIDOS!",
            })

    return render(request,'sistema_2/log_in.html')

def log_out(request):
    logout(request)
    return render(request,'sistema_2/log_in.html',{
        'form': authen_form()
    })

@login_required(login_url='/sistema_2')
def usuarios(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        mensaje = ''
        usuario_nombre = request.POST.get('usuario')
        usuario_contra = request.POST.get('contra')
        usuario_email = request.POST.get('email')
        usuario_tipo = request.POST.get('tipo')
        usuario_celular = request.POST.get('celular')
        ultimo_usuario = userProfile.objects.latest('id')
        id_final = ultimo_usuario.id
        ultimo_usuario.save()
        id_nuevo = int(id_final) + 1
        usuario_nombre = usuario_nombre.lower().title()
        indicador_nombre = 0
        if(len(User.objects.filter(username=usuario_nombre))>0):
            indicador_nombre = 1
            mensaje = mensaje + 'El nombre de usuario ya existe. '
        indicador_email = 0
        if(len(User.objects.filter(email=usuario_email))>0):
            indicador_email = 1
            mensaje = mensaje + 'El email ya esta asociado a otro usuario. '
        indicador_celular = 0
        if(len(userProfile.objects.filter(celular=usuario_celular))>0):
            indicador_celular = 1
            mensaje = mensaje + 'El numero de telefono ya se encuentra asociado a otro usuario.'
        
        if indicador_nombre == 0 and indicador_email == 0 and indicador_celular == 0:
            codigo_nuevo = 'USR-' + str(id_nuevo)
            usuario_django = User.objects.create_user(username=usuario_nombre,password=usuario_contra,email=usuario_email)
            usuario_django.save()
            usuario_nuevo = userProfile(id=id_nuevo,usuario=usuario_django,codigo=codigo_nuevo,tipo=usuario_tipo,celular=usuario_celular)
            usuario_nuevo.save()
            mensaje = 'Usuario creador satisfactoriamente'
            return render(request,'sistema_2/usuarios.html',{
                'usr': usr.order_by('id'),
                'mensaje':mensaje,
                'usuario_logued':str(user_logued.tipo),
                'usr_rol': user_logued,
            })
        else:
            return render(request,'sistema_2/usuarios.html',{
                'usr': usr.order_by('id'),
                'mensaje':mensaje,
                'usuario_logued':str(user_logued.tipo),
                'usr_rol': user_logued,
            })

    return render(request,'sistema_2/usuarios.html',{
        'usr': usr.order_by('id'),
        'usuario_logued':str(user_logued.tipo),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_usuario(request,ind):
    usuario_eliminar = userProfile.objects.get(id=ind)
    if usuario_eliminar.usuario.username == 'Admin':
        return HttpResponseRedirect(reverse('sistema_2:usuarios'))
    else:
        usuario_eliminar.usuario.delete()
        usuario_eliminar.delete()
        return HttpResponseRedirect(reverse('sistema_2:usuarios'))

def actualizar_usuario(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        mensaje = ''
        usuario_actualizar = userProfile.objects.get(id=ind)
        usuario_username = request.POST.get('usuario')
        usuario_email = request.POST.get('email')
        usuario_tipo = request.POST.get('tipo')
        usuario_celular = request.POST.get('celular')
        usuario_contra = request.POST.get('contra')

        usuario_username = usuario_username.lower().title()

        if(usuario_actualizar.usuario.username == usuario_username):
            indicador_nombre = 0
        else:
            indicador_nombre = 0
            if(len(User.objects.filter(username=usuario_username))>0):
                indicador_nombre = 1
                mensaje = mensaje + 'El nombre de usuario ya existe. '
        
        if(usuario_actualizar.usuario.email == usuario_email):
            indicador_email=0
        else:
            indicador_email = 0
            if(len(User.objects.filter(email=usuario_email))>0):
                indicador_email = 1
                mensaje = mensaje + 'El email ya esta asociado a otro usuario. '
            
        if(usuario_actualizar.celular == usuario_celular):
            indicador_celular = 0
        else:
            indicador_celular = 0
            if(len(userProfile.objects.filter(celular=usuario_celular))>0):
                indicador_celular = 1
                mensaje = mensaje + 'El numero de telefono ya se encuentra asociado a otro usuario.'

        if indicador_nombre == 0 and indicador_email == 0 and indicador_celular == 0:
            usuario_django = usuario_actualizar.usuario
            usuario_django.username = usuario_username
            usuario_django.email = usuario_email
            if usuario_contra != '':
                print(usuario_contra)
                usuario_django.set_password(usuario_contra)
            usuario_django.save()
            usuario_actualizar.tipo = usuario_tipo
            usuario_actualizar.celular = usuario_celular
            usuario_actualizar.save()
            mensaje = 'Usuario actualizado satisfactoriamente'
            user_logued = userProfile.objects.get(usuario=usuario_logued)
            return render(request,'sistema_2/usuarios.html',{
                'usr': userProfile.objects.all().order_by('id'),
                'mensaje':mensaje,
                'usuario_logued':str(user_logued.tipo),
                'usr_rol': user_logued,
            })
        else:
            return render(request,'sistema_2/usuarios.html',{
                'usr': userProfile.objects.all().order_by('id'),
                'mensaje':mensaje,
                'usuario_logued':str(user_logued.tipo),
                'usr_rol': user_logued,
            })
    return render(request,'sistema_2/usuarios.html',{
            'usr': userProfile.objects.all().order_by('id'),
            'mensaje':mensaje,
            'usuario_logued':str(user_logued.tipo),
            'usr_rol': user_logued,
        })

@login_required(login_url='/sistema_2')
def servicios(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ser = services.objects.all()
    if request.method == 'POST':
        print(request)
        print(request.POST)
        servicio_nombre = request.POST.get('nombre')
        servicio_categoria = request.POST.get('categoria')
        servicio_subCategoria = request.POST.get('subCategoria')
        servicio_unidad = request.POST.get('unidadMed')
        servicio_pvsinIGV = round(float(request.POST.get('pvsinIGV')),2)
        servicio_pvconIGV = round(servicio_pvsinIGV*1.18,2)
        try:
            ultimo_servicio = services.objects.latest('id')
            servicio_id = int(ultimo_servicio.id) + 1
        except:
            servicio_id = 1
        services(id=servicio_id,nombre=servicio_nombre,categoria=servicio_categoria,sub_categoria=servicio_subCategoria,unidad_med=servicio_unidad,precio_venta_sin_igv=servicio_pvsinIGV,precio_venta_con_igv=servicio_pvconIGV).save()
        return HttpResponseRedirect(reverse('sistema_2:servicios'))
    return render(request,'sistema_2/servicios.html',{
        'ser': ser.order_by('id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_servicio(request,ind):
    servicio_eliminar = services.objects.get(id=ind)
    servicio_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:servicios'))


def actualizar_servicio(request,ind):
    if request.method == 'POST':
        servicio_actualizar = services.objects.get(id=ind)
        servicio_nombre = request.POST.get('nombre')
        servicio_categoria = request.POST.get('categoria')
        servicio_sub_categoria = request.POST.get('subCategoria')
        servicio_unidad = request.POST.get('unidadMed')
        servicio_pvsinIGV = round(float(request.POST.get('pvsinIGV')),2)
        servicio_pvconIGV = round(servicio_pvsinIGV*1.18,2)
        servicio_actualizar.nombre = servicio_nombre
        servicio_actualizar.categoria = servicio_categoria
        servicio_actualizar.sub_categoria = servicio_sub_categoria
        servicio_actualizar.unidad_med = servicio_unidad
        servicio_actualizar.precio_venta_sin_igv = servicio_pvsinIGV
        servicio_actualizar.precio_venta_con_igv = servicio_pvconIGV
        servicio_actualizar.save()
        return HttpResponseRedirect(reverse('sistema_2:servicios'))
    return HttpResponseRedirect(reverse('sistema_2:servicios'))

def importar_servicios(request):
    if request.method == 'POST':
        columnas_servicio = ['NOMBRE','CATEGORIA','SUBCATEGORIA','UNIDAD','PRECIO VENTA']
        archivo=request.FILES['MyFile']
        identificador = 0
        try:
            datos_archivo = pd.read_excel(archivo)
            datos_archivo = datos_archivo.replace(np.nan,'',regex=True)
            identificador = 1
        except:
            identificador = 0
        if identificador == 1:
            mensaje = 'Es un archivo de excel'
            identificador = 0
            if len(datos_archivo.columns) == len(columnas_servicio):
                mensaje = 'Archivo y columnas correctas'
                identificador = 0
                for columna in datos_archivo.columns:
                    if not (columna in columnas_servicio):
                        identificador = 1
                if identificador == 1:
                    mensaje = 'Las columnas del archivo no son las apropiadas'
                else: 
                    mensaje = 'Las columnas del archivo cumplen con los requerimientos'
                    i = 0
                    while i < len(datos_archivo):
                        dat_nombre = datos_archivo.loc[i,'NOMBRE']
                        dat_categoria = datos_archivo.loc[i,'CATEGORIA']
                        dat_sub_categoria = datos_archivo.loc[i,'SUBCATEGORIA']
                        dat_unidad_med = datos_archivo.loc[i,'UNIDAD']
                        dat_precio_venta_sin_igv = datos_archivo.loc[i,'PRECIO VENTA']
                        if dat_precio_venta_sin_igv == '':
                            dat_precio_venta_sin_igv = 0.0
                        else:
                            dat_precio_venta_sin_igv = round(float(dat_precio_venta_sin_igv),2)
                        dat_precio_venta_con_igv = round(dat_precio_venta_sin_igv*1.18,2)
                        try:
                            ultimo_servicio = services.objects.latest('id')
                            dat_id = ultimo_servicio.id + 1
                        except:
                            dat_id = 1
                        services(id=dat_id,nombre=dat_nombre,categoria=dat_categoria,sub_categoria=dat_sub_categoria,unidad_med=dat_unidad_med,precio_venta_sin_igv=dat_precio_venta_sin_igv,precio_venta_con_igv=dat_precio_venta_con_igv).save()
                        i = i+1
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return HttpResponseRedirect(reverse('sistema_2:servicios'))

@login_required(login_url='/sistema_2')
def clientes(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    cli = clients.objects.all()
    if request.method == 'POST':
        cliente_nombre = request.POST.get('nombre')
        cliente_apellido = request.POST.get('apellido')
        cliente_razon = request.POST.get('razon')
        cliente_dni = request.POST.get('dni')
        cliente_ruc = request.POST.get('ruc')
        cliente_email = request.POST.get('email')
        cliente_contacto = request.POST.get('contacto')
        cliente_telefono = request.POST.get('telefono')
        cliente_direccion = request.POST.get('direccion')
        try:
            ultimo_cliente = clients.objects.latest('id')
            cliente_id = int(ultimo_cliente.id) + 1
        except:
            cliente_id = 1
        clients(id=cliente_id,nombre=cliente_nombre,apellido=cliente_apellido,razon_social=cliente_razon,dni=cliente_dni,ruc=cliente_ruc,email=cliente_email,contacto=cliente_contacto,telefono=cliente_telefono,direccion_fiscal=cliente_direccion).save()
        return HttpResponseRedirect(reverse('sistema_2:clientes'))
    return render(request,'sistema_2/clientes.html',{
        'cli': cli.order_by('id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_cliente(request,ind):
    cliente_eliminar = clients.objects.get(id=ind)
    cliente_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:clientes'))

def actualizar_cliente(request,ind):
    if request.method == 'POST':
        cliente_actualizar = clients.objects.get(id=ind)
        cliente_nombre = request.POST.get('nombre')
        cliente_apellido = request.POST.get('apellido')
        cliente_razon = request.POST.get('razon')
        cliente_dni = request.POST.get('dni')
        cliente_ruc = request.POST.get('ruc')
        cliente_email = request.POST.get('email')
        cliente_contacto = request.POST.get('contacto')
        cliente_telefono = request.POST.get('telefono')
        cliente_direccion = request.POST.get('direccion')
        cliente_actualizar.nombre = cliente_nombre
        cliente_actualizar.apellido = cliente_apellido
        cliente_actualizar.razon_social = cliente_razon
        cliente_actualizar.dni = cliente_dni
        cliente_actualizar.ruc = cliente_ruc
        cliente_actualizar.email = cliente_email
        cliente_actualizar.contacto = cliente_contacto
        cliente_actualizar.telefono = cliente_telefono
        cliente_actualizar.direccion_fiscal = cliente_direccion
        cliente_actualizar.save()
        return HttpResponseRedirect(reverse('sistema_2:clientes'))
    return HttpResponseRedirect(reverse('sistema_2:clientes'))

def importar_clientes(request):
    if request.method == 'POST':
        columnas_cliente = ['NOMBRE','APELLIDO','RAZON SOCIAL','DNI','RUC','EMAIL','CONTACTO','TELEFONO']
        archivo=request.FILES['MyFile']
        identificador = 0
        try:
            datos_archivo = pd.read_excel(archivo)
            datos_archivo = datos_archivo.replace(np.nan,'',regex=True)
            identificador = 1
        except:
            identificador = 0
        if identificador == 1:
            mensaje = 'Es un archivo de excel'
            identificador = 0
            if len(datos_archivo.columns) == len(columnas_cliente):
                mensaje = 'Archivo y columnas correctas'
                identificador = 0
                for columna in datos_archivo.columns:
                    if not (columna in columnas_cliente):
                        identificador = 1
                if identificador == 1:
                    mensaje = 'Las columnas del archivo no son las apropiadas'
                else: 
                    mensaje = 'Las columnas del archivo cumplen con los requerimientos'
                    i = 0
                    while i < len(datos_archivo):
                        dat_nombre = datos_archivo.loc[i,'NOMBRE']
                        dat_apellido = datos_archivo.loc[i,'APELLIDO']
                        dat_razon_social = datos_archivo.loc[i,'RAZON SOCIAL']
                        dat_dni_int = str(datos_archivo.loc[i,'DNI'])
                        dat_dni = dat_dni_int.split('.')[0]
                        dat_ruc_int = str(datos_archivo.loc[i,'RUC'])
                        dat_ruc = dat_ruc_int.split('.')[0]
                        dat_email = datos_archivo.loc[i,'EMAIL']
                        dat_contacto = datos_archivo.loc[i,'CONTACTO']
                        dat_telefono_int = str(datos_archivo.loc[i,'TELEFONO'])
                        dat_telefono = dat_telefono_int.split('.')[0]
                        try:
                            ultimo_cliente = clients.objects.latest('id')
                            dat_id = ultimo_cliente.id + 1
                        except:
                            dat_id = 1
                        clients(id=dat_id,nombre=dat_nombre,apellido=dat_apellido,razon_social=dat_razon_social,dni=dat_dni,ruc=dat_ruc,email=dat_email,contacto=dat_contacto,telefono=dat_telefono).save()
                        i = i+1
                        print(dat_id)
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        cli = clients.objects.all()
        return HttpResponseRedirect(reverse('sistema_2:clientes'))
    return HttpResponseRedirect(reverse('sistema_2:clientes'))

def agregar_direcciones(request,ind):
    cliente_actualizar = clients.objects.get(id=ind)
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        if cliente_actualizar.direcciones is None:
            cliente_actualizar.direcciones = []
        cliente_actualizar.direcciones.append(direccion)
        cliente_actualizar.save()
        return HttpResponseRedirect(reverse('sistema_2:clientes'))
    return HttpResponseRedirect(reverse('sistema_2:clientes'))

@login_required(login_url='/sistema_2')
def productos(request):
    pro = products.objects.all().order_by('id')
    usr = userProfile.objects.all().order_by('id')
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    productos_totales = products.objects.all().order_by('id')
    if request.method == 'POST':
        if 'Crear' in request.POST:
            producto_nombre = request.POST.get('nombre')
            producto_codigo = request.POST.get('codigo')
            producto_categoria = request.POST.get('categoria')
            producto_subCategoria = request.POST.get('subCategoria')
            producto_unidad = request.POST.get('unidadMed')
            producto_sunat = request.POST.get('codSunat')
            producto_peso = str(request.POST.get('pesoProducto'))
            producto_pvsinIGV = round(float(request.POST.get('pvsinIGV')),2)
            producto_pvconIGV = round(producto_pvsinIGV*1.18,2)
            producto_pcsinIGV = round(float(request.POST.get('pcsinIGV')),2)
            producto_pcconIGV = round(producto_pcsinIGV*1.18,2)
            producto_moneda = request.POST.get('moneda')
            try:
                ultimo_producto = products.objects.latest('id')
                producto_id = int(ultimo_producto.id) + 1
            except:
                producto_id = 1
            products(pesoProducto=producto_peso,id=producto_id,nombre=producto_nombre,codigo=producto_codigo,categoria=producto_categoria,sub_categoria=producto_subCategoria,unidad_med=producto_unidad,precio_compra_sin_igv=producto_pcsinIGV,precio_compra_con_igv=producto_pcconIGV,precio_venta_sin_igv=producto_pvsinIGV,precio_venta_con_igv=producto_pvconIGV,codigo_sunat=producto_sunat,moneda=producto_moneda).save()
            return HttpResponseRedirect(reverse('sistema_2:productos'))
        elif 'Filtrar' in request.POST:
            filtro_categoria = request.POST.get('filtroCategoria')
            productos_totales = productos_totales.filter(categoria__icontains=filtro_categoria)
    return render(request,'sistema_2/prods.html',{
        'pro': pro,
        'usr':usr,
        'pro_tabla':productos_totales,
        'user_logued':user_logued,
        'usr_rol': user_logued,
    })

def eliminar_producto(request,ind):
    producto_eliminar = products.objects.get(id=ind)
    producto_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:productos'))

def actualizar_producto(request,ind):
    if request.method == 'POST':
        producto_actualizar = products.objects.get(id=ind)
        producto_nombre = request.POST.get('nombre')
        producto_codigo = request.POST.get('codigo')
        producto_categoria = request.POST.get('categoria')
        producto_subCategoria = request.POST.get('subCategoria')
        producto_unidad = request.POST.get('unidadMed')
        producto_sunat = request.POST.get('codSunat')
        producto_peso = str(request.POST.get('pesoProducto'))
        producto_pvsinIGV = round(float(request.POST.get('pvsinIGV')),2)
        producto_pvconIGV = round(producto_pvsinIGV*1.18,2)
        producto_pcsinIGV = round(float(request.POST.get('pcsinIGV')),2)
        producto_pcconIGV = round(producto_pcsinIGV*1.18,2)
        producto_moneda = request.POST.get('moneda')
        producto_actualizar.nombre = producto_nombre
        producto_actualizar.codigo = producto_codigo
        producto_actualizar.categoria = producto_categoria
        producto_actualizar.sub_categoria = producto_subCategoria
        producto_actualizar.unidad_med = producto_unidad
        producto_actualizar.codigo_sunat = producto_sunat
        producto_actualizar.pesoProducto = producto_peso
        producto_actualizar.moneda = producto_moneda
        producto_actualizar.precio_venta_sin_igv = producto_pvsinIGV
        producto_actualizar.precio_venta_con_igv = producto_pvconIGV
        producto_actualizar.precio_compra_sin_igv = producto_pcsinIGV
        producto_actualizar.precio_compra_con_igv = producto_pcconIGV
        producto_actualizar.save()
        return HttpResponseRedirect(reverse('sistema_2:productos'))
    return HttpResponseRedirect(reverse('sistema_2:productos'))

def importar_productos(request):
    if request.method == 'POST':
        columnas_producto = ['CATEGORIA','SUBCATEGORIA','COD PERCAMAR','COD SUNAT','PRODUCTO','UNIDAD','MONEDA','PRECIO COMPRA','PRECIO COMPRA + IGV','PRECIO VENTA','PRECIO VENTA + IGV']
        archivo=request.FILES['MyFile']
        identificador = 0
        try:
            datos_archivo = pd.read_excel(archivo)
            datos_archivo = datos_archivo.replace(np.nan,'',regex=True)
            identificador = 1
        except:
            identificador = 0
        if identificador == 1:
            mensaje = 'Es un archivo de excel'
            identificador = 0
            if len(datos_archivo.columns) == len(columnas_producto):
                mensaje = 'Archivo y columnas correctas'
                identificador = 0
                for columna in datos_archivo.columns:
                    if not (columna in columnas_producto):
                        identificador = 1
                if identificador == 1:
                    mensaje = 'Las columnas del archivo no son las apropiadas'
                else: 
                    mensaje = 'Las columnas del archivo cumplen con los requerimientos'
                    i = 0
                    while i < len(datos_archivo):
                        dat_categoria = datos_archivo.loc[i,'CATEGORIA']
                        dat_sub_categoria = datos_archivo.loc[i,'SUBCATEGORIA']
                        dat_codigo_int = str(datos_archivo.loc[i,'COD PERCAMAR'])
                        dat_codigo = dat_codigo_int.split('.')[0]
                        dat_codigo_sunat_int = str(datos_archivo.loc[i,'COD SUNAT'])
                        dat_codigo_sunat = dat_codigo_sunat_int.split('.')[0]
                        dat_nombre = datos_archivo.loc[i,'PRODUCTO']
                        dat_unidad_med = datos_archivo.loc[i,'UNIDAD']
                        dat_moneda = datos_archivo.loc[i,'MONEDA']
                        dat_precio_compra_sin_igv = datos_archivo.loc[i,'PRECIO COMPRA']
                        if dat_precio_compra_sin_igv == '':
                            dat_precio_compra_sin_igv = round(0.0,2)
                        else:
                            dat_precio_compra_sin_igv = round(float(dat_precio_compra_sin_igv),2)
                        dat_precio_compra_con_igv = datos_archivo.loc[i,'PRECIO COMPRA + IGV']
                        if dat_precio_compra_con_igv == '':
                            dat_precio_compra_con_igv = 0.0
                        else:
                            dat_precio_compra_con_igv = round(float(dat_precio_compra_con_igv),2)
                        dat_precio_venta_sin_igv = datos_archivo.loc[i,'PRECIO VENTA']
                        if dat_precio_venta_sin_igv == '':
                            dat_precio_venta_sin_igv = 0.0
                        else:
                            dat_precio_venta_sin_igv = round(float(dat_precio_venta_sin_igv),2)
                        dat_precio_venta_con_igv = datos_archivo.loc[i,'PRECIO VENTA + IGV']
                        if dat_precio_venta_con_igv == '':
                            dat_precio_venta_con_igv = 0.0
                        else:
                            dat_precio_venta_con_igv = round(float(dat_precio_venta_con_igv),2)
                        try:
                            ultimo_producto = products.objects.latest('id')
                            dat_id = ultimo_producto.id + 1
                        except:
                            dat_id = 1
                        products(id=dat_id,categoria=dat_categoria,sub_categoria=dat_sub_categoria,codigo=dat_codigo,codigo_sunat=dat_codigo_sunat,nombre=dat_nombre,unidad_med=dat_unidad_med,moneda=dat_moneda,precio_compra_sin_igv=dat_precio_compra_sin_igv,precio_compra_con_igv=dat_precio_compra_con_igv,precio_venta_sin_igv=dat_precio_venta_sin_igv,precio_venta_con_igv=dat_precio_venta_con_igv).save()
                        i = i+1
                        print(dat_id)
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return HttpResponseRedirect(reverse('sistema_2:productos'))

@csrf_exempt
def agregar_stock(request):
    if request.method == 'POST':
        usuario_logued = User.objects.get(username=request.user.username)
        user_logued = userProfile.objects.get(usuario=usuario_logued)
        if user_logued.tipo == 'Admin':
            producto_id = request.POST.get('productoId')
            producto_almacen = request.POST.get('almacenStock')
            producto_cantidad = request.POST.get('cantidadStock')
            if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
            else:
                mes = str((datetime.now()-timedelta(hours=5)).month)
            if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
            else:
                dia = str((datetime.now()-timedelta(hours=5)).day)
            producto_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
            producto_vendedor = request.POST.get('vendedorStock')
            print(producto_fecha)
            datos_fecha = producto_fecha.split('-')
            producto_fecha = datos_fecha[2] + '-' + datos_fecha[1] + '-' + datos_fecha[0]
            print(producto_fecha)
            get_nombre_pro = products.objects.get(id=producto_id)
            producto_nombre = get_nombre_pro.nombre
            get_nombre_pro.save()
            usuario_stock = userProfile.objects.get(id=producto_vendedor)
            usuario_info = [producto_vendedor,usuario_stock.usuario.username,usuario_stock.codigo,usuario_stock.tipo,usuario_stock.celular]
            print(producto_id)
            producto_agregar = products.objects.get(id=producto_id)
            if producto_agregar.stock is None:
                producto_agregar.stock = []
                producto_agregar.stock.append([producto_almacen,str(round(float(producto_cantidad),2))])
            else:
                agregado = 0
                for almacen in producto_agregar.stock:
                    if almacen[0] == producto_almacen:
                        agregado = 1
                        almacen[1] = str(round(float(almacen[1]) + float(producto_cantidad),2))
                if agregado == 0:
                    producto_agregar.stock.append([producto_almacen,str(round(float(producto_cantidad),2))])
            print(producto_fecha)
            stockTotal = 0
            for almacen in producto_agregar.stock:
                stockTotal = stockTotal + float(almacen[1])
            stockTotal = str(round(float(stockTotal),2))
            producto_agregar.stockTotal = stockTotal
            ingresos_stock(producto_nombre=producto_nombre,vendedorStock=usuario_info,producto_id=producto_id,producto_codigo=producto_agregar.codigo,almacen=producto_almacen,cantidad=producto_cantidad,fechaIngreso=producto_fecha).save()
            producto_agregar.save()
            return HttpResponseRedirect(reverse('sistema_2:productos'))
        if user_logued.tipo == 'Vendedor':
            producto_id = request.POST.get('productoId')
            producto_almacen = request.POST.get('almacenStock')
            producto_cantidad = request.POST.get('cantidadStock')
            if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
            else:
                mes = str((datetime.now()-timedelta(hours=5)).month)
            if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
            else:
                dia = str((datetime.now()-timedelta(hours=5)).day)
            producto_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
            print(producto_fecha)
            datos_fecha = producto_fecha.split('-')
            producto_fecha = datos_fecha[2] + '-' + datos_fecha[1] + '-' + datos_fecha[0]
            print(producto_fecha)
            get_nombre_pro = products.objects.get(id=producto_id)
            producto_nombre = get_nombre_pro.nombre
            get_nombre_pro.save()
            usuario_info = [user_logued.id,user_logued.usuario.username,user_logued.codigo,user_logued.tipo,user_logued.celular]
            producto_agregar = products.objects.get(id=producto_id)
            if producto_agregar.stock is None:
                producto_agregar.stock = []
                producto_agregar.stock.append([producto_almacen,str(round(float(producto_cantidad),2))])
            else:
                agregado = 0
                for almacen in producto_agregar.stock:
                    if almacen[0] == producto_almacen:
                        agregado = 1
                        almacen[1] = str(round(float(almacen[1]) + float(producto_cantidad),2))
                if agregado == 0:
                    producto_agregar.stock.append([producto_almacen,str(round(float(producto_cantidad),2))])
            print(producto_fecha)
            stockTotal = 0
            for almacen in producto_agregar.stock:
                stockTotal = stockTotal + float(almacen[1])
            stockTotal = str(round(float(stockTotal),2))
            producto_agregar.stockTotal = stockTotal
            ingresos_stock(producto_nombre=producto_nombre,vendedorStock=usuario_info,producto_id=producto_id,producto_codigo=producto_agregar.codigo,almacen=producto_almacen,cantidad=producto_cantidad,fechaIngreso=producto_fecha).save()
            producto_agregar.save()
            return HttpResponseRedirect(reverse('sistema_2:productos'))
    return HttpResponseRedirect(reverse('sistema_2:productos'))

@login_required(login_url='/sistema_2')
@csrf_exempt
def proformas(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        if 'Filtrar' in request.POST:
            print('Se esta filtrando la info')
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                cotizaciones_filtradas = cotizaciones.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                return render(request,'sistema_2/proformas.html',{
                    'cotizaciones':cotizaciones_filtradas.order_by('id'),
                    'fecha_inicial':fecha_inicial,
                    'fecha_final':fecha_final,
                    'usr_rol': user_logued,
                })
        elif 'Exportar' in request.POST:
            print('Se solicita el excel')
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                cotizaciones_filtradas = cotizaciones.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                info_coti=[]
                for coti in cotizaciones_filtradas:
                    total_precio_soles = 0.00
                    total_monto = 0.00
                    total_precio = 0.00
                    for producto in coti.productos:
                        if coti.monedaProforma == 'SOLES':
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(coti.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'SOLES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if coti.monedaProforma == 'DOLARES':
                            if producto[5] == 'SOLES':
                                v_producto = (Decimal(producto[6])/Decimal(coti.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio = Decimal(total_precio) + Decimal(v_producto)
                        if producto[5] == 'DOLARES':
                            v_producto = Decimal(producto[6])*Decimal(coti.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if producto[5] == 'SOLES':
                            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_monto = Decimal(total_monto) + Decimal(producto[6])*Decimal(producto[8])
                        total_precio_soles = Decimal(total_precio_soles) + Decimal(v_producto)
                    info_coti.append([coti.fechaProforma,coti.codigoProforma,coti.cliente[3],coti.estadoProforma,coti.monedaProforma,'%.2f'%total_precio,'%.2f'%total_precio_soles])
                suma_total = 0
                for elemento in info_coti:
                    suma_total = suma_total + float(elemento[5])
                suma_total = round(suma_total,2)
                info_coti.append(['','','','','','Monto Total',str(suma_total)])
                tabla_excel = pd.DataFrame(info_coti,columns=['Fecha','Comprobante','Cliente','Estado','Moneda','Monto de la proforma','Monto (S/)'])
                tabla_excel.to_excel('info_excel.xlsx',index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                coti_exportar = cotizaciones.objects.all()
                info_coti = []
                for coti in coti_exportar:
                    total_precio_soles = 0.00
                    total_precio = 0.00
                    for producto in coti.productos:
                        if coti.monedaProforma == 'SOLES':
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(coti.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'SOLES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if coti.monedaProforma == 'DOLARES':
                            if producto[5] == 'SOLES':
                                v_producto = (Decimal(producto[6])/Decimal(coti.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio = Decimal(total_precio) + Decimal(v_producto)
                        if producto[5] == 'DOLARES':
                            v_producto = Decimal(producto[6])*Decimal(coti.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if producto[5] == 'SOLES':
                            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio_soles = Decimal(total_precio_soles) + Decimal(v_producto)
                    info_coti.append([coti.fechaProforma,coti.codigoProforma,coti.cliente[3],coti.estadoProforma,coti.monedaProforma,'%.2f'%total_precio,'%.2f'%total_precio_soles])
                suma_total = 0
                for elemento in info_coti:
                    suma_total = suma_total + float(elemento[5])
                suma_total = round(suma_total,2)
                info_coti.append(['','','','','','Monto Total',str(suma_total)])
                tabla_excel = pd.DataFrame(info_coti,columns=['Fecha','Comprobante','Cliente','Estado','Moneda','Monto de la proforma','Monto (S/)'])
                tabla_excel.to_excel('info_excel.xlsx',index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
    return render(request,'sistema_2/proformas.html',{
        'cotizaciones': cotizaciones.objects.all().order_by('-id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def crear_proforma(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    r = requests.get('https://www.sbs.gob.pe/app/pp/sistip_portal/paginas/publicacion/tipocambiopromedio.aspx')
    datos = BeautifulSoup(r.text,'html.parser')
    tc_fila = datos.find(id='ctl00_cphContent_rgTipoCambio_ctl00__0')
    tc_fila = tc_fila.find_all(class_='APLI_fila2')
    if len(tc_fila) == 2:
        tc_compra = round(float(tc_fila[0].string),3)
        tc_venta = round(float(tc_fila[1].string),3)
    else:
        tc_compra = 0.000
        tc_venta = 0.000

    pro = products.objects.all()
    cli = clients.objects.all()
    ser = services.objects.all()
    usr = userProfile.objects.all()
    return render(request,'sistema_2/crear_proforma.html',{
        'usr':usr,
        'ser':ser,
        'pro':pro,
        'cli':cli,
        'tc_venta': tc_venta,
        'tc_compra': tc_compra,
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_proforma(request,ind):
    proforma_eliminar = cotizaciones.objects.get(id=ind)
    proforma_eliminar.estadoProforma = 'Anulada'
    proforma_eliminar.save()
    time.sleep(0.5)
    return HttpResponseRedirect(reverse('sistema_2:proformas'))


def obtener_cliente(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            cliente_informacion = clients.objects.get(id=ind)
            print(cliente_informacion.direcciones)
            return JsonResponse(
                {
                    'nombre': cliente_informacion.nombre,
                    'apellido':cliente_informacion.apellido,
                    'razon_social':cliente_informacion.razon_social,
                    'dni':cliente_informacion.dni,
                    'ruc':cliente_informacion.ruc,
                    'email':cliente_informacion.email,
                    'contacto':cliente_informacion.contacto,
                    'telefono':cliente_informacion.telefono,
                    'direccion':cliente_informacion.direccion_fiscal,
                    'direcciones':cliente_informacion.direcciones
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')
    
def obtener_usuario(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            usuario_informacion = userProfile.objects.get(id=ind)
            return JsonResponse(
                {
                    'usuario': usuario_informacion.usuario.username,
                    'codigo':usuario_informacion.codigo,
                    'telefono':usuario_informacion.celular
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def obtener_producto(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            producto_informacion = products.objects.get(id=ind)
            return JsonResponse(
                {
                    'nombre':producto_informacion.nombre,
                    'codigo':producto_informacion.codigo,
                    'unidad_med':producto_informacion.unidad_med,
                    'stock':producto_informacion.stock,
                    'pv_sinIGV':producto_informacion.precio_venta_sin_igv,
                    'moneda':producto_informacion.moneda 
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def obtener_servicio(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            servicio_informacion = services.objects.get(id=ind)
            return JsonResponse(
                {
                    'nombre':servicio_informacion.nombre,
                    'unidad':servicio_informacion.unidad_med,
                    'pvsinIGV':servicio_informacion.precio_venta_sin_igv 
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')  

def agregar_proforma(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            cot_cliente = data.get('cliente')
            if(cot_cliente[0] == '0'):
                try:
                    ultimo_cliente = clients.objects.latest('id')
                    cliente_id = int(ultimo_cliente.id) + 1
                except:
                    cliente_id = 1
                clients(id=cliente_id,nombre=cot_cliente[1],apellido=cot_cliente[2],razon_social=cot_cliente[3],dni=cot_cliente[4],ruc=cot_cliente[5],email=cot_cliente[6],contacto=cot_cliente[7],telefono=cot_cliente[8],direccion_fiscal=cot_cliente[9]).save()
                cot_cliente[0] = str(cliente_id)
            cot_productos = data.get('productos')
            cot_servicios = data.get('servicios')
            cot_vendedor = data.get('vendedor')
            cot_observaciones = data.get('obsProforma')
            cot_nro_documento = data.get('nroDocCot')
            cot_pago = data.get('proforma').get('tipo_pago')
            cot_moneda = data.get('proforma').get('moneda')
            cot_fecha = data.get('proforma').get('fecha')
            cot_fechaVenc = data.get('proforma').get('fecha_vencimiento')
            cot_cantCuotas = str(data.get('nroCuotas'))
            cot_estado = 'Generada'
            cot_tipo = data.get('proforma').get('tipo_proforma')
            cot_descuento = str(data.get('mostrarDescuento'))
            cot_mostrarPU = str(data.get('mostrarPU'))
            cot_mostrarVU = str(data.get('mostrarVU'))
            fecha_nueva = parse(cot_fecha)
            datos_doc = config_docs.objects.get(id=1)
            cot_serie = datos_doc.cotiSerie
            cot_nro = datos_doc.cotiNro
            datos_doc.cotiNro = str(int(datos_doc.cotiNro) + 1)
            datos_doc.save()
            cot_cambio = [data.get('proforma').get('tc_compra'),data.get('proforma').get('tc_venta')]
            nro_imprimir = str(cot_nro)
            while len(nro_imprimir) < 4:
                nro_imprimir = '0' + nro_imprimir
            cot_codigo = str(cot_serie) + '-' + str(nro_imprimir)
            id_last = cotizaciones.objects.latest('id').id
            id_last = int(id_last)
            id_nuevo = id_last + 1
            cotizaciones(id=id_nuevo,fecha_emision=fecha_nueva,cliente=cot_cliente,productos=cot_productos,servicios=cot_servicios,vendedor=cot_vendedor,pagoProforma=cot_pago,monedaProforma=cot_moneda,fechaProforma=cot_fecha,fechaVencProforma=cot_fechaVenc,tipoProforma=cot_tipo,codigoProforma=cot_codigo,tipoCambio=cot_cambio,estadoProforma=cot_estado,imprimirDescuento=cot_descuento,imprimirPU=cot_mostrarPU,imprimirVU=cot_mostrarVU,cantidadCuotas=cot_cantCuotas,observacionesCot=cot_observaciones,nroDocumento=cot_nro_documento,nroCotizacion=cot_nro,serieCotizacion=cot_serie).save()
            time.sleep(0.5)
            return JsonResponse({'status': 'Todo added!'})

@login_required(login_url='/sistema_2')
def generar_guia(request,ind):
    cot_obtener = cotizaciones.objects.get(id=ind)
    guia_codProf = cot_obtener.codigoProforma
    guia_cliente = cot_obtener.cliente
    guia_productos = cot_obtener.productos
    guia_servicios = cot_obtener.servicios
    guia_vendedor = cot_obtener.vendedor
    guia_pago = cot_obtener.pagoProforma
    guia_moneda = cot_obtener.monedaProforma
    if(int(datetime.now().month) < 10):
        mes = '0' + str(datetime.now().month)
    else:
        mes = str(datetime.now().month)
    
    if(int(datetime.now().day) < 10):
        dia = '0' + str(datetime.now().day)
    else:
        dia = str(datetime.now().day)
    
    guia_fecha = str(datetime.now().year) + '-' + mes + '-' + dia
    guia_fecha_venc = guia_fecha
    guia_tipo = cot_obtener.tipoProforma
    guia_codigo = 'GUI-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
    guia_cambio = cot_obtener.tipoCambio
    guia_estado = 'Generada'
    guia_traslado = ['','','','','']
    guia_transportista = ['','']
    datos_doc = config_docs.objects.get(id=1)
    guia_serie = datos_doc.guiaSerie
    guia_nro = datos_doc.guiaNro
    datos_doc.guiaNro = str(int(datos_doc.guiaNro) + 1)
    datos_doc.save()
    guias(serieGuia=guia_serie,nroGuia=guia_nro,datosTraslado=guia_traslado,datosTransportista=guia_transportista,fechaVencGuia=guia_fecha_venc,codigoProforma=guia_codProf,cliente=guia_cliente,productos=guia_productos,servicios=guia_servicios,vendedor=guia_vendedor,pagoGuia=guia_pago,monedaGuia=guia_moneda,fechaGuia=guia_fecha,tipoGuia=guia_tipo,codigoGuia=guia_codigo,tipoCambio=guia_cambio,estadoGuia=guia_estado).save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))

@login_required(login_url='/sistema_2')
def generar_factura(request,ind):
    cot_obtener = cotizaciones.objects.get(id=ind)
    factura_cliente = cot_obtener.cliente
    factura_productos = cot_obtener.productos
    factura_servicios = cot_obtener.servicios
    factura_vendedor = cot_obtener.vendedor
    factura_pago = cot_obtener.pagoProforma
    factura_moneda = cot_obtener.monedaProforma
    if(int(datetime.now().month) < 10):
        mes = '0' + str(datetime.now().month)
    else:
        mes = str(datetime.now().month)
    
    if(int(datetime.now().day) < 10):
        dia = '0' + str(datetime.now().day)
    else:
        dia = str(datetime.now().day)
    
    factura_fecha = str(datetime.now().year) + '-' + mes + '-' + dia
    factura_venc = factura_fecha
    factura_tipo = cot_obtener.tipoProforma
    factura_codigo = 'FAC-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
    factura_cambio = cot_obtener.tipoCambio
    factura_estado = 'Generada'
    factura_dscto = '1'
    factura_cuotas = '1'
    datos_doc = config_docs.objects.get(id=1)
    factura_serie = datos_doc.facturaSerie
    factura_nro = datos_doc.facturaNro
    datos_doc.facturaNro = str(int(datos_doc.facturaNro) + 1)
    datos_doc.save()
    facturas(cuotasFactura=factura_cuotas,serieFactura=factura_serie,nroFactura=factura_nro,imprimirDescuento=factura_dscto,fechaVencFactura=factura_venc,cliente=factura_cliente,productos=factura_productos,servicios=factura_servicios,vendedor=factura_vendedor,pagoFactura=factura_pago,monedaFactura=factura_moneda,fechaFactura=factura_fecha,tipoFactura=factura_tipo,codigoFactura=factura_codigo,tipoCambio=factura_cambio,estadoFactura=factura_estado).save()
    return HttpResponseRedirect(reverse('sistema_2:fact'))

@login_required(login_url='/sistema_2')
def crear_factura(request,ind):
    guia_obtener = guias.objects.get(id=ind)
    factura_cliente = guia_obtener.cliente
    factura_productos = guia_obtener.productos
    factura_servicios = guia_obtener.servicios
    factura_vendedor = guia_obtener.vendedor
    factura_pago = guia_obtener.pagoGuia
    factura_moneda = guia_obtener.monedaGuia
    if(int(datetime.now().month) < 10):
        mes = '0' + str(datetime.now().month)
    else:
        mes = str(datetime.now().month)
    
    if(int(datetime.now().day) < 10):
        dia = '0' + str(datetime.now().day)
    else:
        dia = str(datetime.now().day)
    
    factura_fecha = str(datetime.now().year) + '-' + mes + '-' + dia
    factura_venc = factura_fecha
    factura_guia = guia_obtener.codigoGuia
    factura_tipo = guia_obtener.tipoGuia
    factura_codigo = 'FAC-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
    factura_cambio = guia_obtener.tipoCambio
    factura_estado = 'Generada'
    factura_dscto = '1'
    factura_cuotas = '1'
    datos_doc = config_docs.objects.get(id=1)
    factura_serie = datos_doc.facturaSerie
    factura_nro = datos_doc.facturaNro
    datos_doc.facturaNro = str(int(datos_doc.facturaNro) + 1)
    datos_doc.save()
    facturas(cuotasFactura=factura_cuotas,serieFactura=factura_serie,nroFactura=factura_nro,imprimirDescuento=factura_dscto,fechaVencFactura=factura_venc,codigoGuia=factura_guia,cliente=factura_cliente,productos=factura_productos,servicios=factura_servicios,vendedor=factura_vendedor,pagoFactura=factura_pago,monedaFactura=factura_moneda,fechaFactura=factura_fecha,tipoFactura=factura_tipo,codigoFactura=factura_codigo,tipoCambio=factura_cambio,estadoFactura=factura_estado).save()
    return HttpResponseRedirect(reverse('sistema_2:fact'))

@login_required(login_url='/sistema_2')
def generar_boleta(request,ind):
    cot_obtener = cotizaciones.objects.get(id=ind)
    boleta_cliente = cot_obtener.cliente
    boleta_productos = cot_obtener.productos
    boleta_servicios = cot_obtener.servicios
    boleta_vendedor = cot_obtener.vendedor
    boleta_pago = cot_obtener.pagoProforma
    boleta_moneda = cot_obtener.monedaProforma
    if(int(datetime.now().month) < 10):
        mes = '0' + str(datetime.now().month)
    else:
        mes = str(datetime.now().month)
    
    if(int(datetime.now().day) < 10):
        dia = '0' + str(datetime.now().day)
    else:
        dia = str(datetime.now().day)
    
    boleta_fecha = str(datetime.now().year) + '-' + mes + '-' + dia
    boleta_venc = boleta_fecha
    boleta_tipo = cot_obtener.tipoProforma
    boleta_codigo = 'BOL-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
    boleta_cambio = cot_obtener.tipoCambio
    boleta_estado = 'Generada'
    boleta_dscto = '1'
    datos_doc = config_docs.objects.get(id=1)
    boleta_serie = datos_doc.boletaSerie
    boleta_nro = datos_doc.boletaNro
    datos_doc.boletaNro = str(int(datos_doc.boletaNro) + 1)
    datos_doc.save()
    boletas(serieBoleta=boleta_serie,nroBoleta=boleta_nro,imprimirDescuento=boleta_dscto,fechaVencBoleta=boleta_venc,cliente=boleta_cliente,productos=boleta_productos,servicios=boleta_servicios,vendedor=boleta_vendedor,pagoBoleta=boleta_pago,monedaBoleta=boleta_moneda,fechaBoleta=boleta_fecha,tipoBoleta=boleta_tipo,codigoBoleta=boleta_codigo,tipoCambio=boleta_cambio,estadoBoleta=boleta_estado).save()
    return HttpResponseRedirect(reverse('sistema_2:bole'))

@login_required(login_url='/sistema_2')
def crear_boleta(request,ind):
    guia_obtener = guias.objects.get(id=ind)
    boleta_cliente = guia_obtener.cliente
    boleta_productos = guia_obtener.productos
    boleta_servicios = guia_obtener.servicios
    boleta_vendedor = guia_obtener.vendedor
    boleta_pago = guia_obtener.pagoGuia
    boleta_moneda = guia_obtener.monedaGuia
    if(int(datetime.now().month) < 10):
        mes = '0' + str(datetime.now().month)
    else:
        mes = str(datetime.now().month)
    
    if(int(datetime.now().day) < 10):
        dia = '0' + str(datetime.now().day)
    else:
        dia = str(datetime.now().day)
    
    boleta_fecha = str(datetime.now().year) + '-' + mes + '-' + dia
    boleta_venc = boleta_fecha
    boleta_guia = guia_obtener.codigoGuia
    boleta_tipo = guia_obtener.tipoGuia
    boleta_codigo = 'BOL-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
    boleta_cambio = guia_obtener.tipoCambio
    boleta_estado = 'Generada'
    boleta_dscto = '1'
    datos_doc = config_docs.objects.get(id=1)
    boleta_serie = datos_doc.boletaSerie
    boleta_nro = datos_doc.boletaNro
    datos_doc.boletaNro = str(int(datos_doc.boletaNro) + 1)
    datos_doc.save()
    boletas(serieBoleta=boleta_serie,nroBoleta=boleta_nro,imprimirDescuento=boleta_dscto,fechaVencBoleta=boleta_venc,codigoGuia=boleta_guia,cliente=boleta_cliente,productos=boleta_productos,servicios=boleta_servicios,vendedor=boleta_vendedor,pagoBoleta=boleta_pago,monedaBoleta=boleta_moneda,fechaBoleta=boleta_fecha,tipoBoleta=boleta_tipo,codigoBoleta=boleta_codigo,tipoCambio=boleta_cambio,estadoBoleta=boleta_estado).save()
    return HttpResponseRedirect(reverse('sistema_2:bole'))

@login_required(login_url='/sistema_2')
def editar_proforma(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ser = services.objects.all()
    prod = products.objects.all()
    proforma_editar = cotizaciones.objects.get(id=ind)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            cot_mostrarDescuento = data.get('mostrarDescuento')
            cot_imprimirPU = data.get('mostrarPU')
            cot_imprimirVU = data.get('mostrarVU')
            cot_cliente = data.get('cliente')
            cot_cliente[0] = proforma_editar.cliente[0]
            cot_productos = data.get('productos')
            cot_servicios = data.get('servicios')
            cot_vendedor = data.get('vendedor')
            cot_cantCuotas = data.get('nroCuotas')
            cot_observaciones = data.get('obsProforma')
            cot_nro_documento = data.get('nroDocCot')
            cot_vendedor[0] = proforma_editar.vendedor[0]
            cot_pago = data.get('proforma').get('tipo_pago')
            cot_moneda = data.get('proforma').get('moneda')
            cot_fecha = data.get('proforma').get('fecha')
            cot_tipo = data.get('proforma').get('tipo_proforma')
            cot_estado = data.get('proforma').get('estado_proforma')
            cot_fechaVenc = data.get('proforma').get('fecha_vencimiento')
            cot_cambio = [data.get('proforma').get('tc_compra'),data.get('proforma').get('tc_venta')]
            proforma_editar.cliente = cot_cliente
            print(proforma_editar.cliente)
            proforma_editar.fecha_emision = parse(cot_fecha)
            proforma_editar.cantidadCuotas = cot_cantCuotas
            proforma_editar.productos = cot_productos
            proforma_editar.servicios = cot_servicios
            proforma_editar.vendedor = cot_vendedor
            proforma_editar.pagoProforma = cot_pago
            proforma_editar.monedaProforma = cot_moneda
            proforma_editar.fechaProforma = cot_fecha
            proforma_editar.tipoProforma = cot_tipo
            proforma_editar.tipoCambio = cot_cambio
            proforma_editar.imprimirPU = cot_imprimirPU
            proforma_editar.imprimirVU = cot_imprimirVU
            print(proforma_editar.imprimirPU)
            print(proforma_editar.imprimirVU)
            proforma_editar.imprimirDescuento = cot_mostrarDescuento
            proforma_editar.fechaVencProforma = cot_fechaVenc
            proforma_editar.observacionesCot = cot_observaciones
            proforma_editar.nroDocumento = cot_nro_documento
            proforma_editar.save()
            return JsonResponse({'status': 'Todo added!'})
    return render(request,'sistema_2/editar_proforma.html',{
        'prof':proforma_editar,
        'pro':prod,
        'ser':ser,
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
@csrf_exempt
def gui(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        if 'Filtrar' in request.POST:
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                guias_filtradas = guias.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                return render(request,'sistema_2/guias.html',{
                    'gui':guias_filtradas.order_by('id'),
                    'fecha_inicial':fecha_inicial,
                    'fecha_final':fecha_final,
                    'usr_rol': user_logued,
                })
        elif 'Exportar' in request.POST:
            print('Se solicita el excel')
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                guias_filtradas = guias.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                info_guias=[]
                for guia in guias_filtradas:
                    info_guias.append([guia.codigoGuia,guia.vendedor[1],guia.fechaGuia,guia.monedaGuia,guia.estadoGuia,guia.cliente[3]])
                tabla_excel = pd.DataFrame(info_guias,columns=['Codigo','Vendedor','Fecha','Moneda','Estado','Cliente'])
                tabla_excel.to_excel('info_excel.xlsx')
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                guias_exportar = guias.objects.all()
                info_guias=[]
                for guia in guias_exportar:
                    info_guias.append([guia.codigoGuia,guia.vendedor[1],guia.fechaGuia,guia.monedaGuia,guia.estadoGuia,guia.cliente[3]])
                tabla_excel = pd.DataFrame(info_guias,columns=['Codigo','Vendedor','Fecha','Moneda','Estado','Cliente'])
                tabla_excel.to_excel('info_excel.xlsx')
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
    return render(request,'sistema_2/guias.html',{
        'gui': guias.objects.all().order_by('-id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_guia(request,ind):
    guia_eliminar = guias.objects.get(id=ind)
    guia_eliminar.estadoGuia = 'Anulada'
    if guia_eliminar.tipoGuia == 'Productos':
        if guia_eliminar.cliente[1] == '':
            comprobante_editar = facturas.objects.get(id=guia_eliminar.idFactura)
        else:
            comprobante_editar = boletas.objects.get(id=guia_eliminar.idFactura)
        for producto in guia_eliminar.productos:
            for prod in comprobante_editar.productos:
                if prod[0] == producto[0]:
                    prod[10]  = str(int(prod[10]) + int(producto[8]))
        comprobante_editar.save()
    guia_eliminar.save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))

@login_required(login_url='/sistema_2')
def editar_guia(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ser = services.objects.all()
    prod = products.objects.all()
    proforma_editar = guias.objects.get(id=ind)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            cot_ubigeo = data.get('ubigeoCliente')
            print(cot_ubigeo)
            cot_cliente = data.get('cliente')
            cot_productos = data.get('productos')
            cot_servicios = data.get('servicios')
            cot_vendedor = data.get('vendedor')
            cot_obs = data.get('obsGuia')
            cot_pago = data.get('proforma').get('tipo_pago')
            cot_moneda = data.get('proforma').get('moneda')
            cot_fecha = data.get('proforma').get('fecha')
            cot_fecha_venc = data.get('proforma').get('fecha_vencimiento')
            print(cot_fecha_venc)
            cot_tipo = data.get('proforma').get('tipo_proforma')
            cot_cambio = [data.get('proforma').get('tc_compra'),data.get('proforma').get('tc_venta')]
            cot_estado = 'Generada'
            cot_traslado = data.get('traslado')
            cot_transporte = data.get('transporte')
            cot_vehiculo = data.get('datosVehiculo')
            proforma_editar.fecha_emision = parse(cot_fecha)
            proforma_editar.datosTraslado = cot_traslado
            proforma_editar.cliente = cot_cliente
            proforma_editar.productos = cot_productos
            proforma_editar.servicios = cot_servicios
            proforma_editar.vendedor = cot_vendedor
            proforma_editar.pagoGuia = cot_pago
            proforma_editar.monedaGuia = cot_moneda
            proforma_editar.fechaGuia = cot_fecha
            proforma_editar.tipoGuia = cot_tipo
            proforma_editar.observacionesGuia = cot_obs
            proforma_editar.tipoCambio = cot_cambio
            proforma_editar.fechaVencGuia = cot_fecha_venc
            proforma_editar.datosTransportista = cot_transporte
            proforma_editar.ubigeoGuia = cot_ubigeo
            proforma_editar.datosVehiculo = cot_vehiculo
            print(proforma_editar.fechaVencGuia)
            proforma_editar.save()
            return JsonResponse({'status': 'Todo added!'})
    return render(request,'sistema_2/editar_guia.html',{
        'prof':proforma_editar,
        'pro':prod,
        'ser':ser,
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
@csrf_exempt
def fact(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        if 'Filtrar' in request.POST:
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                facturas_filtradas = facturas.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                return render(request,'sistema_2/facturas.html',{
                    'fac':facturas_filtradas.order_by('id'),
                    'fecha_inicial':fecha_inicial,
                    'fecha_final':fecha_final,
                    'usr_rol': user_logued,
                })
        elif 'Exportar' in request.POST:
            print('Se solicita el excel')
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                facturas_filtradas = facturas.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                info_facturas=[]
                for factura in facturas_filtradas:
                    total_precio_soles = 0.00
                    total_precio = 0.00
                    for producto in factura.productos:
                        if factura.monedaFactura == 'SOLES':
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(factura.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'SOLES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if factura.monedaFactura == 'DOLARES':
                            if producto[5] == 'SOLES':
                                v_producto = (Decimal(producto[6])/Decimal(factura.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio = Decimal(total_precio) + Decimal(v_producto)
                        if producto[5] == 'DOLARES':
                            v_producto = Decimal(producto[6])*Decimal(factura.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if producto[5] == 'SOLES':
                            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio_soles = Decimal(total_precio_soles) + Decimal(v_producto)
                    info_facturas.append([factura.fechaFactura,factura.codigoFactura,factura.cliente[3],factura.estadoFactura,factura.vendedor[2],factura.codigosGuias,factura.monedaFactura,'%.2f'%total_precio,'%.2f'%total_precio_soles])
                suma_total = 0
                for elemento in info_facturas:
                    suma_total = suma_total + float(elemento[7])
                suma_total = round(suma_total,2)
                info_facturas.append(['','','','','','','Monto Total',str(suma_total)])
                tabla_excel = pd.DataFrame(info_facturas,columns=['Fecha','Comprobante','Cliente','Estado','Vendedor','Guias','Moneda','Monto de la factura','Monto (S/)'])
                tabla_excel.to_excel('info_excel.xlsx',index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                facturas_exportar = facturas.objects.all()
                info_facturas=[]
                for factura in facturas_exportar:
                    total_precio_soles = 0.00
                    total_precio = 0.00
                    for producto in factura.productos:
                        if factura.monedaFactura == 'SOLES':
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(factura.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'SOLES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if factura.monedaFactura == 'DOLARES':
                            if producto[5] == 'SOLES':
                                v_producto = (Decimal(producto[6])/Decimal(factura.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                            if producto[5] == 'DOLARES':
                                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio = Decimal(total_precio) + Decimal(v_producto)
                        if producto[5] == 'DOLARES':
                            v_producto = Decimal(producto[6])*Decimal(factura.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        if producto[5] == 'SOLES':
                            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                        total_precio_soles = Decimal(total_precio_soles) + Decimal(v_producto)
                    info_facturas.append([factura.fechaFactura,factura.codigoFactura,factura.cliente[3],factura.estadoFactura,factura.vendedor[2],factura.codigosGuias,factura.monedaFactura,'%.2f'%total_precio,'%.2f'%total_precio_soles])
                suma_total = 0
                for elemento in info_facturas:
                    suma_total = suma_total + float(elemento[7])
                suma_total = round(suma_total,2)
                info_facturas.append(['','','','','','','Monto Total',str(suma_total)])
                tabla_excel = pd.DataFrame(info_facturas,columns=['Fecha','Comprobante','Cliente','Estado','Vendedor','Guias','Moneda','Monto de la factura','Monto (S/)'])
                tabla_excel.to_excel('info_excel.xlsx',index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
    return render(request,'sistema_2/facturas.html',{
        'fac': facturas.objects.all().order_by('-id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_factura(request,ind):
    factura_info = facturas.objects.get(id=ind)
    print(factura_info.cliente)
    print(factura_info.productos)
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    print(mes)
    print(dia)
    nota_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    print(nota_fecha)
    datos_doc = config_docs.objects.get(id=1)
    nota_serie = datos_doc.notaFactSerie
    nota_nro = datos_doc.notaFactNro
    datos_doc.notaFactNro = str(int(datos_doc.notaFactNro) + 1)
    datos_doc.save()
    info_data = armar_json_nota_factura(factura_info,nota_fecha,nota_serie,nota_nro)
    token_info = config_docs.objects.get(id=1)
    headers_info={"X-Auth-Token":token_info.tokenDoc,"Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/nota-credito'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    token_info.save()
    print(r)
    print(r.content)
    if((r.status_code == 200) or (r.status_code == 409)):
        factura_info.estadoFactura = 'Anulada'
        nota_cliente = factura_info.cliente
        nota_productos = factura_info.productos
        nota_servicios = factura_info.servicios
        nota_vendedor = factura_info.vendedor
        nota_nroBoleta = factura_info.nroFactura
        nota_serieBoleta = factura_info.serieFactura
        nota_tipo = 'FACTURA'
        nota_fechaBoleta = factura_info.fechaFactura
        nota_codigoBoleta = factura_info.codigoFactura
        nota_codigo = 'NOT-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
        nota_estado = 'Enviada'
        nota_tipoCambio = factura_info.tipoCambio
        nota_moneda = factura_info.monedaFactura
        nota_tipoItems = factura_info.tipoFactura
        nota_imprimir = '1'
        notaCredito(tipoCambio=nota_tipoCambio,monedaNota=nota_moneda,tipoItemsNota=nota_tipoItems,imprimirDescuento=nota_imprimir,cliente=nota_cliente,servicios=nota_servicios,productos=nota_productos,vendedor=nota_vendedor,tipoComprobante=nota_tipo,serieComprobante=nota_serieBoleta,nroComprobante=nota_nroBoleta,fechaComprobante=nota_fechaBoleta,fechaEmision=nota_fecha,codigoComprobante=nota_codigoBoleta,codigoNotaCredito=nota_codigo,estadoNotaCredito=nota_estado,serieNota=nota_serie,nroNota=nota_nro).save()
    if(r.status_code == 401):
        factura_info.estadoFactura = 'Emitida'
    factura_info.save()
    return HttpResponseRedirect(reverse('sistema_2:fact'))

def armar_json_nota_factura(factura_info,nota_fecha,nota_serie,nota_nro):
    productos = []
    valor_total = 0
    if factura_info.monedaFactura == 'SOLES':
        moneda = "PEN"
        if factura_info.tipoFactura == 'Productos':
            i=1
            for producto in factura_info.productos:
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6])*float(factura_info.tipoCambio[1]),2)
                print(precio_pro)
                valor_total = valor_total + precio_pro*int(producto[8])
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
        if factura_info.tipoFactura == 'Servicios':
            i = 1
            for servicio in factura_info.servicios:
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4])*float(factura_info.tipoCambio[1]),2)
                print(precio_pro)
                valor_total = valor_total + precio_pro
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if factura_info.monedaFactura == 'DOLARES':
        moneda = "USD"
        if factura_info.tipoFactura == 'Productos':
            i = 1
            for producto in factura_info.productos:
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6])/float(factura_info.tipoCambio[1]),2)
                valor_total = valor_total + precio_pro*int(producto[8])
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
        if factura_info.tipoFactura == 'Servicios':
            i = 1
            for servicio in factura_info.servicios:
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4])/float(factura_info.tipoCambio[1]),2)
                print(precio_pro)
                valor_total = valor_total + precio_pro
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if factura_info.pagoFactura == 'CONTADO':
        cuotas_info = null
    if factura_info.pagoFactura == 'CREDITO':
        cuotas_info = []
        i = 0
        tiempo_actual = datetime.today()
        tiempo_cuota = tiempo_actual
        monto = round((valor_total/int(factura_info.cuotasFactura)),2)
        while i < int(factura_info.cuotasFactura):
            cuota = {
                "numero":str(i + 1),
                "fecha":factura_info.fechasCuotas[i],
                "monto":str(monto),
                "moneda":moneda
            }
            tiempo_cuota = tiempo_cuota + relativedelta(months=1)
            i = i + 1
            cuotas_info.append(cuota)
    print(cuotas_info)
    print(productos)
    param_data = {
        "close2u":
        {
            "tipoIntegracion":"OFFLINE",
            "tipoPlantilla":"01",
            "tipoRegistro":"PRECIOS_SIN_IGV"
        }, 
        "comprobanteAjustado":{
            "serie":factura_info.serieFactura,
            "numero":int(factura_info.nroFactura),
            "tipoDocumento":"FACTURA",
            "fechaEmision":str(factura_info.fechaFactura),
        },
        "datosDocumento":
        {
            "serie":nota_serie,
            "numero":int(nota_nro),
            "moneda":moneda,
            "fechaEmision":factura_info.fechaFactura,
            "horaEmision":null,
            "fechaVencimiento":factura_info.fechaVencFactura,
            "formaPago":factura_info.pagoFactura,
            "medioPago": "DEPOSITO_CUENTA",
            "condicionPago": null,
            "ordencompra":null,
            "puntoEmisor":null,
            "glosa":"Anulacion"
        },
        "detalleDocumento":productos,
        "emisor":
        {
            "correo":"info@metalprotec.com",
            "nombreComercial": null,
            "nombreLegal": "METALPROTEC",
            "numeroDocumentoIdentidad": "20541628631",
            "tipoDocumentoIdentidad": "RUC",
            "domicilioFiscal":
            {
                "pais":"PERU",
                "departamento":"ANCASH",
                "provincia":"SANTA",
                "distrito":"NUEVO CHIMBOTE",
                "direccon":"Mza. J4 Lote. 39",
                "ubigeo":"02712"
            }
        },
        "informacionAdicional":
        {
            "tipoOperacion":"VENTA_INTERNA",
            "coVendedor":null
        },
        "motivo":"ANULACION_OPERACION",
        "receptor":
        {
            "correo":factura_info.cliente[6],
            "correoCopia":null,
            "domicilioFiscal":
            {
                "direccion":factura_info.cliente[9],
                "pais":"PERU",
            },
            "nombreComercial":null,
            "nombreLegal":factura_info.cliente[3],
            "numeroDocumentoIdentidad":factura_info.cliente[5],
            "tipoDocumentoIdentidad":"RUC"
        },
        'cuotas':cuotas_info
    }
    return param_data


@login_required(login_url='/sistema_2')
def editar_factura(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ser = services.objects.all()
    prod = products.objects.all()
    proforma_editar = facturas.objects.get(id=ind)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            cot_mostrarDescuento = data.get('mostrarDescuento')
            cot_cliente = data.get('cliente')
            cot_productos = data.get('productos')
            cot_servicios = data.get('servicios')
            cot_vendedor = data.get('vendedor')
            cot_nroDocumento = data.get('nroDocumento')
            cot_fechasFactura = data.get('fechasFactura')
            cot_pago = data.get('proforma').get('tipo_pago')
            cot_moneda = data.get('proforma').get('moneda')
            cot_fecha = data.get('proforma').get('fecha')
            print(cot_fecha)
            print(cot_fechasFactura)
            cot_tipo = data.get('proforma').get('tipo_proforma')
            cot_cambio = [data.get('proforma').get('tc_compra'),data.get('proforma').get('tc_venta')]
            proforma_editar.fecha_emision = parse(cot_fecha)
            proforma_editar.cliente = cot_cliente
            proforma_editar.productos = cot_productos
            proforma_editar.servicios = cot_servicios
            proforma_editar.vendedor = cot_vendedor
            proforma_editar.nroDocumento = cot_nroDocumento
            proforma_editar.pagoFactura = cot_pago
            proforma_editar.monedaFactura = cot_moneda
            proforma_editar.fechaFactura = cot_fecha
            proforma_editar.tipoFactura = cot_tipo
            proforma_editar.fechasCuotas = cot_fechasFactura
            proforma_editar.tipoCambio = cot_cambio
            proforma_editar.imprimirDescuento = cot_mostrarDescuento
            if proforma_editar.pagoFactura == 'CONTADO':
                proforma_editar.fechaVencFactura = cot_fecha
            if proforma_editar.pagoFactura == 'CREDITO':
                proforma_editar.fechaVencFactura = cot_fechasFactura[-1]
            proforma_editar.save()
            time.sleep(0.5)
            return JsonResponse({'status': 'Todo added!'})
    return render(request,'sistema_2/editar_factura.html',{
        'prof':proforma_editar,
        'pro':prod,
        'ser':ser,
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
@csrf_exempt
def bole(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        if 'Filtrar' in request.POST:
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                boletas_filtradas = boletas.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                return render(request,'sistema_2/boletas.html',{
                    'bol':boletas_filtradas.order_by('id'),
                    'fecha_inicial':fecha_inicial,
                    'fecha_final':fecha_final,
                    'usr_rol': user_logued,
                })
        elif 'Exportar' in request.POST:
            print('Se solicita el excel')
            fecha_inicial = str(request.POST.get('fecha_inicio'))
            fecha_final = str(request.POST.get('fecha_fin'))
            if fecha_inicial != '' and fecha_final != '':
                boletas_filtradas = boletas.objects.all().filter(fecha_emision__range=[fecha_inicial,fecha_final])
                info_boletas=[]
                for boleta in boletas_filtradas:
                    info_boletas.append([boleta.codigoBoleta,boleta.vendedor[1],boleta.fechaBoleta,boleta.monedaBoleta,boleta.estadoBoleta,boleta.cliente[3]])
                tabla_excel = pd.DataFrame(info_boletas,columns=['Codigo','Vendedor','Fecha','Moneda','Estado','Cliente'])
                tabla_excel.to_excel('info_excel.xlsx')
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                boletas_exportar = boletas.objects.all()
                info_boletas=[]
                for boleta in boletas_filtradas:
                    info_boletas.append([boleta.codigoBoleta,boleta.vendedor[1],boleta.fechaBoleta,boleta.monedaBoleta,boleta.estadoBoleta,boleta.cliente[3]])
                tabla_excel = pd.DataFrame(info_boletas,columns=['Codigo','Vendedor','Fecha','Moneda','Estado','Cliente'])
                tabla_excel.to_excel('info_excel.xlsx')
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
    return render(request,'sistema_2/boletas.html',{
        'bol': boletas.objects.all().order_by('-id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def editar_boleta(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    ser = services.objects.all()
    prod = products.objects.all()
    proforma_editar = boletas.objects.get(id=ind)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            cot_mostrarDescuento = data.get('mostrarDescuento')
            cot_cliente = data.get('cliente')
            cot_productos = data.get('productos')
            cot_servicios = data.get('servicios')
            cot_vendedor = data.get('vendedor')
            cot_nroDocumento = data.get('nroDocumento')
            cot_pago = data.get('proforma').get('tipo_pago')
            cot_moneda = data.get('proforma').get('moneda')
            cot_fecha = data.get('proforma').get('fecha')
            cot_tipo = data.get('proforma').get('tipo_proforma')
            cot_cambio = [data.get('proforma').get('tc_compra'),data.get('proforma').get('tc_venta')]
            proforma_editar.fecha_emision = parse(cot_fecha)
            proforma_editar.cliente = cot_cliente
            proforma_editar.productos = cot_productos
            proforma_editar.servicios = cot_servicios
            proforma_editar.vendedor = cot_vendedor
            proforma_editar.pagoBoleta = cot_pago
            proforma_editar.monedaBoleta = cot_moneda
            proforma_editar.nroDocumento = cot_nroDocumento
            proforma_editar.fechaBoleta = cot_fecha
            proforma_editar.tipoBoleta = cot_tipo
            proforma_editar.tipoCambio = cot_cambio
            proforma_editar.estadoBoleta = 'Generada'
            proforma_editar.imprimirDescuento = cot_mostrarDescuento
            proforma_editar.save()
            return JsonResponse({'status': 'Todo added!'})
    return render(request,'sistema_2/editar_boleta.html',{
        'prof':proforma_editar,
        'pro':prod,
        'ser':ser,
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def eliminar_boleta(request,ind):
    boleta_eliminar = boletas.objects.get(id=ind)
    print(boleta_eliminar.cliente)
    print(boleta_eliminar.productos)
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    nota_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    datos_doc = config_docs.objects.get(id=1)
    nota_serie = datos_doc.notaSerie
    nota_nro = datos_doc.notaNro
    datos_doc.notaNro = str(int(datos_doc.notaNro) + 1)
    datos_doc.save()
    info_data = armar_json_nota_boleta(boleta_eliminar,nota_fecha,nota_serie,nota_nro)
    token_info = config_docs.objects.get(id=1)
    headers_info={"X-Auth-Token":token_info.tokenDoc,"Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/nota-credito'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    token_info.save()
    print(r)
    print(r.content)
    if((r.status_code == 200) or (r.status_code == 409)):
        boleta_eliminar.estadoBoleta = 'Anulada'
        nota_cliente = boleta_eliminar.cliente
        nota_productos = boleta_eliminar.productos
        nota_servicios = boleta_eliminar.servicios
        nota_vendedor = boleta_eliminar.vendedor
        nota_nroBoleta = boleta_eliminar.nroBoleta
        nota_serieBoleta = boleta_eliminar.serieBoleta
        nota_tipo = 'BOLETA'
        nota_fechaBoleta = boleta_eliminar.fechaBoleta
        nota_codigoBoleta = boleta_eliminar.codigoBoleta
        nota_codigo = 'NOT-' + str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day) + str(datetime.now().hour) + str(datetime.now().minute) + str(datetime.now().second)
        nota_estado = 'Enviada'
        nota_tipoCambio = boleta_eliminar.tipoCambio
        nota_moneda = boleta_eliminar.monedaBoleta
        nota_tipoItems = boleta_eliminar.tipoBoleta
        nota_imprimir = '1'
        notaCredito(tipoCambio=nota_tipoCambio,monedaNota=nota_moneda,tipoItemsNota=nota_tipoItems,imprimirDescuento=nota_imprimir,cliente=nota_cliente,servicios=nota_servicios,productos=nota_productos,vendedor=nota_vendedor,tipoComprobante=nota_tipo,serieComprobante=nota_serieBoleta,nroComprobante=nota_nroBoleta,fechaComprobante=nota_fechaBoleta,fechaEmision=nota_fecha,codigoComprobante=nota_codigoBoleta,codigoNotaCredito=nota_codigo,estadoNotaCredito=nota_estado,serieNota=nota_serie,nroNota=nota_nro).save()
    if(r.status_code == 401):
        boleta_eliminar.estadoBoleta = 'Emitida'
    if(r.status_code == 403):
        boleta_eliminar.estadoBoleta = 'Emitida'
    boleta_eliminar.save()
    return HttpResponseRedirect(reverse('sistema_2:bole'))

def armar_json_nota_boleta(boleta_info,nota_fecha,nota_serie,nota_nro):
    productos = []
    if boleta_info.monedaBoleta == 'SOLES':
        moneda = "PEN"
        if boleta_info.tipoBoleta == 'Productos':
            i=1
            for producto in boleta_info.productos:
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6])*float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True,
                }
                productos.append(info_pro)
                i=i+1
        if boleta_info.tipoBoleta == 'Servicios':
            i = 1
            for servicio in boleta_info.servicios:
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4])*float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if boleta_info.monedaBoleta == 'DOLARES':
        moneda = "USD"
        if boleta_info.tipoBoleta == 'Productos':
            i = 1
            for producto in boleta_info.productos:
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6])/float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "esPorcentaje": True,
                    "numeroOrden":i
                }
                productos.append(info_pro)
                i=i+1
        if boleta_info.tipoBoleta == 'Servicios':
            i = 1
            for servicio in boleta_info.servicios:
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4])/float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje": True,
                }
                productos.append(info_pro)
                i=i+1
    print(productos)
    param_data = {
        "close2u":
        {
            "tipoIntegracion":"OFFLINE",
            "tipoPlantilla":"01",
            "tipoRegistro":"PRECIOS_SIN_IGV"
        },
        "comprobanteAjustado":{
            "serie":str(boleta_info.serieBoleta),
            "numero":int(boleta_info.nroBoleta),
            "tipoDocumento":"BOLETA",
            "fechaEmision":str(boleta_info.fechaBoleta)
        },
        "datosDocumento":
        {
            "fechaEmision":str(nota_fecha),
            "fechaVencimiento":null,
            "formaPago":null,
            "glosa":"Anulacion",
            "horaEmision":null,
            "moneda":moneda,
            "numero":int(nota_nro),
            "ordencompra":null,
            "puntoEmisor":null,
            "serie":nota_serie
        },
        "detalleDocumento": productos,
        "emisor":
        {
            "correo":"info@metalprotec.com",
            "nombreComercial": null,
            "nombreLegal": "METALPROTEC SAC",
            "numeroDocumentoIdentidad": "20541628631",
            "tipoDocumentoIdentidad": "RUC",
            "domicilioFiscal":
            {
                "pais":"PERU",
                "departamento":"ANCASH",
                "provincia":"SANTA",
                "distrito":"NUEVO CHIMBOTE",
                "direccon":"Mza. J4 Lote. 39",
                "ubigeo":"02712"
            }
        },
        "informacionAdicional":
        {
            "tipoOperacion":"VENTA_INTERNA",
            "coVendedor":boleta_info.vendedor[1]
        },
        "motivo":"ANULACION_OPERACION",
        "receptor":
        {
            "correo": boleta_info.cliente[6],
            "correoCopia": null,
            "domicilioFiscal":
            {
                "departamento": null,
                "direccion": boleta_info.cliente[9],
                "distrito": null,
                "pais": "PERU",
                "provincia": null,
                "ubigeo": null,
                "urbanizacion": null
            },
            "nombreComercial": null,
            "nombreLegal": str(boleta_info.cliente[1] + ' ' + boleta_info.cliente[2]),
            "numeroDocumentoIdentidad": boleta_info.cliente[4],
            "tipoDocumentoIdentidad": "DOC_NACIONAL_DE_IDENTIDAD"
        }
    }
    return param_data


@login_required(login_url='/sistema_2')
def descargar_proforma(request,ind):
    #Generacion del documento
    pdf_name = 'coti_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)

    #Obtencion de la informacion
    proforma_info = cotizaciones.objects.get(id=ind)
    proforma_info.monedaProforma = 'SOLES'

    #Generacion del membrete superior derecho
    can.setStrokeColorRGB(0,0,1)
    lista_x = [400,580]
    lista_y = [720,815]
    can.grid(lista_x,lista_y)
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica',12)
    can.drawString(440,785,'RUC: 20541628631')
    can.setFont('Helvetica-Bold',12)
    can.drawString(455,765,'COTIZACION')
    can.setFont('Helvetica',12)
    numImp = str(proforma_info.nroCotizacion)
    if len(numImp) < 4:
        while(len(numImp) < 4):
            numImp = '0' + numImp
    else:
        pass
    can.drawString(460,745,str(proforma_info.serieCotizacion) + ' - ' + numImp)

    #Generacion del logo
    can.drawImage('./sistema_2/static/images/logo_2.png',10,705,width=120,height=120)
    
    #Informacion del remitente
    can.setFont('Helvetica-Bold',10)
    can.drawString(25,705,'METALPROTEC')
    can.setFont('Helvetica',7)
    can.drawString(25,695,'LT 39 MZ. J4 URB. PASEO DEL MAR - ÁNCASH SANTA NUEVO CHIMBOTE')
    can.drawString(25,687,'Teléfono: (043) 282752')
    #can.drawString(25,679,'E-Mail: contabilidad@metalprotec.pe')

    #Generacion de la linea de separacion
    can.line(25,670,580,670)

    #Generacion de los datos del cliente
    can.drawString(25,660,'Señores:')
    if proforma_info.cliente[1] == '':
        can.drawString(120,660,str(proforma_info.cliente[3]))
    else:
        can.drawString(120,660,str(proforma_info.cliente[1]) + ' ' + str(proforma_info.cliente[2]))
    can.drawString(25,650,'Direccion:')
    can.drawString(120,650,str(proforma_info.cliente[9]))
    if proforma_info.cliente[1] == '':
        can.drawString(25,640,'Ruc:')
        can.drawString(120,640,str(proforma_info.cliente[5]))
    else:
        can.drawString(25,640,'Dni:')
        can.drawString(120,640,str(proforma_info.cliente[4]))
    can.drawString(25,630,'Forma de Pago:')
    can.drawString(120,630,str(proforma_info.pagoProforma))

    can.drawString(230,640,'Fecha de emision:')
    can.drawString(320,640,str(proforma_info.fechaProforma))
    can.drawString(230,630,'Fecha de vencimiento:')
    can.drawString(320,630,str(proforma_info.fechaVencProforma))

    can.drawString(430,640,'Nro de Documento:')
    can.drawString(520,640,str(proforma_info.nroDocumento))
    can.drawString(430,630,'Moneda:')
    can.drawString(520,630,str(proforma_info.monedaProforma))

    #Linea de separacion con los datos del vendedor
    can.line(25,620,580,620)

    #Datos del vendedor
    can.drawString(25,610,'Vendedor:')
    can.drawString(120,610,str(proforma_info.vendedor[1]))
    can.drawString(25,600,'Celular:')
    can.drawString(120,600,str(proforma_info.vendedor[3]))

    #Get the vendor email
    vendedor_info = userProfile.objects.get(id=proforma_info.vendedor[0])
    email_vendedor = vendedor_info.usuario.email
    vendedor_info.save()
    can.drawString(25,590,'Email:')
    can.drawString(120,590,str(email_vendedor))

    can.drawString(25,580,'Observacion:')
    can.drawString(120,580,str(proforma_info.observacionesCot))

    #Campos en cabecera
    lista_x = [25,580]
    lista_y = [550,565]
    can.setFillColorRGB(0,0,1)
    can.rect(25,550,555,15,fill=1)

    #Valores iniciales
    lista_x = [25,50,100,310,360,410,460,530]
    lista_y = [550,565]
    #Ingreso de campo cantidad
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[0] + 5, lista_y[0] + 3,'Cant.')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawRightString(lista_x[0] + 20,lista_y[0] + 3,str("{:.2f}".format(round(float(producto[8]),2))))
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de código de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[1] + 5, lista_y[0] + 3,'Código')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[1] + 5,lista_y[0] + 3,producto[2])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de descripcion de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[2] + 5, lista_y[0] + 3,'Descripción')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[2] + 5,lista_y[0] + 3,producto[1])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de unidad de medida de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[3] + 5, lista_y[0] + 3,'Und')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[3] + 5,lista_y[0] + 3,producto[3])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    condicion_imprimir = proforma_info.imprimirVU + proforma_info.imprimirPU + proforma_info.imprimirDescuento
    if condicion_imprimir == '100':
        lista_x[4] = 360
    
    if condicion_imprimir == '010':
        lista_x[5] = 360

    if condicion_imprimir == '001':
        lista_x[6] = 360
    
    if condicion_imprimir == '110':
        lista_x[4] = 360
        lista_x[5] = 420

    if condicion_imprimir == '101':
        lista_x[4] = 360
        lista_x[6] = 420
    
    if condicion_imprimir == '011':
        lista_x[5] = 360
        lista_x[6] = 420
    
    if condicion_imprimir == '111':
        lista_x[4] = 360
        lista_x[5] = 420
        lista_x[6] = 480

    if proforma_info.imprimirVU == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo de unidad de medida de producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[4] - 5, lista_y[0] + 3,'V.U sin IGV')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            if proforma_info.monedaProforma == 'SOLES':
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                if producto[5] == 'SOLES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            if proforma_info.monedaProforma == 'DOLARES':
                if producto[5] == 'SOLES':
                    vu_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            can.drawRightString(lista_x[4] + 20,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % vu_producto)))
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    if proforma_info.imprimirPU == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo del precio con IGV de producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[5] - 5, lista_y[0]+3,'P.U con IGV')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            if proforma_info.monedaProforma == 'SOLES':
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                if producto[5] == 'SOLES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            if proforma_info.monedaProforma == 'DOLARES':
                if producto[5] == 'SOLES':
                    vu_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            can.drawRightString(lista_x[5] + 20,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % (vu_producto*Decimal(1.18)))))
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    if proforma_info.imprimirDescuento == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo de descuento del producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[6], lista_y[0] + 3,'Dscto')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            can.drawRightString(lista_x[6] + 20,lista_y[0] + 3,str(producto[7]) + ' %')
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de valor de venta del producto
    total_precio = Decimal(0.0000)
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[7] + 5, lista_y[0] + 3,'Valor Venta')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        if proforma_info.monedaProforma == 'SOLES':
            if producto[5] == 'DOLARES':
                v_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
            if producto[5] == 'SOLES':
                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        if proforma_info.monedaProforma == 'DOLARES':
            if producto[5] == 'SOLES':
                v_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
            if producto[5] == 'DOLARES':
                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        #v_producto = round(v_producto,2)
        can.drawRightString(lista_x[7] + 45,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % Decimal(v_producto))))
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        total_precio = Decimal(total_precio) + Decimal(v_producto)

    #Linea de separacion con los datos finales
    can.line(25,lista_y[1],580,lista_y[1])

    #Impresion de total venta
    can.drawRightString(480,lista_y[0]+4,'Total Venta Grabada')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % total_precio)))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Impresion de total IGV
    igv_precio = Decimal('%.2f' % total_precio)*Decimal(0.18)
    can.drawRightString(480,lista_y[0]+4,'Total IGV')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % igv_precio)))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Impresion de importe total
    precio_final = Decimal('%.2f' % total_precio)*Decimal(1.18)
    can.drawRightString(480,lista_y[0]+4,'Importe Total de la Venta')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % Decimal(precio_final))))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Calculo de la proforma en dolares
    total_dolares = Decimal(0.0000)
    for producto in proforma_info.productos:
        if producto[5] == 'SOLES':
            v_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        if producto[5] == 'DOLARES':
            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        total_dolares = Decimal(total_dolares) + Decimal(v_producto)
    final_dolares = Decimal('%.2f' % total_dolares)*Decimal(1.18)

    #Impresion de importe en otra moneda
    precio_final = Decimal('%.2f' % total_precio)*Decimal(1.18)
    can.drawRightString(480,lista_y[0]+4,'Importe Total de la Venta')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'$')
        can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % Decimal(final_dolares))))
    else:
        can.drawRightString(490,lista_y[0]+4,'S/')
        can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % (Decimal(precio_final)*Decimal(proforma_info.tipoCambio[1])))))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion con los datos finales
    can.line(25,lista_y[1],580,lista_y[1])



    #Impresion de los datos bancarios
    #Scotiabank
    can.setFont('Helvetica-Bold',8)
    can.drawString(25,60,'Banco Scotiabank')
    can.setFont('Helvetica',8)
    can.drawString(25,50,'Cta Cte Soles: 000 9496505')
    can.drawString(25,40,'Cta Cte Dolares: 000 5151261')

    #BCP
    can.setFont('Helvetica-Bold',8)
    can.drawString(160,60,'Banco de Crédito del Perú')
    can.setFont('Helvetica',8)
    can.drawString(160,50,'Cta Cte Soles: 310 9888337 0 02')
    can.drawString(160,40,'Cta Cte Dolares: 310 9865292 1 35')

    #BBVA
    can.setFont('Helvetica-Bold',8)
    can.drawString(320,60,'Banco Continental BBVA')
    can.setFont('Helvetica',8)
    can.drawString(320,50,'Cta Cte Soles: 0011 0250 0200615638 80')
    can.drawString(320,40,'Cta Cte Dolares: 0011 0250 0200653947 88')

    #Linea final de separacion
    can.line(25,25,580,26)
    can.save() 

    nombre_doc = str(proforma_info.codigoProforma) + '.pdf'
    response = HttpResponse(open('coti_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def descargar_guia(request,ind):
    pdf_name = 'guia_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)
    guia_info = guias.objects.get(id=ind)

    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica-Bold',14)
    can.drawImage('./sistema_2/static/images/logo.png',80,760,width=80,height=80)
    can.drawString(50,755,str('METALPROTEC S.A.C'))
    can.setFont('Helvetica-Bold',10)
    can.drawString(50, 730,str('DATOS DE INICIO DEL TRASLADO'))

    x_grid = [380,560]
    y_grid = [750,820]
    can.grid(x_grid,y_grid)
    
    can.drawString(425,805,'GUIA DE REMISIÓN')
    can.drawString(400,790,'ELECTRONICA - REMITENTE')
    can.drawString(430,775,'RUC: 20541628631')

    nroImp = str(guia_info.nroGuia)
    if len(nroImp) < 4:
        while len(nroImp) < 4:
            nroImp = '0' + nroImp 
    else:
        pass

    can.drawString(445,760,str(guia_info.serieGuia) + ' - ' + nroImp)

    can.setFont('Helvetica-Bold',8)
    can.drawString(50,720,'Fecha de emision :')
    can.drawString(50,710,'Fecha de entrega de bienes :')
    can.drawString(50,700,'Motivo de traslado :')
    can.drawString(50,690,'Modalidad de transporte :')
    can.drawString(50,680,'Tipo de traslado :')
    can.drawString(50,670,'Peso bruto total de la guia (KGM):')

    can.setFont('Helvetica',8)
    can.drawString(250,720,str(guia_info.fechaGuia))
    can.drawString(250,710,str(guia_info.datosTraslado[0]))
    can.drawString(250,700,str(guia_info.datosTraslado[1]))
    can.drawString(250,690,str(guia_info.datosTraslado[2]))
    can.drawString(250,680,str(guia_info.datosTraslado[3]))
    can.drawString(250,670,str(guia_info.datosTraslado[4]))

    can.setFont('Helvetica-Bold',10)
    can.drawString(50,645,str('DATOS DEL DESTINATARIO'))

    can.setFont('Helvetica-Bold',8)
    can.drawString(50,635,str('Apellidos y nombres, denominacion o razón :'))
    can.drawString(50,625,'Documento de identidad :')

    can.setFont('Helvetica',8)
    if(guia_info.cliente[1] == ''):
        can.drawString(250,635,str(guia_info.cliente[3]))
        can.drawString(250,625,str(guia_info.cliente[5]))
    else:
        can.drawString(250,635,str(guia_info.cliente[1] + ' ' + guia_info.cliente[2]))
        can.drawString(250,625,str(guia_info.cliente[4]))

    can.setFont('Helvetica-Bold',10)
    can.drawString(50,605,'DATOS DEL TRANSPORTISTA')
    can.setFont('Helvetica-Bold',8)
    can.drawString(50,595,'Razón social :')
    can.drawString(50,585,'RUC :')

    can.setFont('Helvetica',8)
    can.drawString(250,595,guia_info.datosTransportista[0])
    can.drawString(250,585,guia_info.datosTransportista[1])

    can.setFont('Helvetica-Bold',10)
    can.drawString(50,570,'DATOS DEL CONDUCTOR')
    can.setFont('Helvetica-Bold',8)
    can.drawString(50,560,'Placa del vehiculo :')
    can.drawString(50,550,'Nombre del conductor :')
    can.drawString(50,540,'DNI del conductor :')

    can.setFont('Helvetica',8)
    can.drawString(250,560,guia_info.datosVehiculo[0])
    can.drawString(250,550,guia_info.datosVehiculo[1])
    can.drawString(250,540,guia_info.datosVehiculo[2])
    
    can.setFont('Helvetica-Bold',10)
    can.drawString(50,525,'DATOS DEL PUNTO DE PARTIDA Y PUNTO DE LLEGADA')
    can.setFont('Helvetica-Bold',8)
    can.drawString(50,515,'Direccion del punto de partida :')
    can.drawString(50,505,'Direccion del punto de llegada :')

    can.setFont('Helvetica',8)
    can.drawString(250,515,'021809 - MZA. J4 LOTE. 39 URB. PASEO DEL MAR')
    can.drawString(250,505,guia_info.cliente[10])

    can.setFont('Helvetica-Bold',8)
    can.drawString(50,490,'DATOS DE LOS BIENES')
    
    x_grid = [50,560]
    y_grid = [460,485]
    can.grid(x_grid,y_grid)

    can.drawString(60,465,'Nro')
    can.drawString(90,465,'Cod.Bien')
    can.drawString(190,465,'Descripcion')
    can.drawString(460,475,'Unidad de')
    can.drawString(460,465,'Medida')
    can.drawString(520,465,'Cantidad')

    can.setFont('Helvetica',8)
    nro = 1
    coor_y = 450
    for producto in guia_info.productos:
        can.drawString(60,coor_y,str(nro))
        can.drawString(90,coor_y,str(producto[2]))
        can.drawString(190,coor_y,producto[1])
        can.drawString(460,coor_y,str(producto[3]))
        can.drawString(520,coor_y,str(producto[8]))
        coor_y = coor_y - 10
        nro = nro + 1
    
    can.setFont('Helvetica-Bold',8)
    can.drawString(60,120,'OBSERVACIONES :')
    can.setFont('Helvetica',8)
    can.drawString(60,110,guia_info.observacionesGuia)
    can.showPage()

    #Metodo para agregar segunda pagina
    #can.drawString(50,480,'Segunda pagina')
    #can.showPage()

    can.save()
    nombre_doc = str(guia_info.codigoGuia) + '.pdf'
    response = HttpResponse(open('guia_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def descargar_factura(request,ind):
    pdf_name = 'factura_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)
    proforma_info = facturas.objects.get(id=ind)

    can.drawImage('./sistema_2/static/images/logo.png',50,760,width=80,height=80)
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica-Bold',10)
    can.drawString(263,820,'METALPROTEC')
    can.setFont('Helvetica',8)
    can.drawString(263,810,'Mza. J4 Lote. 39')
    can.drawString(263,800,'info@metalprotec.com')
    can.drawString(263,790,'915256067')

    lista_x = [450,560]
    lista_y = [820,780]

    can.grid(lista_x,lista_y)
    can.setFont('Helvetica-Bold',8)
    can.drawString(469,805,'RUC: 20541628631')
    can.drawString(455,795,'FACTURA ELECTRONICA')

    numImp = str(proforma_info.nroFactura)
    if len(numImp) < 4:
        while(len(numImp) < 4):
            numImp = '0' + numImp
    else:
        pass
    can.drawString(480,785,str(proforma_info.serieFactura) + ' - ' + numImp)

    can.setFont('Helvetica',8)
    lista_x = [30,560]
    lista_y = [750,725]
    can.grid(lista_x,lista_y)
    can.drawString(35,742,'Nombre del cliente')
    can.drawString(35,730,proforma_info.cliente[3])

    lista_x = [30,560]
    lista_y = [725,700]
    can.grid(lista_x,lista_y)
    can.drawString(35,717,'Direccion del cliente')
    can.drawString(35,705,proforma_info.cliente[9])

    lista_x = [30,136,242,348,454,560]
    lista_y = [700,675]
    can.grid(lista_x,lista_y)
    lista_campos = ['Ruc','Condicion de pago','Vencimiento','Emision','Moneda']
    elementos_campos = [str(proforma_info.cliente[5]),str(proforma_info.pagoFactura),str(proforma_info.fechaVencFactura),str(proforma_info.fechaFactura),str(proforma_info.monedaFactura)]
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1
    
    lista_x = [30,265,560]
    lista_y = [675,650]
    can.grid(lista_x,lista_y)
    can.drawString(35,667,'Nro de guia')
    can.drawString(270,667,'Nro de documento')
    can.drawString(270,655,str(proforma_info.nroDocumento))

    if(proforma_info.codigosGuias is not None):
        if len(proforma_info.codigosGuias) > 0:
            can.drawString(35,655,str(proforma_info.codigosGuias))


    if proforma_info.tipoFactura == 'Servicios':
        if proforma_info.monedaFactura == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,140,180,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,140,180,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,140,180,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,140,180,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaFactura == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,140,180,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,140,180,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,140,180,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,140,180,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    if proforma_info.tipoFactura == 'Productos':
        if proforma_info.monedaFactura == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','P.UNI','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(producto[6]),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','P.UNI','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(producto[6]),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaFactura == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','P.UNI','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(producto[6]),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','P.UNI','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(producto[6]),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    lista_x = [400,480,560]
    lista_y = [180,160,140,120]
    lista_campos = ['SUB-TOTAL (S/)','IGV 18%','TOTAL VENTA (S/)']
    can.grid(lista_x,lista_y)
    i=0
    for elemento in lista_campos:
        can.drawString(lista_x[0]+5,lista_y[i]-15,elemento)
        i=i+1
    
    can.drawString(500,165,str("{:,}".format(round(total_proforma*1.0000566,2))))
    can.drawString(500,145,str(str("{:,}".format(round(total_proforma*1.0000566*0.18,2)))))
    can.drawString(500,125,str(str("{:,}".format(round(total_proforma*1.0000566*1.18,2)))))
    #can.drawString(35,165,'Son: ' + str(int(round(total_proforma*1.18,2))) + ' dolares con ' + str(round((total_proforma*1.18 - int(total_proforma*1.18)),2)) + ' centavos')
    
    lista_impresion = 150
    i = 1
    can.setFont('Times-Roman',7)
    if proforma_info.pagoFactura == 'CREDITO':
        for elemento in proforma_info.fechasCuotas:
            can.drawString(35,lista_impresion-8,'Fecha de cuota ' + str(i) + ' :')
            can.drawString(150,lista_impresion-8,elemento)
            lista_impresion = lista_impresion - 8
            i = i + 1
    
    can.save()
    nombre_doc = str(proforma_info.codigoFactura) + '.pdf'
    response = HttpResponse(open('factura_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def descargar_boleta(request,ind):
    pdf_name = 'boleta_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)
    proforma_info = boletas.objects.get(id=ind)

    can.drawImage('./sistema_2/static/images/logo.png',50,760,width=80,height=80)
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica-Bold',10)
    can.drawString(263,820,'METALPROTEC')
    can.setFont('Helvetica',8)
    can.drawString(263,810,'Mza. J4 Lote. 39')
    can.drawString(263,800,'info@metalprotec.com')
    can.drawString(263,790,'915256067')

    lista_x = [450,560]
    lista_y = [820,780]

    can.grid(lista_x,lista_y)
    can.setFont('Helvetica-Bold',8)
    can.drawString(469,805,'RUC: 20541628631')
    can.drawString(455,795,'BOLETA ELECTRONICA')
    numImp = str(proforma_info.nroBoleta)
    print(numImp)
    if len(numImp) < 4:
        while(len(numImp) < 4):
            numImp = '0' + numImp
    else:
        pass
    can.drawString(480,785,str(proforma_info.serieBoleta) + ' - ' + numImp)

    can.setFont('Helvetica',8)
    lista_x = [30,560]
    lista_y = [750,725]
    can.grid(lista_x,lista_y)
    can.drawString(35,742,'Nombre del cliente')
    can.drawString(35,730,proforma_info.cliente[1] + ' ' + proforma_info.cliente[2])

    lista_x = [30,560]
    lista_y = [725,700]
    can.grid(lista_x,lista_y)
    can.drawString(35,717,'Direccion del cliente')
    can.drawString(35,705,proforma_info.cliente[9])

    lista_x = [30,136,242,348,454,560]
    lista_y = [700,675]
    can.grid(lista_x,lista_y)
    lista_campos = ['DNI','Condicion de pago','Vencimiento','Emision','Moneda']
    elementos_campos = [str(proforma_info.cliente[4]),'CONTADO','-',str(proforma_info.fechaBoleta),str(proforma_info.monedaBoleta)]
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1

    lista_x = [30,265,560]
    lista_y = [675,650]
    can.grid(lista_x,lista_y)
    can.drawString(35,667,'Nro de guia')
    can.drawString(270,667,'Nro de documento')
    can.drawString(270,655,str(proforma_info.nroDocumento))

    if(proforma_info.codigosGuias is not None):
        if len(proforma_info.codigosGuias) > 0:
            can.drawString(35,655,str(proforma_info.codigosGuias[0]))


    if proforma_info.tipoBoleta == 'Servicios':
        if proforma_info.monedaBoleta == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaBoleta == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    if proforma_info.tipoBoleta == 'Productos':
        if proforma_info.monedaBoleta == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaBoleta == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,165,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    lista_x = [400,480,560]
    lista_y = [180,160,140,120]
    lista_campos = ['SUB-TOTAL','IGV 18%','TOTAL VENTA']
    can.grid(lista_x,lista_y)
    i=0
    for elemento in lista_campos:
        can.drawString(lista_x[0]+5,lista_y[i]-15,elemento)
        i=i+1
    
    can.drawString(500,165,str(round(total_proforma*1.00002,2)))
    can.drawString(500,145,str(round(total_proforma*0.18,2)))
    can.drawString(500,125,str(round(total_proforma*1.18*1.00002,2)))
    can.drawString(35,165,'Son: ' + str(int(total_proforma)) + ' soles con ' + str(round((total_proforma - int(total_proforma)),2)) + ' centavos')
    can.save()
    nombre_doc = str(proforma_info.codigoBoleta) + '.pdf'
    response = HttpResponse(open('boleta_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def enviar_boleta(request,ind):
    boleta_info = boletas.objects.get(id=ind)
    token_info = config_docs.objects.get(id=1)
    print(boleta_info.cliente)
    print(boleta_info.productos)
    info_data = armar_json_boleta(boleta_info)

    headers_info={"X-Auth-Token":token_info.tokenDoc,"Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/boleta'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    print(r.content)
    if((r.status_code == 200) or (r.status_code == 409)):
        boleta_info.estadoBoleta = 'Enviada'
    if(r.status_code == 401):
        boleta_info.estadoBoleta = 'Generada'
    if(r.status_code == 403):
        boleta_info.estadoBoleta = 'Generada'
    boleta_info.save()
    return HttpResponseRedirect(reverse('sistema_2:bole'))


def armar_json_boleta(boleta_info):
    productos = []
    if boleta_info.monedaBoleta == 'SOLES':
        moneda = "PEN"
        if boleta_info.tipoBoleta == 'Productos':
            i=1
            for producto in boleta_info.productos:
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6])*float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True,
                }
                productos.append(info_pro)
                i=i+1
        if boleta_info.tipoBoleta == 'Servicios':
            i = 1
            for servicio in boleta_info.servicios:
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4])*float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if boleta_info.monedaBoleta == 'DOLARES':
        moneda = "USD"
        if boleta_info.tipoBoleta == 'Productos':
            i = 1
            for producto in boleta_info.productos:
                if producto[5] == 'DOLARES':
                    precio_pro = round(float(producto[6]),2)
                if producto[5] == 'SOLES':
                    precio_pro = round(float(producto[6])/float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":producto[7],
                    },
                    "esPorcentaje": True,
                    "numeroOrden":i
                }
                productos.append(info_pro)
                i=i+1
        if boleta_info.tipoBoleta == 'Servicios':
            i = 1
            for servicio in boleta_info.servicios:
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4])/float(boleta_info.tipoCambio[1]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje": True,
                }
                productos.append(info_pro)
                i=i+1
    print(productos)
    param_data = {
        "close2u":
        {
            "tipoIntegracion":"OFFLINE",
            "tipoPlantilla":"01",
            "tipoRegistro":"PRECIOS_SIN_IGV"
        },
        "datosDocumento":
        {
            "fechaEmision":boleta_info.fechaBoleta,
            "fechaVencimiento":null,
            "formaPago":null,
            "glosa":null,
            "horaEmision":null,
            "moneda":moneda,
            "numero":int(boleta_info.nroBoleta),
            "ordencompra":null,
            "puntoEmisor":null,
            "serie":boleta_info.serieBoleta
        },
        "detalleDocumento": productos,
        "emisor":
        {
            "correo":"info@metalprotec.com",
            "nombreComercial": null,
            "nombreLegal": "METALPROTEC SAC",
            "numeroDocumentoIdentidad": "20541628631",
            "tipoDocumentoIdentidad": "RUC",
            "domicilioFiscal":
            {
                "pais":"PERU",
                "departamento":"ANCASH",
                "provincia":"SANTA",
                "distrito":"NUEVO CHIMBOTE",
                "direccon":"Mza. J4 Lote. 39",
                "ubigeo":"02712"
            }
        },
        "informacionAdicional":
        {
            "tipoOperacion":"VENTA_INTERNA",
            "coVendedor":boleta_info.vendedor[1]
        },
        "receptor":
        {
            "correo": boleta_info.cliente[6],
            "correoCopia": null,
            "domicilioFiscal":
            {
                "departamento": null,
                "direccion": boleta_info.cliente[9],
                "distrito": null,
                "pais": "PERU",
                "provincia": null,
                "ubigeo": null,
                "urbanizacion": null
            },
            "nombreComercial": null,
            "nombreLegal": str(boleta_info.cliente[1] + ' ' + boleta_info.cliente[2]),
            "numeroDocumentoIdentidad": boleta_info.cliente[4],
            "tipoDocumentoIdentidad": "DOC_NACIONAL_DE_IDENTIDAD"
        }
    }
    return param_data

@login_required(login_url='/sistema_2')
def enviar_guia(request,ind):
    guia_info = guias.objects.get(id=ind)
    token_info = config_docs.objects.get(id=1)
    print(guia_info.cliente)
    print(guia_info.productos)
    info_data = armar_json_guia(guia_info)
    print(info_data)
    headers_info={"X-Auth-Token":token_info.tokenDoc,"Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/guia-remision'
    r = requests.post(url_pedido,headers=headers_info,json=info_data)
    print(r)
    print(r.content)
    if((r.status_code == 201) or (r.status_code == 409)):
        guia_info.estadoGuia = 'Enviada'
    if(r.status_code == 401):
        guia_info.estadoGuia = 'Emitida'
    if(r.status_code == 403):
        guia_info.estadoGuia = 'Emitida'
    guia_info.save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))


def armar_json_guia(guia_info):
    productos = []
    peso = 0
    for producto in guia_info.productos:
        peso = peso + round(float(producto[11])*float(producto[8]),2)
    peso = peso + float(guia_info.datosTraslado[4])
    peso = round(peso,2)
    peso = str(int(peso))
    print(peso)
    if guia_info.cliente[3] == '':
        destinatario = {
            "nombreLegal": guia_info.cliente[1] + ' ' + guia_info.cliente[2],
            "numeroDocumentoIdentidad": guia_info.cliente[4],
            "tipoDocumentoIdentidad": "DOC_NACIONAL_DE_IDENTIDAD",
            "correo": guia_info.cliente[6]
        }
    
    if guia_info.cliente[1] == '':
        destinatario = {
            "nombreLegal": guia_info.cliente[3],
            "numeroDocumentoIdentidad": guia_info.cliente[5],
            "tipoDocumentoIdentidad": "RUC",
            "correo": guia_info.cliente[6]
        }

    i = 1
    for producto in guia_info.productos:
        info_pro = {
            "numeroOrden":i,
            "cantidad": int(float(producto[8])),
            "codigoProducto": producto[2],
            "descripcion": producto[1],
            "unidadMedida": "UNIDAD_BIENES"
        }
        productos.append(info_pro)
        i=i+1
    
    if guia_info.datosTraslado[2] == 'PUBLICO':
        guia_transportista = {
            "nombreLegal": guia_info.datosTransportista[0],
            "numeroDocumentoIdentidad": guia_info.datosTransportista[1],
            "tipoDocumentoIdentidad": "RUC"
        }
        guia_vehiculos = null
        param_data = {
            "close2u": 
            {
                "tipoIntegracion": "OFFLINE",
                "tipoPlantilla": "01",
                "tipoRegistro": "PRECIOS_SIN_IGV"
            },
            "datosDocumento":
            {
                "fechaEmision": guia_info.fechaGuia,
                "glosa": str(guia_info.observacionesGuia),
                "numero": int(guia_info.nroGuia),
                "serie": guia_info.serieGuia
            },
            "remitente":
            {
                "nombreLegal": "METALPROTEC",
                "numeroDocumentoIdentidad": "20541628631",
                "tipoDocumentoIdentidad": "RUC"
            },
            "destinatario": destinatario,
            "datosEnvio":
            {
                "motivoTraslado": guia_info.datosTraslado[1],
                "descripcionTraslado": "",
                "transbordoProgramado": "False",
                "pesoBruto": peso,
                "unidadMedida": "KILOS",
                "numeroPallet": "0",
                "modalidadTraslado": guia_info.datosTraslado[2],
                "fechaTraslado": guia_info.datosTraslado[0],
                "fechaEntrega": guia_info.datosTraslado[0],
                "puntoLlegada":
                {
                    "departamento": "",
                    "direccion": guia_info.cliente[10],
                    "distrito": "",
                    "pais": "PERU",
                    "provincia": "",
                    "ubigeo": guia_info.ubigeoGuia,
                    "urbanizacion": ""
                },
                "puntoPartida":
                {
                    "departamento": "02",
                    "direccion": "Mza. J4 Lote. 39",
                    "distrito": "NUEVO CHIMBOTE",
                    "pais": "PERU",
                    "provincia": "SANTA",
                    "ubigeo": "021809",
                    "urbanizacion": ""
                },
                "numeroContenedor": ""
            },
            "transportista": guia_transportista,
            "detalleGuia": productos
        }

    if guia_info.datosTraslado[2] == 'PRIVADO':
        guia_transportista = null
        guia_vehiculos = [
            {
                "placa":guia_info.datosVehiculo[0],
                "conductor":
                {
                    "nombreLegal":guia_info.datosVehiculo[1],
                    "numeroDocumentoIdentidad":guia_info.datosVehiculo[2],
                    "tipoDocumentoIdentidad":"DOC_NACIONAL_DE_IDENTIDAD",
                }
            }
        ]

        param_data = {
            "close2u": 
            {
                "tipoIntegracion": "OFFLINE",
                "tipoPlantilla": "01",
                "tipoRegistro": "PRECIOS_SIN_IGV"
            },
            "datosDocumento":
            {
                "fechaEmision": guia_info.fechaGuia,
                "glosa": "",
                "numero": int(guia_info.nroGuia),
                "serie": guia_info.serieGuia
            },
            "remitente":
            {
                "nombreLegal": "METALPROTEC",
                "numeroDocumentoIdentidad": "20541628631",
                "tipoDocumentoIdentidad": "RUC"
            },
            "destinatario":destinatario,
            "datosEnvio":
            {
                "motivoTraslado": guia_info.datosTraslado[1],
                "descripcionTraslado": "",
                "transbordoProgramado": "False",
                "pesoBruto": peso,
                "unidadMedida": "KILOS",
                "numeroPallet": "0",
                "modalidadTraslado": guia_info.datosTraslado[2],
                "fechaTraslado": guia_info.datosTraslado[0],
                "fechaEntrega": guia_info.datosTraslado[0],
                "puntoLlegada":
                {
                    "departamento": "",
                    "direccion": guia_info.cliente[10],
                    "distrito": "",
                    "pais": "PERU",
                    "provincia": "",
                    "ubigeo": guia_info.ubigeoGuia,
                    "urbanizacion": ""
                },
                "puntoPartida":
                {
                    "departamento": "02",
                    "direccion": "Mza. J4 Lote. 39",
                    "distrito": "NUEVO CHIMBOTE",
                    "pais": "PERU",
                    "provincia": "SANTA",
                    "ubigeo": "021809",
                    "urbanizacion": ""
                },
                "numeroContenedor": ""
            },
            "vehiculos": guia_vehiculos,
            "detalleGuia": productos
        }
    return param_data

@login_required(login_url='/sistema_2')
def enviar_factura(request,ind):
    factura_info = facturas.objects.get(id=ind)
    token_info = config_docs.objects.get(id=1)
    print(factura_info.cliente)
    print(factura_info.productos)
    info_data = armar_json_factura(factura_info)
    print(info_data)
    headers_info={"X-Auth-Token":token_info.tokenDoc,"Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/factura'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    print(r.content)
    if((r.status_code == 200) or (r.status_code == 409)):
        factura_info.estadoFactura = 'Enviada'
    if(r.status_code == 401):
        factura_info.estadoFactura = 'Generada'
    factura_info.save()
    return HttpResponseRedirect(reverse('sistema_2:fact'))


def armar_json_factura(factura_info):
    if len(factura_info.codigosGuias) > 0:
        guias_json = []
        for guia in factura_info.codigosGuias:
            datos_guia = guia.split('-')
            guia_info = {
                "tipoDocumento":"GUIAEMISIONREMITENTE",
                "numero":datos_guia[1],
                "serie":datos_guia[0],
            }
            guias_json.append(guia_info)            
    else:
        guias_json = null
    print(guias_json)
    productos = []
    valor_total = 0
    if factura_info.monedaFactura == 'SOLES':
        moneda = "PEN"
        if factura_info.tipoFactura == 'Productos':
            i=1
            for producto in factura_info.productos:
                if producto[5] == 'SOLES':
                    precio_pro = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                    precio_pro = float('%.2f' % precio_pro)
                if producto[5] == 'DOLARES':
                    precio_pro = Decimal(producto[6])*Decimal(factura_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                    precio_pro = float('%.2f' % precio_pro)
                print(precio_pro)
                valor_total = valor_total + precio_pro*round(float(producto[8]),2)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":'0',
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
        if factura_info.tipoFactura == 'Servicios':
            i = 1
            for servicio in factura_info.servicios:
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4])*float(factura_info.tipoCambio[1]),2)
                print(precio_pro)
                valor_total = valor_total + precio_pro
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if factura_info.monedaFactura == 'DOLARES':
        moneda = "USD"
        if factura_info.tipoFactura == 'Productos':
            i = 1
            for producto in factura_info.productos:
                if producto[5] == 'SOLES':
                    precio_pro = (Decimal(producto[6])/Decimal(factura_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                    precio_pro = float('%.2f' % precio_pro)
                if producto[5] == 'DOLARES':
                    precio_pro = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                    precio_pro = float('%.2f' % precio_pro)
                valor_total = valor_total + precio_pro*round(float(producto[8]),2)
                print(precio_pro)
                info_pro = {
                    "codigoProducto":producto[2],
                    "codigoProductoSunat":"",
                    "descripcion":producto[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_BIENES",
                    "cantidad":producto[8],
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":'0',
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
        if factura_info.tipoFactura == 'Servicios':
            i = 1
            for servicio in factura_info.servicios:
                if servicio[3] == 'DOLARES':
                    precio_pro = round(float(servicio[4]),2)
                if servicio[3] == 'SOLES':
                    precio_pro = round(float(servicio[4])/float(factura_info.tipoCambio[1]),2)
                print(precio_pro)
                valor_total = valor_total + precio_pro
                info_pro = {
                    "codigoProducto":servicio[0],
                    "codigoProductoSunat":"",
                    "descripcion":servicio[1],
                    "tipoAfectacion":"GRAVADO_OPERACION_ONEROSA",
                    "unidadMedida":"UNIDAD_SERVICIOS",
                    "cantidad":1,
                    "valorVentaUnitarioItem":precio_pro,
                    "descuento":{
                        "monto":servicio[5]
                    },
                    "numeroOrden":i,
                    "esPorcentaje":True
                }
                productos.append(info_pro)
                i=i+1
    if factura_info.pagoFactura == 'CONTADO':
        cuotas_info = null
    if factura_info.pagoFactura == 'CREDITO':
        cuotas_info = []
        i = 0
        tiempo_actual = datetime.today()
        tiempo_cuota = tiempo_actual
        print(valor_total)
        valor_cuotas = float('%.2f' % valor_total)
        monto = '%.2f' % ((valor_cuotas*1.18)/int(factura_info.cuotasFactura))
        print(monto)
        while i < int(factura_info.cuotasFactura):
            cuota = {
                "numero":'00' + str(i + 1),
                "fecha":factura_info.fechasCuotas[i],
                "monto":str(monto),
                "moneda":moneda
            }
            tiempo_cuota = tiempo_cuota + relativedelta(months=1)
            i = i + 1
            cuotas_info.append(cuota)
    print(cuotas_info)
    print(productos)
    param_data = {
        "close2u":
        {
            "tipoIntegracion":"OFFLINE",
            "tipoPlantilla":"01",
            "tipoRegistro":"PRECIOS_SIN_IGV"
        }, 
        "datosDocumento":
        {
            "serie":factura_info.serieFactura,
            "numero":factura_info.nroFactura,
            "moneda":moneda,
            "fechaEmision":factura_info.fechaFactura,
            "horaEmision":null,
            "fechaVencimiento":factura_info.fechaVencFactura,
            "formaPago":factura_info.pagoFactura,
            "medioPago": "DEPOSITO_CUENTA",
            "condicionPago": null,
            "ordencompra":factura_info.nroDocumento,
            "puntoEmisor":null,
            "glosa":null
        },
        "detalleDocumento":productos,
        "emisor":
        {
            "correo":"info@metalprotec.com",
            "nombreComercial": null,
            "nombreLegal": "METALPROTEC",
            "numeroDocumentoIdentidad": "20541628631",
            "tipoDocumentoIdentidad": "RUC",
            "domicilioFiscal":
            {
                "pais":"PERU",
                "departamento":"ANCASH",
                "provincia":"SANTA",
                "distrito":"NUEVO CHIMBOTE",
                "direccon":"Mza. J4 Lote. 39",
                "ubigeo":"02712"
            }
        },
        "informacionAdicional":
        {
            "tipoOperacion":"VENTA_INTERNA",
            "coVendedor":null
        },
        "receptor":
        {
            "correo":factura_info.cliente[6],
            "correoCopia":null,
            "domicilioFiscal":
            {
                "direccion":factura_info.cliente[9],
                "pais":"PERU",
            },
            "nombreComercial":null,
            "nombreLegal":factura_info.cliente[3],
            "numeroDocumentoIdentidad":factura_info.cliente[5],
            "tipoDocumentoIdentidad":"RUC"
        },
        'referencias':{
            "documentoReferenciaList":guias_json,
        },
        'cuotas':cuotas_info
    }
    return param_data

@login_required(login_url='/sistema_2')
def configurar_documentos(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    datos_doc = config_docs.objects.get(id=1)
    if request.method == 'POST':
        serieBol = request.POST.get('serieBoleta')
        nroBol = request.POST.get('nroBoleta')
        serieFac = request.POST.get('serieFactura')
        nroFac = request.POST.get('nroFactura')
        serieGui = request.POST.get('serieGuia')
        nroGui = request.POST.get('nroGuia')
        serieNota = request.POST.get('serieNota')
        nroNota = request.POST.get('nroNota')
        serieNotaFactura = request.POST.get('serieNotaFactura')
        nroNotaFactura = request.POST.get('nroNotaFactura')
        serieCoti = request.POST.get('serieCotizacion')
        nroCoti = request.POST.get('nroCotizacion')
        token_doc = request.POST.get('tokenSistema')
        datos_doc.boletaSerie = serieBol
        datos_doc.boletaNro = nroBol
        datos_doc.facturaSerie = serieFac
        datos_doc.facturaNro = serieFac
        datos_doc.facturaNro = nroFac
        datos_doc.guiaSerie = serieGui
        datos_doc.guiaNro = nroGui
        datos_doc.notaSerie = serieNota
        datos_doc.notaNro = nroNota
        datos_doc.notaFactSerie = serieNotaFactura
        datos_doc.notaFactNro = nroNotaFactura
        datos_doc.cotiSerie = serieCoti
        datos_doc.cotiNro = nroCoti
        datos_doc.tokenDoc = token_doc
        datos_doc.save()
        datos_doc = config_docs.objects.get(id=1)
        return HttpResponseRedirect(reverse('sistema_2:dashboard'))
    return render(request,'sistema_2/configurar_documentos.html',{
        'info':datos_doc,
        'usr_rol': user_logued,
    })

def gen_guia_factura(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            factura_id = data.get('factura_id')
            prodIden = data.get('prodIden')
            prodGen = data.get('prodGen')
            print(factura_id)
            print(prodIden)
            print(prodGen)
            factura_guia = facturas.objects.get(id=factura_id)
            prod_Guia = []
            print(factura_guia.productos)
            contador = 0
            while contador < len(prodGen):
                factura_guia.productos[contador][10] = str(round(float(factura_guia.productos[contador][10]),2) - round(float(prodGen[contador]),2))
                prod_Guia.append(factura_guia.productos[contador])
                contador = contador + 1
            print(factura_guia.productos)
            factura_guia.save()

            prod_mod = []
            contador = 0
            for producto in prod_Guia:
                producto[8] = prodGen[contador]
                contador = contador + 1
            
            for producto in prod_Guia:
                if round(float(producto[8]),2) == 0.00:
                    pass
                else:
                    prod_mod.append(producto)

            for producto in prod_mod:
                prod_capturado = products.objects.get(id=producto[0])
                producto.append(str(prod_capturado.pesoProducto))
                prod_capturado.save()

            if len(prod_mod) > 0:
                print('Se creara la guia')
                guia_idFactura = factura_guia.id
                guia_cliente = factura_guia.cliente
                guia_productos = prod_mod
                guia_servicios = factura_guia.servicios
                guia_vendedor = factura_guia.vendedor
                guia_pago = factura_guia.pagoFactura
                guia_moneda = factura_guia.monedaFactura
                if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                    mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
                else:
                    mes = str((datetime.now()-timedelta(hours=5)).month)
                
                if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                    dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
                else:
                    dia = str((datetime.now()-timedelta(hours=5)).day)
                
                guia_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
                guia_fecha_venc = guia_fecha
                guia_tipo = factura_guia.tipoFactura
                guia_codigo = 'GUI-' + str((datetime.now()-timedelta(hours=5)).year) + str((datetime.now()-timedelta(hours=5)).month) + str((datetime.now()-timedelta(hours=5)).day) + str((datetime.now()-timedelta(hours=5)).hour) + str((datetime.now()-timedelta(hours=5)).minute) + str((datetime.now()-timedelta(hours=5)).second)
                guia_cambio = factura_guia.tipoCambio
                guia_estado = 'Generada'
                guia_traslado = ['','','PUBLICO','','']
                guia_transportista = ['','']
                guia_vehiculo = ['','','']
                datos_doc = config_docs.objects.get(id=1)
                guia_serie = datos_doc.guiaSerie
                guia_nro = datos_doc.guiaNro
                datos_doc.guiaNro = str(int(datos_doc.guiaNro) + 1)
                datos_doc.save()
                guias(datosVehiculo=guia_vehiculo,serieGuia=guia_serie,nroGuia=guia_nro,datosTraslado=guia_traslado,datosTransportista=guia_transportista,fechaVencGuia=guia_fecha_venc,idFactura=guia_idFactura,cliente=guia_cliente,productos=guia_productos,servicios=guia_servicios,vendedor=guia_vendedor,pagoGuia=guia_pago,monedaGuia=guia_moneda,fechaGuia=guia_fecha,tipoGuia=guia_tipo,codigoGuia=guia_codigo,tipoCambio=guia_cambio,estadoGuia=guia_estado).save()
            else:
                print('No existen productos para generar la guia')
        return JsonResponse({'status': 'Todo added!'})
    else:
        return pd.json_normalize({'status':'Somenthing went wrong'})

def gen_guia_boleta(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            print(data)
            boleta_id = data.get('boleta_id')
            prodIden = data.get('prodIden')
            prodGen = data.get('prodGen')
            print(boleta_id)
            print(prodIden)
            print(prodGen)
            boleta_guia = boletas.objects.get(id=boleta_id)
            prod_Guia = []
            print(boleta_guia.productos)
            contador = 0
            while contador < len(prodGen):
                boleta_guia.productos[contador][10] = str(int(boleta_guia.productos[contador][10]) - int(prodGen[contador]))
                prod_Guia.append(boleta_guia.productos[contador])
                contador = contador + 1
            print(boleta_guia.productos)
            boleta_guia.save()
            prod_mod = []
            contador = 0
            for producto in prod_Guia:
                producto[8] = prodGen[contador]
                contador = contador + 1
            
            for producto in prod_Guia:
                if int(producto[8]) == 0:
                    pass
                else:
                    prod_mod.append(producto)

            for producto in prod_mod:
                prod_capturado = products.objects.get(id=producto[0])
                producto.append(str(prod_capturado.pesoProducto))
                prod_capturado.save()

            if len(prod_mod) > 0:
                print('Se creara la guia')
                guia_idFactura = boleta_guia.id
                guia_cliente = boleta_guia.cliente
                guia_productos = prod_mod
                guia_servicios = boleta_guia.servicios
                guia_vendedor = boleta_guia.vendedor
                guia_pago = boleta_guia.pagoBoleta
                guia_moneda = boleta_guia.monedaBoleta
                if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                    mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
                else:
                    mes = str((datetime.now()-timedelta(hours=5)).month)
                
                if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                    dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
                else:
                    dia = str((datetime.now()-timedelta(hours=5)).day)
                
                guia_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
                guia_fecha_venc = guia_fecha
                guia_tipo = boleta_guia.tipoBoleta
                guia_codigo = 'GUI-' + str((datetime.now()-timedelta(hours=5)).year) + str((datetime.now()-timedelta(hours=5)).month) + str((datetime.now()-timedelta(hours=5)).day) + str((datetime.now()-timedelta(hours=5)).hour) + str((datetime.now()-timedelta(hours=5)).minute) + str((datetime.now()-timedelta(hours=5)).second)
                guia_cambio = boleta_guia.tipoCambio
                guia_estado = 'Generada'
                guia_traslado = ['','','','','']
                guia_transportista = ['','']
                guia_vehiculo = ['','','']
                datos_doc = config_docs.objects.get(id=1)
                guia_serie = datos_doc.guiaSerie
                guia_nro = datos_doc.guiaNro
                datos_doc.guiaNro = str(int(datos_doc.guiaNro) + 1)
                datos_doc.save()
                guias(datosVehiculo=guia_vehiculo,serieGuia=guia_serie,nroGuia=guia_nro,datosTraslado=guia_traslado,datosTransportista=guia_transportista,fechaVencGuia=guia_fecha_venc,idFactura=guia_idFactura,cliente=guia_cliente,productos=guia_productos,servicios=guia_servicios,vendedor=guia_vendedor,pagoGuia=guia_pago,monedaGuia=guia_moneda,fechaGuia=guia_fecha,tipoGuia=guia_tipo,codigoGuia=guia_codigo,tipoCambio=guia_cambio,estadoGuia=guia_estado).save()
            else:
                print('No existen productos para generar la guia')
        return JsonResponse({'status': 'Todo added!'})
    else:
        return pd.json_normalize({'status':'Somenthing went wrong'})

@login_required(login_url='/sistema_2')
def gen_factura_cot(request,ind):
    moneda_soles = request.POST.get('monedaSoles')
    moneda_dolares = request.POST.get('monedaDolares')

    if moneda_soles == 'on':
        moneda_factura = 'SOLES'
    if moneda_dolares == 'on':
        moneda_factura = 'DOLARES'
    print(moneda_soles)
    print(moneda_dolares)
    cot_obtener = cotizaciones.objects.get(id=ind)
    cot_obtener.estadoProforma = 'Emitida'
    factura_cliente = cot_obtener.cliente
    factura_productos = cot_obtener.productos
    factura_servicios = cot_obtener.servicios
    factura_vendedor = cot_obtener.vendedor
    factura_pago = cot_obtener.pagoProforma
    factura_moneda = moneda_factura
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    factura_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    factura_venc = factura_fecha
    cotiFactura = cot_obtener.codigoProforma
    codigos_cotis = [cotiFactura]
    fecha_nueva = parse(factura_fecha)
    print(factura_fecha)
    factura_tipo = cot_obtener.tipoProforma
    factura_cambio = cot_obtener.tipoCambio
    factura_estado = 'Generada'
    factura_dscto = '1'
    factura_cuotas = cot_obtener.cantidadCuotas
    counter = 0
    fechas_cuotas = []
    while counter < int(factura_cuotas):
        fechas_cuotas.append(factura_fecha)
        counter = counter + 1
    factura_guias = []
    factura_nroDocumento = cot_obtener.nroDocumento
    datos_doc = config_docs.objects.get(id=1)
    factura_serie = datos_doc.facturaSerie
    factura_nro = datos_doc.facturaNro
    datos_doc.facturaNro = str(int(datos_doc.facturaNro) + 1)
    datos_doc.save()
    cot_obtener.save()
    nro_imprimir = str(factura_nro)
    while len(nro_imprimir) < 4:
        nro_imprimir = '0' + nro_imprimir
    factura_codigo = str(factura_serie) + '-' + str(nro_imprimir)
    try:
        id_last = facturas.objects.latest('id').id
        id_last = int(id_last)
    except:
        id_last = 0
    id_nuevo = id_last + 1
    facturas(codigosCotis=codigos_cotis,id=id_nuevo,fecha_emision=fecha_nueva,nroDocumento=factura_nroDocumento,codigosGuias=factura_guias,fechasCuotas=fechas_cuotas,cuotasFactura=factura_cuotas,serieFactura=factura_serie,nroFactura=factura_nro,imprimirDescuento=factura_dscto,fechaVencFactura=factura_venc,cliente=factura_cliente,productos=factura_productos,servicios=factura_servicios,vendedor=factura_vendedor,pagoFactura=factura_pago,monedaFactura=factura_moneda,fechaFactura=factura_fecha,tipoFactura=factura_tipo,codigoFactura=factura_codigo,tipoCambio=factura_cambio,estadoFactura=factura_estado).save()
    time.sleep(0.5)
    return HttpResponseRedirect(reverse('sistema_2:fact'))

@login_required(login_url='/sistema_2')
def gen_boleta_cot(request,ind):
    moneda_soles = request.POST.get('monedaSoles')
    moneda_dolares = request.POST.get('monedaDolares')

    if moneda_soles == 'on':
        moneda_boleta = 'SOLES'
    if moneda_dolares == 'on':
        moneda_boleta = 'DOLARES'
    cot_obtener = cotizaciones.objects.get(id=ind)
    cot_obtener.estadoProforma = 'Emitida'
    boleta_cliente = cot_obtener.cliente
    boleta_productos = cot_obtener.productos
    boleta_servicios = cot_obtener.servicios
    boleta_vendedor = cot_obtener.vendedor
    boleta_pago = cot_obtener.pagoProforma
    boleta_moneda = moneda_boleta
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    print(mes)
    print((datetime.now()-timedelta(hours=5)).month)
    print(dia)
    print((datetime.now()-timedelta(hours=5)).day)
    boleta_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    print(boleta_fecha)
    fecha_nueva = parse(boleta_fecha)
    boleta_venc = ''
    boleta_tipo = cot_obtener.tipoProforma
    boleta_cambio = cot_obtener.tipoCambio
    boleta_estado = 'Generada'
    boleta_dscto = '1'
    boleta_guias = []
    boleta_nroDocumento = cot_obtener.nroDocumento
    datos_doc = config_docs.objects.get(id=1)
    boleta_serie = datos_doc.boletaSerie
    boleta_nro = datos_doc.boletaNro
    datos_doc.boletaNro = str(int(datos_doc.boletaNro) + 1)
    datos_doc.save()
    cot_obtener.save()
    nro_imprimir = str(boleta_nro)
    while len(nro_imprimir) < 4:
        nro_imprimir = '0' + nro_imprimir
    boleta_codigo = str(boleta_serie) + '-' + str(nro_imprimir)
    try:
        id_last = boletas.objects.latest('id').id
        id_last = int(id_last)
    except:
        id_last = 0
    id_nuevo = id_last + 1
    boletas(id=id_nuevo,fecha_emision=fecha_nueva,nroDocumento=boleta_nroDocumento,codigosGuias=boleta_guias,serieBoleta=boleta_serie,nroBoleta=boleta_nro,imprimirDescuento=boleta_dscto,fechaVencBoleta=boleta_venc,cliente=boleta_cliente,productos=boleta_productos,servicios=boleta_servicios,vendedor=boleta_vendedor,pagoBoleta=boleta_pago,monedaBoleta=boleta_moneda,fechaBoleta=boleta_fecha,tipoBoleta=boleta_tipo,codigoBoleta=boleta_codigo,tipoCambio=boleta_cambio,estadoBoleta=boleta_estado).save()
    time.sleep(0.5)
    return HttpResponseRedirect(reverse('sistema_2:bole'))

def emitir_nota_factura(request,ind):
    return HttpResponseRedirect(reverse('sistema_2:dashboard'))

def emitir_nota_boleta(request,ind):
    return HttpResponseRedirect(reverse('sistema_2:dashboard'))

def notas_credito(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    return render(request,'sistema_2/notas_credito.html',{
        'nota':notaCredito.objects.all().order_by('id'),
        'usr_rol': user_logued,
    })

@login_required(login_url='/sistema_2')
def descargar_nota_credito(request,ind):
    pdf_name = 'nota_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)
    proforma_info = notaCredito.objects.get(id=ind)

    can.drawImage('./sistema_2/static/images/logo.png',50,760,width=80,height=80)
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica-Bold',10)
    can.drawString(263,820,'METALPROTEC')
    can.setFont('Helvetica',8)
    can.drawString(263,810,'Mza. J4 Lote. 39')
    can.drawString(263,800,'info@metalprotec.com')
    can.drawString(263,790,'915256067')

    lista_x = [450,560]
    lista_y = [820,780]

    can.grid(lista_x,lista_y)
    can.setFont('Helvetica-Bold',8)
    can.drawString(469,805,'RUC: 20541628631')
    can.drawString(467,795,'NOTA DE CREDITO')
    can.drawString(469,785,str(proforma_info.codigoNotaCredito))

    can.setFont('Helvetica',8)
    lista_x = [30,560]
    lista_y = [750,725]
    can.grid(lista_x,lista_y)
    can.drawString(35,742,'Nombre del cliente')
    if(proforma_info.tipoComprobante == 'FACTURA'):
        can.drawString(35,730,proforma_info.cliente[3])
    
    if(proforma_info.tipoComprobante == 'BOLETA'):
        can.drawString(35,730,proforma_info.cliente[1] + ' ' + proforma_info.cliente[2])

    lista_x = [30,560]
    lista_y = [725,700]
    can.grid(lista_x,lista_y)
    can.drawString(35,717,'Direccion del cliente')
    can.drawString(35,705,proforma_info.cliente[9])

    lista_x = [30,136,242,348,454,560]
    lista_y = [700,675]
    can.grid(lista_x,lista_y)
    if(proforma_info.tipoComprobante == 'FACTURA'):
        lista_campos = ['RUC','Condicion de pago','-','Emision','Moneda']
        elementos_campos = [str(proforma_info.cliente[5]),'CONTADO','-',str(proforma_info.fechaEmision),str(proforma_info.monedaNota)]
    
    if(proforma_info.tipoComprobante == 'BOLETA'):
        lista_campos = ['DNI','Condicion de pago','-','Emision','Moneda']
        elementos_campos = [str(proforma_info.cliente[4]),'CONTADO','-',str(proforma_info.fechaEmision),str(proforma_info.monedaNota)]

    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1
    
    lista_x = [30,295,560]
    lista_y = [675,650]
    can.grid(lista_x,lista_y)
    lista_campos = ['Tipo de Comprobante','Moneda del comprobante']
    elementos_campos = [proforma_info.tipoComprobante,proforma_info.monedaNota]
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1
    

    if proforma_info.tipoItemsNota == 'Servicios':
        if proforma_info.monedaNota == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaNota == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(str(servicio[5])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1                    
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for servicio in proforma_info.servicios:
                    if servicio[3] == 'SOLES':
                        precio_no_descuento = round(float(servicio[4]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100)),2)
                    if servicio[3] == 'DOLARES':
                        precio_no_descuento = round(float(servicio[4])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(servicio[4])*float(1.00-(float(servicio[5])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),'-','1',str(servicio[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    if proforma_info.tipoItemsNota == 'Productos':
        if proforma_info.monedaNota == 'DOLARES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])/float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))/float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
        if proforma_info.monedaNota == 'SOLES':
            if proforma_info.imprimirDescuento == '1':
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,440,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(str(producto[7])+' %'),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
            else:
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [650,625]
                can.grid(lista_x,lista_y)
                can.setFont('Times-Roman',8)
                lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','P.VENTA']
                i = 0
                for elemento in lista_campos:
                    can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
                    i=i+1
                lista_x = [30,60,160,200,480,520,560]
                lista_y = [625,200]
                can.grid(lista_x,lista_y)
                can.setFont('Helvetica',8)
                total_proforma = 0.00
                i = 1
                for producto in proforma_info.productos:
                    if producto[5] == 'SOLES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100)),2)
                    if producto[5] == 'DOLARES':
                        precio_no_descuento = round(float(producto[8])*float(producto[6])*float(proforma_info.tipoCambio[1]),2)
                        precio_total = round(float(producto[8])*float(producto[6])*float(1.00-(float(producto[7])/100))*float(proforma_info.tipoCambio[1]),2)
                    total_proforma=total_proforma+precio_total
                    campos = [str(i),str(producto[2]),str(producto[8]),str(producto[1]),str(precio_no_descuento),str(precio_total)]
                    j=0
                    for campo in campos:
                        can.drawString(lista_x[j]+5,lista_y[0]-(i*15),campo)
                        j = j + 1
                    i = i + 1
    lista_x = [400,480,560]
    lista_y = [180,160,140,120]
    lista_campos = ['SUB-TOTAL','IGV 18%','TOTAL VENTA']
    can.grid(lista_x,lista_y)
    i=0
    for elemento in lista_campos:
        can.drawString(lista_x[0]+5,lista_y[i]-15,elemento)
        i=i+1
    
    can.drawString(500,165,str(round(total_proforma,2)))
    can.drawString(500,145,str(round(total_proforma*0.18,2)))
    can.drawString(500,125,str(round(total_proforma*1.18,2)))
    can.drawString(35,165,'Son: ' + str(int(total_proforma)) + ' soles con ' + str(round((total_proforma - int(total_proforma)),2)) + ' centavos')
    can.save()
    nombre_doc = str(proforma_info.codigoNotaCredito) + '.pdf'
    response = HttpResponse(open('nota_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response


def enviar_nota_credito(request,ind):
    return HttpResponseRedirect(reverse('sistema_2:dashboard'))

def eliminar_nota_credito(request,ind):
    return HttpResponseRedirect(reverse('sistema_2:dashboard'))

def verificar_guia(request,ind):
    guia_verificar = guias.objects.get(id=ind)
    verificador = True

    for producto in guia_verificar.productos:
        producto_comp = products.objects.get(id=producto[0])
        print(producto_comp.stock)
        print(producto)
        if producto_comp.stock is None:
            verificador = False
        else:
            i = 0
            while i < len(producto_comp.stock):
                if producto[4] == producto_comp.stock[i][0]:
                    if round(float(producto[8]),2) > round(float(producto_comp.stock[i][1]),2):
                        verificador = False
                        print('No hay suficiente Stock')
                i = i + 1

    if verificador == True:
        guia_verificar.estadoGuia = 'Verificada'
    else:
        guia_verificar.estadoGuia = 'Generada'
    
    guia_verificar.save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))

@login_required(login_url='/sistema_2')
def gen_guia_cot(request,ind):
    moneda_soles = request.POST.get('monedaSoles')
    moneda_dolares = request.POST.get('monedaDolares')

    if moneda_soles == 'on':
        moneda_guia = 'SOLES'
    if moneda_dolares == 'on':
        moneda_guia = 'DOLARES'
    cot_gen = cotizaciones.objects.get(id=ind)
    guia_cliente = cot_gen.cliente
    guia_productos = cot_gen.productos
    print(guia_productos)
    for producto in guia_productos:
        print(producto[0])
        prod_capturado = products.objects.get(id=producto[0])
        print(prod_capturado.id)
        producto.append(str(prod_capturado.pesoProducto))
        prod_capturado.save()
    guia_servicios = cot_gen.servicios
    guia_vendedor = cot_gen.vendedor
    guia_pago = cot_gen.pagoProforma
    guia_moneda = moneda_guia
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    
    guia_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    cotiGuia = cot_gen.codigoProforma
    guia_fecha_venc = guia_fecha
    fecha_nueva = parse(guia_fecha)
    guia_tipo = cot_gen.tipoProforma
    guia_nro_cuotas = cot_gen.cantidadCuotas
    guia_cambio = cot_gen.tipoCambio
    guia_nroDocumento = cot_gen.nroDocumento
    guia_obs = cot_gen.observacionesCot
    guia_estado = 'Generada'
    guia_traslado = ['','','PUBLICO','','0']
    guia_transportista = ['','']
    guia_vehiculo = ['','','']
    datos_doc = config_docs.objects.get(id=1)
    guia_serie = datos_doc.guiaSerie
    guia_nro = datos_doc.guiaNro
    datos_doc.guiaNro = str(int(datos_doc.guiaNro) + 1)
    datos_doc.save()
    nro_imprimir = str(guia_nro)
    while len(nro_imprimir) < 4:
        nro_imprimir = '0' + nro_imprimir
    guia_codigo = str(guia_serie) + '-' + str(nro_imprimir)
    try:
        id_last = guias.objects.latest('id').id
        id_last = int(id_last)
    except:
        id_last = 0
    id_nuevo = id_last + 1
    guias(cotiRelacionada=cotiGuia,id=id_nuevo,fecha_emision=fecha_nueva,observacionesGuia=guia_obs,nroDocumento=guia_nroDocumento,cantidadCuotas=guia_nro_cuotas,datosVehiculo=guia_vehiculo,serieGuia=guia_serie,nroGuia=guia_nro,datosTraslado=guia_traslado,datosTransportista=guia_transportista,fechaVencGuia=guia_fecha_venc,cliente=guia_cliente,productos=guia_productos,servicios=guia_servicios,vendedor=guia_vendedor,pagoGuia=guia_pago,monedaGuia=guia_moneda,fechaGuia=guia_fecha,tipoGuia=guia_tipo,codigoGuia=guia_codigo,tipoCambio=guia_cambio,estadoGuia=guia_estado).save()
    cot_gen.estadoProforma = 'Emitida'
    cot_gen.save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))

@login_required(login_url='/sistema_2')
def gen_boleta_guia(request,ind):
    guia_obtener = guias.objects.get(id=ind)
    guia_obtener.estadoGuia = 'Emitida'
    boleta_cliente = guia_obtener.cliente
    boleta_productos = guia_obtener.productos
    boleta_servicios = guia_obtener.servicios
    boleta_vendedor = guia_obtener.vendedor
    boleta_pago = guia_obtener.pagoGuia
    boleta_nroDocumento = guia_obtener.nroDocumento
    boleta_moneda = guia_obtener.monedaGuia
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    print(mes)
    print((datetime.now()-timedelta(hours=5)).month)
    print(dia)
    print((datetime.now()-timedelta(hours=5)).day)
    boleta_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    print(boleta_fecha)
    fecha_nueva = parse(boleta_fecha)
    boleta_venc = ''
    boleta_tipo = guia_obtener.tipoGuia
    boleta_cambio = guia_obtener.tipoCambio
    boleta_estado = 'Generada'
    boleta_dscto = '1'
    nro_Guia = str(guia_obtener.nroGuia)
    if len(nro_Guia) < 4:
        while(len(nro_Guia) < 4):
            nro_Guia = '0' + nro_Guia
    else:
        pass
    cod_guia = guia_obtener.serieGuia + '-' + nro_Guia
    boleta_guias = []
    boleta_guias.append(cod_guia)
    datos_doc = config_docs.objects.get(id=1)
    boleta_serie = datos_doc.boletaSerie
    boleta_nro = datos_doc.boletaNro
    datos_doc.boletaNro = str(int(datos_doc.boletaNro) + 1)
    datos_doc.save()
    guia_obtener.save()
    nro_imprimir = str(boleta_nro)
    while len(nro_imprimir) < 4:
        nro_imprimir = '0' + nro_imprimir
    boleta_codigo = str(boleta_serie) + '-' + str(nro_imprimir)
    try:
        id_last = boletas.objects.latest('id').id
        id_last = int(id_last)
    except:
        id_last = 0
    id_nuevo = id_last + 1
    boletas(id=id_nuevo,fecha_emision=fecha_nueva,nroDocumento=boleta_nroDocumento,codigosGuias=boleta_guias,serieBoleta=boleta_serie,nroBoleta=boleta_nro,imprimirDescuento=boleta_dscto,fechaVencBoleta=boleta_venc,cliente=boleta_cliente,productos=boleta_productos,servicios=boleta_servicios,vendedor=boleta_vendedor,pagoBoleta=boleta_pago,monedaBoleta=boleta_moneda,fechaBoleta=boleta_fecha,tipoBoleta=boleta_tipo,codigoBoleta=boleta_codigo,tipoCambio=boleta_cambio,estadoBoleta=boleta_estado).save()
    time.sleep(0.5)
    return HttpResponseRedirect(reverse('sistema_2:bole'))

@login_required(login_url='/sistema_2')
def gen_factura_guia(request,ind):
    guia_obtener = guias.objects.get(id=ind)
    guia_obtener.estadoGuia = 'Emitida'
    factura_cliente = guia_obtener.cliente
    factura_productos = guia_obtener.productos
    factura_servicios = guia_obtener.servicios
    factura_vendedor = guia_obtener.vendedor
    factura_pago = guia_obtener.pagoGuia
    factura_nroDocumento = guia_obtener.nroDocumento
    factura_moneda = guia_obtener.monedaGuia
    if(int((datetime.now()-timedelta(hours=5)).month) < 10):
        mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
    else:
        mes = str((datetime.now()-timedelta(hours=5)).month)
    
    if(int((datetime.now()-timedelta(hours=5)).day) < 10):
        dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
    else:
        dia = str((datetime.now()-timedelta(hours=5)).day)
    factura_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
    factura_venc = factura_fecha
    print(factura_fecha)
    fecha_nueva = parse(factura_fecha)
    factura_tipo = guia_obtener.tipoGuia
    factura_cambio = guia_obtener.tipoCambio
    factura_estado = 'Generada'
    factura_dscto = '1'
    factura_cuotas = guia_obtener.cantidadCuotas
    counter = 0
    fechas_cuotas = []
    while counter < int(factura_cuotas):
        fechas_cuotas.append(factura_fecha)
        counter = counter + 1
    nro_Guia = str(guia_obtener.nroGuia)
    if len(nro_Guia) < 4:
        while(len(nro_Guia) < 4):
            nro_Guia = '0' + nro_Guia
    else:
        pass
    cod_guia = guia_obtener.serieGuia + '-' + nro_Guia
    factura_guias = []
    factura_guias.append(cod_guia)
    factura_cotis = []
    factura_cotis.append(guia_obtener.cotiRelacionada) 
    datos_doc = config_docs.objects.get(id=1)
    factura_serie = datos_doc.facturaSerie
    factura_nro = datos_doc.facturaNro
    datos_doc.facturaNro = str(int(datos_doc.facturaNro) + 1)
    datos_doc.save()
    guia_obtener.save()
    nro_imprimir = str(factura_nro)
    while len(nro_imprimir) < 4:
        nro_imprimir = '0' + nro_imprimir
    factura_codigo = str(factura_serie) + '-' + str(nro_imprimir)
    try:
        id_last = facturas.objects.latest('id').id
        id_last = int(id_last)
    except:
        id_last = 0
    id_nuevo = id_last + 1
    facturas(codigosCotis=factura_cotis,id=id_nuevo,fecha_emision=fecha_nueva,nroDocumento=factura_nroDocumento,codigosGuias=factura_guias,fechasCuotas=fechas_cuotas,cuotasFactura=factura_cuotas,serieFactura=factura_serie,nroFactura=factura_nro,imprimirDescuento=factura_dscto,fechaVencFactura=factura_venc,cliente=factura_cliente,productos=factura_productos,servicios=factura_servicios,vendedor=factura_vendedor,pagoFactura=factura_pago,monedaFactura=factura_moneda,fechaFactura=factura_fecha,tipoFactura=factura_tipo,codigoFactura=factura_codigo,tipoCambio=factura_cambio,estadoFactura=factura_estado).save()
    time.sleep(0.5)
    return HttpResponseRedirect(reverse('sistema_2:fact'))

def crear_factura_guias(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            guias_factura = data.get('guias')
            if comprobar_cliente(guias_factura):
                #Se extrae los datos de la guia
                guia_obtener = guias.objects.get(id=guias_factura[0])
                factura_cliente = guia_obtener.cliente
                factura_vendedor = guia_obtener.vendedor
                factura_pago = guia_obtener.pagoGuia
                factura_nroDocumento = guia_obtener.nroDocumento
                factura_moneda = guia_obtener.monedaGuia
                if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                    mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
                else:
                    mes = str((datetime.now()-timedelta(hours=5)).month)
                
                if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                    dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
                else:
                    dia = str((datetime.now()-timedelta(hours=5)).day)
                factura_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
                factura_venc = factura_fecha
                print(factura_fecha)
                fecha_nueva = parse(factura_fecha)
                factura_tipo = guia_obtener.tipoGuia
                factura_cambio = guia_obtener.tipoCambio
                factura_estado = 'Generada'
                factura_dscto = '1'
                factura_cuotas = guia_obtener.cantidadCuotas
                counter = 0
                fechas_cuotas = []
                while counter < int(factura_cuotas):
                    fechas_cuotas.append(factura_fecha)
                    counter = counter + 1
                datos_doc = config_docs.objects.get(id=1)
                factura_serie = datos_doc.facturaSerie
                factura_nro = datos_doc.facturaNro
                datos_doc.facturaNro = str(int(datos_doc.facturaNro) + 1)
                datos_doc.save()
                guia_obtener.save()
                nro_imprimir = str(factura_nro)
                while len(nro_imprimir) < 4:
                    nro_imprimir = '0' + nro_imprimir
                factura_codigo = str(factura_serie) + '-' + str(nro_imprimir)
                factura_guias = []
                productos = []
                ids_productos = []
                for guia in guias_factura:
                    guia_obtener = guias.objects.get(id=guia)
                    guia_obtener.estadoGuia = 'Emitida'
                    nro_Guia = str(guia_obtener.nroGuia)
                    if len(nro_Guia) < 4:
                        while(len(nro_Guia) < 4):
                            nro_Guia = '0' + nro_Guia
                    else:
                        pass
                    cod_guia = guia_obtener.serieGuia + '-' + nro_Guia
                    factura_guias.append(cod_guia)
                    for producto in guia_obtener.productos:
                        if str(producto[0]) in ids_productos:
                            for prods in productos:
                                if prods[0] == producto[0]:
                                    prods[8] = str(round(float(prods[8]) + float(producto[8]),2))
                                else:
                                    pass
                        else:
                            ids_productos.append(str(producto[0]))
                            productos.append(producto)
                    guia_obtener.save()
                id_last = facturas.objects.latest('id').id
                id_last = int(id_last)
                id_nuevo = id_last + 1
                factura_cotis = []
                for guia_info in factura_guias:
                    guia_mod = guias.objects.get(codigoGuia=guia_info)
                    factura_cotis.append(guia_mod.cotiRelacionada)
                    guia_mod.save()
                facturas(codigosCotis=factura_cotis,id=id_nuevo,fecha_emision=fecha_nueva,nroDocumento=factura_nroDocumento,codigosGuias=factura_guias,fechasCuotas=fechas_cuotas,cuotasFactura=factura_cuotas,serieFactura=factura_serie,nroFactura=factura_nro,imprimirDescuento=factura_dscto,fechaVencFactura=factura_venc,cliente=factura_cliente,productos=productos,vendedor=factura_vendedor,pagoFactura=factura_pago,monedaFactura=factura_moneda,fechaFactura=factura_fecha,tipoFactura=factura_tipo,codigoFactura=factura_codigo,tipoCambio=factura_cambio,estadoFactura=factura_estado).save()
            else:
                print('No se tiene al mismo cliente')
            return JsonResponse({'status': 'Todo added!'})


def crear_boleta_guias(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'POST':
            data = json.load(request)
            guias_factura = data.get('guias')
            if comprobar_cliente(guias_factura):
                #Se extrae los datos de la guia
                guia_obtener = guias.objects.get(id=guias_factura[0])
                boleta_cliente = guia_obtener.cliente
                boleta_vendedor = guia_obtener.vendedor
                boleta_pago = guia_obtener.pagoGuia
                boleta_nroDocumento = guia_obtener.nroDocumento
                boleta_moneda = guia_obtener.monedaGuia
                if(int((datetime.now()-timedelta(hours=5)).month) < 10):
                    mes = '0' + str((datetime.now()-timedelta(hours=5)).month)
                else:
                    mes = str((datetime.now()-timedelta(hours=5)).month)
                
                if(int((datetime.now()-timedelta(hours=5)).day) < 10):
                    dia = '0' + str((datetime.now()-timedelta(hours=5)).day)
                else:
                    dia = str((datetime.now()-timedelta(hours=5)).day)
                boleta_fecha = str((datetime.now()-timedelta(hours=5)).year) + '-' + mes + '-' + dia
                boleta_venc = boleta_fecha
                print(boleta_fecha)
                fecha_nueva = parse(boleta_fecha)
                boleta_tipo = guia_obtener.tipoGuia
                boleta_cambio = guia_obtener.tipoCambio
                boleta_estado = 'Generada'
                boleta_dscto = '1'
                datos_doc = config_docs.objects.get(id=1)
                boleta_serie = datos_doc.boletaSerie
                boleta_nro = datos_doc.boletaNro
                datos_doc.boletaNro = str(int(datos_doc.boletaNro) + 1)
                datos_doc.save()
                guia_obtener.save()
                nro_imprimir = str(boleta_nro)
                while len(nro_imprimir) < 4:
                    nro_imprimir = '0' + nro_imprimir
                boleta_codigo = str(boleta_serie) + '-' + str(nro_imprimir)
                boleta_guias = []
                productos = []
                ids_productos = []
                for guia in guias_factura:
                    guia_obtener = guias.objects.get(id=guia)
                    guia_obtener.estadoGuia = 'Emitida'
                    nro_Guia = str(guia_obtener.nroGuia)
                    if len(nro_Guia) < 4:
                        while(len(nro_Guia) < 4):
                            nro_Guia = '0' + nro_Guia
                    else:
                        pass
                    cod_guia = guia_obtener.serieGuia + '-' + nro_Guia
                    boleta_guias.append(cod_guia)
                    for producto in guia_obtener.productos:
                        if str(producto[0]) in ids_productos:
                            for prods in productos:
                                if prods[0] == producto[0]:
                                    prods[8] = str(round(float(prods[8]) + float(producto[8]),2))
                                else:
                                    pass
                        else:
                            ids_productos.append(str(producto[0]))
                            productos.append(producto)
                    guia_obtener.save()
                id_last = boletas.objects.latest('id').id
                id_last = int(id_last)
                id_nuevo = id_last + 1
                boletas(id=id_nuevo,fecha_emision=fecha_nueva,cliente=boleta_cliente,productos=productos,vendedor=boleta_vendedor,pagoBoleta=boleta_pago,monedaBoleta=boleta_moneda,fechaBoleta=boleta_fecha,tipoBoleta=boleta_tipo,codigoBoleta=boleta_codigo,tipoCambio=boleta_cambio,estadoBoleta=boleta_estado,fechaVenBoleta=boleta_venc,imprimirDescuento=boleta_dscto,serieBoleta=boleta_serie,nroBoleta=boleta_nro,codigosGuias=boleta_guias,nroDocumento=boleta_nroDocumento).save()
            else:
                print('No se tiene al mismo cliente')
            return JsonResponse({'status': 'Todo added!'})


def comprobar_cliente(guias_factura):
    tipoGuia = ''
    ruc = ''
    dni = ''
    if len(guias_factura) > 0:
        guia_obtener = guias.objects.get(id=guias_factura[0])
        if guia_obtener.cliente[4] == '':
            tipoGuia = 'factura'
            ruc = guia_obtener.cliente[5]
        else:
            tipoGuia = 'boleta'
            dni = guia_obtener.cliente[4]
        guia_obtener.save()

        for guia in guias_factura:
            guia_obtener = guias.objects.get(id=guia)
            if tipoGuia == 'factura':
                if guia_obtener.cliente[5] == ruc:
                    pass
                else:
                    return False
            else:
                if guia_obtener.cliente[4] == dni:
                    pass
                else:
                    return False
            guia_obtener.save()
        return True
    else:
        return False

@login_required(login_url='/sistema_2')
def download_factura(request,ind):
    factura_descargar = facturas.objects.get(id=ind)
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarPdf'
    info_data = {
        "emisor":"20541628631",
        "numero":int(factura_descargar.nroFactura),
        "serie":factura_descargar.serieFactura,
        "tipoComprobante":"01"
    }
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    convert_b64 = r.content
    info_decoded = b64decode(convert_b64,validate=True)

    if info_decoded[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')
    
    nombre_factura = 'factura_generada.pdf'
    f = open(nombre_factura, 'wb')
    f.write(info_decoded)
    f.close()
    factura_descargar.save()
    response = HttpResponse(open(nombre_factura,'rb'),content_type='application/pdf')
    nombre_descarga = str(factura_descargar.serieFactura) + '-' + str(factura_descargar.nroFactura) + '.pdf'
    nombre = 'attachment; ' + 'filename=' + nombre_descarga
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def download_boleta(request,ind):
    boleta_descargar = boletas.objects.get(id=ind)
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarPdf'
    info_data = {
        "emisor":"20541628631",
        "numero":int(boleta_descargar.nroBoleta),
        "serie":boleta_descargar.serieBoleta,
        "tipoComprobante":"03"
    }
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    convert_b64 = r.content
    info_decoded = b64decode(convert_b64,validate=True)

    if info_decoded[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')
    
    nombre_boleta = 'boleta_generada.pdf'
    f = open(nombre_boleta, 'wb')
    f.write(info_decoded)
    f.close()
    boleta_descargar.save()
    response = HttpResponse(open(nombre_boleta,'rb'),content_type='application/pdf')
    nombre_descarga = str(boleta_descargar.serieBoleta) + '-' + str(boleta_descargar.nroBoleta) + '.pdf'
    nombre = 'attachment; ' + 'filename=' + nombre_descarga
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def download_guia(request,ind):
    guia_descargar = guias.objects.get(id=ind)
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarPdf'
    info_data = {
        "emisor":"20541628631",
        "numero":int(guia_descargar.nroGuia),
        "serie":guia_descargar.serieGuia,
        "tipoComprobante":"09"
    }
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    convert_b64 = r.content
    info_decoded = b64decode(convert_b64,validate=True)

    if info_decoded[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')
    
    nombre_guia = 'guia_generada.pdf'
    nombre_descarga = str(guia_descargar.serieGuia) + '-' + str(guia_descargar.nroGuia) + '.pdf'
    f = open(nombre_guia, 'wb')
    f.write(info_decoded)
    f.close()
    guia_descargar.save()
    response = HttpResponse(open(nombre_guia,'rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_descarga
    response['Content-Disposition'] = nombre
    return response

@login_required(login_url='/sistema_2')
def verificar_factura_teFacturo(request,ind):
    factura_verificar = facturas.objects.get(id=ind)
    info_data = {
        'emisor':'20541628631',
        'numero':str(factura_verificar.nroFactura),
        'serie':str(factura_verificar.serieFactura),
        'tipoComprobante':'01'
    }
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarEstado'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    print(r.content)
    factura_verificar.estadoSunat = r.json().get('estadoSunat').get('valor')
    factura_verificar.save()
    if factura_verificar.estadoSunat == 'Aceptado' and factura_verificar.stockAct == '0':
        factura_verificar.stockAct = '1'
        factura_verificar.save()
        for producto in factura_verificar.productos:
            prod_mod = products.objects.get(codigo=producto[2])
            stknow = float(prod_mod.stockTotal)
            stkact = stknow - float(producto[8])
            stkact = str(round(stkact,2))
            prod_mod.stockTotal = stkact
            prod_mod.save()
            for almacen in prod_mod.stock:
                if almacen[0] == producto[4]:
                    almacen[1] = str(round(float(almacen[1]) - float(producto[8]),2))
                    prod_mod.save()
            prod_mod.save()
    if factura_verificar.estadoSunat == 'Anulado' and factura_verificar.stockAct == '1':
        factura_verificar.stockAct == '0'
        factura_verificar.save()
        for producto in factura_verificar.productos:
            prod_mod = products.objects.get(codigo=producto[2])
            stknow = float(prod_mod.stockTotal)
            stkact = stknow + float(producto[8])
            stkact = str(round(stkact,2))
            prod_mod.stockTotal = stkact
            prod_mod.save()
            for almacen in prod_mod.stock:
                if almacen[0] == producto[4]:
                    almacen[1] = str(round(float(almacen[1]) + float(producto[8]),2))
                    prod_mod.save()
            prod_mod.save()
    return HttpResponseRedirect(reverse('sistema_2:fact'))

@login_required(login_url='/sistema_2')
def verificar_boleta_teFacturo(request,ind):
    boleta_verificar = boletas.objects.get(id=ind)
    info_data = {
        'emisor':'20541628631',
        'numero':str(boleta_verificar.nroBoleta),
        'serie':str(boleta_verificar.serieBoleta),
        'tipoComprobante':'03'
    }
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarEstado'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    print(r.content)
    boleta_verificar.estadoSunat = r.json().get('estadoSunat').get('valor')
    boleta_verificar.save()
    return HttpResponseRedirect(reverse('sistema_2:bol'))

@login_required(login_url='/sistema_2')
def verificar_guia_teFacturo(request,ind):
    guia_verificar = guias.objects.get(id=ind)
    info_data = {
        'emisor':'20541628631',
        'numero':str(guia_verificar.nroGuia),
        'serie':str(guia_verificar.serieGuia),
        'tipoComprobante':'09'
    }
    headers_info = {"X-Auth-Token":"HUR89LVdEfuKRdtpIqHYEbj5+3YFgJxBi2ecFzzQfVB5AAERhObWzBNga6NjSgH7","Content-Type":"application/json"}
    url_pedido = 'https://invoice2u.pe/apiemisor/invoice2u/integracion/consultarEstado'
    r = requests.put(url_pedido,headers=headers_info,json=info_data)
    print(r)
    guia_verificar.estadoSunat = r.json().get('estadoSunat').get('valor')
    guia_verificar.save()
    return HttpResponseRedirect(reverse('sistema_2:gui'))

class EnSUNAT(object):
    def __init__(self):
        self.TipoRespuesta = 0
        self.MensajeRespuesta = ""
        self.RUC = ""
        self.TipoContribuyente = ""
        self.NombreComercial = ""
        self.FechaInscripcion = ""
        self.FechaInicioActividades = ""
        self.EstadoContribuyente = ""
        self.CondicionContribuyente = ""
        self.DomicilioFiscal = ""
        self.SistemaEmisionComprobante = ""
        self.ActividadComercioExterior = ""
        self.SistemaContabilidiad = ""
        self.ActividadesEconomicas = ""
        self.ComprobantesPago = ""
        self.SistemaEmisionElectrónica = ""
        self.EmisorElectrónicoDesde = ""
        self.ComprobantesElectronicos = ""
        self.AfiliadoPLEDesde = ""
        self.Padrones = ""

def ExtraerContenidoEntreTagString(cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
    respuesta = ""
    if(sensitivo):
        cadena2 = cadena.lower()
        nombreInicio = nombreInicio.lower()
        nombreFin=nombreFin.lower()
        posicionInicio = cadena2.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena2.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                respuesta = cadena[posicionInicio:posicionFin]
    else:
        posicionInicio = cadena.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                respuesta = cadena[posicionInicio:posicionFin]
    return respuesta

def ExtraerContenidoEntreTag(cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
    respuesta = list()
    if(sensitivo):
        cadena2 = cadena.lower()
        nombreInicio = nombreInicio.lower()
        nombreFin=nombreFin.lower()
        posicionInicio = cadena2.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena2.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                posicion = posicionFin + len(nombreFin)
                respuesta = [posicion, cadena[posicionInicio:posicionFin]]
    else:
        posicionInicio = cadena.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                posicion = posicionFin + len(nombreFin)
                respuesta = [posicion, cadena[posicionInicio:posicionFin]]
    return respuesta

def ObtenerDatosRUC(contenidoHTML):
    oEnSUNAT = EnSUNAT()
    nombreInicio = ""
    nombreFin = ""
    posicion = 0
    arrResultado = list()

    nombreInicio = "<HEAD><TITLE>"
    nombreFin = "</TITLE></HEAD>"
    contenidoBusqueda = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
    if (contenidoBusqueda == ".:: Pagina de Mensajes ::."):
        nombreInicio = "<p class=\"error\">"
        nombreFin = "</p>"
        oEnSUNAT.TipoRespuesta = 2
        oEnSUNAT.MensajeRespuesta = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
    elif (contenidoBusqueda == ".:: Pagina de Error ::."):
        nombreInicio = "<p class=\"error\">"
        nombreFin = "</p>"
        oEnSUNAT.TipoRespuesta = 3
        oEnSUNAT.MensajeRespuesta = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
    else:
        oEnSUNAT.TipoRespuesta = 2

        nombreInicio = "<div class=\"list-group\">"
        nombreFin = "<div class=\"panel-footer text-center\">"
        contenidoBusqueda = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        if (contenidoBusqueda == ""):
            nombreInicio = "<strong>"
            nombreFin = "</strong>"
            oEnSUNAT.MensajeRespuesta = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
            if(oEnSUNAT.MensajeRespuesta == ""):
                oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos del RUC, porque no existe la clase principal \"list-group\" en el contenido HTML"
        else:
            nombreInicio = "<h4 class=\"list-group-item-heading\">"
            nombreFin = "</h4>"
            posicion = 0

            arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
            if(len(arrResultado)> 0):
                posicion = int(arrResultado[0])
                arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                posicion = int(arrResultado[0])
                oEnSUNAT.RUC = arrResultado[1]
                oEnSUNAT.TipoRespuesta = 1
            else:
                oEnSUNAT.MensajeRespuesta = "No se puede obtener la \"Razon Social\", porque no existe la clase \"list-group-item-heading\" en el contenido HTML"

            if(oEnSUNAT.TipoRespuesta == 1):
                '''
                # Mensaje cuando el estado es "BAJA DE OFICIO" caso contrario inicia con "Tipo Contribuyente"
                # Tipo Contribuyente
                # Nombre Comercial
                # Fecha de Inscripción
                # Fecha de Inicio de Actividades
                # Estado del Contribuyente
                # Condición del Contribuyente
                # Domicilio Fiscal
                # Sistema Emisión de Comprobante
                # Actividad Comercio Exterior
                # Sistema Contabilidiad
                # Emisor electrónico desde:
                # Comprobantes Electrónicos:
                # Afiliado al PLE desde
                # n/a
                '''
                lCadena = list()
                nombreInicio = "<p class=\"list-group-item-text\">"
                nombreFin = "</p>"
                posicion = 0
                arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                while(len(arrResultado)>0):
                    posicion = int(arrResultado[0])
                    lCadena.append(arrResultado[1].strip())
                    arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                # print(lCadena)
                if(len(lCadena) == 0):
                    oEnSUNAT.TipoRespuesta = 2
                    oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos básicos, porque no existe la clase \"list-group-item-text\" en el contenido HTML"
                else:
                    inicio = 0 
                    if(len(lCadena) > 14): # Si estado es "BAJA DE OFICIO" caso contrario es 14
                        inicio = 1
                    oEnSUNAT.TipoContribuyente = lCadena[inicio]
                    oEnSUNAT.NombreComercial = lCadena[inicio + 1]
                    oEnSUNAT.FechaInscripcion = lCadena[inicio + 2]
                    oEnSUNAT.FechaInicioActividades = lCadena[inicio + 3]
                    oEnSUNAT.EstadoContribuyente = lCadena[inicio + 4]
                    oEnSUNAT.CondicionContribuyente = lCadena[inicio + 5]
                    oEnSUNAT.DomicilioFiscal = lCadena[inicio + 6]
                    oEnSUNAT.SistemaEmisionComprobante = lCadena[inicio + 7]
                    oEnSUNAT.ActividadComercioExterior = lCadena[inicio + 8]
                    oEnSUNAT.SistemaContabilidiad = lCadena[inicio + 9]
                    oEnSUNAT.EmisorElectrónicoDesde = lCadena[inicio + 10]
                    oEnSUNAT.ComprobantesElectronicos = lCadena[inicio + 11]
                    oEnSUNAT.AfiliadoPLEDesde = lCadena[inicio + 12]

                    '''
                    # Actividad(es) Económica(s)
                    # Comprobantes de Pago c/aut. de impresión (F. 806 u 816)
                    # Sistema de Emisión Electrónica # (opcional, em algunos casos no aparece)
                    # Padrones 
                    '''
                    lCadena = list()
                    nombreInicio = "<tbody>"
                    nombreFin = "</tbody>"
                    posicion = 0
                    arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    while(len(arrResultado)>0):
                        posicion = int(arrResultado[0])
                        lCadena.append(arrResultado[1].strip().replace('\r\n', ' ').replace('\t', ' '))
                        arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    if(len(lCadena) == 0):
                        oEnSUNAT.TipoRespuesta = 2
                        oEnSUNAT.MensajeRespuesta = "No se puede obtener los datos de las tablas, porque no existe el tag \"tbody\" en el contenido HTML"
                    else:
                        oEnSUNAT.ActividadesEconomicas = lCadena[0]
                        oEnSUNAT.ComprobantesPago = lCadena[1]
                        if(len(lCadena) == 4):
                            oEnSUNAT.SistemaEmisionElectrónica = lCadena[2]
                            oEnSUNAT.Padrones = lCadena[3]
                        else:
                            oEnSUNAT.Padrones = lCadena[2]

    return oEnSUNAT

def ConsultarContenidoRUC(sesion, urlReferencia, numeroRUC, numeroRandom):
    tipoRespuesta = 2
    mensajeRespuesta = ""
    obj_info = ''

    payload={}
    headers = {
    'Host': 'e-consultaruc.sunat.gob.pe',
    'Origin': 'https://e-consultaruc.sunat.gob.pe',
    'Referer': urlReferencia,
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (numeroRUC, numeroRandom)
    response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
    contenidoHTML = response.text
    

    if(response.status_code == 200):
        oEnSUNAT = ObtenerDatosRUC(contenidoHTML)
        if (oEnSUNAT.TipoRespuesta == 1):
            print(oEnSUNAT)
            tipoRespuesta = 1
            mensajeRespuesta = "Se realizó exitosamente la consulta del número de RUC " + numeroRUC
            obj_info = oEnSUNAT
        else:
            tipoRespuesta = oEnSUNAT.TipoRespuesta
            mensajeRespuesta = "No se pudo realizar la consulta del número de RUC %s.\r\nDetalle: %s" % (numeroRUC, oEnSUNAT.MensajeRespuesta)
            obj_info = ''
    else:
        mensajeRespuesta = "Ocurrió un inconveniente (%s) al consultar los datos del RUC %s.\r\nDetalle: %s" % (response.status_code, numeroRUC, contenidoHTML)
    
    return tipoRespuesta, mensajeRespuesta, response.status_code,obj_info


def ConsultarRUC(numeroRUC):
    tipoRespuesta = 2
    indicador = 0
    mensajeRespuesta = ""

    try:
        textoAleatorio = "IMPORTANTE LAS PALABRAS CLAVES DEBE SER ALEATORIO EXISTIR LETRAS Y ESTAR EN MAYUSCULA COMO RANDOM UAP UPC LIMA HOLA MUNDO COMO ESTAS TEST comparte LOS VIDEOS EN TUS REDES SOCIALES PARA MAS CONTENIDOS si quieres aprender sobre web api revisa lista de reproduccion del canal mr angel".upper()
        arrNombreAleatorio = textoAleatorio.split(' ')
        nPalabra = random.randint(0, len(arrNombreAleatorio) - 1)

        urlInicial = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"

        payload={}
        headers = {
            'Host': 'e-consultaruc.sunat.gob.pe',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }

        sesion = requests.Session()
        response = sesion.request("GET", urlInicial, headers=headers, data=payload, verify=True)

        if(response.status_code == 200):
            payload={}
            headers = {
            'Host': 'e-consultaruc.sunat.gob.pe',
            'Origin': 'https://e-consultaruc.sunat.gob.pe',
            'Referer': urlInicial,
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            }

            numeroDNI = "12345678"; # cualquier número DNI pero que exista en SUNAT.
            url = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorTipdoc&razSoc=&nroRuc=&nrodoc={numeroDNI}&contexto=ti-it&modo=1&search1=&rbtnTipo=2&tipdoc=1&search2={numeroDNI}&search3=&codigo="
            
            contenidoHTML = ""
            nIntentos = 0
            codigoEstado = 401
            # Validamos que intente hasta 3 veces si el código de respuesta es 401 Unauthorized
            while(nIntentos < 3 and codigoEstado == 401):
                response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
                codigoEstado = response.status_code
                contenidoHTML = response.text 
                nIntentos = nIntentos + 1

            if(codigoEstado == 200):
                numeroRandom = ExtraerContenidoEntreTagString(contenidoHTML, 0, "name=\"numRnd\" value=\"", "\">")
                nIntentos = 0
                codigoEstado = 401
                obj_info = ''
                # Validamos que intente hasta 3 veces si el código de respuesta es 401 Unauthorized
                while(nIntentos < 3 and codigoEstado == 401):
                    tipoRespuesta, mensajeRespuesta, codigoEstado, obj_info = ConsultarContenidoRUC(sesion, urlInicial, numeroRUC, numeroRandom)
                    nIntentos = nIntentos + 1
                indicador = 1
                if codigoEstado == 200:
                    obj_datos = obj_info
                    indicador = 1
                else:
                    obj_datos = ''
                    indicador = 0
                return indicador,obj_datos
            else:
                mensajeRespuesta = "Ocurrió un inconveniente (%s) al consultar el número ramdom del RUC %s.\r\nDetalle: %s" % (response.status_code, numeroRUC, contenidoHTML)
                indicador = 0
                obj_datos = ''
                return indicador,obj_datos                
        else:
            mensajeRespuesta = "Ocurrió un inconveniente (%s) al consultar la página principal con el RUC %s.\r\nDetalle: %s" % (response.status_code, numeroRUC, response.text)
            indicador = 0
            obj_datos = ''
            return indicador,obj_datos
        
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        print("Ocurrió el error \"%s\" al obtener los datos del RUC.\nDetalle: %s" % (str(sys.exc_info()[1]), tbinfo))
        print()
        tipoRespuesta = 3
        mensajeRespuesta = "Ocurrió el error \"%s\" al obtener los datos del RUC.\nDetalle: %s" % (str(sys.exc_info()[1]), tbinfo)
        indicador = 0
        obj_datos = ''
        return indicador,obj_datos

def obtener_datos_ruc(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            infoEmpresa = api_consultas.get_company(ind)
            if(infoEmpresa==null):
                indicador = 0
            else:
                indicador = 1
                print(infoEmpresa['nombre'])
                print(infoEmpresa['direccion'])
                print(infoEmpresa)
            if indicador == 0:
                return JsonResponse({
                    'indicador':str(indicador),
                    'Error':'No existe la info'
                })
            if indicador == 1:
                return JsonResponse({
                    'indicador':'1',
                    'domicilioFiscal':infoEmpresa['direccion'],
                    'razonSocial':infoEmpresa['nombre']

                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def obtener_stock_producto(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            producto_informacion = products.objects.get(id=ind)
            print(producto_informacion.stock)
            return JsonResponse(
                {
                    'stockPro': producto_informacion.stock,
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def actualizar_info_producto(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            producto_informacion = products.objects.get(id=ind)
            return JsonResponse(
                {
                    'nombre': producto_informacion.nombre,
                    'codigo': producto_informacion.codigo,
                    'categoria': producto_informacion.categoria,
                    'subCategoria': producto_informacion.sub_categoria,
                    'unidad_med': producto_informacion.unidad_med,
                    'cod_sunat': producto_informacion.codigo_sunat,
                    'pv_sinIGV': producto_informacion.precio_venta_sin_igv,
                    'pc_sinIGV': producto_informacion.precio_compra_sin_igv,
                    'moneda': producto_informacion.moneda,
                    'peso': producto_informacion.pesoProducto,
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def eliminar_producto_tabla(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            producto_informacion = products.objects.get(id=ind)
            producto_informacion.delete()
            return JsonResponse(
                {
                    'status':'Exitoso'
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def update_producto(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    producto_actualizar = products.objects.get(id=ind)
    return render(request,'sistema_2/update_producto.html',{
        'producto':producto_actualizar,
        'usr_rol': user_logued,
    })

def registros_bancarios(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        bancoCuenta = request.POST.get('bancoCuenta')
        monedaCuenta = request.POST.get('monedaCuenta')
        nroCuenta = request.POST.get('nroCuenta')
        saldoCuenta = request.POST.get('saldoCuenta')
        regCuenta(bancoCuenta=bancoCuenta,monedaCuenta=monedaCuenta,nroCuenta=nroCuenta,saldoCuenta=saldoCuenta).save()
        return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))
    return render(request,'sistema_2/registros_bancarios.html',{
        'cuentasBancos':regCuenta.objects.all().order_by('id'),
        'usr_rol': user_logued,
    })

def actualizar_cuenta(request,ind):
    if request.method == 'POST':
        cuenta_modificar = regCuenta.objects.get(id=ind)
        bancoCuenta = request.POST.get('bancoCuenta')
        monedaCuenta = request.POST.get('monedaCuenta')
        nroCuenta = request.POST.get('nroCuenta')
        saldoCuenta = request.POST.get('saldoCuenta')
        cuenta_modificar.bancoCuenta=bancoCuenta
        cuenta_modificar.monedaCuenta=monedaCuenta
        cuenta_modificar.nroCuenta=nroCuenta
        cuenta_modificar.saldoCuenta=saldoCuenta
        cuenta_modificar.save()
        return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))

def importar_movimientos(request):
    if request.method == 'POST':
        archivo=request.FILES['archivoExcel']
        cuentas_bancarias = regCuenta.objects.all().order_by('id')
        nombres_excel = []
        for cuenta in cuentas_bancarias:
            nombres_excel.append(cuenta.bancoCuenta + ' ' + cuenta.monedaCuenta)
        #print(nombres_excel)
        for nombre in nombres_excel:
            datos_archivo = pd.read_excel(archivo,sheet_name=nombre)
            nombre = nombre.split()
            if nombre[0] == 'BCP':
                bancoCuenta = regCuenta.objects.filter(bancoCuenta=nombre[0]).filter(monedaCuenta=nombre[1]).first()
                if bancoCuenta is not None:
                    i = 1
                    saldo_inicial = round(float(bancoCuenta.saldoCuenta),2)
                    while i < int(datos_archivo.shape[0]):
                        referencia2 = str(datos_archivo.loc[i,datos_archivo.columns[10]])
                        clienteExcel = str(datos_archivo.loc[i,datos_archivo.columns[11]])
                        saldoOperacion = str(datos_archivo.loc[i,datos_archivo.columns[4]])
                        lugarOperacion = str(datos_archivo.loc[i,datos_archivo.columns[5]])
                        horaOperacion = str(datos_archivo.loc[i,datos_archivo.columns[7]])
                        utcOperacion = str(datos_archivo.loc[i,datos_archivo.columns[9]])
                        usuarioOperacion = str(datos_archivo.loc[i,datos_archivo.columns[8]])
                        try:
                            fechaOperacion = str(datos_archivo.loc[i,datos_archivo.columns[0]])
                            print(fechaOperacion)
                            fechaOperacion = datetime.strptime(fechaOperacion,'%d/%m/%Y')
                            fechaOperacion = fechaOperacion.strftime('%d-%m-%Y')
                            fechaOperacion = parse(fechaOperacion)
                        except:
                            print('Error en la fecha anterior revisar')
                            fechaOperacion = '2022-06-05'
                            fechaOperacion = parse(fechaOperacion)
                        detalleOperacion = str(datos_archivo.loc[i,datos_archivo.columns[2]])
                        nroOperacion = str(datos_archivo.loc[i,datos_archivo.columns[6]])
                        monto = str(datos_archivo.loc[i,datos_archivo.columns[3]])
                        monto = float(monto)
                        if monto < 0:
                            tipoOperacion = 'EGRESO'
                        else:
                            tipoOperacion = 'INGRESO'
                        saldo_inicial = saldo_inicial + monto
                        montoOperacion = str(monto)
                        try:
                            ultimo_movimiento = regOperacion.objects.latest('id')
                            dat_id = ultimo_movimiento.id + 1
                        except:
                            dat_id = 1
                        regOperacion(referencia2=referencia2,clienteExcel=clienteExcel,horaOperacion=horaOperacion,usuarioOperacion=usuarioOperacion,utcOperacion=utcOperacion,lugarOperacion=lugarOperacion,saldoOperacion=saldoOperacion,id=dat_id,idCuentaBank=str(bancoCuenta.id),monedaOperacion=bancoCuenta.monedaCuenta,fechaOperacion=fechaOperacion,detalleOperacion=detalleOperacion,nroOperacion=nroOperacion,montoOperacion=montoOperacion,tipoOperacion=tipoOperacion).save()
                        i = i + 1
                    bancoCuenta.saldoCuenta = str(round(saldo_inicial,2))
                    bancoCuenta.save()
            if nombre[0] == 'BBVA':
                bancoCuenta = regCuenta.objects.filter(bancoCuenta=nombre[0]).filter(monedaCuenta=nombre[1]).first()
                if bancoCuenta is not None:
                    i = 1
                    saldo_inicial = round(float(bancoCuenta.saldoCuenta),2)
                    while i < int(datos_archivo.shape[0]):
                        clienteExcel = str(datos_archivo.loc[i,datos_archivo.columns[7]])
                        referencia2 = str(datos_archivo.loc[i,datos_archivo.columns[6]])
                        fechaOperacion = str(datos_archivo.loc[i,datos_archivo.columns[0]])
                        fechaOperacion = parse(fechaOperacion)
                        detalleOperacion = str(datos_archivo.loc[i,datos_archivo.columns[2]])
                        nroOperacion = str(datos_archivo.loc[i,datos_archivo.columns[5]])
                        monto1 = float(datos_archivo.loc[i,datos_archivo.columns[3]])
                        monto2 = float(datos_archivo.loc[i,datos_archivo.columns[4]])
                        montoOperacion = round(monto1 + monto2,2)
                        if montoOperacion < 0:
                            tipoOperacion = 'EGRESO'
                        else:
                            tipoOperacion = 'INGRESO'
                        saldo_inicial = saldo_inicial + montoOperacion
                        montoOperacion = str(round(monto1,2))
                        itfOperacion = str(round(monto2,2))
                        try:
                            ultimo_movimiento = regOperacion.objects.latest('id')
                            dat_id = ultimo_movimiento.id + 1
                        except:
                            dat_id = 1
                        regOperacion(referencia2=referencia2,clienteExcel=clienteExcel,itfOperacion=itfOperacion,id=dat_id,idCuentaBank=str(bancoCuenta.id),monedaOperacion=bancoCuenta.monedaCuenta,fechaOperacion=fechaOperacion,detalleOperacion=detalleOperacion,nroOperacion=nroOperacion,montoOperacion=montoOperacion,tipoOperacion=tipoOperacion).save()
                        i = i + 1
                    bancoCuenta.saldoCuenta = str(round(saldo_inicial,2))
                    bancoCuenta.save()
            if nombre[0] == 'SCOTIA':
                bancoCuenta = regCuenta.objects.filter(bancoCuenta=nombre[0]).filter(monedaCuenta=nombre[1]).first()
                if bancoCuenta is not None:
                    i = 1
                    saldo_inicial = round(float(bancoCuenta.saldoCuenta),2)
                    while i < int(datos_archivo.shape[0]):
                        clienteExcel = str(datos_archivo.loc[i,datos_archivo.columns[6]])
                        referencia2 = str(datos_archivo.loc[i,datos_archivo.columns[5]])
                        fechaOperacion = str(datos_archivo.loc[i,datos_archivo.columns[0]])
                        fechaOperacion = parse(fechaOperacion)
                        detalleOperacion = str(datos_archivo.loc[i,datos_archivo.columns[1]])
                        nroOperacion = str(datos_archivo.loc[i,datos_archivo.columns[2]])
                        monto1 = datos_archivo.loc[i,datos_archivo.columns[3]]
                        if math.isnan(monto1):
                            monto1 = 0
                        else:
                            monto1 = (-1)*float(monto1)
                        monto2 = datos_archivo.loc[i,datos_archivo.columns[4]]
                        if math.isnan(monto2):
                            monto2 = 0
                        else:
                            monto2 = float(monto2)
                        montoOperacion = round(monto1 + monto2,2)
                        cargoOperacion = str(round(monto1,2))
                        if montoOperacion < 0:
                            tipoOperacion = 'EGRESO'
                        else:
                            tipoOperacion = 'INGRESO'
                        try:
                            ultimo_movimiento = regOperacion.objects.latest('id')
                            dat_id = ultimo_movimiento.id + 1
                        except:
                            dat_id = 1
                        
                        #Actualizar Saldo:
                        saldo_inicial = saldo_inicial + montoOperacion
                        montoOperacion = str(round(monto2,2))
                        regOperacion(referencia2=referencia2,clienteExcel=clienteExcel,cargoOperacion=cargoOperacion,id=dat_id,idCuentaBank=str(bancoCuenta.id),monedaOperacion=bancoCuenta.monedaCuenta,fechaOperacion=fechaOperacion,detalleOperacion=detalleOperacion,nroOperacion=nroOperacion,montoOperacion=montoOperacion,tipoOperacion=tipoOperacion).save()
                        i = i + 1
                    bancoCuenta.saldoCuenta = str(round(saldo_inicial,2))
                    bancoCuenta.save()    
        return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))

def eliminar_cuenta(request,ind):
    regCuenta.objects.get(id=ind).delete()
    return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))

def ver_movimientos(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    registros_mov = regOperacion.objects.filter(idCuentaBank=ind).order_by('-fechaOperacion')
    cuenta_info = regCuenta.objects.get(id=ind)
    nombreBanco = cuenta_info.bancoCuenta
    monedaBanco = cuenta_info.monedaCuenta
    saldoBanco = cuenta_info.saldoCuenta
    cuenta_info.save()

    if 'Filtrar' in request.POST:
        print('Se esta filtrando la info')
        fecha_inicial = str(request.POST.get('fecha_inicio'))
        fecha_final = str(request.POST.get('fecha_fin'))
        if fecha_inicial != '' and fecha_final != '':
            movimientos_filtrados = registros_mov.filter(fechaOperacion__range=[fecha_inicial,fecha_final])
            return render(request,'sistema_2/mov_bancarios.html',{
                'operacionBanco':movimientos_filtrados.order_by('-fechaOperacion'),
                'fecha_inicial':fecha_inicial,
                'fecha_final':fecha_final,
                'nombreBanco': nombreBanco,
                'monedaBanco': monedaBanco,
                'saldoBanco':saldoBanco,
                'identificador':ind,
                'usr_rol': user_logued,
            })
    elif 'Exportar' in request.POST:
        print('Se solicita el excel')
        fecha_inicial = str(request.POST.get('fecha_inicio'))
        fecha_final = str(request.POST.get('fecha_fin'))
        datos_banco = regCuenta.objects.get(id=ind)
        nombre_excel = datos_banco.bancoCuenta + ' ' + datos_banco.monedaCuenta
        if datos_banco.bancoCuenta == 'BCP':
            if fecha_inicial != '' and fecha_final != '':
                movimientos_filtrados = registros_mov.filter(fechaOperacion__range=[fecha_inicial,fecha_final])
                info_movimientos=[]
                for movi_info in movimientos_filtrados:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.saldoOperacion,movi_info.lugarOperacion,movi_info.nroOperacion,movi_info.horaOperacion,movi_info.usuarioOperacion,movi_info.utcOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['Fecha','Fecha valuta','Descripcion operacion','Monto','Saldo','Sucursal-Agencia','Operacion numero','Operacion hora','Usuario','UTC','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.active.column_dimensions['K'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                mov_exportar = regOperacion.objects.filter(idCuentaBank=ind).order_by('-fechaOperacion')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.saldoOperacion,movi_info.lugarOperacion,movi_info.nroOperacion,movi_info.horaOperacion,movi_info.usuarioOperacion,movi_info.utcOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['Fecha','Fecha valuta','Descripcion operacion','Monto','Saldo','Sucursal-Agencia','Operacion numero','Operacion hora','Usuario','UTC','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.active.column_dimensions['K'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
        if datos_banco.bancoCuenta == 'BBVA':
            if fecha_inicial != '' and fecha_final != '':
                movimientos_filtrados = registros_mov.filter(fechaOperacion__range=[fecha_inicial,fecha_final])
                info_movimientos=[]
                for movi_info in movimientos_filtrados:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.itfOperacion,movi_info.nroOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['F.Operacion','F.Valor','Referencia','Importe','ITF','Num.Mvto','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                mov_exportar = regOperacion.objects.filter(idCuentaBank=ind).order_by('-fechaOperacion')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.itfOperacion,movi_info.nroOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['F.Operacion','F.Valor','Referencia','Importe','ITF','Num.Mvto','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
        if datos_banco.bancoCuenta == 'SCOTIA':
            if fecha_inicial != '' and fecha_final != '':
                movimientos_filtrados = registros_mov.filter(fechaOperacion__range=[fecha_inicial,fecha_final])
                info_movimientos=[]
                for movi_info in movimientos_filtrados:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.detalleOperacion,movi_info.nroOperacion,movi_info.cargoOperacion,movi_info.montoOperacion,movi_info.clienteExcel,movi_info.referencia2,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['FECHA','DESCRIPCION','Nro.DOC','CARGO','ABONO','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
            else:
                mov_exportar = regOperacion.objects.filter(idCuentaBank=ind).order_by('-fechaOperacion')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.detalleOperacion,movi_info.nroOperacion,movi_info.cargoOperacion,movi_info.montoOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['FECHA','DESCRIPCION','Nro.DOC','CARGO','ABONO','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel('info_excel.xlsx',sheet_name=nombre_excel,index=False)
                doc_excel = openpyxl.load_workbook("info_excel.xlsx")
                doc_excel.active.column_dimensions['A'].width = 30
                doc_excel.active.column_dimensions['B'].width = 30
                doc_excel.active.column_dimensions['C'].width = 30
                doc_excel.active.column_dimensions['D'].width = 30
                doc_excel.active.column_dimensions['E'].width = 30
                doc_excel.active.column_dimensions['F'].width = 30
                doc_excel.active.column_dimensions['G'].width = 30
                doc_excel.active.column_dimensions['H'].width = 30
                doc_excel.active.column_dimensions['I'].width = 30
                doc_excel.active.column_dimensions['J'].width = 30
                doc_excel.save("info_excel.xlsx")
                response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
                response['Content-Disposition'] = nombre
                return response
    return render(request,'sistema_2/mov_bancarios.html',{
        'operacionBanco':registros_mov,
        'nombreBanco': nombreBanco,
        'monedaBanco': monedaBanco,
        'saldoBanco':saldoBanco,
        'identificador':ind,
        'usr_rol': user_logued,
    })

def update_mov(request,ind):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    mov_actualizar = regOperacion.objects.get(id=ind)
    clientes = clients.objects.all()
    users_info = userProfile.objects.all()
    facturas_info = facturas.objects.all()
    guias_info = guias.objects.all()
    try:
        vendedor_info = str(mov_actualizar.vendedorOperacion[0])
    except:
        vendedor_info = '0'
    try:
        cliente_info = int(mov_actualizar.clienteOperacion[0])
    except:
        cliente_info = 0
    return render(request,'sistema_2/update_mov.html',{
        'operacion':mov_actualizar,
        'clientes':clientes,
        'usuarios':users_info,
        'facturas':facturas_info,
        'guias':guias_info,
        'id_bank':mov_actualizar.idCuentaBank,
        'vendedor':vendedor_info,
        'cliente_info':cliente_info,
        'usr_rol': user_logued,
    })

def actualizar_mov(request,ind):
    if request.method == 'POST':
        mov_actualizar = regOperacion.objects.get(id=ind)
        info_cliente = request.POST.get('infoCliente')
        info_factura = request.POST.get('infoFactura')
        info_guia = request.POST.get('infoGuia')
        info_vendedor = request.POST.get('infoVendedor')
        info_cotizacion = request.POST.get('infoCotizacion')
        clienteReg = clients.objects.get(id=info_cliente)
        arreglo_cliente = [clienteReg.id,clienteReg.nombre,clienteReg.apellido,clienteReg.razon_social,clienteReg.dni,clienteReg.ruc]
        clienteReg.save()
        arreglo_guias = info_guia.split(',')
        arreglo_facturas = info_factura.split(',')
        arreglo_cotis = info_cotizacion.split(',')
        print(info_vendedor)
        if info_vendedor != '':
            vendedorReg = userProfile.objects.get(codigo=info_vendedor)
            arreglo_vendedor = [vendedorReg.id,vendedorReg.usuario.username,vendedorReg.codigo]
        else:
            arreglo_vendedor = []
        vendedorReg.save()
        mov_actualizar.clienteOperacion = arreglo_cliente
        mov_actualizar.comprobanteOperacion = arreglo_facturas
        mov_actualizar.cotizacionOperacion = arreglo_cotis
        mov_actualizar.guiaOperacion = arreglo_guias
        mov_actualizar.vendedorOperacion = arreglo_vendedor

        print(mov_actualizar.comprobanteOperacion[0] == None)
        if (mov_actualizar.comprobanteOperacion[0] == None or mov_actualizar.comprobanteOperacion[0] == 'SinSeleccion'):
            mov_actualizar.estadoOperacion = 'INCOMPLETO'
        else:
            mov_actualizar.estadoOperacion = 'COMPLETO'
        ruta_nombre = '/sistema_2/ver_movimientos/' + str(mov_actualizar.idCuentaBank)
        mov_actualizar.save()
        return redirect(ruta_nombre)
        #return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))
    

def obtener_facturas_cotizaciones_cliente(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            print(ind)
            cliente_info = clients.objects.get(id=ind)
            facturas_info = facturas.objects.all().filter(facturaPagada='0')
            boletas_info = boletas.objects.all()
            cotis_info = cotizaciones.objects.all()
            facturas_seleccionadas = list()
            boletas_seleccionadas = list()
            cotis_seleccionadas = list()
            tipoCliente = ''
            if cliente_info.nombre == '':
                tipoCliente = 'Empresa'
                for facturaSeleccionada in facturas_info:
                    if facturaSeleccionada.cliente[5] == cliente_info.ruc:
                        arreglo_info = []
                        arreglo_info.append(facturaSeleccionada.codigoFactura)
                        facturas_seleccionadas.append(arreglo_info)
                for cotiSeleccionada in cotis_info:
                    if cotiSeleccionada.cliente[5] == cliente_info.ruc:
                        arreglo_info = []
                        arreglo_info.append(cotiSeleccionada.codigoProforma)
                        cotis_seleccionadas.append(arreglo_info)
            else:
                tipoCliente = 'Persona'
                for boletaSeleccionada in boletas_info:
                    if boletaSeleccionada.cliente[4] == cliente_info.dni:
                        arreglo_info = []
                        arreglo_info.append(boletaSeleccionada.codigoBoleta)
                        boletas_seleccionadas.append(arreglo_info)
                for cotiSeleccionada in cotis_info:
                    if cotiSeleccionada.cliente[5] == cliente_info.ruc:
                        arreglo_info = []
                        arreglo_info.append(cotiSeleccionada.codigoProforma)
                        cotis_seleccionadas.append(arreglo_info)
            return JsonResponse(
                {
                    'facturas': facturas_seleccionadas,
                    'boletas':boletas_seleccionadas,
                    'cotizaciones':cotis_seleccionadas,
                    'tipoCliente':tipoCliente,
                })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def obtener_guias_factura(request,ind):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        if request.method == 'GET':
            if(ind != 'SinSeleccion'):
                facturas_info = facturas.objects.get(codigoFactura=ind)
                print(facturas_info.codigosGuias)
                return JsonResponse(
                    {
                        'guias': facturas_info.codigosGuias,
                        'proformas':facturas_info.codigosCotis,
                        'vendedor':facturas_info.vendedor[2]
                    })
            else:
                return JsonResponse(
                    {
                        'guias': [],
                        'proformas':[]
                    })
        return JsonResponse({'status': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')

def exportar_todo(request):
    excel_total = pd.ExcelWriter('info_excel.xlsx',engine='openpyxl')
    total_cuentas = regCuenta.objects.all().order_by('id')
    for cuenta in total_cuentas:
        nombre_banco = cuenta.bancoCuenta
        nombre_pagina = cuenta.bancoCuenta + ' ' + cuenta.monedaCuenta
        if nombre_banco == 'BCP':
            mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id).order_by('id')
            info_movimientos=[]
            for movi_info in mov_exportar:
                if(len(movi_info.cotizacionOperacion)>0):
                    coti_info = movi_info.cotizacionOperacion[0]
                else:
                    coti_info = ''
                if(len(movi_info.guiaOperacion)>0):
                    guia_info = movi_info.guiaOperacion
                else:
                    guia_info = ''
                if(len(movi_info.comprobanteOperacion)>0):
                    comprobante_info = movi_info.comprobanteOperacion[0]
                else:
                    comprobante_info = ''
                if(len(movi_info.vendedorOperacion)>0):
                    vendedor_info = movi_info.vendedorOperacion[2]
                else:
                    vendedor_info = ''
                info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.saldoOperacion,movi_info.lugarOperacion,movi_info.nroOperacion,movi_info.horaOperacion,movi_info.usuarioOperacion,movi_info.utcOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
            tabla_excel = pd.DataFrame(info_movimientos,columns=['Fecha','Fecha valuta','Descripcion operacion','Monto','Saldo','Sucursal-Agencia','Operacion numero','Operacion hora','Usuario','UTC','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
            tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
        if nombre_banco == 'BBVA':
            mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id).order_by('id')
            info_movimientos=[]
            for movi_info in mov_exportar:
                if(len(movi_info.cotizacionOperacion)>0):
                    coti_info = movi_info.cotizacionOperacion[0]
                else:
                    coti_info = ''
                if(len(movi_info.guiaOperacion)>0):
                    guia_info = movi_info.guiaOperacion
                else:
                    guia_info = ''
                if(len(movi_info.comprobanteOperacion)>0):
                    comprobante_info = movi_info.comprobanteOperacion[0]
                else:
                    comprobante_info = ''
                if(len(movi_info.vendedorOperacion)>0):
                    vendedor_info = movi_info.vendedorOperacion[2]
                else:
                    vendedor_info = ''
                info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.itfOperacion,movi_info.nroOperacion,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
            tabla_excel = pd.DataFrame(info_movimientos,columns=['F.Operacion','F.Valor','Referencia','Importe','ITF','Num.Mvto','Cliente','Cotizacion','Guia','F/B','Vendedor'])
            tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
        if nombre_banco == 'SCOTIA':
            mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id).order_by('id')
            info_movimientos=[]
            for movi_info in mov_exportar:
                if(len(movi_info.cotizacionOperacion)>0):
                    coti_info = movi_info.cotizacionOperacion[0]
                else:
                    coti_info = ''
                if(len(movi_info.guiaOperacion)>0):
                    guia_info = movi_info.guiaOperacion
                else:
                    guia_info = ''
                if(len(movi_info.comprobanteOperacion)>0):
                    comprobante_info = movi_info.comprobanteOperacion[0]
                else:
                    comprobante_info = ''
                if(len(movi_info.vendedorOperacion)>0):
                    vendedor_info = movi_info.vendedorOperacion[2]
                else:
                    vendedor_info = ''
                info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.detalleOperacion,movi_info.nroOperacion,movi_info.cargoOperacion,movi_info.montoOperacion,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
            tabla_excel = pd.DataFrame(info_movimientos,columns=['FECHA','DESCRIPCION','Nro.DOC','CARGO','ABONO','Cliente','Cotizacion','Guia','F/B','Vendedor'])
            tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
    excel_total.save()
    doc_excel = openpyxl.load_workbook('info_excel.xlsx')
    for sheet in doc_excel.sheetnames:
        doc_excel[sheet].column_dimensions['A'].width = 30
        doc_excel[sheet].column_dimensions['B'].width = 30
        doc_excel[sheet].column_dimensions['C'].width = 30
        doc_excel[sheet].column_dimensions['D'].width = 30
        doc_excel[sheet].column_dimensions['E'].width = 30
        doc_excel[sheet].column_dimensions['F'].width = 30
        doc_excel[sheet].column_dimensions['G'].width = 30
        doc_excel[sheet].column_dimensions['H'].width = 30
        doc_excel[sheet].column_dimensions['I'].width = 30
        doc_excel[sheet].column_dimensions['J'].width = 30
        doc_excel[sheet].column_dimensions['K'].width = 30
        doc_excel[sheet].column_dimensions['L'].width = 30
        doc_excel[sheet].column_dimensions['M'].width = 30
        doc_excel[sheet].column_dimensions['N'].width = 30
        doc_excel[sheet].column_dimensions['O'].width = 30
        doc_excel[sheet].column_dimensions['P'].width = 30
    doc_excel.save("info_excel.xlsx")
    response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
    response['Content-Disposition'] = nombre
    return response

def descargar_filtrado(request):
    if request.method == 'POST':
        month_filter = str(request.POST.get('monthInfo'))
        while len(month_filter) < 2:
            month_filter = '0' + month_filter
        year_filter = str(request.POST.get('yearInfo'))
        print(month_filter)
        print(year_filter)
        excel_total = pd.ExcelWriter('info_excel.xlsx',engine='openpyxl')
        total_cuentas = regCuenta.objects.all().order_by('id')
        for cuenta in total_cuentas:
            nombre_banco = cuenta.bancoCuenta
            nombre_pagina = cuenta.bancoCuenta + ' ' + cuenta.monedaCuenta
            if nombre_banco == 'BCP':
                mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id,fechaOperacion__month=month_filter,fechaOperacion__year=year_filter).order_by('id')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.saldoOperacion,movi_info.lugarOperacion,movi_info.nroOperacion,movi_info.horaOperacion,movi_info.usuarioOperacion,movi_info.utcOperacion,movi_info.referencia2,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['Fecha','Fecha valuta','Descripcion operacion','Monto','Saldo','Sucursal-Agencia','Operacion numero','Operacion hora','Usuario','UTC','Referencia2','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
            if nombre_banco == 'BBVA':
                mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id,fechaOperacion__month=month_filter,fechaOperacion__year=year_filter).order_by('id')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.fechaValuta,movi_info.detalleOperacion,movi_info.montoOperacion,movi_info.itfOperacion,movi_info.nroOperacion,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['F.Operacion','F.Valor','Referencia','Importe','ITF','Num.Mvto','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
            if nombre_banco == 'SCOTIA':
                mov_exportar = regOperacion.objects.filter(idCuentaBank=cuenta.id,fechaOperacion__month=month_filter,fechaOperacion__year=year_filter).order_by('id')
                info_movimientos=[]
                for movi_info in mov_exportar:
                    if(len(movi_info.cotizacionOperacion)>0):
                        coti_info = movi_info.cotizacionOperacion[0]
                    else:
                        coti_info = ''
                    if(len(movi_info.guiaOperacion)>0):
                        guia_info = movi_info.guiaOperacion
                    else:
                        guia_info = ''
                    if(len(movi_info.comprobanteOperacion)>0):
                        comprobante_info = movi_info.comprobanteOperacion[0]
                    else:
                        comprobante_info = ''
                    if(len(movi_info.vendedorOperacion)>0):
                        vendedor_info = movi_info.vendedorOperacion[2]
                    else:
                        vendedor_info = ''
                    info_movimientos.append([movi_info.fechaOperacion.strftime('%d/%m/%Y'),movi_info.detalleOperacion,movi_info.nroOperacion,movi_info.cargoOperacion,movi_info.montoOperacion,movi_info.clienteExcel,coti_info,guia_info,comprobante_info,vendedor_info])
                tabla_excel = pd.DataFrame(info_movimientos,columns=['FECHA','DESCRIPCION','Nro.DOC','CARGO','ABONO','Cliente','Cotizacion','Guia','F/B','Vendedor'])
                tabla_excel.to_excel(excel_total,sheet_name=nombre_pagina,index=False)
        excel_total.save()
        doc_excel = openpyxl.load_workbook('info_excel.xlsx')
        for sheet in doc_excel.sheetnames:
            doc_excel[sheet].column_dimensions['A'].width = 30
            doc_excel[sheet].column_dimensions['B'].width = 30
            doc_excel[sheet].column_dimensions['C'].width = 30
            doc_excel[sheet].column_dimensions['D'].width = 30
            doc_excel[sheet].column_dimensions['E'].width = 30
            doc_excel[sheet].column_dimensions['F'].width = 30
            doc_excel[sheet].column_dimensions['G'].width = 30
            doc_excel[sheet].column_dimensions['H'].width = 30
            doc_excel[sheet].column_dimensions['I'].width = 30
            doc_excel[sheet].column_dimensions['J'].width = 30
            doc_excel[sheet].column_dimensions['K'].width = 30
            doc_excel[sheet].column_dimensions['L'].width = 30
            doc_excel[sheet].column_dimensions['M'].width = 30
            doc_excel[sheet].column_dimensions['N'].width = 30
            doc_excel[sheet].column_dimensions['O'].width = 30
            doc_excel[sheet].column_dimensions['P'].width = 30
        doc_excel.save("info_excel.xlsx")
        response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
        response['Content-Disposition'] = nombre
        return response

def comisiones(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    registros_vendedor = []
    codigoVendedor = ''
    monto_total = 0
    monto_comision = 0
    month_filter = '01'
    year_filter = '2022'
    if request.method == 'POST':
        if 'Filtrar' in request.POST:
            month_filter = str(request.POST.get('monthInfo'))
            while len(month_filter) < 2:
                month_filter = '0' + month_filter
            year_filter = str(request.POST.get('yearInfo'))
            id_vendedor = request.POST.get('id_vendedor')
            codigoVendedor = '0'
            if id_vendedor != '0':
                codigoVendedor = userProfile.objects.get(id=id_vendedor).codigo
                registros_totales = regOperacion.objects.all().order_by('fechaOperacion')
                registros_totales = registros_totales.filter(tipoOperacion='INGRESO')
                registros_totales = registros_totales.filter(estadoOperacion='COMPLETO')
                registros_totales = registros_totales.filter(fechaOperacion__month=month_filter,fechaOperacion__year=year_filter)
                for registro in registros_totales:
                    if len(registro.vendedorOperacion) > 0:
                        if registro.vendedorOperacion[0] == str(id_vendedor):
                            registros_vendedor.append(registro)
                for registro in registros_vendedor:
                    if registro.monedaOperacion == 'DOLARES':
                        factura_seleccionada = facturas.objects.filter(codigoFactura=registro.comprobanteOperacion[0]).first()
                        tipo_Cambio = float(factura_seleccionada.tipoCambio[1])
                        dato_sumar = float(registro.montoOperacion)*(tipo_Cambio)
                    if registro.monedaOperacion == 'SOLES':
                        dato_sumar = float(registro.montoOperacion)
                    monto_total = monto_total + dato_sumar
                monto_total = (monto_total / 1.18)
                monto_comision = monto_total*0.01
                monto_total = "{:.2f}".format(round(float(monto_total),2))
                monto_comision = "{:.2f}".format(round(float(monto_comision),2))
            return render(request,'sistema_2/comisiones.html',{
                'usuariosInfo':userProfile.objects.all().order_by('id'),
                'operacionesVendedor':registros_vendedor,
                'id_vendedor':codigoVendedor,
                'month_filter':month_filter,
                'year_filter':year_filter,
                'monto_total':str(monto_total),
                'monto_comision':monto_comision,
                'tipoUsuario':str(user_logued.tipo),
                'usuarioSistema':str(user_logued.codigo),
                'usr_rol': user_logued,
            })
        elif 'Exportar' in request.POST:
            month_filter = str(request.POST.get('monthInfo'))
            while len(month_filter) < 2:
                month_filter = '0' + month_filter
            year_filter = str(request.POST.get('yearInfo'))
            id_vendedor = request.POST.get('id_vendedor')
            if id_vendedor != '0':
                registros_totales = regOperacion.objects.all().order_by('fechaOperacion')
                registros_totales = registros_totales.filter(tipoOperacion='INGRESO')
                registros_totales = registros_totales.filter(estadoOperacion='COMPLETO')
                registros_totales = registros_totales.filter(fechaOperacion__month=month_filter,fechaOperacion__year=year_filter)
                for registro in registros_totales:
                    if len(registro.vendedorOperacion) > 0:
                        if registro.vendedorOperacion[0] == str(id_vendedor):
                            registros_vendedor.append(registro)
                for registro in registros_vendedor:
                    if registro.monedaOperacion == 'DOLARES':
                        factura_seleccionada = facturas.objects.filter(codigoFactura=registro.comprobanteOperacion[0]).first()
                        tipo_Cambio = float(factura_seleccionada.tipoCambio[1])
                        dato_sumar = float(registro.montoOperacion)*(tipo_Cambio)
                    if registro.monedaOperacion == 'SOLES':
                        dato_sumar = float(registro.montoOperacion)
                    monto_total = monto_total + dato_sumar
                monto_total = (monto_total / 1.18)
                monto_comision = monto_total*0.01
                monto_total = "{:.2f}".format(round(float(monto_total),2))
                monto_comision = "{:.2f}".format(round(float(monto_comision),2))
            #Metodo a efectuar con el arreglo registro vendedor y exportar sus registros en excel
            info_registro = []
            print(registros_vendedor)
            for registro in registros_vendedor:
                if registro.monedaOperacion == 'DOLARES':
                    factura_seleccionada = facturas.objects.filter(codigoFactura=registro.comprobanteOperacion[0]).first()
                    tipo_Cambio = float(factura_seleccionada.tipoCambio[1])
                    monto_convertido = round(float(registro.montoOperacion)*(tipo_Cambio),2)
                    tipo_Cambio = str(round(float(tipo_Cambio),2))
                else:
                    monto_convertido =round(float(registro.montoOperacion),2)
                    tipo_Cambio = str(1.00)
                monto_convertido = str(monto_convertido)
                monto_sinigv = str(round(float(monto_convertido)/1.18,2))
                info_registro.append([registro.fechaOperacion.strftime('%d/%m/%Y'),registro.detalleOperacion,registro.nroOperacion,registro.vendedorOperacion[2],str(regCuenta.objects.get(id=registro.idCuentaBank).bancoCuenta),registro.monedaOperacion,registro.montoOperacion,tipo_Cambio,monto_convertido,monto_sinigv])            
            info_registro.append(['','','','','','','','Monto total',str(monto_total)])
            tabla_excel = pd.DataFrame(info_registro,columns=['Fecha','Descricion','Nro de operacion','Codigo del vendedor','Banco','Moneda','Monto','Tipo de Cambio','Monto (S./)','Monto final'])
            tabla_excel.to_excel('info_excel.xlsx',index=False)
            doc_excel = openpyxl.load_workbook("info_excel.xlsx")
            doc_excel.active.column_dimensions['A'].width = 30
            doc_excel.active.column_dimensions['B'].width = 30
            doc_excel.active.column_dimensions['C'].width = 30
            doc_excel.active.column_dimensions['D'].width = 30
            doc_excel.active.column_dimensions['E'].width = 30
            doc_excel.active.column_dimensions['F'].width = 30
            doc_excel.active.column_dimensions['G'].width = 30
            doc_excel.active.column_dimensions['H'].width = 30
            doc_excel.active.column_dimensions['I'].width = 30
            doc_excel.active.column_dimensions['I'].width = 30
            doc_excel.save("info_excel.xlsx")
            response = HttpResponse(open('info_excel.xlsx','rb'),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            nombre = 'attachment; ' + 'filename=' + 'info.xlsx'
            response['Content-Disposition'] = nombre
            return response
            #Fin del metodo de exportacion
    return render(request,'sistema_2/comisiones.html',{
        'usuariosInfo':userProfile.objects.all().order_by('id'),
        'operacionesVendedor':registros_vendedor,
        'month_filter':month_filter,
        'year_filter':year_filter,
        'id_vendedor':codigoVendedor,
        'monto_total':str(monto_total),
        'monto_comision':monto_comision,
        'tipoUsuario':str(user_logued.tipo),
        'usuarioSistema':str(user_logued.codigo),
        'usr_rol': user_logued,
    })

def eliminarTodo(request):
    products.objects.all().delete()
    return HttpResponseRedirect(reverse('sistema_2:productos'))

def descargar_manual(request):
    nombre_doc = 'manual_diccionario.pdf'
    response = HttpResponse(open('manual_diccionario.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response


def descargar_proforma_dolares(request,ind):
    #Generacion del documento
    pdf_name = 'coti_generada.pdf'
    can = canvas.Canvas(pdf_name,pagesize=A4)

    #Obtencion de la informacion
    proforma_info = cotizaciones.objects.get(id=ind)
    proforma_info.monedaProforma = 'DOLARES'

    #Generacion del membrete superior derecho
    can.setStrokeColorRGB(0,0,1)
    lista_x = [400,580]
    lista_y = [720,815]
    can.grid(lista_x,lista_y)
    can.setFillColorRGB(0,0,0)
    can.setFont('Helvetica',12)
    can.drawString(440,785,'RUC: 20541628631')
    can.setFont('Helvetica-Bold',12)
    can.drawString(455,765,'COTIZACION')
    can.setFont('Helvetica',12)
    numImp = str(proforma_info.nroCotizacion)
    if len(numImp) < 4:
        while(len(numImp) < 4):
            numImp = '0' + numImp
    else:
        pass
    can.drawString(460,745,str(proforma_info.serieCotizacion) + ' - ' + numImp)

    #Generacion del logo
    can.drawImage('./sistema_2/static/images/logo_2.png',10,705,width=120,height=120)
    
    #Informacion del remitente
    can.setFont('Helvetica-Bold',10)
    can.drawString(25,705,'METALPROTEC')
    can.setFont('Helvetica',7)
    can.drawString(25,695,'LT 39 MZ. J4 URB. PASEO DEL MAR - ÁNCASH SANTA NUEVO CHIMBOTE')
    can.drawString(25,687,'Teléfono: (043) 282752')
    #can.drawString(25,679,'E-Mail: contabilidad@metalprotec.pe')

    #Generacion de la linea de separacion
    can.line(25,670,580,670)

    #Generacion de los datos del cliente
    can.drawString(25,660,'Señores:')
    if proforma_info.cliente[1] == '':
        can.drawString(120,660,str(proforma_info.cliente[3]))
    else:
        can.drawString(120,660,str(proforma_info.cliente[1]) + ' ' + str(proforma_info.cliente[2]))
    can.drawString(25,650,'Direccion:')
    can.drawString(120,650,str(proforma_info.cliente[9]))
    if proforma_info.cliente[1] == '':
        can.drawString(25,640,'Ruc:')
        can.drawString(120,640,str(proforma_info.cliente[5]))
    else:
        can.drawString(25,640,'Dni:')
        can.drawString(120,640,str(proforma_info.cliente[4]))
    can.drawString(25,630,'Forma de Pago:')
    can.drawString(120,630,str(proforma_info.pagoProforma))

    can.drawString(230,640,'Fecha de emision:')
    can.drawString(320,640,str(proforma_info.fechaProforma))
    can.drawString(230,630,'Fecha de vencimiento:')
    can.drawString(320,630,str(proforma_info.fechaVencProforma))

    can.drawString(430,640,'Nro de Documento:')
    can.drawString(520,640,str(proforma_info.nroDocumento))
    can.drawString(430,630,'Moneda:')
    can.drawString(520,630,str(proforma_info.monedaProforma))

    #Linea de separacion con los datos del vendedor
    can.line(25,620,580,620)

    #Datos del vendedor
    can.drawString(25,610,'Vendedor:')
    can.drawString(120,610,str(proforma_info.vendedor[1]))
    can.drawString(25,600,'Celular:')
    can.drawString(120,600,str(proforma_info.vendedor[3]))

    #Get the vendor email
    vendedor_info = userProfile.objects.get(id=proforma_info.vendedor[0])
    email_vendedor = vendedor_info.usuario.email
    vendedor_info.save()
    can.drawString(25,590,'Email:')
    can.drawString(120,590,str(email_vendedor))

    can.drawString(25,580,'Observacion:')
    can.drawString(120,580,str(proforma_info.observacionesCot))

    #Campos en cabecera
    lista_x = [25,580]
    lista_y = [550,565]
    can.setFillColorRGB(0,0,1)
    can.rect(25,550,555,15,fill=1)

    #Valores iniciales
    lista_x = [25,50,100,310,360,410,460,530]
    lista_y = [550,565]
    #Ingreso de campo cantidad
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[0] + 5, lista_y[0] + 3,'Cant.')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawRightString(lista_x[0] + 20,lista_y[0] + 3,str("{:.2f}".format(round(float(producto[8]),2))))
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de código de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[1] + 5, lista_y[0] + 3,'Código')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[1] + 5,lista_y[0] + 3,producto[2])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de descripcion de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[2] + 5, lista_y[0] + 3,'Descripción')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[2] + 5,lista_y[0] + 3,producto[1])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de unidad de medida de producto
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[3] + 5, lista_y[0] + 3,'Und')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        can.drawString(lista_x[3] + 5,lista_y[0] + 3,producto[3])
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    condicion_imprimir = proforma_info.imprimirVU + proforma_info.imprimirPU + proforma_info.imprimirDescuento
    if condicion_imprimir == '100':
        lista_x[4] = 360
    
    if condicion_imprimir == '010':
        lista_x[5] = 360

    if condicion_imprimir == '001':
        lista_x[6] = 360
    
    if condicion_imprimir == '110':
        lista_x[4] = 360
        lista_x[5] = 420

    if condicion_imprimir == '101':
        lista_x[4] = 360
        lista_x[6] = 420
    
    if condicion_imprimir == '011':
        lista_x[5] = 360
        lista_x[6] = 420
    
    if condicion_imprimir == '111':
        lista_x[4] = 360
        lista_x[5] = 420
        lista_x[6] = 480

    if proforma_info.imprimirVU == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo de unidad de medida de producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[4] - 5, lista_y[0] + 3,'V.U sin IGV')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            if proforma_info.monedaProforma == 'SOLES':
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                if producto[5] == 'SOLES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            if proforma_info.monedaProforma == 'DOLARES':
                if producto[5] == 'SOLES':
                    vu_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            can.drawRightString(lista_x[4] + 20,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % vu_producto)))
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    if proforma_info.imprimirPU == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo del precio con IGV de producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[5] - 5, lista_y[0]+3,'P.U con IGV')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            if proforma_info.monedaProforma == 'SOLES':
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                if producto[5] == 'SOLES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            if proforma_info.monedaProforma == 'DOLARES':
                if producto[5] == 'SOLES':
                    vu_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                if producto[5] == 'DOLARES':
                    vu_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            can.drawRightString(lista_x[5] + 20,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % (vu_producto*Decimal(1.18)))))
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    
    if proforma_info.imprimirDescuento == '1':
        #Valores iniciales
        lista_y = [550,565]
        #Ingreso de campo de descuento del producto
        can.setFillColorRGB(1,1,1)
        can.setFont('Helvetica-Bold',7)
        can.drawString(lista_x[6], lista_y[0] + 3,'Dscto')
        can.setFont('Helvetica',7)
        can.setFillColorRGB(0,0,0)
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        for producto in proforma_info.productos:
            can.drawRightString(lista_x[6] + 20,lista_y[0] + 3,str(producto[7]) + ' %')
            lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Valores iniciales
    lista_y = [550,565]
    #Ingreso de campo de valor de venta del producto
    total_precio = Decimal(0.0000)
    can.setFillColorRGB(1,1,1)
    can.setFont('Helvetica-Bold',7)
    can.drawString(lista_x[7] + 5, lista_y[0] + 3,'Valor Venta')
    can.setFont('Helvetica',7)
    can.setFillColorRGB(0,0,0)
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]
    for producto in proforma_info.productos:
        if proforma_info.monedaProforma == 'SOLES':
            if producto[5] == 'DOLARES':
                v_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
            if producto[5] == 'SOLES':
                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        if proforma_info.monedaProforma == 'DOLARES':
            if producto[5] == 'SOLES':
                v_producto = (Decimal(producto[6])/Decimal(proforma_info.tipoCambio[1]))*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
            if producto[5] == 'DOLARES':
                v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        #v_producto = round(v_producto,2)
        can.drawRightString(lista_x[7] + 45,lista_y[0] + 3,"{:,}".format(Decimal('%.2f' % Decimal(v_producto))))
        lista_y = [lista_y[0] - 15,lista_y[1] - 15]
        total_precio = Decimal(total_precio) + Decimal(v_producto)

    #Linea de separacion con los datos finales
    can.line(25,lista_y[1],580,lista_y[1])

    #Impresion de total venta
    can.drawRightString(480,lista_y[0]+4,'Total Venta Grabada')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % total_precio)))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Impresion de total IGV
    igv_precio = Decimal('%.2f' % total_precio)*Decimal(0.18)
    can.drawRightString(480,lista_y[0]+4,'Total IGV')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % igv_precio)))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Impresion de importe total
    precio_final = Decimal('%.2f' % total_precio)*Decimal(1.18)
    can.drawRightString(480,lista_y[0]+4,'Importe Total de la Venta')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'S/')
    else:
        can.drawRightString(490,lista_y[0]+4,'$')
    can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % Decimal(precio_final))))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion
    can.line(480,lista_y[1],580,lista_y[1])

    #Calculo del valor en soles
    total_soles = Decimal(0.0000)
    for producto in proforma_info.productos:
        if producto[5] == 'DOLARES':
            v_producto = Decimal(producto[6])*Decimal(proforma_info.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        if producto[5] == 'SOLES':
            v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
            v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
        total_soles = Decimal(total_soles) + Decimal(v_producto)
    final_soles = Decimal('%.2f' % total_soles)*Decimal(1.18)


    #Impresion de importe en otra moneda
    precio_final = Decimal('%.2f' % total_precio)*Decimal(1.18)
    can.drawRightString(480,lista_y[0]+4,'Importe Total de la Venta')
    if proforma_info.monedaProforma == 'SOLES':
        can.drawRightString(490,lista_y[0]+4,'$')
        can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % (Decimal(precio_final)/Decimal(proforma_info.tipoCambio[0])))))
    else:
        can.drawRightString(490,lista_y[0]+4,'S/')
        can.drawRightString(lista_x[7]+45,lista_y[0]+4,"{:,}".format(Decimal('%.2f' % Decimal(final_soles))))
    lista_y = [lista_y[0] - 15,lista_y[1] - 15]

    #Linea de separacion con los datos finales
    can.line(25,lista_y[1],580,lista_y[1])



    #Impresion de los datos bancarios
    #Scotiabank
    can.setFont('Helvetica-Bold',8)
    can.drawString(25,60,'Banco Scotiabank')
    can.setFont('Helvetica',8)
    can.drawString(25,50,'Cta Cte Soles: 000 9496505')
    can.drawString(25,40,'Cta Cte Dolares: 000 5151261')

    #BCP
    can.setFont('Helvetica-Bold',8)
    can.drawString(160,60,'Banco de Crédito del Perú')
    can.setFont('Helvetica',8)
    can.drawString(160,50,'Cta Cte Soles: 310 9888337 0 02')
    can.drawString(160,40,'Cta Cte Dolares: 310 9865292 1 35')

    #BBVA
    can.setFont('Helvetica-Bold',8)
    can.drawString(320,60,'Banco Continental BBVA')
    can.setFont('Helvetica',8)
    can.drawString(320,50,'Cta Cte Soles: 0011 0250 0200615638 80')
    can.drawString(320,40,'Cta Cte Dolares: 0011 0250 0200653947 88')

    #Linea final de separacion
    can.line(25,25,580,26)
    can.save() 

    nombre_doc = str(proforma_info.codigoProforma) + '.pdf'
    response = HttpResponse(open('coti_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

def registro_abonos(request):
    usr = userProfile.objects.all()
    usuario_logued = User.objects.get(username=request.user.username)
    user_logued = userProfile.objects.get(usuario=usuario_logued)
    if request.method == 'POST':
        print('Hola a todos')
        id_banco = request.POST.get('bancoAbono')
        nro_operacion = request.POST.get('nroOperacionAbono')
        id_cliente = request.POST.get('clienteAbono')
        codigo_comprobante = request.POST.get('facturas_cliente')
        codigo_guia = request.POST.get('guiaSeleccionada')
        codigo_coti = request.POST.get('cotiSeleccionada')
        codigo_vendedor = request.POST.get('vendedorSeleccionado')
        facturaCancelada = request.POST.get('facturaCancelada')
        datos_banco = [regCuenta.objects.get(id=id_banco).id,regCuenta.objects.get(id=id_banco).bancoCuenta,regCuenta.objects.get(id=id_banco).monedaCuenta]
        datos_cliente = [clients.objects.get(id=id_cliente).id,clients.objects.get(id=id_cliente).razon_social,clients.objects.get(id=id_cliente).ruc]
        print(id_banco)
        print(nro_operacion)
        print(id_cliente)
        print(codigo_comprobante)
        print(codigo_guia)
        print(codigo_coti)
        print(codigo_vendedor)
        abonoEstado = 'PENDIENTE'
        if facturaCancelada == 'on':
            abonoEstado = 'CANCELADO'
            comprobante_abono = facturas.objects.get(codigoFactura=codigo_comprobante)
            comprobante_abono.facturaPagada = '1'
            comprobante_abono.save()
            abonos_totales = abonosOperacion.objects.all().filter(codigo_comprobante=codigo_comprobante)
            for abono in abonos_totales:
                abono.comprobanteCancelado = 'CANCELADO'
                abono.save()
        abonosOperacion(comprobanteCancelado=abonoEstado,datos_banco=datos_banco,datos_cliente=datos_cliente,nro_operacion=nro_operacion,codigo_comprobante=codigo_comprobante,codigo_guia=codigo_guia,codigo_coti=codigo_coti,codigo_vendedor=codigo_vendedor).save()
        return HttpResponseRedirect(reverse('sistema_2:registro_abonos'))
    return render(request,'sistema_2/registro_abonos.html',{
        'bancos_totales':regCuenta.objects.all().order_by('id'),
        'clientes_totales':clients.objects.all().order_by('id'),
        'abonos_info':abonosOperacion.objects.all().order_by('id'),
        'usr_rol': user_logued,
    })

def comprobar_abonos(request):
    registros_bancos = regOperacion.objects.all().order_by('id')
    registros_abonos = abonosOperacion.objects.all().order_by('id')
    for registro in registros_abonos:
        for reg in registros_bancos:
            if(registro.nro_operacion == reg.nroOperacion) and (str(registro.datos_banco[0]) == str(reg.idCuentaBank)) and (registro.conectado == '0') and (reg.conectado_abono == '0'):
                reg.conectado_abono = '1'
                reg.comprobanteOperacion = [registro.codigo_comprobante]
                reg.guiaOperacion = [registro.codigo_guia]
                reg.cotizacionOperacion = [registro.codigo_coti]
                usuario_info = userProfile.objects.get(codigo=registro.codigo_vendedor)
                reg.vendedorOperacion = [str(usuario_info.id),str(usuario_info.usuario.username),str(usuario_info.codigo)]
                reg.estadoOperacion = 'COMPLETO'
                clienteReg = clients.objects.get(id=str(registro.datos_cliente[0]))
                reg.clienteOperacion = [clienteReg.id,clienteReg.nombre,clienteReg.apellido,clienteReg.razon_social,clienteReg.dni,clienteReg.ruc]
                reg.save()
                registro.conectado = '1'
                registro.idRegistroOp = str(reg.id)
                registro.save()
    return HttpResponseRedirect(reverse('sistema_2:registros_bancarios'))

def eliminar_abono(request,ind):
    abono_eliminar = abonosOperacion.objects.get(id=ind)
    if abono_eliminar.conectado == '1':
        regBanc = regOperacion.objects.get(id=abono_eliminar.idRegistroOp)
        regBanc.comprobanteOperacion = []
        regBanc.guiaOperacion = []
        regBanc.cotizacionOperacion = []
        regBanc.vendedorOperacion = []
        regBanc.clienteOperacion = []
        regBanc.estadoOperacion = 'INCOMPLETO'
        regBanc.conectado_abono = '0'
        regBanc.save()
    if abono_eliminar.comprobanteCancelado == 'CANCELADO':
        abonos_asociados = abonosOperacion.objects.all().filter(codigo_comprobante=abono_eliminar.codigo_comprobante)
        for abono in abonos_asociados:
            abono.comprobanteCancelado = 'PENDIENTE'
            abono.save()
        factura_abono = facturas.objects.get(codigoFactura=abono_eliminar.codigo_comprobante)
        factura_abono.facturaPagada = '0'
        factura_abono.save()
    abono_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:registro_abonos'))

def actualizar_abono(request,ind):
    if request.method == 'POST':
        abonoActualizar = abonosOperacion.objects.get(id=ind)
        id_banco = request.POST.get('bancoAbono')
        nro_operacion = request.POST.get('nroOperacionAbono')
        factura_cancelada = request.POST.get('facturaCancelada')
        datos_banco = [regCuenta.objects.get(id=id_banco).id,regCuenta.objects.get(id=id_banco).bancoCuenta,regCuenta.objects.get(id=id_banco).monedaCuenta]
        abonoActualizar.datos_banco = datos_banco
        abonoActualizar.nro_operacion = nro_operacion
        #Desenlazar abono:
        if abonoActualizar.conectado == '1':
            regBanc = regOperacion.objects.get(id=abonoActualizar.idRegistroOp)
            regBanc.comprobanteOperacion = []
            regBanc.guiaOperacion = []
            regBanc.cotizacionOperacion = []
            regBanc.vendedorOperacion = []
            regBanc.clienteOperacion = []
            regBanc.estadoOperacion = 'INCOMPLETO'
            regBanc.conectado_abono = '0'
            regBanc.save()
        
        if factura_cancelada == 'on':
            abonoActualizar.comprobanteCancelado = 'CANCELADO'
            abonos_relacionados = abonosOperacion.objects.all().filter(codigo_comprobante = abonoActualizar.codigo_comprobante)
            for abono in abonos_relacionados:
                abono.comprobanteCancelado = 'CANCELADO'
                abono.save()
            abonoActualizar.save()
        abonoActualizar.conectado = '0'
        abonoActualizar.idRegistroOp = '0'
        abonoActualizar.save()
    return HttpResponseRedirect(reverse('sistema_2:registro_abonos'))

def descargar_guia(request):
    nombre_doc = 'guia_excel.pdf'
    response = HttpResponse(open('guia_excel.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=' + nombre_doc
    response['Content-Disposition'] = nombre
    return response

def actualizar_roles(request,ind):
    if request.method == 'POST':
        rolAdmin = request.POST.get('admin')
        rolVendedor = request.POST.get('vendedor')
        rolContable = request.POST.get('contable')
        rolesUsuario = []
        if rolAdmin == 'on':
            rolesUsuario.append('1')
        else:
            rolesUsuario.append('0')
        if rolVendedor == 'on':
            rolesUsuario.append('1')
        else:
            rolesUsuario.append('0')
        if rolContable == 'on':
            rolesUsuario.append('1')
        else:
            rolesUsuario.append('0')
        usuarioMod = userProfile.objects.get(id=ind)
        usuarioMod.rolesUsuario = rolesUsuario
        usuarioMod.save()
    return HttpResponseRedirect(reverse('sistema_2:usuarios'))

def get_clients_statistics(request,ind):
    clientes_mas_ventas = []
    ventas_clientes = []
    datos_clientes = []
    facturas_info = facturas.objects.all()
    for factura in facturas_info:
        datos_clientes.append(factura.cliente[5])
    estadistica_clientes = pd.Series(datos_clientes)

    resultados_finales = estadistica_clientes.value_counts()
    for i in range(len(resultados_finales)):
        ventas_clientes.append(int(resultados_finales[i]))

    clientes_mas_ventas = list(resultados_finales.index.tolist())
    ventas_clientes = list(ventas_clientes)
    return JsonResponse({
        'clientes_mas_ventas':clientes_mas_ventas[:int(ind)],
        'ventas_clientes':ventas_clientes[:int(ind)],
    })

def get_products_statistics(request,ind):
    productos_mas_ventas = []
    ventas_productos = []
    datos_productos = []
    facturas_info = facturas.objects.all()
    for factura in facturas_info:
        for producto in factura.productos:
            datos_productos.append(producto[2])
    
    estadistica_productos = pd.Series(datos_productos)

    resultados_finales = estadistica_productos.value_counts()
    for i in range(len(resultados_finales)):
        ventas_productos.append(int(resultados_finales[i]))

    productos_mas_ventas = list(resultados_finales.index.tolist())
    ventas_productos = list(ventas_productos)
    print(productos_mas_ventas)
    print(ventas_productos)
    return JsonResponse({
        'productos_mas_ventas':productos_mas_ventas[:int(ind)],
        'ventas_productos':ventas_productos[:int(ind)],
    })

def get_vendedor_statistics(request,ind):
    vendedor_mas_ventas = []
    ventas_vendedor = []
    datos_vendedor = []
    facturas_info = facturas.objects.all()
    for factura in facturas_info:
        datos_vendedor.append(factura.vendedor[2])
    
    estadistica_vendedor = pd.Series(datos_vendedor)

    resultados_finales = estadistica_vendedor.value_counts()
    for i in range(len(resultados_finales)):
        ventas_vendedor.append(int(resultados_finales[i]))

    vendedor_mas_ventas = list(resultados_finales.index.tolist())
    ventas_vendedor = list(ventas_vendedor)
    return JsonResponse({
        'vendedor_mas_ventas':vendedor_mas_ventas[:int(ind)],
        'ventas_vendedor':ventas_vendedor[:int(ind)],
    })

def get_ventas_meses(request,ind):
    meses_totales = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    lista_meses = []
    ventas_meses = []
    mes_actual = datetime.now().month
    i = 0
    while(i < int(ind)):
        if (mes_actual - i)<1:
            indice_mes = 12 - (i-mes_actual)
        else:
            indice_mes = mes_actual - i
        lista_meses.append(meses_totales[indice_mes-1])
        facturas_filtradas = facturas.objects.filter(fecha_emision__month=indice_mes)
        monto_total_mes = 0.00
        for factura in facturas_filtradas:
            total_precio_soles = 0.00
            for producto in factura.productos:
                if producto[5] == 'DOLARES':
                    v_producto = Decimal(producto[6])*Decimal(factura.tipoCambio[1])*Decimal(Decimal(1.00) - Decimal(producto[7])/100)
                    v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                if producto[5] == 'SOLES':
                    v_producto = Decimal(producto[6])*Decimal(Decimal(1.00) - (Decimal(producto[7])/100))
                    v_producto = Decimal('%.2f' % v_producto)*Decimal(producto[8])
                total_precio_soles = Decimal(total_precio_soles) + Decimal(v_producto)
            monto_total_mes = Decimal(monto_total_mes) + Decimal(total_precio_soles)
        ventas_meses.append(round(monto_total_mes,2))
        i = i + 1
    return JsonResponse({
        'lista_meses':lista_meses,
        'ventas_meses':ventas_meses,
    })