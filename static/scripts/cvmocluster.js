/* Arrows */
var ServicesUpArrow;
var ServicesDownArrow;
var ArrowHideTimeout;

/* Autocomple field */
var NSContextNameAutocomplete;

/* Add DOM Ready event */
window.addEvent( "domready", __servicesTable_domReady );

/***** Table events *****/

function __servicesTable_domReady()
{
	/* Set Globals */
	ServicesUpArrow = $$( "#services_container img.up.arrow" )[0];
	ServicesDownArrow = $$( "#services_container img.down.arrow" )[0];
	
	/* Add service rows events */
	__addServiceRowsEvents();
	
	/* Add add row event */
	$$( "#services_container a.add-row" )[0].addEvent( "click", __addRow_click );
	
	/* Set arrows events */
	$$( "#services_container img.arrow" ).each( function( r ) { r.addEvent( "click", __servicesArrow_click ); } );
	$$( "#services_container img.arrow" ).each( function( r ) { r.addEvent( "mouseover", __servicesArrow_mouseOver ); } );
	$$( "#services_container img.arrow" ).each( function( r ) { r.addEvent( "mouseout", __servicesArrow_mouseOut ); } );
	
	/* Create autocomplete */
	NSContextNameAutocomplete = new CVMO.Widgets.AutoComplete( $( "ns_context_name" ), {
		"url": "/ajax/context/list",
		"onSelectChoice": __nsContextName_selectChoice
	} );
	
	/* Check tfoot visibility for services table */
	__checkServicesFooter();
}

function __addServiceRowsEvents()
{
	/* Are there any rows ? */
	if( $$( "#services_container table#services tr.base-row" ).length == 0 ) return;
	
	/* Set mouse over/out events in each */
	$$( "#services_container table#services tr.base-row" ).each( function( r ) { r.addEvent( "mouseover", __servicesTableRow_mouseOver ); } );
	$$( "#services_container table#services tr.base-row" ).each( function( r ) { r.addEvent( "mouseout", __servicesTableRow_mouseOut ); } );
	
	/* Add row add / remove events */
	$$( "#services_container table#services tr.base-row a.remove-row" ).each( function( r ) { r.addEvent( "click", __removeRow_click ); } );
}

function __checkServicesFooter()
{
	if( $$( "#services_container table#services tr.base-row" ).length == 0 ) {
		/* Show tfoot */
		$$( "#services_container table#services tfoot tr" )[0].setStyle( "display", "table-row" );
	} else {
		/* Hide tfoot */
		$$( "#services_container table#services tfoot tr" )[0].setStyle( "display", "none" );
	}
}

/***** Table rows events *****/

function __servicesTableRow_mouseOver( event )
{				
	var row = $( this );
	if( row.expanded ) {
		showArrow( ServicesUpArrow, row );
	} else {
		showArrow( ServicesDownArrow, row );
	}
}

function __servicesTableRow_mouseOut( event )
{
	var row = $( this );
	/* Arrow will be visible for half a second */
	ArrowHideTimeout = setTimeout( function(){ hideArrows( row ); }, 500 );
}

/***** Arrows events *****/

function __servicesArrow_click( event ) 
{
	var row = $( this ).shown_for;
	var detailsRow = row.getSiblings( "tr.details-row" )[0];
	
	/* Hide instantly arrow */
	hideArrows( row );
	
	/* Is expanded? */
	if( row.expanded ) {
		/* Hide details */		
		detailsRow.setStyle( "display", "none" );
		/* Change arrow */
		row.expanded = false;
		showArrow( ServicesDownArrow, row );
	} else {
		/* Show details */
		detailsRow.setStyle( "display", "table-row" );
		/* Change arrow */
		row.expanded = true;
		showArrow( ServicesUpArrow, row );
	}	
}

function __servicesArrow_mouseOver( event ) 
{
	/* Clear timeout */
	clearTimeout( ArrowHideTimeout );
}

function __servicesArrow_mouseOut( event ) 
{
	/* Arrow will be visible for half a second */	
	var arrow = $( this );
	ArrowHideTimeout = setTimeout( function(){ hideArrows( arrow.shown_for ); }, 500 );	
}

/***** Add / remove row events *****/

function __removeRow_click( event )
{
	event.preventDefault();
	
	/* Get rows */
	var baseRow = $( this ).getParent( "tr" );
	if( !baseRow ) return;
	var detailsRow = baseRow.getSiblings( "tr.details-row" )[0];
	
	/* Remove row and next row */
	baseRow.dispose();
	detailsRow.dispose();	
	
	/* Check tfoot visibility for services table */
	__checkServicesFooter();
	
	/* Hide the arrows */
	hideArrows();
}

function __addRow_click( event )
{
	event.preventDefault();
	
	/* Get the service object */
	var service = {
		"uid": $( "ns_uid" ).value,
		"context_name": $( "ns_context_name" ).value,
		"context_uid": $( "ns_context_uid" ).value,
		"context_has_key": $( "ns_context_has_key" ).value,
		"context_key": $( "ns_context_key" ).value,
		"template_uid": $( "ns_template_uid" ).value,
		"service_offering_uid": $( "ns_service_offering_uid" ).value,
		"disk_offering_uid": $( "ns_disk_offering_uid" ).value,
		"network_offering_uid": $( "ns_network_offering_uid" ).value
	};
		
	try {
		/* Validate the service */
		validateService( service );
		
		/* Add row */
		addService( service );
		
		/* Check tfoot visibility for services table */
		__checkServicesFooter();
		
		/* Reset the fields */ 
		$( "ns_uid" ).value = "";
		$( "ns_context_name" ).value = "";
		$( "ns_context_uid" ).value = "";
		$( "ns_context_has_key" ).value = "0";
		$( "ns_context_key" ).value = "";
		$( "ns_context_key_container" ).setStyle( "display", "none" );
		$( "ns_service_offering_uid" ).value = DefaultServiceOffering;
		$( "ns_disk_offering_uid" ).value = DefaultDiskOffering;
		$( "ns_network_offering_uid" ).value = DefaultNetworkOffering;
		$( "ns_template_uid" ).value = DefaultTemplate;
	} catch( exception ) {
		/* Display error */
		alert( exception );
	}	
}

