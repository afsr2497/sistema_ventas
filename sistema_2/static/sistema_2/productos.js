document.addEventListener('DOMContentLoaded',()=>{
    $('#productosTable').DataTable({
        paging: true,
        pageLength: 20,
        lenghtChange: true,
        autoWidth: false,
        serching: true,
        bInfo: false,
        bSort: false,
    })

    Date.prototype.toDateInputValue = (function() {
        var local = new Date(this);
        local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
        return local.toJSON().slice(0,10);
    });
    

    $('#agregarStock').on('show.bs.modal', function (event) {
        $("#agregarStock input").val("");
        $('#fechaStock').val(new Date().toDateInputValue());
    });
})