$(document).ready( function() {
$('#searchInput').bind('keydown', function(e) {
    var keyCode;
    if(e.keyCode > 0)
        keyCode = e.keyCode;
    else if(typeof(e.charCode) != "undefined")
        keyCode = e.charCode;
    if(keyCode == 8) {
        $('#searchForm').submit();
    }
});

$('#searchInput').bind('keyup', function(e) {
    if($(this).val().length >= 3) {
        $('#searchForm').submit();
    }
});

$('#searchForm').submit(function() {
    $.ajax({
        data: $(this).serialize(),
        type: $(this).attr('method'),
        url: $(this).attr('action'),
        success: function(response) {
            $('#tableContainer').html(response);
        },
    });
    return false;
});
});

$('#upload_form input').change(function() {
   $('#upload_form').submit();
});
