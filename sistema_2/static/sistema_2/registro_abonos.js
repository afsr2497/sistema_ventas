function actualizarAbono(abonoID)
{
    idAbono = abonoID.slice(4)
    fetch(`/sistema_2/getDatosAbono?ind=${idAbono}`)
    .then(response => response.json())
    .then(data => {
        console.log(data)
    })
}

function nuevoAbonoInfo()
{
    let facturas_cliente = document.getElementById('facturas_cliente')
    let guiaSeleccionada = document.getElementById('guiaSeleccionada')
    let cotiSeleccionada = document.getElementById('cotiSeleccionada')
    let vendedorSeleccionado = document.getElementById('vendedorSeleccionado')
    let nroOperacionAbono = document.getElementById('nroOperacionAbono')

    facturas_cliente.innerHTML = ''
    $('.selectpicker').selectpicker('refresh')
    guiaSeleccionada.value = ''
    cotiSeleccionada.value = ''
    vendedorSeleccionado.value = ''
    nroOperacionAbono.value = ''
}

addEventListener('DOMContentLoaded',()=>{

    let clienteAbono = document.getElementById('clienteAbono')


    let facturas_cliente = document.getElementById('facturas_cliente')
    let guiaSeleccionada = document.getElementById('guiaSeleccionada')
    let cotiSeleccionada = document.getElementById('cotiSeleccionada')
    let vendedorSeleccionado = document.getElementById('vendedorSeleccionado')
    console.log(facturas_cliente)

    $('#abonosTable').DataTable({
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

    clienteAbono.onchange = function() 
    {
        console.log('Se ha cambiado de cliente')
        facturas_cliente.innerHTML = ''

        var opcionCreada = document.createElement('option')
        opcionCreada.value = ''
        opcionCreada.text = ''
        facturas_cliente.add(opcionCreada)
        $('.selectpicker').selectpicker('refresh')

        cotiSeleccionada.value = ''
        guiaSeleccionada.value = ''
        vendedorSeleccionado.value = ''
        
        url = '/sistema_2/obtener_facturas_cotizaciones_cliente/' + clienteAbono.value
        async function get_data() {
            const res = await fetch(url,{
                                    method:"GET",
                                    headers: {
                                        "X-Requested-With": "XMLHttpRequest",
                                    },})
            cliente_info=await res.json()
            console.log(cliente_info)
            if(cliente_info.tipoCliente === 'Empresa')
            {
                for(var i = 0; i < cliente_info.facturas.length; i++)
                {
                    console.log('Se ingreso al bucle')
                    var opcionCreada = document.createElement('option')
                    opcionCreada.value = cliente_info.facturas[i]
                    opcionCreada.text = cliente_info.facturas[i]
                    facturas_cliente.add(opcionCreada)
                }
                $('.selectpicker').selectpicker('refresh')
            }
            if(cliente_info.tipoCliente === 'Persona')
            {
                for(var i = 0; i < cliente_info.boletas.length; i++)
                {
                    console.log('Se ingreso al bucle')
                    var opcionCreada = document.createElement('option')
                    opcionCreada.value = cliente_info.boletas[i]
                    opcionCreada.text = cliente_info.boletas[i]
                    facturas_cliente.add(opcionCreada)
                }
                $('.selectpicker').selectpicker('refresh')
            }
        }
        get_data()
    }

    facturas_cliente.onchange = function()
    {
        url = '/sistema_2/obtener_guias_factura/' + facturas_cliente.value
        async function get_data() {
            const res = await fetch(url,{
                                    method:"GET",
                                    headers: {
                                        "X-Requested-With": "XMLHttpRequest",
                                    },})
            cliente_info=await res.json()
            console.log(cliente_info)
            guiaSeleccionada.value = ''
            cotiSeleccionada.value = ''
            vendedorSeleccionado.value = ''
            vendedorSeleccionado.value = cliente_info.vendedor
            cotiSeleccionada.value = cliente_info.proformas
            guiaSeleccionada.value = cliente_info.guias

        }
        get_data()
    }
})