/***** New service context name field events *****/

function __nsContextName_selectChoice( item, attributes ) 
{
	$( "ns_context_uid" ).value = attributes["uid"];
	if( attributes["has_key"] ) {   
		$( "ns_context_has_key" ).value = "1";
		$( "ns_context_key_container" ).setStyle( "display", "table-row" );
		$( "ns_context_key" ).addClass( 'invalid' );
		$( "ns_context_key" ).addEvent( "keyup", 
			function( event )
			{    	
				var value = $( "ns_context_key" ).get( "value" ) + "";
				if( value != "" ) {
					$( "ns_context_key" ).removeClass( "invalid" );
				} else {
					$( "ns_context_key" ).addClass( "invalid" );
				}
			}
		);
	} else {
		$( "ns_context_has_key" ).value = "0";
		$( "ns_context_key_container" ).setStyle( "display", "none" );
	}
	return true;
}

/***** Add service *****/

function addService( service )
{
	/* Create Base Row */
	var baseRowHTML = "<td>" + service.uid + "</td>";
	baseRowHTML += "<td>" + Templates[service.template_uid] + "</td>";
	baseRowHTML += "<td>" + service.context_name + "</td>";
	baseRowHTML += "<td class=\"operations\">" +
		"<a href=\"#\" class=\"softbutton remove-row\">" +
		"<img border=\"0\" src=\"" + DeleteImgPath + "\" align=\"absmiddle\" />" +
		" Remove Service" +
		"</a>" +
		"</td>";
	var baseRow = new Element( "tr", { "html": baseRowHTML, "class": "base-row" }  );	
	
	/* Create Details row */
	var detailsRowHTML = "<td colspan=\"4\">";
	detailsRowHTML += "<ul class=\"offerings\">";
	detailsRowHTML += "<li><strong>Service offering:</strong> " + ServiceOfferings[service.service_offering_uid] + "</li>";
	if( DiskOfferings[service.disk_offering_uid] )
		detailsRowHTML += "<li><strong>Disk offering:</strong> " + DiskOfferings[service.disk_offering_uid] + "</li>";
	if( NetworkOfferings[service.network_offering_uid] )
		detailsRowHTML += "<li><strong>Network offering:</strong> " + NetworkOfferings[service.network_offering_uid] + "</li>";
	detailsRowHTML += "</ul>";
		
	/* Add hidden fields */
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][uid]\" value=\"" + service.uid + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][context_uid]\" value=\"" + service.context_uid + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][context_key]\" value=\"" + service.context_key + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][template_uid]\" value=\"" + service.template_uid + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][service_offering_uid]\" value=\"" + service.service_offering_uid + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][network_offering_uid]\" value=\"" + service.network_offering_uid + "\" />";
	detailsRowHTML += "<input type=\"hidden\" name=\"values[services][disk_offering_uid]\" value=\"" + service.disk_offering_uid + "\" />";	
	
	detailsRowHTML += "</td>";
	var detailsRow = new Element( "tr", { "html": detailsRowHTML, "class": "details-row" }  );
	
	/* Add rows to table */
	var tbody = $$( "#services_container table#services tbody" )[0];
	baseRow.inject( tbody );
	detailsRow.inject( tbody );	
	
	/* Add events */
	__addServiceRowsEvents();
}

function validateService( service )
{
	if( service.uid.length == 0 ) throw "Service key is required";
	if( service.uid.length > 16 ) throw "Service key should be less than 16 characters.";
	if( service.context_uid.length == 0 ) throw "Context is required";
	if( service.context_has_key == 1 && service.context_key.length == 0 ) 
		throw "Context is encrypted, please provide key";
	if( service.template_uid.length == 0 ) throw "Template is required";
	if( service.service_offering_uid.length == 0 ) throw "Service offering is required";
}

/***** Arrow Show / Hide methods *****/

function showArrow( arrow, row )
{
	/* Clear timeout */
	clearTimeout( ArrowHideTimeout );
	
	/* Get row position and height */
	var rowPosition = row.getPosition();
	var rowHeight = row.getHeight();
	
	/* Get height and position of the arrow */
	var arrowHeight = arrow.getHeight();
	var arrowWidth = arrow.getWidth();
	var arrowPosition = rowPosition;	
	arrowPosition.x -= arrowWidth + 5;
	arrowPosition.y += ( rowHeight - arrowHeight ) / 2;
	
	/* Show the arrow */	
	arrow.setStyle( "visibility", "visible" );
	arrow.setPosition( arrowPosition );
	arrow.shown_for = row; // arrow should know next to which row is shown
	row.arrow_shown = true; // flag that arrow is shown	
}

function hideArrows( row )
{
	$$( "#services_container img.arrow" ).each( function( r ) { r.setStyle( "visibility", "collapse" ); } );	
	$$( "#services_container img.arrow" ).each( function( r ) { r.shown_for = 0; } );
	if( row ) row.arrow_shown = false;
	clearTimeout( ArrowHideTimeout );
}
