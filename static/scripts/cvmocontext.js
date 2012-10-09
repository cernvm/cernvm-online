
CVMO.ContextUI = { };
CVMO.ContextUI.Init = function(groups) { window.addEvent('domready', function(){  // Run only when we are fully loaded
    
    CVMO.ContextUI.groups = groups;
    
    // Replace lists with drag/drop widgets
    CVMO.ContextUI.repositories = new CVMO.Widgets.DragLists([
        [ 'available_repos', 'available_repos_text' ],
        [ 'active_repos', 'active_repos_text' ]
    ]);
    CVMO.ContextUI.services = new CVMO.Widgets.DragLists([
        [ 'available_services', 'available_services_text' ],
        [ 'active_services', 'active_services_text' ]
    ]);
    
    // Prepare accordion
    CVMO.ContextUI.Accordion = new Fx.Accordion($('content-accordion'), '#content-accordion .accordion-header', '#content-accordion .accordion-content', {
        alwaysHide: false
    });
    
    // Prepare the switches for the modules
    $$('#content-accordion .cvmo-module').each(function(el) {
        var header = el,
            checkbox = el.getElement('input'),
            content = header.getNext(),
            fx = new Fx.Morph(content),
            updateView = function() {
                if (checkbox.get('checked')) {
                    header.addClass('accordion-header');
                    content.addClass('accordion-content');
                    header.removeClass('accordion-inactive-header');
                    content.removeClass('accordion-inactive-content');
                    CVMO.ContextUI.Accordion.addSection(header, content);
                    CVMO.ContextUI.Accordion.display(content);
                } else {
                    
                    // Locate the previous element to display, only if we were
                    // selected
                    var select_index = -1;
                    for (var i=0; i<CVMO.ContextUI.Accordion.elements.length; i++) {
                        if (CVMO.ContextUI.Accordion.elements[i] == content) {
                            if (CVMO.ContextUI.Accordion.previous != i) { select_index = -1; }
                            break;
                        } else {
                            select_index=i;
                        }
                    }
                    
                    CVMO.ContextUI.Accordion.removeSection(header);
                    if (select_index!=-1) CVMO.ContextUI.Accordion.display(select_index);
                    
                    fx.start({
                        'height': [content.getSize().y, 0]
                    }).chain(function() {
                        content.addClass('accordion-inactive-content');
                        content.removeClass('accordion-content');
                        header.addClass('accordion-inactive-header');
                        header.removeClass('accordion-header');
                    });
                }
            };
        
        header.addEvent('change', updateView);
        updateView();
    });
    
    // If we are using disabled mode, disable all the inputs
    if ($('content-accordion').hasClass('cvmo-context-disabled')) {
        $('content-accordion').getElements('input').each(function(e) { $(e).set('disabled',true); });
        $('content-accordion').getElements('select').each(function(e) { $(e).set('disabled',true); });
        $('content-accordion').getElements('textarea').each(function(e) { $(e).set('disabled',true); });
    }
    
    // Update group name
    $(window).addEvent('domready',function() {
        var grp = $('organisation').getProperty('value');
        if (grp != 'None') $('new_user_group').setProperty('value', grp.toLowerCase());
    });

    // Enable sliders on browsers that support it
    if (Browser.chrome || Browser.safari || Browser.opera) {
        $$('.cvmo-headcontrol').each(function(e) { 
            $(e).addClass('slider');
        });
    } else {
        $$('.cvmo-headcontrol').each(function(e) { 
            $(e).addClass('thin-slider');
        });
    }
    
    // Add validation command for custom command user
    jQuery.validator.addMethod( "except_value", 
    	function( value, element, forbiddenVal ) {
    		if( typeof forbiddenVal == "undefined" ) {
    			return true;
    		} else {
	    		return this.optional( element )
	    			|| value != forbiddenVal 
    		}
    	}, "Please check field value." );
    jQuery( "#create_context_form" ).validate(
    	{
    		rules: {
    			"values[name]": "required",
    			"values[general][cvm_raa_password]": "required",
    			"values[general][context_cmd_user]": {
    				required: "#f_contextcmd:filled",
    				except_value: "root"
    			}
    		},
    		messages: {
    			"values[general][context_cmd_user]": {    				
    				except_value: "Please do not use user root here."
    			}
    		},
    		highlight: function( element, errorClass, validClass ) 
    			{
    				jQuery( element ).addClass( errorClass ).removeClass( validClass );
    				/* Find block */
    				if( jQuery( element ).parents( "div.accordion-content" ).length == 0 )
    					return;
    				var block = jQuery( element ).parents( "div.accordion-content" )[0];
    				/* Does block has invalid inputs? */
    				if( jQuery( "input.error", block ).length > 0 ) {
    					CVMO.ContextUI.BlockSetError( block );
    				} else {
    					CVMO.ContextUI.BlockRemoveError( block );
    				}
    			},

    		unhighlight: function( element, errorClass, validClass ) 
    			{
    				jQuery( element ).addClass( validClass ).removeClass( errorClass );
    				/* Find block */
    				if( jQuery( element ).parents( "div.accordion-content" ).length == 0 )
    					return;
    				var block = jQuery( element ).parents( "div.accordion-content" )[0];
    				/* Does block has invalid inputs? */
    				if( jQuery( "input.error", block ).length > 0 ) {
    					CVMO.ContextUI.BlockSetError( block );
    				} else {
    					CVMO.ContextUI.BlockRemoveError( block );
    				}
    			}
    	}
    );
})};

