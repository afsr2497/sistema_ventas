
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
    
    $('#facturasTable').DataTable({
        paging: true,
        pageLength: 10,
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