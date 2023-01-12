document.addEventListener("DOMContentLoaded",()=>{
    let btnAgregar = document.getElementById('agregarProducto')
    let btnCrear = document.getElementById('crearProforma')
    let btnCancelar = document.getElementById('cancelarProforma')

    let productoSeleccionado = document.getElementById('productSelect')
    let productoNombre = document.getElementById('nombrePro')
    let productoCodigo = document.getElementById('codigoPro')
    let productoPVsinigv = document.getElementById('pvsinIGV')
    let productoCantidad = document.getElementById('cantidadPro')
    let productoMoneda= document.getElementById('monedaProducto')
    let productosTabla = document.getElementById('proCuerpo')

    let rucProveedor = document.getElementById('rucProveedor')
    let nombreProveedor = document.getElementById('nombreProveedor')
    let ciudadProveedor = document.getElementById('ciudadProveedor')
    let destinoProveedor = document.getElementById('destinoProveedor')


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
            productoPVsinigv.value = producto_info.pv_sinIGV

            if(producto_info.moneda === 'DOLARES')
            {
                productoMoneda.selectedIndex = '1'
            }
            if(producto_info.moneda === 'SOLES')
            {
                productoMoneda.selectedIndex = '0'
            }
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
                    <td><input class="form-control" style="width:80px;" value="${productoPVsinigv.value}"></td>
                    <td><input class="form-control" style="width:80px;" value="${productoCantidad.value}"></td>
                    <td><input type="button" class="btn btn-secondary" value="Eliminar"></td>
                </tr>`;
        productosTabla.innerHTML += nuevaFila
    })

    btnCrear.addEventListener('click',()=>{

        arregloProductos = []
        let longitudProductos = productosTabla.rows.length
        console.log(longitudProductos)
        for(var i = 0;i < longitudProductos; i++)
        {
            let celdas = productosTabla.rows.item(i)
            let productoArreglo = [celdas.cells.item(0).innerHTML,celdas.cells.item(1).innerHTML,celdas.cells.item(2).innerHTML,celdas.cells.item(3).innerHTML,celdas.cells.item(4).firstChild.value,celdas.cells.item(5).firstChild.value] 
            arregloProductos.push(productoArreglo)
        }

        url = '/sistema_2/crear_orden'
        ejemplo = {
            'productos':arregloProductos,
            'rucProveedor':rucProveedor.value,
            'nombreProveedor':nombreProveedor.value,
            'ciudadProveedor':ciudadProveedor.value,
            'destinoProveedor':destinoProveedor.value,
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