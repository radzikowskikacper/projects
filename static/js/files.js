$(document).ready(function(){
    $('#file_download_btn').click(function(){
        //url(r'^projects/(?P<project_pk>\d+)/file/(?P<file_id>\d+)/download$', views.do_download, name="download_file"),

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
})