(function($) {
    $.extend({
      getUrlVars: function(){
          var vars = [], hash;
          var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
          for(var i = 0; i < hashes.length; i++)
          {
                hash = hashes[i].split('=');
                vars.push(hash[0]);
                vars[hash[0]] = hash[1];
              }
          return vars;
        },
      getUrlVar: function(name){
          return $.getUrlVars()[name];
        }
    });
    if ($.getUrlVar("e") == null) {
        $(document).ready(function($) {
                $(".object-tools").append('<li><a href="?e=1" class="changelink">Edit all</a></li>');
            });
    } else {
        $(document).ready(function($) {
                $(".object-tools").append('<li><a href="?" class="changelink">Back</a></li>');
            });
    }
})(django.jQuery);
