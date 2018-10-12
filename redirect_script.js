<!-- Update idMap and add script tag in Document Head template of source HC's theme -->


  /*
  DOC REDIRECTS
  Performs redirect on the error page after HC detects doc is missing.
  Place in the document ready block.
  */
  (function(){
    var error_page_class = document.getElementsByClassName('error-page');
    if (error_page_class.length > 0) {
      var url = window.location.href;
      var this_hc = 'support.zendesk.com';
      var articles = {
        200625646: {hc: this_hc, id: 360000355328},
        200937457: {hc: 'help.zendesk.com', id: 206223868},
        205777498: {hc: 'help.zendesk.com', id: 360001994188},
        206416187: {hc: 'help.zendesk.com', id: 360002014167},
        206494147: {hc: 'help.zendesk.com', id: 360002014147},
        213550488: {hc: 'help.zendesk.com', id: 360001994168}
      };
      for (var article in articles) {
        if (url.indexOf(article) !== -1) {
          url = url.replace(article, articles[article].id);
          var hc = articles[article].hc;
          if (this_hc !== hc) {
            url = url.replace(this_hc, hc);
          }
          location.href = url;
        }
      }
    }
  })();
