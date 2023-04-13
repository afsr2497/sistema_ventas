function mostrarDatos(registroId)
{
    razonCosto = document.getElementById('razonCosto')
    fechaCosto = document.getElementById('fechaCosto')
    rucCosto = document.getElementById('rucCosto')
    conceptoCosto = document.getElementById('conceptoCosto')
    importeCosto = document.getElementById('importeCosto')
    monedaCosto = document.getElementById('monedaCosto')
    divisionCosto = document.getElementById('divisionCosto')
    categoriaCosto = document.getElementById('categoriaCosto')
    departamentoCosto = document.getElementById('departamentoCosto')
    tipoCosto = document.getElementById('tipoCosto')
    comportamientoCosto = document.getElementById('comportamientoCosto')
    operativoCosto = document.getElementById('operativoCosto')

    fetch(`/sistema_2/consultarDatosRegistro?registroId=${registroId}`)
    .then(response => response.json())
    .then(data => {
        razonCosto.value = data.razonCosto
        fechaCosto.value = data.fechaCosto
        rucCosto.value = data.rucCosto
        conceptoCosto.value = data.conceptoCosto
        importeCosto.value = data.importeCosto
        monedaCosto.value = data.monedaCosto
        divisionCosto.value = data.divisionCosto
        categoriaCosto.value = data.categoriaCosto
        departamentoCosto.value = data.departamentoCosto
        tipoCosto.value = data.tipoCosto
        comportamientoCosto.value = data.comportamientoCosto
        operativoCosto.value = data.operativoCosto
    })
}


function eliminarInfo()
{
    razonCosto = document.getElementById('razonCosto')
    fechaCosto = document.getElementById('fechaCosto')
    rucCosto = document.getElementById('rucCosto')
    conceptoCosto = document.getElementById('conceptoCosto')
    importeCosto = document.getElementById('importeCosto')
    monedaCosto = document.getElementById('monedaCosto')
    divisionCosto = document.getElementById('divisionCosto')
    categoriaCosto = document.getElementById('categoriaCosto')
    departamentoCosto = document.getElementById('departamentoCosto')
    tipoCosto = document.getElementById('tipoCosto')
    comportamientoCosto = document.getElementById('comportamientoCosto')
    operativoCosto = document.getElementById('operativoCosto')

    razonCosto.value = ''
    fechaCosto.value = ''
    rucCosto.value = ''
    conceptoCosto.value = ''
    importeCosto.value = ''
    monedaCosto.value = ''
    divisionCosto.value = ''
    categoriaCosto.value = ''
    departamentoCosto.value = ''
    tipoCosto.value = ''
    comportamientoCosto.value = ''
    operativoCosto.value = ''
}

document.addEventListener('DOMContentLoaded',()=>{
    $('#costosTable').DataTable({
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

    let seleccionDivision = document.getElementById('divisionInfo')
    let categoriaInfo = document.getElementById('categoriaInfo')
    let departamentoInfo = document.getElementById('departamentoInfo')
    seleccionDivision.onchange = function()
    {
        if(seleccionDivision.value === '')
        {
            categoriaInfo.value = ''
            departamentoInfo.value = ''
        }
        else
        {
            fetch(`/sistema_2/retornarDatosCostos?idDivision=${seleccionDivision.value}`)
            .then(response => response.json())
            .then(data => {
                categoriaInfo.value = data.categoria
                departamentoInfo.value = data.departamento
            })
        }
    }


})