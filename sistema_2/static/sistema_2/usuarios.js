document.addEventListener('DOMContentLoaded',()=>{
    //Parametros para ordenar la tabla de usuarios luego de la carga completa del DOM
    $('#usuariosTable').DataTable({
        paging: true,
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        serching: true,
        bInfo: false,
        bSort: false,
    })
    setTimeout(function() {
        $("#mensaje_info").fadeOut(3000);
    },3000);
})