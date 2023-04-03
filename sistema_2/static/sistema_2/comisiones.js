document.addEventListener('DOMContentLoaded',()=>{
    usuarioSeleccionado = document.getElementById('usuarioSeleccionado')
    configuracionSeleccionada = document.getElementById('configuracionSeleccionada')

    usuarioSeleccionado.onchange = function() {
        idUsuario = usuarioSeleccionado.value
        fetch(`/sistema_2/obtenerConfiguraciones/${idUsuario}`)
        .then(response => response.json())
        .then(data => {
            while(configuracionSeleccionada.length > 0)
            {
                configuracionSeleccionada.remove(0)
            }

            optionCreada = document.createElement('option')
            optionCreada.value = ''
            optionCreada.innerHTML = ''
            configuracionSeleccionada.appendChild(optionCreada)

            for(let i = 0; i < data.usuariosTotales.length;i++)
            {
                mensaje = ""
                optionCreada = document.createElement('option')
                optionCreada.value = data.usuariosTotales[i][0]
                optionCreada.innerHTML = data.usuariosTotales[i][3]
                configuracionSeleccionada.appendChild(optionCreada)
            }
            configuracionSeleccionada.selectedIndex = '0'
            $('#configuracionSeleccionada').selectpicker('refresh')
        })
    }
})