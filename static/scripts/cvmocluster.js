(function(mt) {
    var $ = jQuery; 
    // ============================
    // |  jQuery - Friendly Code  |
    // ============================
    // Import mootools '$' as 'mt'
    // Alias jQuery to '$'
    
    function __nsContextName_selectChoice( item, attributes )  {
    	window.console.log(item,attributes,'OK?');
    	return true;
    }
    
    /**
     * Update the 'order' data fields of each service entry in a
     * first-found seuence.
     */
    function __nsUpdateOrderField() {
        var container = $('#services_container'),
            elements = container.find(".services-list .service-row");
        for (var i=0; i<elements.length; i++) {
            __svcUpdateData($(elements[i]), { order: i });
        }
    }
    
    /**
     * Show or hide the '(no xxxx services defined)' placeholders, depending
     * on if we have items in that particular list or not.
     */
    function __nsUpdateEmptyPlaceholders() {
        if ($('#scalable-services-sortable').children().length == 1) {
            $('#label-no-scalable').show();
        } else {
            $('#label-no-scalable').hide();
        }
        if ($('#fixed-services-sortable').children().length == 1) {
            $('#label-no-fixed').show();
        } else {
            $('#label-no-fixed').hide();
        }
    }
    
    /**
     * Parse the data field of the given <tr /> entry and return a hash
     * with the stored values. 
     */
    function __svcParseData(tr) {
        var e_data = tr.find(".service-data input[type=hidden]"),
            ans = { };
        for (var i=0; i<e_data.length; i++) {
            var elm_name = e_data[i].get('name'),
                elm_value = e_data[i].get('value'),
                p = elm_name.split("][");
            elm_name = p[p.length-1];
            elm_name = elm_name.substr(0,elm_name.length-1);
            ans[elm_name] = elm_value;
        }
        return ans;
    }
    
    /**
     * Update the UI and /or the data fields of the given <tr /> using the given
     * visual and/or data information.
     */
    function __svcUpdateData(tr, data) {
        var e_data = tr.find(".service-data input[type=hidden]"),
            ans = { };
        
        // Update data fields (easy part)
        for (var i=0; i<e_data.length; i++) {
            var elm_name = e_data[i].get('name'),
                p = elm_name.split("][");
            
            // Update the UID
            if (data['uid'] != undefined) {
                p[p.length-2] = data['uid'];
                e_data[i].set('name', p.join(']['));
            }
            
            elm_name = p[p.length-1];
            elm_name = elm_name.substr(0,elm_name.length-1);
            if (data[elm_name] != undefined)
                e_data[i].set('value', data[elm_name]);
        }
        
        // Update UI fields (we hope for the best!)
        var e_visual = tr.find("td, th");
        for (var i=0; i<e_visual.length; i++) {
            var e = $(e_visual[i]);
            window.console.log(i);
            switch (i) {
                case 1: if (data['uid']!=undefined) e.html(data['uid'] || ''); break;
                case 2: if (data['template']!=undefined) e.html(data['template'] || ''); break;
                case 3: if (data['context']!=undefined) e.html(data['context'] || ''); break;
                case 4: if (data['network_offering']!=undefined) e.html(data['network_offering'] || ''); break;
                case 5: if (data['disk_offering']!=undefined) e.html(data['disk_offering'] || ''); break;
                case 6: if (data['service_offering']!=undefined) e.html(data['service_offering'] || ''); break;
            }
        }
    }
    
    /**
     * Create a new <tr /> compatible with the previously mentioned format
     * You can also provide the path of the static directory (assumed to be: /static/)
     */
    function __svcNewRow(d_static) {
        if (!d_static) d_static='/static/';
        return jQuery('<tr class="service-row">\
			<td class="handle"><img src="'+d_static+'images/handle.png" /></td>\
			<th>&nbsp;</th>\
			<td>&nbsp;</td>\
			<td>&nbsp;</td>\
			<td>&nbsp;</td>\
			<td>&nbsp;</td>\
			<td>&nbsp;</td>\
			<td class="operations">\
				<a href="javascript:;" onclick="deleteService(this)" class="softbutton">\
					<img border="0" src="'+d_static+'images/delete.png" align="absmiddle" /> Del\
				</a>\
				&nbsp;\
				<a href="javascript:;" onclick="editService(this)" class="softbutton">\
					<img border="0" src="'+d_static+'images/edit.png" align="absmiddle" /> Edit\
				</a>\
				<span class="service-data">\
				    <input type="hidden" name="values[services][placeholder][uid]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][context]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][template]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][network_offering]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][disk_offering]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][service_offering]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][order]" value="placeholder" />\
					<input type="hidden" name="values[services][placeholder][min_instances]" value="placeholder" />\
				</span>\
			</td>\
		</tr>');
    }
    
    /**
     * Return an empty, new data
     */
    function __newData() {
        return {
            'uid': '',
            'context': '',
            'template': '',
            'min_instances': 1,
            'service_offering': '',
            'disk_offering': '',
            'network_offering': ''   
        }
    }
    
    /**
     * Render the edit form with the given data and call the 'callback' when it's about
     * to update the field information.
     */
    var __submit_callback = function() { };
    function __editData(data, callback) {
		$("#add-service-error").hide();
		
		// Render Data
		$("#ns_uid").val(data['uid']);
		$("#ns_context_name").val(data['context']);
		$("#ns_template").val(data['template']);
		$("#ns_instances").val(data['min_instances']);
		$("#ns_service_offering").val(data['service_offering']);
		$("#ns_disk_offering").val(data['disk_offering']);
		$("#ns_network_offering").val(data['network_offering']);
		
		// Register callback
		__submit_callback = function(elm) {
		    callback({
		        'uid': $("#ns_uid").val(),
		        'context': $("#ns_context_name").val(),
		        'template': $("#ns_template").val(),
		        'min_instances': $("#ns_instances").val(),
		        'service_offering': $("#ns_service_offering").val(),
		        'disk_offering': $("#ns_disk_offering").val(),
		        'network_offering': $("#ns_network_offering").val(),
		    });
		}
		
		// Open dialog
        $( "#add-service-container" ).dialog( "open" );
    }
    
    /**********************************
     *        EXPORTED FUNCTIONS  
     **********************************/
    
    window.editService = function(button) {
        var parent = $($(button).parents('tr')[0]),
            data = __svcParseData(parent);
        __editData(data, function(data) {
            __svcUpdateData(parent, data);
        });
    };
    
    window.deleteService = function(button) {
        var parent = $($(button).parents('tr')[0]);
        parent.remove();        
    };
    
    /**********************************
     *      INITIALIZATION PART  
     **********************************/
    $(function() {

        // Setup autocomplete
        var NSContextNameAutocomplete = new CVMO.Widgets.AutoComplete( mt( "ns_context_name" ), {
    		"url": "/ajax/context/list"
    	});
    	
        // Setup accordion
        $( "#content-accordion" ).accordion({ 
            header: '.accordion-header',
            heightStyle: 'content'
        });
        
        // Setup sortable table
        $( "#fixed-services-sortable, #scalable-services-sortable" ).sortable({
            placeholder: "services-sortable-placeholder",
            connectWith: '.services-list',
            handle: '.handle',
            cancel: "#label-no-fixed, label-no-scalable",
            helper: function(e,o) {
                var elm = o.clone();
                elm.addClass('services-sortable-helper');
                return elm;
            },
            start: function(e, ui) {
                var obj = jQuery('<td colspan="8"></td>');
                    elm = $(".services-sortable-placeholder");
                obj.appendTo(elm);
            },
            stop: function(e, ui) {
                __nsUpdateEmptyPlaceholders();
                __nsUpdateOrderField();
            }
        });
        $( "#fixed-services-sortable" ).disableSelection();
        $( "#scalable-services-sortable" ).disableSelection();

        // Setup validator
        jQuery.validator.messages.required = "";
        jQuery.validator.addMethod("validate-context", function( value, element ) {
        		return NSContextNameAutocomplete.valid;
        	}, "");
        jQuery.validator.addMethod("positive", function( value, element ) {
        		return (value > 0);
        	}, "");
		$("#add-service-error").hide();
        $('#add-service-form').validate({
            invalidHandler: function(e, validator) {
    			var errors = validator.numberOfInvalids();
    			if (errors) {
    				var message = errors == 1
    					? 'You missed 1 field. It has been highlighted below'
    					: 'You missed ' + errors + ' fields.  They have been highlighted below';
    				$("#add-service-error span").html(message);
    				$("#add-service-error").show();
    			} else {
    				$("#add-service-error").hide();
    			}
    		},
        });
        
        // Setup dialog
        $('#add-service-container').dialog({
            autoOpen: false,
            height: 380,
            width: 450,
            modal: true,
            resizable: false,
            draggable: false,
            title: "Service editor",
            show: 'fade',
            buttons: {
                "Save": function() {
                    if ($('#add-service-form').valid() && NSContextNameAutocomplete.valid) {
                        $( this ).dialog( "close" );
                        __submit_callback( this );
                    }
                },
                Cancel: function() {
    				$("#add-service-error").hide();
                    $( this ).dialog( "close" );
                }
            }
        });
    	
    	// Setup service buttons
        $('#add-service').click(function() { 
            __editData(__newData(), function(data) {
                var elm = __svcNewRow();
                __svcUpdateData(elm, data);
                elm.appendTo('#scalable-services-sortable');
                __nsUpdateEmptyPlaceholders();
                __nsUpdateOrderField();
            })
        });
        
        // Update placeholders
        __nsUpdateEmptyPlaceholders();

    });
})($);
