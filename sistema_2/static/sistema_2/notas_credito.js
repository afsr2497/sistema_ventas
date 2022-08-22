document.addEventListener('DOMContentLoaded',()=>{
    
    $('#notasTable').DataTable({
        paging: true,
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        serching: true,
        bInfo: false,
        bSort: false,
    })
})