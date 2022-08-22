document.addEventListener('DOMContentLoaded',()=>{
    $('#ingresosTable').DataTable({
        paging: true,
        pageLength: 20,
        lenghtChange: true,
        autoWidth: false,
        serching: true,
        bInfo: false,
        bSort: false,
    })
})