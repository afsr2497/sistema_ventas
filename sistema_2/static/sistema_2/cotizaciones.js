document.addEventListener('DOMContentLoaded',()=>{

    document.querySelectorAll('.formatoV1').forEach(elemento => {
        elemento.style.display = 'none'
    })
    document.querySelectorAll('.formatoV2').forEach(elemento => {
        elemento.style.display = 'none'
    })

    $('#proformasTable').DataTable({
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


    seleccionarFormato = document.getElementById('seleccionarFormato')
    seleccionarFormato.onchange = function()
    {
        informacionFormato = document.getElementById('seleccionarFormato').value

        if(informacionFormato === '')
        {
            document.querySelectorAll('.formatoV1').forEach(elemento => {
                elemento.style.display = 'none'
            })
            document.querySelectorAll('.formatoV2').forEach(elemento => {
                elemento.style.display = 'none'
            })
        }

        if(informacionFormato === 'V1')
        {
            document.querySelectorAll('.formatoV1').forEach(elemento => {
                elemento.style.display = 'none'
            })
            document.querySelectorAll('.formatoV2').forEach(elemento => {
                elemento.style.display = 'none'
            })

            document.querySelectorAll('.formatoV1').forEach(elemento => {
                elemento.style.display = ''
            })
        }

        if(informacionFormato === 'V2')
        {
            document.querySelectorAll('.formatoV1').forEach(elemento => {
                elemento.style.display = 'none'
            })
            document.querySelectorAll('.formatoV2').forEach(elemento => {
                elemento.style.display = 'none'
            })

            document.querySelectorAll('.formatoV2').forEach(elemento => {
                elemento.style.display = ''
            })   
        }
    }
})