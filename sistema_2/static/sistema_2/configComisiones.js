function agregarTabla()
{
    let tablaGlobal = document.getElementById('tablaGlobal')

    let usuarioTabla = document.getElementById('usuarioTabla')
    let porcentajeTabla = document.getElementById('porcentajeTabla').value
    let igvTabla = $('#igvTabla').prop('checked')
    let usuarioCodigo = usuarioTabla.options[usuarioTabla.selectedIndex].dataset.codigo
    let usuarioNombre = usuarioTabla.options[usuarioTabla.selectedIndex].innerHTML

    if(igvTabla)
    {
        igvTabla = '1'
    }
    else
    {
        igvTabla = '0'
    }

    tablaGlobal.innerHTML += `
    <tr>
        <td>${usuarioTabla.value}</td>
        <td>${usuarioNombre}</td>
        <td>${usuarioCodigo}</td>
        <td>${porcentajeTabla}</td>
        <td>${igvTabla}</td>
        <td><input type="button" class="btn btn-danger" value="Eliminar"></td>
    </tr>`



}

function registrarComision()
{
    let usuarioPrincipal = document.getElementById('usuarioPrincipal')
    if (usuarioPrincipal.value === '')
    {
        alert('Seleccione un usuario principal')
    }
    else 
    {
        url = '/sistema_2/crearComisionGlobal'
        let tablaGlobal = document.getElementById('tablaGlobal')
        arregloComisiones = []
        let longitudComisiones = tablaGlobal.rows.length
        for(var i = 0;i < longitudComisiones; i++)
        {
            let celdas = tablaGlobal.rows.item(i)
            let usuarioArreglo = [celdas.cells.item(0).innerHTML,celdas.cells.item(1).innerHTML,celdas.cells.item(2).innerHTML,celdas.cells.item(3).innerHTML,celdas.cells.item(4).innerHTML]
            arregloComisiones.push(usuarioArreglo)
        }
        informacion = {
            'idUsuario':usuarioPrincipal.value,
            'tipoComision':'GLOBAL',
            'arregloComisiones':arregloComisiones,
        }

        fetch(url,{
            method:"POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body:JSON.stringify(informacion)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
        });
        setTimeout(()=>{
            window.location = '/sistema_2/configComisiones'
        },500)
    }
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
    $('#tablaGlobal').on('click', 'input[type="button"]', function(e){
        $(this).closest('tr').remove()
    })
})