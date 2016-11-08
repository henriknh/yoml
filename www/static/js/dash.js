window.onresize = function(event) {
    resize_tvshows();
};
window.onload = function() {
	resize_tvshows();
};
function resize_tvshows() {
	//var height = $( ".episode_thumbnail_img" ).css( "height" );
	$( ".episode_thumbnail" ).each(function( index ) {
		//$( this ).css("height", height);
	});
	$( ".progress" ).each(function( index ) {
		//$( this ).css("height", height);
	});
}