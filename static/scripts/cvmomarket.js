
(function($) {
    
    CVMO.closeElement = null;
    CVMO.isLoading = false;
    CVMO.pendingElements = false;
    CVMO.activeGroup = null;
    CVMO.activeOffset = 0;
    
    CVMO.entries = [ ];
    
    CVMO.resetDescription = function() {
        $("#market_title").html("Select an item");
        $("#market_description").html("Select one of the items on the left to see more details.");
        $("#market_options").hide();
    };
    
    CVMO.resetItems = function() {
        $("#marketplace > ul").empty();
        CVMO.resetDescription();
        CVMO.activeOffset = 0;
        CVMO.entries = [ ];
    }
    
    CVMO.updateDetails = function( i ) {
        var details = CVMO.entries[i];
        if (!details) {
            CVMO.resetDescription();
            return;
        }
        
        $("#market_options").show();
        $("#market_title").html(details.label);
        $("#market_description").html(details.details);
        $("#market_author").html(details.owner);
        $("#market_tags").html(details.tags);
        $("#market_access").html(details.encrypted ? "<strong>Restricted</strong>" : "Open")
        $("#market_template").attr("href", "/context/clone/" + details.uid);
        $("#market_pair").attr("href", "/machine/pair/" + details.uid);
    };
    
    CVMO.addItems = function( data, offset ) {
        var ul = $("#marketplace > ul");
        for (var i=0; i<data.length; i++) {
            var id = i+offset;
            ul.append($(
                '<li>\
        			<input type="radio" id="i'+id+'" onclick="CVMO.updateDetails('+id+')" name="template" />\
        			<div>\
        				<label for="i'+id+'" style="background-image: url('+data[i].icon+')">'+data[i].label+'</label>\
        				<div class="details">'+data[i].description+'</div>\
        			</div>\
        		</li>'
        	));
        	CVMO.entries.push(data[i]);
        }
        
        // If we are empty, show empty message
        if (CVMO.entries.length == 0) $("#marketplace_empty").show();
    }
    
    CVMO.ajaxUpdate = function() {
        $("#marketplace_empty").hide();
        $("#marketplace_loader").show();
        CVMO.isLoading = true;
        
        $.ajax({
          url: "list.search",
          type: "GET",
          dataType: "json",
          data: {
              'query': $("#market_search").val(),
              'group': CVMO.activeGroup,
              'offset': CVMO.activeOffset
          }
        }).done(function( msg ) {
            $("#marketplace_loader").hide();
            CVMO.isLoading = false;
            window.console.log(msg);
            CVMO.pendingElements = ( msg.more ? true : false );
            CVMO.addItems( msg.items, CVMO.activeOffset );
            CVMO.activeOffset = msg.offset;
        }).error(function(err,textStatus, errorThrown) {
            window.console.error(textStatus);
            window.err = errorThrown;
        });
    }

    CVMO.initMarket = function() {
        CVMO.closeElement = $("#marketfilter > div.searchbar > div > a");
        CVMO.closeElement.hide();
        $("#marketplace_loader").hide();
        
        /**
         * Register the reset search button
         */
        CVMO.closeElement.click(function(e) {
            e.preventDefault(); 
            CVMO.closeElement.hide();
            $("#market_search").attr("value", "");
            CVMO.activeOffset = 0;
            CVMO.resetItems();
            CVMO.ajaxUpdate();
        });
        
        /**
         * Handle on search field the ENTER keypress
         */
        $("#market_search").keyup(function(c) {
            if (c.keyCode == 13) {
                var text = $("#market_search").val();
                if (text == "") {
                    CVMO.closeElement.hide();
                } else {
                    CVMO.closeElement.show();
                }
                CVMO.activeOffset = 0;
                CVMO.resetItems();
                CVMO.ajaxUpdate();
            }
        });
        
        /**
         * Handle group changes
         */
        $("#marketfilter > ul > li").each(function(i,elm) {
            var a = $(elm).children("a"),
                id = $(a).prop("class").split("-")[1];
            if (CVMO.activeGroup === null) {
                CVMO.activeGroup=id;
                $(elm).addClass("active");
            }
            
            var _id = id;
            $(a).click(function(e) {
                e.preventDefault(); 
                $("#marketfilter > ul > li").removeClass("active");
                $(elm).addClass("active");
                
                CVMO.activeGroup=_id;
                CVMO.activeOffset = 0;
                CVMO.resetItems();
                CVMO.ajaxUpdate();
            });
        });
        
        /**
         * Handle scroll-update
         */
        $("#marketplace").scroll(function(s) {
            var h = $("#marketplace").prop('scrollHeight') - $("#marketplace").height(),
                t = $("#marketplace").scrollTop();
                
            if ((t > h-40) && CVMO.pendingElements && !CVMO.isLoading) {
                CVMO.ajaxUpdate();
            }
        });
        
        // Initialize first batch
        $("#marketplace_empty").hide();
        CVMO.resetDescription();
        CVMO.resetItems();
        CVMO.ajaxUpdate();
    };
        
})(jQuery);
