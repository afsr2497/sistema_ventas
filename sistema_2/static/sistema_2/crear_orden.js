document.addEventListener("DOMContentLoaded",()=>{
    let btnAgregar = document.getElementById('agregarProducto')
    let btnCancelarProducto = document.getElementById('cancelarProducto')
    let btnCrear = document.getElementById('crearProforma')
    let btnCancelar = document.getElementById('cancelarProforma')

    let productoSeleccionado = document.getElementById('productSelect')
    let productoNombre = document.getElementById('nombrePro')
    let productoCodigo = document.getElementById('codigoPro')
    let productoPCsinigv = document.getElementById('pcsinIGV')
    let productoCantidad = document.getElementById('cantidadPro')
    let productoDescuento = document.getElementById('descuentoPro')
    let productoMoneda= document.getElementById('monedaProducto')
    let productosTabla = document.getElementById('proCuerpo')

    let rucProveedor = document.getElementById('rucProveedor')
    let fechaOrden = document.getElementById('fechaOrden')
    let condicionOrden = document.getElementById('condicionOrden')
    let codigoOrden = document.getElementById('codigoOrden')
    let direccionProveedor = document.getElementById('direccionProveedor')
    let nombreProveedor = document.getElementById('nombreProveedor')
    
    let ciudadCliente = document.getElementById('ciudadCliente')
    let atencionCliente = document.getElementById('atencionCliente')
    let destinoCliente = document.getElementById('destinoCliente')
    let monedaOrden = document.getElementById('monedaOrden')

    let tcCompraOrden = document.getElementById('tcCompraOrden')
    let tcVentaOrden = document.getElementById('tcVentaOrden')


    btnCancelarProducto.addEventListener('click',()=>{
        productoNombre.value = ''
        productoCodigo.value = ''
        productoPCsinigv.value = '0.00'
        productoCantidad.value = '0.00'
        productoDescuento.value = '0.00'
        productoSeleccionado.selectedIndex = '0'
        $('#productSelect').selectpicker('refresh')
    })

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
            productoPCsinigv.value = producto_info.pc_sinIGV

            if(producto_info.moneda === 'DOLARES')
            {
                console.log('Se selecciono dolares')
                productoMoneda.selectedIndex = '1'
            }
            if(producto_info.moneda === 'SOLES')
            {
                console.log('Se selecciono Soles')
                productoMoneda.selectedIndex = '0'
            }
            $('#monedaProducto').selectpicker('refresh')
        }
        get_data()
    }

    btnAgregar.addEventListener('click',()=>{
        let nuevaFila = `
                <tr>
                    <td>${productoSeleccionado.value}</td>
                    <td>${productoNombre.value}</td>
                    <td>${productoCodigo.value}</td>
                    <td>${productoMoneda.value}</td>
                    <td><input class="form-control" style="width:80px;" value="${productoPCsinigv.value}"></td>
                    <td><input class="form-control" style="width:80px;" value="${productoCantidad.value}"></td>
                    <td><input class="form-control" style="width:80px;" value="${productoDescuento.value}"></td>
                    <td><input type="button" class="btn btn-secondary" value="Eliminar"></td>
                </tr>`;
        productosTabla.innerHTML += nuevaFila

        productoNombre.value = ''
        productoCodigo.value = ''
        productoPCsinigv.value = '0.00'
        productoCantidad.value = '0.00'
        productoDescuento.value = '0.00'
        productoSeleccionado.selectedIndex = '0'
        $('#productSelect').selectpicker('refresh')
    })

    btnCrear.addEventListener('click',()=>{

        let mostrarDescuento = '0'
        let mostrarVU = '0'

        if($('#mostrarDescuento').prop('checked')){
            mostrarDescuento = '1'
        }
        else{
            mostrarDescuento = '0'
        }

        if($('#mostrarVU').prop('checked')){
            mostrarVU = '1'
        }
        else{
            mostrarVU = '0'
        }

        arregloProductos = []
        let longitudProductos = productosTabla.rows.length
        console.log(longitudProductos)
        for(var i = 0;i < longitudProductos; i++)
        {
            let celdas = productosTabla.rows.item(i)
            let productoArreglo = [celdas.cells.item(0).innerHTML,celdas.cells.item(1).innerHTML,celdas.cells.item(2).innerHTML,celdas.cells.item(3).innerHTML,celdas.cells.item(4).firstChild.value,celdas.cells.item(5).firstChild.value,celdas.cells.item(6).firstChild.value] 
            arregloProductos.push(productoArreglo)
        }

        url = '/sistema_2/crear_orden'
        ejemplo = {
            'productos':arregloProductos,
            'rucProveedor':rucProveedor.value,
            'fechaOrden':fechaOrden.value,
            'condicionOrden':condicionOrden.value,
            'codigoOrden':codigoOrden.value,
            'direccionProveedor':direccionProveedor.value,
            'nombreProveedor':nombreProveedor.value,
            'ciudadCliente':ciudadCliente.value,
            'destinoCliente':destinoCliente.value,
            'atencionCliente':atencionCliente.value,
            'monedaOrden':monedaOrden.value,
            'tcCompraOrden':tcCompraOrden.value,
            'tcVentaOrden':tcVentaOrden.value,
            'mostrarDescuento':mostrarDescuento,
            'mostrarVU':mostrarVU,
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
        window.location.assign('/sistema_2/emisionoc')
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

    btnCancelar.addEventListener('click',()=>{
        window.location.assign('/sistema_2/emisionoc')
    })

    $('table').on('click', 'input[type="button"]', function(e){
        $(this).closest('tr').remove()
    })
})