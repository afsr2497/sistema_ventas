function deshabilitarVerificacion()
{
    document.querySelectorAll('.verificacionInfo').forEach(elemento => {
        elemento.disabled = true
    })
}


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

function emitirNota()
{
    let infoNota = document.getElementById('facturaId').innerHTML
    console.log(infoNota)
    let tipoNota = document.getElementById('tipoNota').value
    console.log(tipoNota)
    let productosNota = document.getElementById('productosNota')
    console.log(productosNota)

    arregloProductos = []
    longitudProductos = productosNota.rows.length
    for(let i = 0;i < longitudProductos; i++)
    {
        let fila = productosNota.rows.item(i)
        let productoInfoNota = [fila.cells.item(0).innerHTML,fila.cells.item(1).innerHTML,fila.cells.item(2).firstChild.value]
        arregloProductos.push(productoInfoNota)
    }

    fetch('/sistema_2/crear_nota_credito',{
        method:'POST',
        headers:{
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body:JSON.stringify({
            'infoNota':infoNota,
            'tipoNota':tipoNota,
            'arregloProductos':arregloProductos
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
    window.location.assign('/sistema_2/fact')
}

function eliminarInfo()
{
    let cuerpoProductos = document.getElementById('productosNota')
    cuerpoProductos.innerHTML = ''
}



function generarNota(idFactura)
{
    elementoFactura = document.getElementById('facturaId')
    elementoFactura.innerHTML = ''
    elementoFactura.innerHTML = idFactura
    console.log(idFactura)
    fetch(`/sistema_2/get_productos_factura?factura=${idFactura}`)
    .then(response => response.json())
    .then(data => {
        console.log(data)
        let cuerpoProductos = document.getElementById('productosNota')
        cuerpoProductos.innerHTML = ''
        for(let i = 0; i < data.respuesta.length; i++)
        {
            cuerpoProductos.innerHTML += `
            <tr style='font-size:11px;'>
                <td>${data.respuesta[i][0]}</td>
                <td>${data.respuesta[i][1]}</td>
                <td style='text-align:center;'><input class='form-control' type='number' style='width:60px; font-size:10px; height:20px;' value=${data.respuesta[i][2]} max=${data.respuesta[i][2]}></td>
                <td style='text-align:center;'><input type='button' class='btn btn-info' style='font-size:9px;' value='Eliminar'></td>
            </tr>`
        }
    })
    //Limpiar la ventana de datos
    //Obtener datos de la factura

    //Crear los elementos
}

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


document.addEventListener('DOMContentLoaded',()=>{
    $('table').on('click', 'input[type="button"]', function(e){
        $(this).closest('tr').remove()
    })
    $('#facturasTable').DataTable({
        paging: true,
        pageLength: 20,
        lenghtChange: true,
        autoWidth: false,
        serching: true,
        bInfo: false,
        bSort: false,
        language: {
            "decimal": "",
            "emptyTable": "No hay información",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ Entradas",
            "infoEmpty": "Mostrando 0 to 0 of 0 Entradas",
            "infoFiltered": "(Filtrado de _MAX_ total entradas)",
            "infoPostFix": "",
            "thousands": ",",
            "lengthMenu": "Mostrar _MENU_ Entradas",
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "search": "Buscar:",
            "zeroRecords": "Sin resultados encontrados",
            "paginate": {
                "first": "Primero",
                "last": "Ultimo",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        }
    })

    
    document.querySelectorAll('.generar').forEach(function(button){
        button.onclick = function() {

            claseSelect = '.proFact' + String(button.dataset.fact)

            prodGuia = document.querySelectorAll(claseSelect)
            longPro = prodGuia.length
            prodIden = []
            prodGen = []
            factura_id = button.dataset.fact
            for(var i = 0; i < longPro; i++)
            {
                console.log(prodGuia)
                prodIden.push(prodGuia[i].dataset.id)
                prodGen.push(prodGuia[i].firstElementChild.value)
            }
            console.log(factura_id)
            console.log(prodIden)
            console.log(prodGen)

            informacion_guia = {
                'factura_id':factura_id,
                'prodIden':prodIden,
                'prodGen':prodGen,
            }

            console.log(informacion_guia)

            url = '/sistema_2/gen_guia_factura'

            fetch(url,{
                method:"POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body:JSON.stringify(informacion_guia)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
            })
            window.location = '/sistema_2/gui'
        }
    })

    $('.modal').on('show.bs.modal', function (event) {
        $(".modal input").val("0");
    });
})