CVMO.ContextUI.SelectServices = function(services) {
    CVMO.ContextUI.services.moveall(1,0);
    CVMO.ContextUI.services.select(1, services);
}

var i=1;
CVMO.ContextUI.AddUserFromForm = function() {
    CVMO.ContextUI.AddUser(
            $('new_user_name').getProperty('value'),
            $('new_user_group').getProperty('value'),
            $('new_user_home').getProperty('value'),
            $('new_user_password').getProperty('value')
        );
    i++;
    $('new_user_name').setProperty('value','user'+i);
    $('new_user_home').setProperty('value','/home/user'+i);
    $('new_user_password').setProperty('value','');
}

CVMO.ContextUI.RemoveUser = function(id) {
    $('user'+id).dispose();
};

CVMO.ContextUI.AddUser = function(name, group, home, password) {
    var table = $('table_users'),
        table_nu_form = $('newuser_row'),
        id = 0;
        
    // Find the last used user ID
    $$('tr.cvmo-user-entry').each(function(el) { 
        var eid = el.get('id');
        if (eid.substr(0,4) == 'user') {
            eid = eid.substr(4);
            if (eid>id) id=eid;
        }
    });
    id++;

    // Allocate user entry
    var row = new Element('tr', { 'class':'cvmo-user-entry', id: 'user'+id});
    new Element('td', { html: '<input type="hidden" name="values[general][users]['+id+'][name]" value="'+name+'" />'+name }).inject(row);
    new Element('td', { html: '<input type="hidden" name="values[general][users]['+id+'][group]" value="'+group+'" />'+group }).inject(row);
    new Element('td', { html: '<input type="hidden" name="values[general][users]['+id+'][home]" value="'+home+'" />'+home }).inject(row);
    new Element('td', { html: '<input type="hidden" name="values[general][users]['+id+'][password]" value="'+password+'" />****' }).inject(row);    
    new Element('td', { html: '<a href="javascript:;" onclick="CVMO.ContextUI.RemoveUser('+id+');" class="softbutton"><img border="0" src="/static/images/user_delete.png" align="absmiddle"> Remove user</a>' }).inject(row);
    row.inject(table_nu_form, 'before');
    new Fx.Reveal(row.getChildren(), {duration: 500, mode: 'vertical', opacity: 0});
    
}

CVMO.ContextUI.UpdateGroups = function(selected_group) {
    var grp = String(selected_group).toUpperCase();
    var groups = CVMO.ContextUI.groups;
    $('new_user_group').setProperty('value', String(selected_group).toLowerCase());
    if (groups[grp] == undefined) return;
    CVMO.ContextUI.repositories.select(1, groups[grp]); // Select that options on list #1
};

// API => Add environment variable from the form
CVMO.ContextUI.AddEnvFromForm = function() {
	// Do not let environment variables without a name
	if( $('new_env_var').getProperty('value') == "" ) {
		return;
	}
    // Create instance
    CVMO.ContextUI.AddEnv(
            $('new_env_var').getProperty('value'),
            $('new_env_value').getProperty('value')
        );
    $('new_env_var').setProperty('value','');
    $('new_env_value').setProperty('value','');
}

// API => Add environment variable row
CVMO.ContextUI.AddEnv = function(variable, value) {
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
    new Element('td', { align: 'left',   html: '<input type="hidden" name="values[general][environment]['+variable+']" value="'+value+'" />'+value }).inject(row);
    new Element('td', { align: 'center', 'class': 'v-center', html: '<a href="javascript:;" onclick="CVMO.ContextUI.RemoveEnv(\''+id+'\');" class="softbutton"><img border="0" src="/static/images/page_delete.png" align="absmiddle"> Remove variable</a>' }).inject(row);
    row.inject(table);
    new Fx.Reveal(row.getChildren(), {duration: 500, mode: 'vertical', opacity: 0});
    
}

// API => Remove environment variable row
CVMO.ContextUI.RemoveEnv = function(id) {
    // Dispose
    $(id).dispose();
}

/**************************************************
 * Blocks error set
 **************************************************/

CVMO.ContextUI.BlockSetError = function( block )
{
	/* Check that block has correct CSS class */
	if( !jQuery( block ).is( ".accordion-content" ) ) {
		return;
	}
	
	/* Find header */
	var header = jQuery( block ).prev( ".accordion-header" );
	
	/* Add classes */
	jQuery( block ).addClass( "error" );
	jQuery( header ).addClass( "error" );
	
	/* Show first with error */
	CVMO.ContextUI.ShowFirstErrorBlock();
}

CVMO.ContextUI.BlockRemoveError = function( block )
{
	/* Check that block has correct CSS class */
	if( !jQuery( block ).is( ".accordion-content" ) ) {
		return;
	}
	
	/* Find header */
	var header = jQuery( block ).prev( ".accordion-header" );
	
	/* Remove classes */
	jQuery( block ).removeClass( "error" );
	jQuery( header ).removeClass( "error" );
}

CVMO.ContextUI.ShowFirstErrorBlock = function()
{
	/* Are there any blocks with error? */
	if( jQuery( "div.accordion-content.error" ).length == 0 ) {
		return;
	}
	
	/* Find the first one */
	var firstBlock = jQuery( "div.accordion-content.error" )[0];
	
	/* Display it */
	CVMO.ContextUI.Accordion.display( firstBlock );
}
