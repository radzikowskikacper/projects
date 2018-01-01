function getCookie(name) {
    var cookieValue = null;
    if(document.cookie && document.cookie != ''){
    	var cookies = document.cookie.split(';');

        for(var i = 0; i < cookies.length; i++){
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if(cookie.substring(0, name.length + 1) == (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

$(document).ready(function(){
    var open_iframe = function(src){
    	var hiddenIFrameID = 'hiddenDownloader';
		iframe = document.getElementById(hiddenIFrameID);
		if (iframe === null){
			iframe = document.createElement('iframe');
			iframe.id = hiddenIFrameID;
			iframe.style.display = 'none';
			document.body.appendChild(iframe);
		}
		iframe.src = src;
    };

    $('#lec_file_download_btn').click(function(event){
        open_iframe('file/' + $(this).attr('file_id') + '/';)
    })

    $('#st_file_download_btn').click(function(event){
        event.preventDefault();

        open_iframe($(this).closest('table').attr('project_id') + '/file/' + $(this).closest('tr').attr('file_id') + '/';)
    })

    $('#file_delete_btn').click(function(event){
        event.preventDefault();

        t = $(this);
        $.ajax({
            url : $(this).closest('table').attr('project_id') + '/file/' + $(this).closest('tr').attr('file_id') + '/',
            method : 'DELETE',
            success : function(data){
                t.parent().parent().parent().remove();
            },
            headers : {
	            'X-CSRFToken' : getCookie('csrftoken'),
	        }
        })
    })

    $('#file_upload_btn').click(function(){

    })
})