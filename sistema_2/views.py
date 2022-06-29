import datetime
from django.contrib.auth.models import User
from django.db.models import F
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django import forms
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from .models import Clientes, Productos, Usuarios, Servicios, Proformas, Guias, Facturas
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from django.db.models import Q
from reportlab.lib.pagesizes import A4
import pandas as pd
import numpy as np

class DateInput(forms.DateInput):
    input_type = 'date'

class form_filtro(forms.Form):
    fil_categoria = forms.CharField(label='Categoria :',required=False)

class authen_form(forms.Form):
    user = forms.CharField(label='Username',required=True)
    user_psw = forms.CharField(label='Password',widget=forms.PasswordInput(),required=True)

class cliente_form(forms.Form):
    cli_nombre = forms.CharField(label='Nombre :',required=True)
    cli_apellido = forms.CharField(label='Apellido :', required=True)
    cli_razon_social = forms.CharField(label='Razon Social :',required=True)
    cli_dni = forms.CharField(label='DNI :',required=True)
    cli_ruc = forms.CharField(label='RUC :',required=True)
    cli_email = forms.CharField(label='Email :',required=True)
    cli_contacto = forms.CharField(label='Contacto :',required=True)
    cli_telefono = forms.CharField(label='Telefono :',required=True)
    cli_department = forms.CharField(label='Departamento :',required=True)
    cli_provincia = forms.CharField(label='Provincia :',required=True)
    cli_distrito = forms.CharField(label='Distrito :',required=True)

class producto_form(forms.Form):
    pro_nombre = forms.CharField(label='Nombre :',required=True)
    pro_codigo = forms.CharField(label='Codigo :',required=True)
    pro_categoria = forms.CharField(label='Categoria :',required=True)
    pro_sub_categoria = forms.CharField(label='Sub Categoria :',required=True)
    pro_unidad_med = forms.CharField(label='Unidad de medida :',required=True)
    pro_precio_compra_con_igv = forms.FloatField(label='Precio de compra (Con IGV) :',required=True)
    pro_precio_venta_sin_igv = forms.FloatField(label='Precio de venta (Sin IGV) :',required=True)
    pro_codigo_sunat = forms.CharField(label='Codigo sunat :',required=True)
    pro_moneda = forms.ChoiceField(label='Moneda :',required=False, choices=(('DOLARES','DOLARES'),('SOLES','SOLES')))
    pro_stock = forms.IntegerField(label='Stock :',required=True)
    pro_almacen = forms.CharField(label='Almacen :',required=True)

class servicio_form(forms.Form):
    ser_nombre = forms.CharField(label='Nombre :',required=True)
    ser_categoria = forms.CharField(label='Categoria :', required=True)
    ser_sub_categoria = forms.CharField(label='Sub Categoria :', required=False)
    ser_unidad_med = forms.CharField(label='Unidad de medida',required=False)
    ser_precio_venta_sin_igv = forms.FloatField(label='Precio de venta (Sin IGV) :',required=True)

class usuario_form(forms.Form):
    usr_usuario = forms.CharField(label='Usuario :',required=True)
    usr_password = forms.CharField(label='Password',required=True)
    usr_email = forms.CharField(label='Email :',required=True)
    usr_tipo = forms.ChoiceField(label = 'Tipo :',required=True, choices=(('admin','admin'),('vendedor','vendedor')))
    usr_celular = forms.CharField(label='Celular :',required=True)

class proforma_form(forms.Form):
    prof_fecha = forms.DateField(label='Fecha de la proforma :',required=True,widget=DateInput)
    prof_vendedor = forms.CharField(label='Vendedor :')

class producto_proforma_form(forms.Form):
    prod_prof_cantidad = forms.IntegerField(label='Cantidad de productos :')
    prod_prof_identificador = forms.CharField(label='ID del producto :')

class cliente_proforma_form(forms.Form):
    cli_prof_id = forms.CharField(label='Id del cliente :')

lista_productos = []
datos_cliente = []

# Create your views here.
def dashboard(request):
    return render(request,'sistema_2/dashboard.html')

def login_view(request):
    if request.method == "POST":
        usuario_sistema = request.POST["user"]
        password_sistema = request.POST["user_psw"]
        usuario = authenticate(request,username=usuario_sistema,password=password_sistema)
        if usuario is not None:
            login(request, usuario)
            return HttpResponseRedirect("dashboard")
        else:
            return render(request,'sistema_2/log_in.html',{
                "message": "DATOS INVALIDOS!",
                "form": authen_form()
            })

    return render(request,'sistema_2/log_in.html',{
        "form": authen_form()
    })

def clientes(request):
    bus_nombre = request.GET.get('nombre')
    bus_apellido = request.GET.get('apellido')
    bus_razon_social = request.GET.get('razon-social')
    bus_dni = request.GET.get('dni')
    bus_ruc = request.GET.get('ruc')
    bus_departamento = request.GET.get('departamento')
    bus_provincia = request.GET.get('provincia')
    bus_distrito = request.GET.get('distrito')
    cli = Clientes.objects.all().order_by('id')
    if bus_nombre:
        cli = cli.filter(
            Q(cli_nombre__icontains = bus_nombre)
        ).distinct()
    
    if bus_apellido:
        cli = cli.filter(
            Q(cli_apellido__icontains = bus_apellido)
        ).distinct()
    
    if bus_razon_social:
        cli = cli.filter(
            Q(cli_razon_social__icontains = bus_razon_social)
        ).distinct()
    
    if bus_dni:
        cli = cli.filter(
            Q(cli_dni__icontains = bus_dni)
        ).distinct()
    
    if bus_ruc:
        cli = cli.filter(
            Q(cli_ruc__icontains = bus_ruc)
        ).distinct()

    if bus_departamento:
        cli = cli.filter(
            Q(cli_department__icontains = bus_departamento)
        ).distinct()
    
    if bus_provincia:
        cli = cli.filter(
            Q(cli_provincia__icontains = bus_provincia)
        ).distinct()
    
    if bus_distrito:
        cli = cli.filter(
            Q(cli_distrito__icontains = bus_distrito)
        ).distinct()
    return render(request,'sistema_2/clientes.html',{
        'cli': cli.order_by('id')
    })

def servicios(request):
    bus_nombre = request.GET.get('nombre')
    bus_categoria =request.GET.get('categoria')
    bus_sub_categoria = request.GET.get('sub-categoria')
    bus_unidad_med = request.GET.get('unidad-med')
    ser = Servicios.objects.all()
    if bus_nombre:
        ser = ser.filter(
            Q(ser_nombre__icontains = bus_nombre)
        ).distinct()
    if bus_categoria:
        ser = ser.filter(
            Q(ser_categoria__icontains = bus_categoria)
        ).distinct()
    if bus_sub_categoria:
        ser = ser.filter(
            Q(ser_sub_categoria__icontains = bus_sub_categoria)
        ).distinct()
    if bus_unidad_med:
        ser = ser.filter(
            Q(ser_unidad_med__icontains = bus_unidad_med)
        ).distinct()
    return render(request,'sistema_2/servicios.html',{
        'ser': ser.order_by('id')
    })

