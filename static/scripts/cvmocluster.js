CVMO.ClusterUI = { };
window.addEvent('domready', function(){  // Run only when we are fully loaded	
	/* Add event for onSubmit of the form */	
	var __clusterCreate_onSubmit = function( event )
	{
		/* Check if there is context with password */
		var rows = $$( "tr.cvm-cluster-entry" );
		/* Are there rows? */
		if( rows == undefined || rows.length == 0 ) {
			alert( "Please select some contexts to include in the cluster!" );
			return false;
		}
		
		/* Forearch row - does it have a key? */
		var i, row, input;
		var thereIsContextWithKey = false;
		for( i = 0; i < rows.length; i++ ) {
			row = rows[i];
			input = $( row ).getElements( "input[name=\"values[instances][" + ( i + 1 ) + "][key]\"]" );
//			assert( typeof input == "object" && input.length == 1 && input[0] != undefined );
			if( $( input[0] ).getProperty( "value" ) != "" ) {
				thereIsContextWithKey = true;
				break;
			}
		}
		
		/* If there is a context with key, cluster must have a key as well */
		if( thereIsContextWithKey ) {
			var input = $( "cluster_key" );
			if( input.get( "disabled" ) != "" || input.get( "value" ) == "" ) {
				alert( "Please use a key for the cluster definition!" );
				return false;
			}
		}
				
		return true;
	}
	$( "cluster_create_form" ).addEvent( "submit", __clusterCreate_onSubmit );
    
    // Setup auto complete for context
    var autocomplete_field;
    if ($('new_context')) {
    	var contextSelected = function( item, attributes ) {
    		if( attributes["has_key"] ) {    			
    			$( "new_key" ).setStyle( "display", "block" );
    			$( "new_key" ).addClass('invalid');
    			$( "new_key" ).addEvent( "keyup", 
					function( event )
					{    	
    					var value = $( "new_key" ).get( "value" ) + "";
    					if( value != "" ) {
    						$( "new_key" ).removeClass( "invalid" );
    					} else {
    						$( "new_key" ).addClass( "invalid" );
    					}
					}
    			);
    		} else {
    			$( "new_key" ).tween( "display", "none" );
    		}
    		return true;
    	}
        autocomplete_field = new CVMO.Widgets.AutoComplete($('new_context'), {
            url: '/ajax/context/list',
            onSelectChoice: contextSelected
        });
    }
    
    // Prepare accordion
    var accordion = new Fx.Accordion($('content-accordion'), '#content-accordion .accordion-header', '#content-accordion .accordion-content', {
        alwaysHide: false
    });
    
    // Prepare some helper functions
    var reorder_names = function() {
        var id=0;
        $$('#table_cluster tbody tr').each(function(e) { // Elements will be always scanned top-to-bottom
            var i=++id;
            $(e).getElements('input, select').each(function(ie) {
                var name = ie.get('name');
                name = name.replace(/\[\d+\]/, '['+i+']');
                ie.set('name',name);
            });
        });
    };
    
    // Setup sortables
    var sort_list = $$("#table_cluster tbody");
    var table_sortables = new Sortables(sort_list, { 
        revert: true,
        onComplete: function(elm, ev) {
            // Reorder the names of the fields to match the
            // new order
            reorder_names();
        }
    });
    
    // API => Add instance from the form
    CVMO.ClusterUI.AddInstanceFromForm = function() {
        // Require valid auto-completed input
        if (!autocomplete_field.valid) return;    	
        if( $( "new_key" ).getStyle( "display" ) != "none" && $( "new_key" ).hasClass( "invalid" ) ) 
        	return;
        
        // Create instance
        var selectedOption = $$( "#new_service_offering option:selected" )[0];
        CVMO.ClusterUI.AddInstance(
                $('new_context').getProperty('value'),
                $('new_from_amt').getProperty('value'),
                $('new_to_amt').getProperty('value'),
                $('new_elastic').getProperty('checked'),
                $('new_key').getProperty('value'),
                $( selectedOption ).get( "value" ),
                $( selectedOption ).text
            );        
        $('new_context').setProperty('value','');
        $('new_from_amt').setProperty('value','1');
        $('new_to_amt').setProperty('value','1');
        $('new_elastic').setProperty('checked', "");
        $('new_key').setProperty('value', "");
        $( selectedOption ).set( "selected", "" )
    }

    // API => Add instance row
    CVMO.ClusterUI.AddInstance = function(context, fromAmt, toAmt, elastic, key, serviceOfferingValue, serviceOfferingLabel) {
        var table = $('table_cluster_body'),
            id = $$('#table_cluster tbody tr').length+1;

        window.console.log(table,id);

        // Allocate instance entry
        var row = new Element('tr', { 'class':'cvm-cluster-entry', 'id': 'instance'+id});
//        new Element('td', { align: 'center', html: '<img  id="instance_handle{{forloop.counter}}" class="cvm-context-handle handle" src="/static/images/handle.png" alt="=" />' }).inject(row);
        new Element('td', { html: '<input type="hidden" name="values[instances]['+id+'][context]" value="'+context+'" />'+context }).inject(row);
        new Element('td', { html: '<input type="text" style="width:50px" name="values[instances]['+id+'][from_amt]" value="'+fromAmt+'" />' }).inject(row);
        new Element('td', { html: '<input type="text" style="width:50px" name="values[instances]['+id+'][to_amt]" value="'+toAmt+'" />' }).inject(row);
        new Element('td', { align: 'center', html: '<input type="checkbox" name="values[instances]['+id+'][elastic]" value="1" '+(elastic?'checked="checked"':'')+'" />' }).inject(row);
        new Element('td', { align: 'center', html: serviceOfferingLabel + '<input type="hidden" name="values[instances]['+id+'][service_offering]" value="'+serviceOfferingValue+'" />' }).inject(row);
        var passwdText = "";
        if( key != "" ) {
        	passwdText  = "******";
        }
        new Element('td', { align: 'center', html: passwdText  + '<input type="hidden" name="values[instances]['+id+'][key]" value="'+key+'" />' }).inject(row);        
        new Element('td', { align: 'center', 'class': 'v-center', html: '<a href="javascript:;" onclick="CVMO.ClusterUI.RemoveInstance(\'instance'+id+'\');" class="softbutton"><img border="0" src="/static/images/vm_remove.png" align="absmiddle"> Remove instance</a>' }).inject(row);
        row.inject(table);
        new Fx.Reveal(row.getChildren(), {duration: 500, mode: 'vertical', opacity: 0});
        
        // Manage by sortables
        table_sortables.addItems(row);

    }

    // API => Remove instance row
    CVMO.ClusterUI.RemoveInstance = function(id) {
        // Unmanage from sortables
        table_sortables.removeItems($(id));
        
        // Dispose
        $(id).dispose();
        
        // Calculate new order
        reorder_names();
    }

    
    // API => Add environment variable from the form
    CVMO.ClusterUI.AddEnvFromForm = function() {
    	// Do not let environment variables without a name
    	if( $('new_env_var').getProperty('value') == "" ) {
    		return;
    	}
        // Create instance
        CVMO.ClusterUI.AddEnv(
                $('new_env_var').getProperty('value'),
                $('new_env_value').getProperty('value')
            );
        $('new_env_var').setProperty('value','');
        $('new_env_value').setProperty('value','');
        
    }

    // API => Add environment variable row
    CVMO.ClusterUI.AddEnv = function(variable, value) {
        var table = $('table_env_body'),
            id = 'env-entry-'+variable;

        // Allocate environment variable entry
        var row = new Element('tr', { 'class':'cvm-environment-entry', 'id': id});
        
        // Validate name
        variable = String(variable).replace(/['"]/g, '');
        variable = String(variable).replace(/\s/g, '_');
        
        // Create the element
        new Element('td', { align: 'right',  html: '<strong>'+variable+'</strong>' }).inject(row);
        new Element('td', { html: '=' }).inject(row);
        new Element('td', { align: 'left',   html: '<input type="hidden" name="values[environment]['+variable+']" value="'+value+'" />'+value }).inject(row);
        new Element('td', { align: 'center', 'class': 'v-center', html: '<a href="javascript:;" onclick="CVMO.ClusterUI.RemoveEnv(\''+id+'\');" class="softbutton"><img border="0" src="/static/images/page_delete.png" align="absmiddle"> Remove variable</a>' }).inject(row);
        row.inject(table);
        new Fx.Reveal(row.getChildren(), {duration: 500, mode: 'vertical', opacity: 0});
        
    }

    // API => Remove environment variable row
    CVMO.ClusterUI.RemoveEnv = function(id) {
        // Dispose
        $(id).dispose();
    }
        
});
