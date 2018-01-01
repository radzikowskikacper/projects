$(document).ready(function(){
    function download_file(project_id, file_id){
        //url(r'^projects/(?P<project_pk>\d+)/file/(?P<file_id>\d+)/download$', views.do_download, name="download_file"),

        url = 'file/' + file_id + '/';
		var hiddenIFrameID = 'hiddenDownloader';
		iframe = document.getElementById(hiddenIFrameID);
		if (iframe === null){
			iframe = document.createElement('iframe');
			iframe.id = hiddenIFrameID;
			iframe.style.display = 'none';
			document.body.appendChild(iframe);
		}
		iframe.src = url;
    })
})