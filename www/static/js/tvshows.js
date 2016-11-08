window.onresize = function(event) {
    resize_tvshows();
};
window.onload = function() {
	resize_tvshows();
};
function resize_tvshows() {
	var height = $( ".thumbnail" ).css( "height" );
	$( ".episode_status" ).each(function( index ) {
		//$( this ).css("margin-top", '-'+height);
		//$( this ).css("margin-top", '0px');
	});
}