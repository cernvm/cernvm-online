
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
    var accordion = new Fx.Accordion($('content-accordion'), '#content-accordion .accordion-header', '#content-accordion .accordion-content', {
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
                    accordion.addSection(header, content);
                    accordion.display(content);
                } else {
                    
                    // Locate the previous element to display, only if we were
                    // selected
                    var select_index = -1;
                    for (var i=0; i<accordion.elements.length; i++) {
                        if (accordion.elements[i] == content) {
                            if (accordion.previous != i) { select_index = -1; }
                            break;
                        } else {
                            select_index=i;
                        }
                    }
                    
                    accordion.removeSection(header);
                    if (select_index!=-1) accordion.display(select_index);
                    
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
    
})};

CVMO.ContextUI.SelectServices = function(services) {
    CVMO.ContextUI.services.moveall(1,0);
    CVMO.ContextUI.services.select(1, services);
}

CVMO.ContextUI.AddUserFromForm = function() {
    CVMO.ContextUI.AddUser(
            $('new_user_name').getProperty('value'),
            $('new_user_group').getProperty('value'),
            $('new_user_home').getProperty('value'),
            $('new_user_password').getProperty('value')
        );
    $('new_user_name').setProperty('value','');
    $('new_user_home').setProperty('value','');
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
    if (groups[grp] == undefined) return;
     $('new_user_group').setProperty('value', String(selected_group).toLowerCase());
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