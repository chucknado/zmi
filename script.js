(function ($) {

  if (window.location.pathname.indexOf('/hc/communities') > -1 ||
      window.location.pathname.indexOf('/community/') > -1) {
    $('html').addClass('community');
  }

  $(document).ready(function () {

      /* REDIRECTS TO DESTINATION HELP CENTER */
      var newIds = {
    232191168:231954207,
    207090577:229136687,
    203658816:229492148,
    203658996:229492168,
    203658876:229140167
  };

  $('body').on('click', 'a[data-id]', function(e){
    var oldId = $(e.currentTarget).data('id');
    var newId = newIds[oldId];
    // console.log(oldId, newId);
    if(newId != undefined){
       e.preventDefault();
    	window.location = 'https://{subdomain}.zendesk.com/hc/en-us/articles/' + newId;
    }
    else{
    	console.log(newIds, oldId, newId);
    }
  });

  // Capture external page requests...
  var url = window.location.href;
  if (url.indexOf('/en-us/articles/') > -1) {
  	var partial = url.split('/en-us/articles/')[1];
    var id = partial.slice(0, 9);
    if (!isNaN(id)) {
      if (newIds[id]) {
        var newId = newIds[id];
  	    var new_href = url.replace(id, newId);
        new_href = new_href.replace('{src_subdomain}.zendesk.com', '{dst_subdomain}.zendesk.com');
      location.href = new_href;
      }
  	}
  }

  /* END OF REDIRECTS */

  // ...
  });

}(jQuery));


// INTERNAL LINK REDIRECTS TO DESTINATION HC

function redirect_to_HC_landing_page(e) {
	var href = e.target.href;
	if (!href || href.indexOf('{src_subdomain}.zendesk.com/hc/') == -1)
		return;
	var newIds = {
		'articles/231548527': 'sections/206223668'
	};
	var oldIds = Object.getOwnPropertyNames(newIds);
	for (var i = 0; i < oldIds.length; i++) {
		if (href.indexOf(oldIds[i]) > -1) {  // if the old id (a property name) is in the url
			e.preventDefault();
			var oldId = oldIds[i];
			var newId = newIds[oldId];
			var href = href.replace(oldId, newId);
			href = href.replace('{src_subdomain}.zendesk.com', '{dst_subdomain}.zendesk.com');
			location.href = href;
		}
	}
}

window.addEventListener('click', redirect_to_HC_landing_page, false);

// END OF REDIRECTS