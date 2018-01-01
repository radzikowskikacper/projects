$(document).ready(function(){
    $('#file_download_btn').click(function(){
		var hiddenIFrameID = 'hiddenDownloader';
		iframe = document.getElementById(hiddenIFrameID);
		if (iframe === null){
			iframe = document.createElement('iframe');
			iframe.id = hiddenIFrameID;
			iframe.style.display = 'none';
			document.body.appendChild(iframe);
		}
		iframe.src = 'file/' + $(this).attr('file_id') + '/';
    })

    $('#file_delete_btn').click(function(){
        $.ajax({
            url : 'file/' + $(this).attr('file_id') + '/',
            method : 'DELETE',
            success : function(data){
                $(this).parent().parent().parent().remove();
            }
        })
    })

    $('#file_upload_btn').click(function(){

    })
})