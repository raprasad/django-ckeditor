/* For the ckeditor kama skin, this fixes an alignment problem 
 when displaying the ckeditor in the django admin on firefox */
$(document).ready(function(){
//	$('#id_content').before('<br /><br />');    // fix "content" TextField attribute from a django model
    $('textarea').before('<br /><br />');   
});