def productos(request):
    bus_nombre = request.GET.get('nombre')
    bus_codigo = request.GET.get('codigo')
    bus_categoria = request.GET.get('categoria')
    bus_sub_categoria = request.GET.get('sub-categoria')
    bus_unidad_med = request.GET.get('unidad-med')
    bus_codigo_su = request.GET.get('codigo-su')
    bus_moneda = request.GET.get('moneda')
    bus_almacen = request.GET.get('almacen')
    pro = Productos.objects.all()
    if bus_nombre:
        pro = pro.filter(
            Q(pro_nombre__icontains = bus_nombre)
        ).distinct()
    if bus_codigo:
        pro = pro.filter(
            Q(pro_codigo__icontains = bus_codigo)
        ).distinct()
    if bus_categoria:
        pro = pro.filter(
            Q(pro_categoria__icontains = bus_categoria)
        ).distinct()
    if bus_sub_categoria:
        pro = pro.filter(
            Q(pro_sub_categoria__icontains = bus_sub_categoria)
        ).distinct()
    if bus_unidad_med:
        pro = pro.filter(
            Q(pro_unidad_med__icontains = bus_unidad_med)
        ).distinct()
    if bus_codigo_su:
        pro = pro.filter(
            Q(pro_codigo_sunat__icontains = bus_codigo_su)
        ).distinct()
    if bus_moneda:
        pro = pro.filter(
            Q(pro_moneda__icontains = bus_moneda)
        ).distinct()
    if bus_almacen:
        pro = pro.filter(
            Q(pro_almacen__icontains = bus_almacen)
        ).distinct()
    return render(request,'sistema_2/productos.html',{
        'pro': pro.order_by('id'),
    })

def usuarios(request):
    bus_usuario = request.GET.get('usuario')
    bus_email = request.GET.get('email')
    bus_tipo = request.GET.get('tipo')
    bus_celular = request.GET.get('celular')
    usuarios = User.objects.all()
    if bus_usuario:
        usuarios = usuarios.filter(
            Q(username__icontains = bus_usuario)
        ).distinct()
    if bus_email:
        usuarios = usuarios.filter(
            Q(email__icontains = bus_email)
        )
    if bus_tipo:
        usuarios = usuarios.filter(
            Q(first_name__icontains = bus_tipo)
        )
    if bus_celular:
        usuarios = usuarios.filter(
            Q(last_name__icontains = bus_celular)
        )
    return render(request,'sistema_2/usuarios.html',{
        'usr': usuarios.order_by('id')
    })

def proformas(request):
    return render(request,'sistema_2/proformas.html',{
        'prof': Proformas.objects.all()
    })

def facturas(request):
    return render(request,'sistema_2/facturas.html',{
        'fac': Facturas.objects.all()
    })

def crear_factura(request):
    return render(request,'sistema_2/crear_factura.html')

def guias(request):
    return render(request,'sistema_2/guias.html',{
        'gui': Guias.objects.all()
    })

def crear_guia(request):
    return render(request,'sistema_2/crear_guia.html')

def add_client(request):
    if request.method == 'POST':
        datos_cliente = cliente_form(request.POST)
        if datos_cliente.is_valid():
            dat_nombre = datos_cliente.cleaned_data["cli_nombre"]
            dat_apellido = datos_cliente.cleaned_data["cli_apellido"]
            dat_razon_social = datos_cliente.cleaned_data["cli_razon_social"]
            dat_dni = datos_cliente.cleaned_data["cli_dni"]
            dat_ruc = datos_cliente.cleaned_data["cli_ruc"]
            dat_email = datos_cliente.cleaned_data["cli_email"]
            dat_contacto = datos_cliente.cleaned_data["cli_contacto"]
            dat_telefono = datos_cliente.cleaned_data["cli_telefono"]
            dat_department = datos_cliente.cleaned_data["cli_department"]
            dat_provincia = datos_cliente.cleaned_data["cli_provincia"]
            dat_distrito = datos_cliente.cleaned_data["cli_distrito"]
            try:
                ultimo_cliente = Clientes.objects.latest('id')
                dat_id = ultimo_cliente.id + 1
            except:
                dat_id = 1
            Clientes(id=dat_id,cli_nombre=dat_nombre,cli_apellido=dat_apellido,cli_razon_social=dat_razon_social,cli_dni=dat_dni,cli_ruc=dat_ruc,cli_email=dat_email,cli_contacto=dat_contacto,cli_telefono=dat_telefono,cli_department=dat_department,cli_provincia=dat_provincia,cli_distrito=dat_distrito).save()
        else:
            return render(request,"sistema_2/add_client.html",{
                'form_client': datos_cliente
            })
    return render(request,'sistema_2/add_client.html',{
        'form_client': cliente_form() 
    })

def add_product(request):
    if request.method == 'POST':
        datos_producto = producto_form(request.POST)
        if datos_producto.is_valid():
            dat_nombre = datos_producto.cleaned_data['pro_nombre']
            dat_codigo = datos_producto.cleaned_data['pro_codigo']
            dat_categoria = datos_producto.cleaned_data['pro_categoria']
            dat_sub_categoria = datos_producto.cleaned_data['pro_sub_categoria']
            dat_unidad_med = datos_producto.cleaned_data['pro_unidad_med']
            dat_precio_compra_con_igv = datos_producto.cleaned_data['pro_precio_compra_con_igv']
            dat_precio_compra_sin_igv = round(dat_precio_compra_con_igv/1.18,2)
            dat_precio_venta_sin_igv = datos_producto.cleaned_data['pro_precio_venta_sin_igv']
            dat_precio_venta_con_igv = round(dat_precio_venta_sin_igv*1.18,2)
            dat_codigo_sunat = datos_producto.cleaned_data['pro_codigo_sunat']
            dat_moneda = datos_producto.cleaned_data['pro_moneda']
            dat_stock = datos_producto.cleaned_data['pro_stock']
            dat_almacen = datos_producto.cleaned_data['pro_almacen']
            try:
                ultimo_producto = Productos.objects.latest('id')
                dat_id = ultimo_producto.id + 1
            except:
                dat_id = 1
            Productos(id=dat_id,pro_nombre=dat_nombre,pro_codigo=dat_codigo,pro_categoria=dat_categoria,pro_sub_categoria=dat_sub_categoria,pro_unidad_med=dat_unidad_med,pro_precio_compra_con_igv=dat_precio_compra_con_igv,pro_precio_compra_sin_igv=dat_precio_compra_sin_igv,pro_precio_venta_sin_igv=dat_precio_venta_sin_igv,pro_precio_venta_con_igv=dat_precio_venta_con_igv,pro_codigo_sunat=dat_codigo_sunat,pro_moneda=dat_moneda,pro_stock=dat_stock,pro_almacen=dat_almacen).save()
        else:
            return render(request,"sistema_2/add_product.html",{
                'form_product': datos_producto
            })
    return render(request,'sistema_2/add_product.html',{
        'form_product': producto_form() 
    })

def add_service(request):
    if request.method == 'POST':
        datos_servicio = servicio_form(request.POST)
        if datos_servicio.is_valid():
            dat_nombre = datos_servicio.cleaned_data['ser_nombre']
            dat_categoria = datos_servicio.cleaned_data['ser_categoria']
            dat_sub_categoria = datos_servicio.cleaned_data['ser_sub_categoria']
            dat_unidad_med = datos_servicio.cleaned_data['ser_unidad_med']
            dat_precio_venta_sin_igv = datos_servicio.cleaned_data['ser_precio_venta_sin_igv']
            dat_precio_venta_con_igv = dat_precio_venta_sin_igv*1.18
            try:
                ultimo_servicio = Servicios.objects.latest('id')
                dat_id = ultimo_servicio.id + 1
            except:
                dat_id = 1
            Servicios(id=dat_id,ser_nombre=dat_nombre,ser_categoria=dat_categoria,ser_sub_categoria=dat_sub_categoria,ser_unidad_med=dat_unidad_med,ser_precio_venta_sin_igv=dat_precio_venta_sin_igv,ser_precio_venta_con_igv=dat_precio_venta_con_igv).save()
        else:
            return render(request,"sistema_2/add_service.html",{
                'form_service': datos_servicio
            })
    return render(request,'sistema_2/add_service.html',{
        'form_service': servicio_form() 
    })

