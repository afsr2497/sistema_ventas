document.addEventListener('DOMContentLoaded',()=>{
    departamentoSeleccionado = document.getElementById('departamentoSeleccionado')
    categoriaSeleccionada = document.getElementById('categoriaSeleccionada')

    departamentoSeleccionado.onchange = function()
    {
        idDepartamento = departamentoSeleccionado.value
        fetch(`/sistema_2/consultarCategorias?idDepartamento=${idDepartamento}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            while(categoriaSeleccionada.length > 0)
            {
                categoriaSeleccionada.remove(0)
            }

            optionCreada = document.createElement('option')
            optionCreada.value = ''
            optionCreada.innerHTML = ''
            categoriaSeleccionada.appendChild(optionCreada)

            for(let i = 0; i < data.categoriasDepartamento.length;i++)
            {
                mensaje = ""
                optionCreada = document.createElement('option')
                optionCreada.value = data.categoriasDepartamento[i][0]
                optionCreada.innerHTML = data.categoriasDepartamento[i][1]
                categoriaSeleccionada.appendChild(optionCreada)
            }
            categoriaSeleccionada.selectedIndex = '0'
            $('#categoriaSeleccionada').selectpicker('refresh')
        })
    }

    $('#tablaDivisiones').DataTable({
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
})