window.onresize = function(event) {
    resize_tvshow();
};
window.onload = function() {
	resize_tvshow();
};
function resize_tvshow() {
	var height = $( ".episode_thumbnail_img" ).css( "height" );
	$( ".episode_thumbnail" ).each(function( index ) {
		$( this ).css("height", height);
	});
	$( ".episode_status" ).each(function( index ) {
		$( this ).css("margin-top", '-'+height);
	});
	$( ".progress" ).each(function( index ) {
		$( this ).css("height", height);
	});
	$( ".coming" ).each(function( index ) {
		$( this ).css("line-height", height);
	});
}