def add_user(request):
    if request.method == 'POST':
        datos_usuario = usuario_form(request.POST)
        if datos_usuario.is_valid():
            dat_usuario = datos_usuario.cleaned_data['usr_usuario']
            dat_password = datos_usuario.cleaned_data['usr_password']
            dat_email = datos_usuario.cleaned_data['usr_email']
            dat_tipo = datos_usuario.cleaned_data['usr_tipo']
            dat_celular = datos_usuario.cleaned_data['usr_celular']
            try:
                ultimo_usuario = User.objects.latest('id')
                dat_id = ultimo_usuario.id + 1
            except:
                dat_id = 1
            nuevo_usuario = User.objects.create_user(dat_usuario,dat_email,dat_password)
            nuevo_usuario.first_name = dat_tipo
            nuevo_usuario.last_name = dat_celular
            nuevo_usuario.id = dat_id
            nuevo_usuario.save()
        else:
            return render(request,"sistema_2/add_user.html",{
                'form_user': datos_usuario
            })
    return render(request,'sistema_2/add_user.html',{
        'form_user': usuario_form() 
    })

def add_proforma(request):
    if request.method == 'POST':
        datos_proforma = proforma_form(request.POST)
        if datos_proforma.is_valid():
            dat_fecha = datos_proforma.cleaned_data['prof_fecha']
            dat_vendedor = datos_proforma.cleaned_data['prof_vendedor']
            vendedor = User.objects.get(id=dat_vendedor)
            dat_valor_total=0
            dat_estado = 'NoGenerada'
            dat_productos = []
            dat_cliente = []
            datos_vendedor = []
            datos_vendedor.append(vendedor.id)
            datos_vendedor.append(vendedor.username)
            datos_vendedor.append(vendedor.first_name)
            datos_vendedor.append(vendedor.last_name)
            for producto in lista_productos:
                dat_productos.append(producto)
            for dato in datos_cliente:
                dat_cliente.append(dato)
            Proformas(prof_cliente=dat_cliente,prof_fecha=dat_fecha,prof_valor_total=dat_valor_total,prof_estado=dat_estado,prof_productos=dat_productos,prof_vendedor=datos_vendedor).save()
            lista_productos.clear()
            datos_cliente.clear()
        else:
            return render(request,'sistema_2/add_proforma.html',{
                'form_proforma': datos_proforma,
                'lista_productos': lista_productos
            })
    return render(request,'sistema_2/add_proforma.html',{
        'form_proforma': proforma_form(),
        'lista_productos': lista_productos,
        'cliente': datos_cliente,
    })

def add_producto_proforma(request):
    bus_nombre = request.GET.get('nombre')
    bus_codigo = request.GET.get('codigo')
    bus_categoria = request.GET.get('categoria')
    bus_sub_categoria = request.GET.get('sub-categoria')
    bus_unidad_med = request.GET.get('unidad-med')
    bus_codigo_su = request.GET.get('codigo-su')
    bus_moneda = request.GET.get('moneda')
    bus_almacen = request.GET.get('almacen')
    pro = Productos.objects.all()
    if bus_nombre:
        pro = pro.filter(
            Q(pro_nombre__icontains = bus_nombre)
        ).distinct()
    if bus_codigo:
        pro = pro.filter(
            Q(pro_codigo__icontains = bus_codigo)
        ).distinct()
    if bus_categoria:
        pro = pro.filter(
            Q(pro_categoria__icontains = bus_categoria)
        ).distinct()
    if bus_sub_categoria:
        pro = pro.filter(
            Q(pro_sub_categoria__icontains = bus_sub_categoria)
        ).distinct()
    if bus_unidad_med:
        pro = pro.filter(
            Q(pro_unidad_med__icontains = bus_unidad_med)
        ).distinct()
    if bus_codigo_su:
        pro = pro.filter(
            Q(pro_codigo_sunat__icontains = bus_codigo_su)
        ).distinct()
    if bus_moneda:
        pro = pro.filter(
            Q(pro_moneda__icontains = bus_moneda)
        ).distinct()
    if bus_almacen:
        pro = pro.filter(
            Q(pro_almacen__icontains = bus_almacen)
        ).distinct()
    if request.method == 'POST':
        datos_producto_proforma = producto_proforma_form(request.POST)
        if datos_producto_proforma.is_valid():
            informacion = []
            info_producto = Productos.objects.get(id=datos_producto_proforma.cleaned_data['prod_prof_identificador'])
            informacion.append(info_producto.id)
            informacion.append(info_producto.pro_nombre)
            informacion.append(info_producto.pro_codigo)
            informacion.append(info_producto.pro_categoria)
            informacion.append(info_producto.pro_sub_categoria)
            informacion.append(info_producto.pro_precio_venta_sin_igv)
            informacion.append(info_producto.pro_codigo_sunat)
            informacion.append(info_producto.pro_moneda)
            cantidad_productos = datos_producto_proforma.cleaned_data['prod_prof_cantidad']
            if cantidad_productos < info_producto.pro_stock:
                informacion.append(cantidad_productos)
                lista_productos.append(informacion)
                return HttpResponseRedirect(reverse('sistema_2:add_proforma'))
            else:
                mensaje = 'No se cuenta con el stock de productos'
                return render(request,'sistema_2/add_producto_proforma.html',{
                    'form_product_proforma': datos_producto_proforma,
                    'pro': pro,
                    'mensaje': mensaje,
                })

        else:
            return render(request,'sistema_2/add_producto_proforma.html',{
                'form_product_proforma': datos_producto_proforma,
                'pro': pro,
            })
    return render(request,'sistema_2/add_producto_proforma.html',{
        'form_product_proforma': producto_proforma_form(),
        'pro': pro,
    })

def add_cliente_proforma(request):
    cli = Clientes.objects.all()
    bus_nombre = request.GET.get('nombre')
    bus_apellido = request.GET.get('apellido')
    bus_razon_social = request.GET.get('razon-social')
    bus_dni = request.GET.get('dni')
    bus_ruc = request.GET.get('ruc')
    bus_departamento = request.GET.get('departamento')
    bus_provincia = request.GET.get('provincia')
    bus_distrito = request.GET.get('distrito')
    cli = Clientes.objects.all().order_by('id')
    if bus_nombre:
        cli = cli.filter(
            Q(cli_nombre__icontains = bus_nombre)
        ).distinct()
    
    if bus_apellido:
        cli = cli.filter(
            Q(cli_apellido__icontains = bus_apellido)
        ).distinct()
    
    if bus_razon_social:
        cli = cli.filter(
            Q(cli_razon_social__icontains = bus_razon_social)
        ).distinct()
    
    if bus_dni:
        cli = cli.filter(
            Q(cli_dni__icontains = bus_dni)
        ).distinct()
    
    if bus_ruc:
        cli = cli.filter(
            Q(cli_ruc__icontains = bus_ruc)
        ).distinct()

    if bus_departamento:
        cli = cli.filter(
            Q(cli_department__icontains = bus_departamento)
        ).distinct()
    
    if bus_provincia:
        cli = cli.filter(
            Q(cli_provincia__icontains = bus_provincia)
        ).distinct()
    
    if bus_distrito:
        cli = cli.filter(
            Q(cli_distrito__icontains = bus_distrito)
        ).distinct()

    if request.method == 'POST':
        datos_cliente_proforma = cliente_proforma_form(request.POST)
        if datos_cliente_proforma.is_valid():
            id_cliente = datos_cliente_proforma.cleaned_data['cli_prof_id']
            cliente_db = Clientes.objects.get(id=id_cliente)
            datos_cliente.append(cliente_db.id)
            datos_cliente.append(cliente_db.cli_nombre)
            datos_cliente.append(cliente_db.cli_apellido)
            datos_cliente.append(cliente_db.cli_razon_social)
            datos_cliente.append(cliente_db.cli_ruc)
            datos_cliente.append(cliente_db.cli_dni)
            return HttpResponseRedirect(reverse('sistema_2:add_proforma'))
        else:
            return render(request,'sistema_2/add_producto_proforma.html',{
                'form_cliente_proforma': datos_cliente_proforma,
                'cli': Clientes.objects.all()
            })
            
    return render(request,'sistema_2/add_cliente_proforma.html',{
        'form_cliente_proforma': cliente_proforma_form(),
        'cli': cli,
    })

