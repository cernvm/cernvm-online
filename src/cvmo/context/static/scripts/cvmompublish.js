
// jQuery-Compatible environment
(function($) {

    CVMO.Market = { };
    
    CVMO.Market.removeEnv = function( id ) {
        $("#"+id).detach();
    };
    
    CVMO.Market.addEnv = function( name, value, required ) {
        name = name.trim();
        value = value.trim();
        if (name == "") return;
        if (value == "") return;
		$('#table_env_body').append(jQuery('<tr id="env-entry-'+name+'" class="cvm-environment-entry">\
			<td align="right"><strong>'+name+'</strong></td>\
			<td align="center">=</td>\
			<td><input type="hidden" name="environment['+name+'][value]" value="'+value+'" />'+value+'</td>\
			<td align="center"><input type="checkbox" name="environment['+name+'][required]" value="1"'+(required ? ' checked="checked"' : '')+' /></td>\
			<td class="v-middle" align="center"><a href="javascript:;" onclick="CVMO.Market.removeEnv(\'env-entry-'+name+'\');" class="softbutton"><img border="0" src="/static/images/page_delete.png" align="absmiddle"> Remove variable</a></td>\
		</tr>'));
    };
    
    CVMO.Market.addEnvFromForm = function( host ) {
        CVMO.Market.addEnv(
                $("#new_env_var").val(),
                $("#new_env_value").val(),
                $("#new_env_required").attr("checked")
            );
        $("#new_env_var").val("");
        $("#new_env_value").val("");
        $("#new_env_required").attr("checked", false);
    };

    /**********************************
     *      INITIALIZATION PART  
     **********************************/
    $(function() {
        
        // Setup accordion
        $( "#content-accordion" ).accordion({ 
            header: '.accordion-header',
            heightStyle: 'content'
        });
        
        // Hook & Setup environment table
        $("#table_env")
        
    });

})(jQuery);
