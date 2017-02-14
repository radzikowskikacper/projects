$(document).ready( function() {
$('#pickProjSubmitBtn').click(function(e) {
    var checked_radio = document.querySelector('input[name="to_pick"]:checked');
    if (checked_radio == null)
        return false;

    if ($('#teams_'+checked_radio.value).text() > 0) {
        $('#pickConfirmModal').modal('show');
        e.preventDefault();
    }
});
});