def eliminar_usuario(request,ind):
    usuario_eliminar = User.objects.get(id=ind)
    usuario_eliminar.delete()      
    return HttpResponseRedirect(reverse('sistema_2:usuarios'))

def eliminar_producto(request,ind):
    producto_eliminar = Productos.objects.get(id=ind)
    producto_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:productos'))

def eliminar_servicio(request,ind):
    servicio_eliminar = Servicios.objects.get(id=ind)
    servicio_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:servicios'))

def eliminar_cliente(request,ind):
    cliente_eliminar = Clientes.objects.get(id=ind)
    cliente_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:clientes'))

def eliminar_proforma(request,ind):
    proforma_eliminar = Proformas.objects.get(id=ind)
    proforma_eliminar.delete()
    return HttpResponseRedirect(reverse('sistema_2:proformas'))

def generar_proforma(request,ind):
    
    proforma_info = Proformas.objects.get(id=ind)
    cliente_info = Clientes.objects.get(id=int(proforma_info.prof_cliente[0]))
    vendedor_info = User.objects.get(id=proforma_info.prof_vendedor[0])
    packet = io.BytesIO()
    can = canvas.Canvas(packet,pagesize=A4)
    can.setFillColorRGB(0,0,0)
    can.setFont('Times-Roman',20)
    nombre_cot = 'COTIZACION Nro ' + str(proforma_info.id)
    can.drawString(30,725,nombre_cot)

    can.setFont('Times-Roman',10)
    can.drawString(30,700,'Fecha')
    can.drawString(80,700,':')
    can.drawString(90,700,proforma_info.prof_fecha)
    can.drawString(30,690,'Cliente')
    can.drawString(80,690,':')
    can.drawString(90,690,cliente_info.cli_razon_social)
    can.drawString(30,680,'RUC')
    can.drawString(80,680,':')
    can.drawString(90,680,cliente_info.cli_ruc)
    can.drawString(30,670,'Direccion')
    can.drawString(80,670,':')
    can.drawString(90,670,cliente_info.cli_distrito)

    lista_x = [30,90,320,390,460,500,570]
    lista_y = [650,635]
    can.grid(lista_x,lista_y)
    can.drawString(35,640,'Cantidad')
    can.drawString(95,640,'Producto')
    can.drawString(325,640,'Unidad')
    can.drawString(395,640,'PU sin IGV')
    can.drawString(465,640,'DSCT')
    can.drawString(505,640,'Total')

    i = 0
    for producto in proforma_info.prof_productos:
        print(producto)
        print(type(producto))
        producto_info = Productos.objects.get(id=producto[0])
        lista_y = [lista_y[1],lista_y[1]-15]
        can.drawString(35,lista_y[1] + 5,str(producto[8]))
        can.drawString(95,lista_y[1] + 5,str(producto_info.pro_nombre.split(',')[0]))
        can.drawString(325,lista_y[1] + 5,str(producto_info.pro_unidad_med))
        if producto[7] == 'SOLES':
            can.drawString(395,lista_y[1] + 5,str(round(producto_info.pro_precio_venta_sin_igv,2)))
            can.drawString(465,lista_y[1] + 5,str(proforma_info.prof_descuentos[i]))
            can.drawString(505,lista_y[1] + 5,str(round(float(1.00-float(proforma_info.prof_descuentos[i]))*float(producto[8])*float(producto_info.pro_precio_venta_sin_igv),2)))
        if producto[7] == 'DOLARES':
            print(proforma_info.prof_tipo_cambio)
            can.drawString(395,lista_y[1] + 5,str(round(producto_info.pro_precio_venta_sin_igv*proforma_info.prof_tipo_cambio,2)))
            can.drawString(465,lista_y[1] + 5,str(proforma_info.prof_descuentos[i]))
            can.drawString(505,lista_y[1] + 5,str(round(float(1.00-float(proforma_info.prof_descuentos[i]))*float(producto[8])*float(producto_info.pro_precio_venta_sin_igv*proforma_info.prof_tipo_cambio),2)))
        can.grid(lista_x,lista_y)
        i = i + 1
    
    lista_x = [390,500,570]
    lista_y = [lista_y[1]-40,lista_y[1]-55]
    lista_datos = ['Total (-dscto)','IGV (18%)','Total a pagar']
    i = 0
    while i < 3:
        can.grid(lista_x,lista_y)
        can.drawString(395,lista_y[1]+5,lista_datos[i])
        lista_y = [lista_y[1],lista_y[1]-15]
        i=i+1
    
    can.drawString(505,lista_y[1]+50,str(round(float(proforma_info.prof_valor_total),2)))
    can.drawString(505,lista_y[1]+35,str(round(float(proforma_info.prof_valor_total)*0.18,2)))
    can.drawString(505,lista_y[1]+20,str(round(float(proforma_info.prof_valor_total)*1.18,2)))


    can.drawString(30,lista_y[1]+50,'Nombre del vendedor : ')
    can.drawString(30,lista_y[1]+35,'Celular del vendedor : ')
    can.drawString(120,lista_y[1]+50,str(vendedor_info.username))
    can.drawString(120,lista_y[1]+35,str(vendedor_info.last_name))


    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader('proforma.pdf','rb')
    salida_pdf = PdfFileWriter()
    pagina = existing_pdf.getPage(0)
    pagina.mergePage(new_pdf.getPage(0))
    salida_pdf.addPage(pagina)
    salida_doc = open('proforma_generada.pdf','wb')
    salida_pdf.write(salida_doc)
    salida_doc.close()
    response = HttpResponse(open('proforma_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=proforma_id_' + str(ind) + '.pdf'
    response['Content-Disposition'] = nombre
    return response

def importar_usuarios(request):
    if request.method == 'POST':
        columnas_usuario = ['USUARIO','PASSWORD','EMAIL']
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
            if len(datos_archivo.columns) == len(columnas_usuario):
                mensaje = 'Archivo y columnas correctas'
                identificador = 0
                for columna in datos_archivo.columns:
                    if not (columna in columnas_usuario):
                        identificador = 1
                if identificador == 1:
                    mensaje = 'Las columnas del archivo no son las apropiadas'
                else: 
                    mensaje = 'Las columnas del archivo cumplen con los requerimientos'
                    i = 0
                    while i < len(datos_archivo):
                        dat_usuario = datos_archivo.loc[i,'USUARIO']
                        dat_password = datos_archivo.loc[i,'PASSWORD']
                        dat_email = datos_archivo.loc[i,'EMAIL']
                        try:
                            ultimo_usuario = Usuarios.objects.latest('id')
                            dat_id = ultimo_usuario.id + 1
                        except:
                            dat_id = 1
                        Usuarios(id=dat_id,usr_usuario=dat_usuario,usr_password=dat_password,usr_email=dat_email).save()
                        i = i+1
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return render(request,'sistema_2/importar_usuarios.html',{
            'mensaje': mensaje,
        })

    return render(request,'sistema_2/importar_usuarios.html')

def importar_clientes(request):
    if request.method == 'POST':
        columnas_cliente = ['NOMBRE','APELLIDO','RAZON SOCIAL','DNI','RUC','EMAIL','CONTACTO','TELEFONO','DEPARTAMENTO','PROVINCIA','DISTRITO']
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
                        dat_departamento = datos_archivo.loc[i,'DEPARTAMENTO']
                        dat_provincia = datos_archivo.loc[i,'PROVINCIA']
                        dat_distrito = datos_archivo.loc[i,'DISTRITO']
                        try:
                            ultimo_cliente = Clientes.objects.latest('id')
                            dat_id = ultimo_cliente.id + 1
                        except:
                            dat_id = 1
                        Clientes(id=dat_id,cli_nombre=dat_nombre,cli_apellido=dat_apellido,cli_razon_social=dat_razon_social,cli_dni=dat_dni,cli_ruc=dat_ruc,cli_email=dat_email,cli_contacto=dat_contacto,cli_telefono=dat_telefono,cli_department=dat_departamento,cli_provincia=dat_provincia,cli_distrito=dat_distrito).save()
                        i = i+1
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return render(request,'sistema_2/importar_clientes.html',{
            'mensaje': mensaje,
        })

    return render(request,'sistema_2/importar_clientes.html')

def importar_productos(request):
    if request.method == 'POST':
        columnas_producto = ['CATEGORIA','SUBCATEGORIA','COD PERCAMAR','COD SUNAT','PRODUCTO','UNIDAD','MONEDA','PRECIO COMPRA','PRECIO COMPRA + IGV','PRECIO VENTA','PRECIO VENTA + IGV','STOCK','ALMACEN']
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
                            dat_precio_compra_sin_igv = 0.0
                        else:
                            dat_precio_compra_sin_igv = round(float(dat_precio_compra_sin_igv),5)
                        dat_precio_compra_con_igv = datos_archivo.loc[i,'PRECIO COMPRA + IGV']
                        if dat_precio_compra_con_igv == '':
                            dat_precio_compra_con_igv = 0.0
                        else:
                            dat_precio_compra_con_igv = round(float(dat_precio_compra_con_igv),5)
                        dat_precio_venta_sin_igv = datos_archivo.loc[i,'PRECIO VENTA']
                        if dat_precio_venta_sin_igv == '':
                            dat_precio_venta_sin_igv = 0.0
                        else:
                            dat_precio_venta_sin_igv = round(float(dat_precio_venta_sin_igv),5)
                        dat_precio_venta_con_igv = datos_archivo.loc[i,'PRECIO VENTA + IGV']
                        if dat_precio_venta_con_igv == '':
                            dat_precio_venta_con_igv = 0.0
                        else:
                            dat_precio_venta_con_igv = round(float(dat_precio_venta_con_igv),5)
                        dat_stock = datos_archivo.loc[i,'STOCK']
                        if dat_stock == '':
                            dat_stock = 0
                        else:
                            dat_stock = int(float(dat_stock))
                        dat_almacen = datos_archivo.loc[i,'ALMACEN']
                        try:
                            ultimo_producto = Productos.objects.latest('id')
                            dat_id = ultimo_producto.id + 1
                        except:
                            dat_id = 1
                        Productos(id=dat_id,pro_categoria=dat_categoria,pro_sub_categoria=dat_sub_categoria,pro_codigo=dat_codigo,pro_codigo_sunat=dat_codigo_sunat,pro_nombre=dat_nombre,pro_unidad_med=dat_unidad_med,pro_moneda=dat_moneda,pro_precio_compra_sin_igv=dat_precio_compra_sin_igv,pro_precio_compra_con_igv=dat_precio_compra_con_igv,pro_precio_venta_sin_igv=dat_precio_venta_sin_igv,pro_precio_venta_con_igv=dat_precio_venta_con_igv,pro_stock=dat_stock,pro_almacen=dat_almacen).save()
                        i = i+1
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return render(request,'sistema_2/importar_productos.html',{
            'mensaje': mensaje,
        })

    return render(request,'sistema_2/importar_productos.html')

def importar_servicios(request):
    if request.method == 'POST':
        columnas_servicio = ['NOMBRE','CATEGORIA','SUBCATEGORIA','UNIDAD','PRECIO VENTA','PRECIO VENTA + IGV']
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
                            dat_precio_venta_sin_igv = round(float(dat_precio_venta_sin_igv),5)
                        dat_precio_venta_con_igv = datos_archivo.loc[i,'PRECIO VENTA + IGV']
                        if dat_precio_venta_con_igv == '':
                            dat_precio_venta_con_igv = 0.0
                        else:
                            dat_precio_venta_con_igv = round(float(dat_precio_venta_con_igv))
                        try:
                            ultimo_servicio = Servicios.objects.latest('id')
                            dat_id = ultimo_servicio.id + 1
                        except:
                            dat_id = 1
                        Servicios(id=dat_id,ser_nombre=dat_nombre,ser_categoria=dat_categoria,ser_sub_categoria=dat_sub_categoria,ser_unidad_med=dat_unidad_med,ser_precio_venta_sin_igv=dat_precio_venta_sin_igv,ser_precio_venta_con_igv=dat_precio_venta_con_igv).save()
                        i = i+1
                    mensaje='Los datos han sido cargados correctamente'
            else:
                mensaje = 'Las columnas del archivo no estan completas'

        else:
            mensaje = 'No es un archivo de excel'
            identificador = 0
        return render(request,'sistema_2/importar_servicios.html',{
            'mensaje': mensaje,
        })

    return render(request,'sistema_2/importar_servicios.html')

def update_user(request,ind):
    usuario_info = User.objects.get(id=ind)
    datos_iniciales = {
        'usr_usuario': usuario_info.username,
        'usr_password': '',
        'usr_email': usuario_info.email,
        'usr_tipo': usuario_info.first_name,
        'usr_celular': usuario_info.last_name,
    }
    if request.method == 'POST':
        usuario_actualizado = usuario_form(request.POST)
        if usuario_actualizado.is_valid():
            usr_upd_usuario = usuario_actualizado.cleaned_data['usr_usuario']
            usr_upd_password = usuario_actualizado.cleaned_data['usr_password']
            usr_udp_email = usuario_actualizado.cleaned_data['usr_email']
            usr_udp_tipo = usuario_actualizado.cleaned_data['usr_tipo']
            usr_udp_celular = usuario_actualizado.cleaned_data['usr_celular']
            usuario_info.set_password(usr_upd_password)
            usuario_info.username = usr_upd_usuario
            usuario_info.email = usr_udp_email
            usuario_info.first_name = usr_udp_tipo
            usuario_info.last_name = usr_udp_celular
            usuario_info.save()
            return HttpResponseRedirect(reverse('sistema_2:usuarios'))
        else:
            return render(request,'sistema_2/update_user.html',{
                'form_user': usuario_actualizado,
                'id_usuario': ind,
            })
    return render(request,'sistema_2/update_user.html',{
        'form_user': usuario_form(initial=datos_iniciales),
        'id_usuario': ind,
    })

def update_client(request,ind):
    cliente_info = Clientes.objects.get(id=ind)
    datos_iniciales = {
        'cli_nombre': cliente_info.cli_nombre,
        'cli_apellido': cliente_info.cli_apellido,
        'cli_razon_social': cliente_info.cli_razon_social,
        'cli_dni': cliente_info.cli_dni,
        'cli_ruc': cliente_info.cli_ruc,
        'cli_email': cliente_info.cli_email,
        'cli_contato': cliente_info.cli_contacto,
        'cli_telefono': cliente_info.cli_telefono,
        'cli_department': cliente_info.cli_department,
        'cli_provincia': cliente_info.cli_provincia,
        'cli_distrito': cliente_info.cli_distrito
    }
    if request.method == 'POST':
        cliente_actualizado = cliente_form(request.POST)
        if cliente_actualizado.is_valid():
            cli_udp_nombre = cliente_actualizado.cleaned_data['cli_nombre']
            cli_udp_apellido = cliente_actualizado.cleaned_data['cli_apellido']
            cli_udp_razon_social = cliente_actualizado.cleaned_data['cli_razon_social']
            cli_udp_dni = cliente_actualizado.cleaned_data['cli_dni']
            cli_udp_ruc = cliente_actualizado.cleaned_data['cli_ruc']
            cli_udp_email = cliente_actualizado.cleaned_data['cli_email']
            cli_udp_contacto = cliente_actualizado.cleaned_data['cli_contacto']
            cli_udp_telefono = cliente_actualizado.cleaned_data['cli_telefono']
            cli_udp_department = cliente_actualizado.cleaned_data['cli_department']
            cli_udp_provincia = cliente_actualizado.cleaned_data['cli_provincia']
            cli_udp_distrito = cliente_actualizado.cleaned_data['cli_distrito']
            Clientes(id=ind,cli_nombre=cli_udp_nombre,cli_apellido=cli_udp_apellido,cli_razon_social=cli_udp_razon_social,cli_dni=cli_udp_dni,cli_ruc=cli_udp_ruc,cli_email=cli_udp_email,cli_contacto=cli_udp_contacto,cli_telefono=cli_udp_telefono,cli_department=cli_udp_department,cli_provincia=cli_udp_provincia,cli_distrito=cli_udp_distrito).save()
            return HttpResponseRedirect(reverse('sistema_2:clientes'))
        else:
            return render(request,'sistema_2/update_client.html',{
                'form_client': cliente_actualizado,
                'id_cliente': ind,
            })
    return render(request,'sistema_2/update_client.html',{
        'form_client': cliente_form(initial=datos_iniciales),
        'id_cliente': ind,
    })

def update_service(request,ind):
    servicio_info = Servicios.objects.get(id=ind)
    datos_iniciales = {
        'ser_nombre': servicio_info.ser_nombre,
        'ser_categoria': servicio_info.ser_categoria,
        'ser_sub_categoria': servicio_info.ser_sub_categoria,
        'ser_unidad_med': servicio_info.ser_unidad_med,
        'ser_precio_venta_sin_igv': servicio_info.ser_precio_venta_sin_igv,
    }
    if request.method == 'POST':
        servicio_actualizado = servicio_form(request.POST)
        if servicio_actualizado.is_valid():
            ser_udp_nombre = servicio_actualizado.cleaned_data['ser_nombre']
            ser_udp_categoria = servicio_actualizado.cleaned_data['ser_categoria']
            ser_udp_sub_categoria = servicio_actualizado.cleaned_data['ser_sub_categoria']
            ser_udp_unidad_med = servicio_actualizado.cleaned_data['ser_unidad_med']
            ser_udp_precio_venta_sin_igv = servicio_actualizado.cleaned_data['ser_precio_venta_sin_igv']
            ser_udp_precio_venta_con_igv = ser_udp_precio_venta_sin_igv*1.18
            Servicios(id=ind,ser_nombre=ser_udp_nombre,ser_categoria=ser_udp_categoria,ser_sub_categoria=ser_udp_sub_categoria,ser_unidad_med=ser_udp_unidad_med,ser_precio_venta_sin_igv=ser_udp_precio_venta_sin_igv,ser_precio_venta_con_igv=ser_udp_precio_venta_con_igv).save()
            return HttpResponseRedirect(reverse('sistema_2:servicios'))
        else:
            return render(request,'sistema_2/update_service.html',{
                'form_service': servicio_actualizado,
                'id_servicio': ind,
            })
    return render(request,'sistema_2/update_service.html',{
        'form_service': servicio_form(initial=datos_iniciales),
        'id_servicio': ind,
    })

def update_product(request,ind):
    producto_info = Productos.objects.get(id=ind)
    datos_iniciales = {
        'pro_nombre': producto_info.pro_nombre,
        'pro_codigo': producto_info.pro_codigo,
        'pro_categoria': producto_info.pro_categoria,
        'pro_sub_categoria': producto_info.pro_sub_categoria,
        'pro_unidad_med': producto_info.pro_unidad_med,
        'pro_precio_compra_sin_igv': producto_info.pro_precio_compra_sin_igv,
        'pro_precio_compra_con_igv': producto_info.pro_precio_compra_con_igv,
        'pro_precio_venta_sin_igv': producto_info.pro_precio_venta_sin_igv,
        'pro_precio_venta_con_igv': producto_info.pro_precio_venta_con_igv,
        'pro_codigo_sunat': producto_info.pro_codigo_sunat,
        'pro_moneda': producto_info.pro_moneda,
        'pro_stock': producto_info.pro_stock,
        'pro_almacen': producto_info.pro_almacen,
    }
    if request.method == 'POST':
        producto_actualizado = producto_form(request.POST)
        if producto_actualizado.is_valid():
            pro_udp_nombre = producto_actualizado.cleaned_data['pro_nombre']
            pro_udp_codigo = producto_actualizado.cleaned_data['pro_codigo']
            pro_udp_categoria = producto_actualizado.cleaned_data['pro_categoria']
            pro_udp_sub_categoria = producto_actualizado.cleaned_data['pro_sub_categoria']
            pro_udp_unidad_med = producto_actualizado.cleaned_data['pro_unidad_med']
            pro_udp_precio_compra_con_igv = producto_actualizado.cleaned_data['pro_precio_compra_con_igv']
            pro_udp_precio_compra_sin_igv = pro_udp_precio_compra_con_igv/1.18
            pro_udp_precio_venta_sin_igv = producto_actualizado.cleaned_data['pro_precio_venta_sin_igv']
            pro_udp_precio_venta_con_igv = pro_udp_precio_venta_sin_igv*1.18
            pro_udp_codigo_sunat = producto_actualizado.cleaned_data['pro_codigo_sunat']
            pro_udp_moneda = producto_actualizado.cleaned_data['pro_moneda']
            pro_udp_stock = producto_actualizado.cleaned_data['pro_stock']
            pro_udp_almacen = producto_actualizado.cleaned_data['pro_almacen']
            Productos(id=ind,pro_nombre=pro_udp_nombre,pro_codigo=pro_udp_codigo,pro_categoria=pro_udp_categoria,pro_sub_categoria=pro_udp_sub_categoria,pro_unidad_med=pro_udp_unidad_med,pro_precio_compra_sin_igv=pro_udp_precio_compra_sin_igv,pro_precio_compra_con_igv=pro_udp_precio_compra_con_igv,pro_precio_venta_sin_igv=pro_udp_precio_venta_sin_igv,pro_precio_venta_con_igv=pro_udp_precio_venta_con_igv,pro_codigo_sunat=pro_udp_codigo_sunat,pro_moneda=pro_udp_moneda,pro_stock=pro_udp_stock,pro_almacen=pro_udp_almacen).save()
            return HttpResponseRedirect(reverse('sistema_2:productos'))
        else:
            return render(request,'sistema_2/update_product.html',{
                'form_product': producto_actualizado,
                'id_producto': ind,
            })
    return render(request,'sistema_2/update_product.html',{
        'form_product': producto_form(initial=datos_iniciales),
        'id_producto': ind,
    })

def generar_guia(request,ind):
    guia_generada = Proformas.objects.get(id=ind)
    guia_generada.prof_estado = 'Ejecutada'
    guia_generada.save()
    dat_cliente = guia_generada.prof_cliente
    dat_codigo = 'MP-G' + str(ind)
    fecha = datetime.datetime.now()
    dat_fecha = str(fecha.year) + '-' + str(fecha.month) + '-' + str(fecha.day)
    dat_valor_total = guia_generada.prof_valor_total
    dat_estado = 'Generada'
    dat_productos = guia_generada.prof_productos
    dat_descuentos = guia_generada.prof_descuentos
    dat_tipo_cambio = guia_generada.prof_tipo_cambio
    Guias(gui_cliente=dat_cliente,gui_fecha=dat_fecha,gui_valor_total=dat_valor_total,gui_estado=dat_estado,gui_productos=dat_productos,gui_codigo=dat_codigo,gui_descuentos=dat_descuentos,gui_tipo_cambio=dat_tipo_cambio).save()
    return HttpResponseRedirect(reverse('sistema_2:proformas'))

def generar_factura(request,ind):
    """
    Para generar una factura primero se debe registrar sus datos en el sistema Tefacturo a traves de un request.PUT
    Esta seccion es de prueba hasta realizar las validaciones correspondientes
    params = 
    {
        "close2u": 
        {
            "tipoIntegracion": "OFFLINE", "tipoPlantilla": "01",
            "tipoRegistro": "PRECIOS_CON_IGV"
        }, 
        "datosDocumento": 
        {
            "fechaEmision": "2019-08-20", "formaPago": "EFECTIVO",
            "glosa": "UNA OBSERVACION SIN TILDES", "moneda": "PEN",
            "numero": 2,
            "serie": "FFA5"
        }, 
        "detalleDocumento": 
        [
            {
                "cantidad": 3,
                "codigoProducto": "PROD2",
                "codigoProductoSunat": “53103001”,
                "descripcion": "COMISION DE RECARGAS",
                "numeroOrden": 1,
                "precioVentaUnitarioItem": 25,
                "tipoAfectacion": "GRAVADO_OPERACION_ONEROSA",
                "unidadMedida": "UNIDAD_SERVICIOS"
            } 
        ],
        "emisor": 
        {
            "correo": " facturacion@emisor.com.pe ", "domicilioFiscal": 
            {
                "departamento": "LIMA",
                "direccion": "DIRECCION DE VENDEMAS",
                "distrito": "MIRAFLORES",
                "pais": "PERU",
                "provincia": "LIMA",
                "ubigeo": "150133",
                "urbanizacion": ""
            },
            "nombreComercial": "VENDEMAS",
            "nombreLegal": "ARMIDA VICTORIA OCHOA TAMARIZ", numeroDocumentoIdentidad": "10324047366",
            "tipoDocumentoIdentidad": "RUC"
        },
        "informacionAdicional": 
        {
            "tipoOperacion": "VENTA_INTERNA"},
            "receptor": 
            {
                "correo": "armida.ochoa@close2u.pe", "correoCopia": "",
                "domicilioFiscal": 
                {
                    "departamento": null,
                    "direccion": "AV. PTE PIEDRA NRO. 386 COO. AMPLIACIÓN LAS UVAS - PRO - LIMA LIMA PUENTE PIEDRA",
                    "distrito": null,
                    "pais": "PERU",
                    "provincia": null,
                    "ubigeo": null
                },
                "nombreComercial": "CORPORACION E INVERSIONES PEPITO Y CLAUDIA S.A.C.", "nombreLegal":
                "CORPORACION E INVERSIONES PEPITO Y CLAUDIA S.A.C.", "numeroDocumentoIdentidad": "20603076550",
                "tipoDocumentoIdentidad": "RUC"
            } 
        }
    }
    response = request.PUT(url=url_del_endpoint,params=params)
    if response is code(OK):
        La factura ha sido generada y se registra en la base de datos
    else:
        La factura no se genera y se muestra un mensaje de error
    
    """
    fact_generada = Guias.objects.get(id=ind)
    fact_generada.gui_estado = 'Factura generada'
    fact_generada.save()
    dat_cliente = fact_generada.gui_cliente
    fecha = datetime.datetime.now()
    dat_fecha = str(fecha.year) + '-' + str(fecha.month) + '-' + str(fecha.day)
    dat_valor_total = fact_generada.gui_valor_total
    dat_estado = 'Generada'
    dat_productos = fact_generada.gui_productos
    dat_descuentos = fact_generada.gui_descuentos
    dat_gui_codigo = fact_generada.gui_codigo
    dat_tipo_cambio = fact_generada.gui_tipo_cambio
    Facturas(fac_cliente=dat_cliente,fac_fecha=dat_fecha,fac_valor_total=dat_valor_total,fac_estado=dat_estado,fac_productos=dat_productos,fac_descuentos=dat_descuentos,fac_gui_codigo=dat_gui_codigo,fac_tipo_cambio=dat_tipo_cambio).save()
    return HttpResponseRedirect(reverse('sistema_2:guias'))

def descargar_guia(request,ind):

    packet = io.BytesIO()
    can = canvas.Canvas(packet,pagesize=A4)
    guia_info = Guias.objects.get(id=ind)
    cliente_info = Clientes.objects.get(id=guia_info.gui_cliente[0])
    can.setFillColorRGB(0,0,0)
    can.setFont('Times-Roman',12)
    can.drawString(70,670,str(guia_info.gui_fecha))
    can.drawString(250,670,str(guia_info.gui_fecha))

    can.drawString(30,640,'DIRECCION ALMACEN METALPROTEC')
    can.drawString(30,625,'DIRECCION ALMACEN METALPROTEC')
    can.drawString(350,640,'DIRECCION CLIENTE')
    direccion_cliente = str(cliente_info.cli_department) + '-' + str(cliente_info.cli_provincia) + '-' + str(cliente_info.cli_distrito)
    can.drawString(350,625,direccion_cliente)

    can.drawString(30,585,cliente_info.cli_razon_social)
    can.drawString(30,570,cliente_info.cli_ruc)

    lista_x = [30,190,450,500,550]
    lista_y = [560,545]
    can.drawString(35,550,'Codigo')
    can.drawString(195,550,'Descripcion')
    can.drawString(455,550,'Unidad')
    can.drawString(505,550,'Cantidad')

    for producto in guia_info.gui_productos:
        producto_info = Productos.objects.get(id=producto[0])
        lista_y = [lista_y[1],lista_y[1]-15]
        can.drawString(35,lista_y[1] + 5,str(producto_info.pro_codigo))
        can.drawString(195,lista_y[1] + 5,str(producto_info.pro_nombre.split(',')[0]))
        can.drawString(455,lista_y[1] + 5,str(producto_info.pro_unidad_med))
        can.drawString(505,lista_y[1] + 5,str(producto[8]))
    
    can.drawString(35,90,'ALMACEN METALPROTEC')
    can.drawString(35,70,'RUC METALPROTEC')

    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader('proforma.pdf','rb')
    salida_pdf = PdfFileWriter()
    pagina = existing_pdf.getPage(0)
    pagina.mergePage(new_pdf.getPage(0))
    salida_pdf.addPage(pagina)
    salida_doc = open('proforma_generada.pdf','wb')
    salida_pdf.write(salida_doc)
    salida_doc.close()
    response = HttpResponse(open('proforma_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=guia_id_' + str(ind) + '.pdf'
    response['Content-Disposition'] = nombre
    return response

def descargar_factura(request,ind):
    packet = io.BytesIO()
    can = canvas.Canvas(packet,pagesize=A4)
    factura_info = Facturas.objects.get(id=ind)
    cliente_info = Clientes.objects.get(id=factura_info.fac_cliente[0])
    can.setFillColorRGB(0,0,0)
    can.setFont('Times-Roman',8)
    can.drawString(263,740,'Direccion Metalprotec')
    can.drawString(263,732,'Correo Metalprotec')
    can.drawString(263,724,'Telefono Metalprotec')

    lista_x = [460,560]
    lista_y = [720,670]

    can.grid(lista_x,lista_y)

    can.drawString(465,705,'RUC METALPROTEC')
    can.drawString(465,695,'FACTURA ELECTRONICA')
    can.drawString(465,685,str(factura_info.fac_codigo))

    lista_x = [30,560]
    lista_y = [650,625]
    can.grid(lista_x,lista_y)
    can.drawString(35,642,'Nombre del cliente')
    can.drawString(35,630,cliente_info.cli_razon_social)

    lista_x = [30,560]
    lista_y = [625,600]
    can.grid(lista_x,lista_y)
    can.drawString(35,617,'Direccion del cliente')
    can.drawString(35,605,str(cliente_info.cli_department + ' - ' + cliente_info.cli_provincia + ' - ' + cliente_info.cli_distrito))

    lista_x = [30,136,242,348,454,560]
    lista_y = [600,575]
    can.grid(lista_x,lista_y)
    lista_campos = ['Ruc','Condicion de pago','Vencimiento','Emision','Moneda']
    print(factura_info.fac_condi_pago)
    elementos_campos = [str(cliente_info.cli_ruc),str(factura_info.fac_condi_pago),str(factura_info.fac_fecha_vencimiento),str(factura_info.fac_fecha),'SOLES']
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1
    
    lista_x = [30,295,560]
    lista_y = [575,550]
    can.grid(lista_x,lista_y)
    lista_campos = ['Nro de Guia','Nro de orden de compra']
    elementos_campos = [factura_info.fac_gui_codigo,'-']
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-8,elemento)
        can.drawString(lista_x[i] + 5,lista_y[1] + 5,elementos_campos[i])
        i=i+1

    lista_x = [30,60,160,200,440,480,520,560]
    lista_y = [550,525]
    can.grid(lista_x,lista_y)
    can.setFont('Times-Roman',8)
    lista_campos = ['NRO','CODIGO','CANT','DESCRIPCION','TOTAL','DSCTO','P.VENTA']
    i = 0
    for elemento in lista_campos:
        can.drawString(lista_x[i] + 5,lista_y[0]-15,elemento)
        i=i+1
    
    lista_x = [30,60,160,200,440,480,520,560]
    lista_y = [525,200]
    can.grid(lista_x,lista_y)
    i = 1
    total_factura = 0
    for producto in factura_info.fac_productos:
        producto_info = Productos.objects.get(id=producto[0])
        if producto_info.pro_moneda == 'SOLES':
            precio_no_descuento = round(float(producto[8])*float(producto_info.pro_precio_venta_sin_igv),2)
            precio_total = round(float(producto[8])*float(producto_info.pro_precio_venta_sin_igv)*float(1.00-float(factura_info.fac_descuentos[i-1])),2)
        if producto_info.pro_moneda == 'DOLARES':
            precio_no_descuento = round(float(factura_info.fac_tipo_cambio)*float(producto[8])*float(producto_info.pro_precio_venta_sin_igv),2)
            precio_total = round(float(factura_info.fac_tipo_cambio)*float(producto[8])*float(producto_info.pro_precio_venta_sin_igv)*float(1.00-float(factura_info.fac_descuentos[i-1])),2)
        
        total_factura=total_factura+precio_total
        print(factura_info.fac_descuentos[0])
        campos = [str(i),producto_info.pro_codigo,str(producto[8]),producto_info.pro_nombre.split(',')[0],str(precio_no_descuento),str(factura_info.fac_descuentos[i-1]),str(precio_total)]
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
    
    can.drawString(500,165,str(round(total_factura,2)))
    can.drawString(500,145,str(round(total_factura*0.18,2)))
    can.drawString(500,125,str(round(total_factura*1.18,2)))
    can.drawString(35,165,'Son: ' + str(int(total_factura)) + 'soles con ' + str(round((total_factura - int(total_factura)),2)) + ' centavos')

    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader('proforma.pdf','rb')
    salida_pdf = PdfFileWriter()
    pagina = existing_pdf.getPage(0)
    pagina.mergePage(new_pdf.getPage(0))
    salida_pdf.addPage(pagina)
    salida_doc = open('proforma_generada.pdf','wb')
    salida_pdf.write(salida_doc)
    salida_doc.close()
    response = HttpResponse(open('proforma_generada.pdf','rb'),content_type='application/pdf')
    nombre = 'attachment; ' + 'filename=factura_id_' + str(ind) + '.pdf'
    response['Content-Disposition'] = nombre
    return response

def log_out(request):
    logout(request)
    return render(request,'sistema_2/log_in.html',{
        'form': authen_form()
    })

class agregar_form(forms.Form):
    stock_add = forms.IntegerField(initial=0)


def add_stock(request,ind):
    if request.method == 'POST':
        datos_stock = agregar_form(request.POST)
        if datos_stock.is_valid():
            producto = Productos.objects.get(id=ind)
            producto.pro_stock = producto.pro_stock + datos_stock.cleaned_data['stock_add']
            producto.save()
        else:
            return render(request,'sistema_2/add_stock.html',{
                'agregar_form': datos_stock,
                'id': ind,
            })
    return render(request,'sistema_2/add_stock.html',{
        'agregar_form':agregar_form(),
        'id': ind,
    })

def ver_factura(request,ind):
    factura_info = Facturas.objects.get(id=ind)
    if request.method == 'POST':
        fecha_emision = request.POST.get('fecha-emision')
        fecha_vencimiento = request.POST.get('fecha-vencimiento')
        condi_pago = request.POST.get('condi-pago')
        print(condi_pago)
        print(fecha_emision)
        factura_info.fac_fecha = str(fecha_emision)
        factura_info.fac_fecha_vencimiento = str(fecha_vencimiento)
        factura_info.fac_condi_pago = condi_pago
        print(factura_info.fac_condi_pago)
        factura_info.fac_estado = 'Emitida'
        factura_info.fac_codigo = 'MP-FAC-00' + str(factura_info.id)
        for producto in factura_info.fac_productos:
            pro_mod = Productos.objects.get(id=producto[0])
            pro_mod.pro_stock = pro_mod.pro_stock - int(producto[8])
            pro_mod.save()
        factura_info.save()
        return HttpResponseRedirect(reverse('sistema_2:facturas'))

    return render(request,'sistema_2/ver_factura.html',{
        'productos':factura_info.fac_productos,
        'id_factura': ind
    })

def ver_proforma(request,ind):
    proforma_info = Proformas.objects.get(id=ind)
    if request.method == 'POST':
        tipo_cambio = request.POST.get('tipo-cambio')
        dat_productos = len(proforma_info.prof_productos)
        i=0
        descuentos_proforma = []
        while i < dat_productos:
            descuentos_proforma.append(float(request.POST.get(str(proforma_info.prof_productos[i][0]))))
            i=i+1
        proforma_info.prof_descuentos = descuentos_proforma
        proforma_info.prof_tipo_cambio = float(tipo_cambio)
        proforma_info.prof_estado = 'Generada'
        proforma_info.prof_valor_total = 0
        i = 0
        for producto in proforma_info.prof_productos:
            precio_producto = 0
            if producto[7] == 'SOLES':
                precio_producto = float(producto[5])*int(producto[8])*float((1.00-float(descuentos_proforma[i])))
            if producto[7] == 'DOLARES':
                precio_producto = float(producto[5])*int(producto[8])*float((1.00-float(descuentos_proforma[i]))*float(tipo_cambio))
            i=i+1
            print(precio_producto)
            proforma_info.prof_valor_total = proforma_info.prof_valor_total + precio_producto
        proforma_info.prof_valor_total = round(float(proforma_info.prof_valor_total),2)
        proforma_info.save()
        return HttpResponseRedirect(reverse('sistema_2:proformas'))
    return render(request,'sistema_2/ver_proforma.html',{
        'productos': proforma_info.prof_productos,
        'id_proforma': ind,
    })