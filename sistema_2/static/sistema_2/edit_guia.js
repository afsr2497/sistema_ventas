var info_cot = 
{
    tipo_cot: 'Servicios',
}

addEventListener('DOMContentLoaded',()=>{
    let origenDep = document.getElementById('origenDep')
    let origenDir = document.getElementById('origenDir')
    let origenDis = document.getElementById('origenDis')
    let origenPro = document.getElementById('origenPro')
    let origenUbi = document.getElementById('origenUbi')

    let idenProforma = document.getElementById('idProforma')
    let tipo_proforma = document.getElementById('tipoProforma')
    let seccionServicios = document.getElementById('serviciosSec')
    let seccionProductos = document.getElementById('productosSec')

    let entregaFecha = document.getElementById('fechaEntrega')
    let trasladoMotivo = document.getElementById('motivoTraslado')
    let transporteModalidad = document.getElementById('modalidadTransporte')
    let pesoTotal = document.getElementById('pesoBruto')
    let ubigeoCliente = document.getElementById('ubigeoCliente')

    let transportistaRazon = document.getElementById('transRazon')
    let transportistaRuc = document.getElementById('transRuc')

    let productoSeleccionado = document.getElementById('productSelect')
    let servicioSeleccionado = document.getElementById('serviceSelect')

    let clienteNombre = document.getElementById('nombreCliente')
    let clienteApellido = document.getElementById('apellidoCliente')
    let clienteRazon = document.getElementById('razonCliente')
    let clienteDni = document.getElementById('dniCliente')
    let clienteRuc = document.getElementById('rucCliente')
    let clienteEmail = document.getElementById('emailCliente')
    let clienteContacto = document.getElementById('contactoCliente')
    let clienteTelefono = document.getElementById('telefonoCliente')
    let clienteDireccion = document.getElementById('direccionCliente')
    let direccionEntrega = document.getElementById('entregarCliente')

    let usuarioNombre = document.getElementById('usuarioUsr')
    let usuarioCodigo = document.getElementById('codigoUsr')
    let usuarioTelefono = document.getElementById('telefonoUsr')

    let proformaFecha = document.getElementById('fechaProf')
    let proformaVencFecha = document.getElementById('fechaVencProf')
    let proformaTCcompra = document.getElementById('tccompraProf')
    let proformaTCventa = document.getElementById('tcventaProf')
    let proformaMoneda = document.getElementById('monedaProf')
    let proformaPago = document.getElementById('pagoProf')

    let productoNombre = document.getElementById('nombrePro')
    let productoCodigo = document.getElementById('codigoPro')
    let productoUnidad = document.getElementById('unidadPro')
    let productoPVsinigv = document.getElementById('pvsinIGV')
    let productoDescuento = document.getElementById('descuentoPro')
    let productoCantidad = document.getElementById('cantidadPro')
    let productoAlmacen = document.getElementById('almacenPro')
    let productoAlmacenes = document.getElementById('almacenesPro')
    let proAlmacenes = document.getElementById('seleccionAlmacen')
    let productoMoneda= document.getElementById('monedaProducto')
    
    let servicioNombre = document.getElementById('nombreSer')
    let servicioUnidad = document.getElementById('unidadSer')
    let servicioPVsinigv = document.getElementById('pvsinIGVSer')
    let servicioDescuento = document.getElementById('descuentoSer')
    let servicioMoneda = document.getElementById('monedaSer')
    
    let productosTabla = document.getElementById('proCuerpo')
    let serviciosTabla = document.getElementById('serCuerpo')

    let btnCrear = document.getElementById('crearProforma')
    let btnCancelar = document.getElementById('cancelarProforma')
    let btnAgregar = document.getElementById('agregarProducto')
    let btnAgregarSer = document.getElementById('agregarServicio')

    let placaVehiculo = document.getElementById('placaVehiculo')
    let nombreConductor = document.getElementById('nombreConductor')
    let dniConductor = document.getElementById('dniConductor')

    let cliente_info
    let almacenes


    if (tipo_proforma.value === 'Servicios')
    {
        seccionServicios.style.display = 'block'
        seccionProductos.style.display = 'none'
    }

    if (tipo_proforma.value === 'Productos')
    {
        seccionServicios.style.display = 'none'
        seccionProductos.style.display = 'block'
    }

    productoSeleccionado.onchange = function() {
        url = '/sistema_2/obtener_producto/' + productoSeleccionado.value
        async function get_data() {
            const res = await fetch(url,{
                                    method:"GET",
                                    headers: {
                                        "X-Requested-With": "XMLHttpRequest",
                                    },})
            producto_info=await res.json()
            console.log(producto_info)

            productoNombre.value = producto_info.nombre
            productoCodigo.value = producto_info.codigo
            productoUnidad.value = producto_info.unidad_med
            productoPVsinigv.value = producto_info.pv_sinIGV
            productoMoneda.value = producto_info.moneda

            if(producto_info.moneda === 'DOLARES')
            {
                productoMoneda.selectedIndex = '1'
            }
            if(producto_info.moneda === 'SOLES')
            {
                productoMoneda.selectedIndex = '0'
            }
            almacenes = producto_info.stock
            if(almacenes === null) 
            {
                $('#seleccionAlmacen option').remove()
                console.log('No se tienen direcciones')
            }
            else
            {
                $('#seleccionAlmacen option').remove()
                for(var i = 0; i < almacenes.length;i++)
                {
                    $("#seleccionAlmacen").append($('<option>', {value: almacenes[i][0], text: almacenes[i][0]}));
                }
            }
        }
        get_data()
    }

    servicioSeleccionado.onchange = function() {
        url = '/sistema_2/obtener_servicio/' + servicioSeleccionado.value
        async function get_data() {
            const res = await fetch(url,{
                                    method:"GET",
                                    headers: {
                                        "X-Requested-With": "XMLHttpRequest",
                                    },})
            servicio_info=await res.json()
            console.log(servicio_info)
            servicioNombre.value = servicio_info.nombre
            servicioUnidad.value = servicio_info.unidad
            servicioPVsinigv.value = servicio_info.pvsinIGV
        }
        get_data()
    }

    btnAgregar.addEventListener('click',()=>{
        if(proAlmacenes.value === '')
        {
            alert('El producto no tiene stock')
        }
        else
        {
            if(productoCantidad.value !== '')
            {
                let posAlmacen = 5
                for(var i = 0;i < almacenes.length; i++)
                {
                    if(proAlmacenes.value === almacenes[i][0])
                    {
                        posAlmacen = i
                        console.log(almacenes[i][0])
                    }
                }
                if(posAlmacen!==5)
                {
                    if(Number(productoCantidad.value) < Number(almacenes[posAlmacen][1]))
                    {
                        let nuevaFila = `
                                <tr>
                                    <td>${productoSeleccionado.value}</td>
                                    <td>${productoNombre.value}</td>
                                    <td>${productoCodigo.value}</td>
                                    <td>${productoUnidad.value}</td>
                                    <td>${proAlmacenes.value}</td>
                                    <td>${productoMoneda.value}</td>
                                    <td><input class="form-control" style="width:80px;" value="${productoPVsinigv.value}"></td>
                                    <td><input class="form-control" style="width:80px;" value="${productoDescuento.value}"></td>
                                    <td><input class="form-control" style="width:80px;" value="${productoCantidad.value}"></td>
                                    <td><input type="button" class="btn btn-secondary" value="Eliminar"></td>
                                </tr>`;
                        productosTabla.innerHTML += nuevaFila
                    }
                    else
                    {
                        alert('No se tiene suficiente stock del producto')
                    }
                }
                else
                {
                    alert('No existe el almacen seleccionado')
                }
                
            }
            else
            {
                alert('Datos ingresados de forma incorrecta')
            }
        }
    })

    btnAgregarSer.addEventListener('click',()=>{
        let nuevaFila = `
                        <tr>
                            <td>${servicioSeleccionado.value}</td>
                            <td>${servicioNombre.value}</td>
                            <td>${servicioUnidad.value}</td>
                            <td>${servicioMoneda.value}</td>
                            <td><input class="form-control" style="width:80px;" value="${servicioPVsinigv.value}"></td>
                            <td><input class="form-control" style="width:80px;" value="${servicioDescuento.value}"></td>
                            <td><input type="button" class="btn btn-secondary" value="Eliminar"></td>
                        </tr>`;
        serviciosTabla.innerHTML += nuevaFila
    })

    btnCancelar.addEventListener('click',()=>{
        window.location = '/sistema_2/gui'
    })

    btnCrear.addEventListener('click',()=>{

        if (tipo_proforma.value === 'Servicios')
        {
            arregloProductos = []
            arregloServicios = []
            let longitudServicios = serviciosTabla.rows.length
            console.log(longitudServicios)
            for(var i = 0;i < longitudServicios; i++)
            {
                let celdas = serviciosTabla.rows.item(i)
                let servicioArreglo = [celdas.cells.item(0).innerHTML,celdas.cells.item(1).innerHTML,celdas.cells.item(2).innerHTML,celdas.cells.item(3).innerHTML,celdas.cells.item(4).firstChild.value,celdas.cells.item(5).firstChild.value] 
                arregloServicios.push(servicioArreglo)
            }
        }

        if (tipo_proforma.value === 'Productos')
        {
            arregloProductos = []
            arregloServicios = []
            let longitudProductos = productosTabla.rows.length
            console.log(longitudProductos)
            for(var i = 0;i < longitudProductos; i++)
            {
                let celdas = productosTabla.rows.item(i)
                let productoArreglo = [celdas.cells.item(0).innerHTML,celdas.cells.item(1).innerHTML,celdas.cells.item(2).innerHTML,celdas.cells.item(3).innerHTML,celdas.cells.item(4).innerHTML,celdas.cells.item(5).innerHTML,celdas.cells.item(6).firstChild.value,celdas.cells.item(7).firstChild.value,celdas.cells.item(8).firstChild.value,'1',celdas.cells.item(8).firstChild.value,celdas.cells.item(9).firstChild.value] 
                arregloProductos.push(productoArreglo)
            }
        }

        let arregloTraslado = [entregaFecha.value,trasladoMotivo.value,transporteModalidad.value,'-',pesoTotal.value]
        let arregloCliente = ['0',clienteNombre.value,clienteApellido.value,clienteRazon.value,clienteDni.value,clienteRuc.value,clienteEmail.value,clienteContacto.value,clienteTelefono.value,clienteDireccion.value,direccionEntrega.value]
        let arregloVendedor = ['0',usuarioNombre.value,usuarioCodigo.value,usuarioTelefono.value]
        let arregloTransporte = [transportistaRazon.value,transportistaRuc.value]
        let datosVehiculo = [placaVehiculo.value,nombreConductor.value,dniConductor.value]

        let origenGuia = [origenDep.value,origenDir.value,origenDis.value,origenPro.value,origenUbi.value]

        let observacionesGuia = document.getElementById('obsGuia')

        url = '/sistema_2/editar_guia/' + idenProforma.value
        console.log(url)
        ejemplo = {
            'origenGuia':origenGuia,
            'obsGuia':observacionesGuia.value,
            'ubigeoCliente':ubigeoCliente.value,
            'transporte':arregloTransporte,
            'traslado':arregloTraslado,
            'cliente':arregloCliente,
            'vendedor':arregloVendedor,
            'datosVehiculo':datosVehiculo,
            'proforma':
            {
                
                'fecha':proformaFecha.value,
                'fecha_vencimiento':proformaVencFecha.value,
                'tc_compra':proformaTCcompra.value,
                'tc_venta':proformaTCventa.value,
                'moneda':proformaMoneda.value,
                'tipo_pago': proformaPago.value,
                'tipo_proforma':tipo_proforma.value,
            },
            'productos':arregloProductos,
            'servicios':arregloServicios,
        }
        fetch(url,{
            method:"POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body:JSON.stringify(ejemplo)
        })
        .then(response => response.json())
        .then(data => {
        console.log(data);
        });
        window.location = '/sistema_2/gui'
    })

    $('table').on('click', 'input[type="button"]', function(e){
        $(this).closest('tr').remove()
    })



    function getCookie(name) 
    {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") 
        {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) 
            {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) 
                {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    $('#seleccionarProducto').on('show.bs.modal', function (event) {
        $("#seleccionarProducto input").val("");
    });
    $('#seleccionarServicio').on('show.bs.modal', function (event) {
        $("#seleccionarServicio input").val("");
    });


})