$(document).ready(function() {
    $('.project-dropdown').click(function(){
      $(this).parent().parent().next().toggle()
    });
    $('[data-toggle="tooltip"]').tooltip();
});
