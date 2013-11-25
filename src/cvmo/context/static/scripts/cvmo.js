
var CVMO = {
    Version: '0.1b',
    Widgets: { }
};

/**
 * A quick validation utility based on CSS selectors
 *
 * To use this widget: 
 *  1) Add on an <input> element the 'cvmo-validate' class
 *  2) (Optionally) add a -cvmo-validate= attribute to specialize the validation
 *     by default the system will check for empty fields.
 *
 * -cvmo-validate can be:
 *
 *  = required              : To require the field to be non-empty
 *  = equals:<CSS Selector> : To be equal with the value of another <input /> element
 *  = regex:<Regexp>        : To match a specified regular expression
 *
 * The attribute -cvmo-validate will be removed right after the page
 * is loaded.
 *
 */
CVMO.Widgets.ValidateInput = function( element ) {
    var requiredStar = new Element('span', { html: ' *', style: 'color: red' }),
        validation = element.getProperty('-cvmo-validate'),
        error_msg = "Field '%' has invalid value",
        e = $(element),
        
        validate = function() { 
            // Placeholder for later
            return true; 
        },
        skip_validation = function() {
            // Chceck if for some reasons we must skip the validation
            
        },
        guess_name = function() {
            // Try to lookup a name for the input element
            
            // 1) Use the element's 'alt' attrbiute 
            var h_alt=e.get('alt');
            if (h_alt) return h_alt;
            
            // 2) Lookup a label and get the innerText
            var h_id=e.get('id');
            if (h_id) {
                var items = $$('label[for='+h_id+']');
                if (items.length>0) {
                    if (document['all']) {
                        return items[0].innerText.replace(/["':]/,'').toLowerCase();
                    } else{
                        return items[0].textContent.replace(/["':]/,'').toLowerCase();
                    }
                }
            }
            
            // 3) Use the element's 'name' attrbiute if it's clean
            var h_name=e.get('name');
            if (h_name) {
                // Skip weird, or structured names that are not really good
                // to show on the users
                if (h_name.match(/[\[\]\{\}\(\)\<\>\/\\]/) == null)
                    return h_name;
            }
             
            // Found nothing...
            return false;
            
        },
        set_valid = function(is_valid) {
            // Mark this element as valid or invalid
            if (is_valid) {
                e.removeClass('cvmo-validator-invalid');
            } else {
                e.addClass('cvmo-validator-invalid');
            }
        },
        do_validation = function() {
            // Perform the validation process and return the status
            var valid = validate();
            set_valid(valid);
            return valid;
        };
        
    // Remove cvmo-validate property to be HTML-compatible
    element.removeProperty('cvmo-validate');

    // Simple 'REQUIRED' validation (Default)
    if ((!validation) || (validation == 'required')) {
        
        // Inject the 'required' star after the item
        requiredStar.inject(element, 'after');
        error_msg = "Field '%' is required!";
        
        // Prepare the validation function
        validate = function() { return (e.get('value') != '' || e.get('disabled')); };
        
    // Simple required and 'EQUALS' validation
    } else if (validation.substr(0,7) == 'equals:') {

        // Inject the 'required' star after the item
        requiredStar.inject(element, 'after');
        error_msg = "Field '%' does not match!";

        // Prepare the validation function
        var elm = $$(validation.substr(7))[0];
        if (elm != undefined) {
            validate = function() { 
                return (e.get('value') != '') && (e.get('value') == elm.get('value')) || e.get('disabled'); 
            };
        }

    // Simple 'RERGULAR EXPRESSION' validation
    } else if (validation.substr(0,6) == 'regex:') {

        // Inject the 'required' star after the item
        requiredStar.inject(element, 'after');
        error_msg = "Field '%' has not a valid value!";

        // Prepare the validation function
        validate = function() {
            var r = new RegExp(validation.substr(6),'i');
            return (String(e.get('value')).match(r) != null) || e.get('disabled'); 
        };

    }
    
    // Register do_validation on blur
    e.addEvent('blur', do_validation);
    
    // If we have a parent form, register a submit event
    var f = e.getParent('form');
    if (f) {
        f.addEvent('submit', function() {
            if (!do_validation()) { 
                var name = guess_name();
                if (name != false) {
                    alert(error_msg.replace('%',name));
                } else {
                    alert('Please fill all the required fields!');
                }
                return false;
            };
        });
    }
    
};
$(window).addEvent('load', function() {
    $$('input.cvmo-validate').each(function(e) {
        var ne = e; // Clone e
        new CVMO.Widgets.ValidateInput(ne);
    });
});

/**
 * A checkbox that disables/enables elements with specified class
 *
 * This component allows a <input type="checkbox" /> elemet to enable/disable a set
 * of other elements depending on the value.
 *
 * To use this widget: 
 *  1) Add on a <input> element the 'cvmo-disabling' class
 *  2) Give a unique ID on the <input>
 *  3) For every item you want to be hidden when the input is disabled
 *     put this class on it: 'cvmo-disabling-<input id>'
 *
 * For example, check the following snippet:
 *
 * <input type="checkbox" class="cvmo-disabling" id="curtain" />
 * <p class="cvmo-disabling-curtain">The curtain is visible</p>
 *
 */
CVMO.Widgets.DisablingCheckbox = function( element ) {
    var id = element.get('id');
    
    // Populate the elements to work upon
    var elements=[];
    $$('.cvmo-disabling-'+id).each(function(e) {
        if (!e.get('disabled')) elements.push(e);
    });
    
    // Create helper functions
    var updateItems = function() {
        var value = element.get('checked');
        Array.each(elements, function(e) {
            $(e).set('disabled',!value);
            $(e).removeClass('cvmo-disabling-disabled');
            if (!value) $(e).addClass('cvmo-disabling-disabled');
        });
    }
    // Bind the change listener
    $(element).addEvent('click', updateItems);
    // Activate the ones witht he current value
    updateItems();
};
$(window).addEvent('load', function() {
    $$('input.cvmo-disabling').each(function(e) {
        var ne = e; // Clone e
        new CVMO.Widgets.DisablingCheckbox(ne);
    });
});

/**
 * A List that discloses other items
 *
 * This component allows a <select /> elemet to act as a disclosing component of
 * other HTML elements.
 *
 * To use this widget: 
 *  1) Add on a <select> element the 'cvmo-disclose' class
 *  2) Give a unique ID on the <select>
 *  3) For every item you want to be visible when a specific option is
 *     selected, put this class on it: 'cvmo-disclose-<select id>-<option value>'
 *
 * For example, check the following snippet:
 *
 * <select id="curtain" class="cvmo-disclose">
 *      <option value="1">Show</option>
 *      <option value="0">Hide</option>
 * </select>
 * <p class="cvmo-disclose-curtain-1">The curtain is visible</p>
 * <p class="cvmo-disclose-curtain-0">The curtain is hidden</p>
 *
 * This code also works for checkboxes. Consider the following example:
 *
 * <input type="checkbox" id="curtain" class="cvmo-disclose"/>
 * <p class="cvmo-disclose-curtain-checked">The curtain is visible</p>
 * <p class="cvmo-disclose-curtain-unchecked">The curtain is hidden</p>
 *
 * Special "value suffixes" are "checked" and "unchecked".
 */
CVMO.Widgets.DisclosureList = function( list ) {
    var options = list.getChildren("option"),
        id = list.get('id'),
        updateVisibleItems = function() {

            // Checkbox
            if ( list.get('type') == 'checkbox' ) {

                var checked = list.get('checked');
                var classChecked  = '.cvmo-disclose-' + id + '-checked';
                var classUnchecked = '.cvmo-disclose-' + id + '-unchecked';

                if (checked) {
                    classToEnable = classChecked;
                    classToDisable = classUnchecked;
                }
                else {
                    classToEnable = classUnchecked;
                    classToDisable = classChecked;
                }

                // Enable
                $$(classToEnable).each(function(e) {
                    $(e).addClass('cvmo-disclosed');  // show
                });
                $$(classToEnable + ' input').each(function(e) {
                    $(e).set('disabled', false);  // enable
                });

                // Disable
                $$(classToDisable).each(function(e) {
                    $(e).removeClass('cvmo-disclosed');  // hide
                });
                $$(classToDisable).each(function(e) {
                    $(e).set('disabled', true);  // disable
                });

            }
            else {

                // Get selection
                var value = list.get('value');
                // Hide all
                for (var i=0; i<options.length; i++) {
                    $$('.cvmo-disclose-'+id+'-'+options[i].get('value')).each(function(e) {
                        $(e).addClass('cvmo-disclosed');
                    });
                    $$('.cvmo-disclose-'+id+'-'+options[i].get('value')+' input').each(function(e) {                	
                    	$(e).set('disabled', true);
                    });
                }
                // Activate only the ones that have that value
                $$('.cvmo-disclose-'+id+'-'+value).each(function(el) {
                    el.removeClass('cvmo-disclosed');
                });
                $$('.cvmo-disclose-'+id+'-'+value+' input').each(function(el) {
                	el.set('disabled', false);
                });

            }

        };
    
    // Bind the change listener
    $(list).addEvent('change', updateVisibleItems);
    
    // Activate the ones witht he current value
    updateVisibleItems();
};
$(window).addEvent('load', function() {
    $$('select.cvmo-disclose').each(function(e) {
        new CVMO.Widgets.DisclosureList(e);
    });
    $$('input[type=checkbox].cvmo-disclose').each(function(e) {
        //alert('yay');
        new CVMO.Widgets.DisclosureList(e);
    });
});

/**
 * Draggable/Droppable List
 *
 * This component links one or more lists into a draggable set.
 * Use like this:
 *
 * var dl = new CVMO.Widgets.DragLists([
 *    [ 'Id of the list', 'id of the text element', ( optional callback ) ],
 *    ...
 * ]);
 *
 * Every list is expected to be an unordered <ul> element. The text element is an
 * <input type="text" /> element that will hold the serialized result of the list.
 *
 */
CVMO.Widgets.DragLists = function( lists, options ) {
    var lists_ui = [ ], lists_text = [ ], lists_cb = [ ], sortable;
    var opt = options || { };
    if (opt.separator == undefined) opt.separator=',';
    if (opt.populate == undefined) opt.populate=true;
    if (opt.deduplicate == undefined) opt.deduplicate=true;
    if (opt.disabled == undefined) opt.disabled=false;
    if (opt.autodisable == undefined) opt.autodisable=true;
    if (opt.capitalize == undefined) opt.capitalize=false;

    // Helper functions
    var list_callbacks = function( list, cb_empty ) {
            var children = $(list).getChildren('li');
            if (cb_empty == null) return;
            if (children.empty()) {
                cb_empty(list, true);
            } else {
                cb_empty(list, false);
            }
        },    
        update_all = function() {
            for (var i=0; i<lists_ui.length; i++) {
                // Serialize text
                lists_text[i].setProperty('value', sortable.serialize(i, function(element, index){
                    return element.innerHTML;
                }).join(opt.separator));
                // Trigger callbacks for display/hide empty element
                list_callbacks(lists_ui[i], lists_cb[i]);
            }
        };

    // Fetch lists information
    var populate=opt.populate;
    for (var i=0; i<lists.length; i++) {
        lists_ui.push($(lists[i][0]));
        lists_text.push($(lists[i][1]));
        if (lists[i].length>2) { lists_cb.push(lists[i][2]) } else { lists_cb.push(null) };
        if (!lists_ui[i].getChildren().empty()) populate=false;
    }
    
    // If we don't have list items, populate them now
    if (populate) {
        var dedup=[];
        for (var i=lists.length-1; i>=0; i--) {
            var items = String(lists_text[i].getProperty('value')).split(opt.separator);
            if (opt.autodisable && lists_text[i].get('disabled')) opt.disabled=true;
            if (items[0]=='') continue;
            Array.each(items, function(e) {
                if (opt.deduplicate) {
                    if (dedup.indexOf(e)>=0) return;
                    dedup.push(e);
                }
                new Element('li', { html: e, styles:{ 'text-transform': (opt.capitalize?'capitalize':'none') } }).inject(lists_ui[i]);
            });
        }
    }
    
    // Create sortable magic on the UI
    sortable = new Sortables(lists_ui, {
      clone: true,
      revert: true,
      opacity: 0.7,
      onComplete: function() { setTimeout(update_all, 1000); }
    });
    
    // Check for disabled status
    if (opt.disabled) sortable.detach();
    
    // Update text fields
    update_all();
    
    // Register my functions
    this.select = function(to_list, names) {
            var put_elm = [ ];
            for (var i=0; i<lists.length; i++) {
                var children = lists_ui[i].getChildren();
                Array.each(children, function(child) {
                    var item = child.innerHTML;
                    Array.each(names, function(name) {
                        if (name == item) {
                            if (i != to_list) {
                                lists_ui[to_list].grab(child); // Adopt child into the defined list
                            }
                        }
                    });
                });
            }
            update_all();
        };
        
    this.moveall = function(from_list, to_list) {
            Array.each(lists_ui[from_list].getChildren(), function(e) { 
                lists_ui[to_list].grab(e);
            });
        };

    
};

/**
 * Textual Auto-Complete widget
 *
 * (I wasn't satisfied with the existing implementations... sorry.. :)
 * Use like this:
 * 
 * var ac = new CVMO.Widgets.AutoComplete( '#my_input', {
 *      url: '<base url>'
 * });
 *
 * This widget requests the URL defined in the configuration dictionary and sends
 * the current contents of the text field in the 'query' GET parameter.
 *
 * It expects a JSON reply in the following format:
 * [
 *     { label: '<text label>', text: '<HTML Contents that describe the item>' },
 *     ...
 * ]
 * 
 */
CVMO.Widgets.AutoCompleteDropdown = null;
CVMO.Widgets.AutoComplete = function( element, options ) {
    var el = element,
        items = [],
        query = null,
        index = -1,
        self = this;
    
    /* Set browser autocomplete to off */
    $( el ).set( "autocomplete", "off" );
    $( el ).addEvent( "change", 
		function( event )
		{
    		if( $( el ).get( "value" ) == "" ) {
    			set_valid( true );
    		}
		}
    );

    // Prepare dropdown element
    if (CVMO.Widgets.AutoCompleteDropdown == null) {
        CVMO.Widgets.AutoCompleteDropdown = new Element('div', { id: 'cvmo-autocomplete-dropdown' });
        CVMO.Widgets.AutoCompleteDropdown.inject(document.body)
    }
    var dropdown = CVMO.Widgets.AutoCompleteDropdown;
    
    // Prepare exports
    this.valid = false;
    
    // Update the validity state of the input    
    var set_valid = function(isValid) {
        self.valid = isValid;
        $(el).removeClass('invalid');
        if (!isValid) $(el).addClass('invalid');
    }
    
    // UI -> Select ite
    var select_item = function(item) {
        for (var i=0; i<items.length; i++) {
            $(items[i][0]).removeClass('active');
            if (i==item) {
                index=item;
                $(items[i][0]).addClass('active');
                var pos = $(items[i][0]).getPosition(dropdown),
                    siz = $(items[i][0]).getSize(),
                    scr = $(dropdown).getScroll(),
                    osz = $(dropdown).getSize();
//                window.console.log(pos,siz,scr,osz);
            };
        }
    };
    
    // UI -> Empty the list
    var reset_list = function() {
        // Empty list
        if (dropdown != null) {
            Array.each(items, function(e) { $(e[0]).destroy() });
            dropdown.setStyle('display', 'none');
            dropdown.empty();
        }
        
        // Clear list
        items=[];
        index=-1;
    };
    
    // UI -> Fetch data from the server
    var update_list = function() {
        
        // Cancel pending queries
        if (query!=null)
            if (query.isRunning())
                query.cancel();
        
        // Place spinner
        $(el).addClass('cvmo-autocomplete-spinner');
        
        // Send request
        var q = $(el).get('value');
        query = new Request.JSON({url: options.url, onSuccess: function(data){
            // Remove spinner
            $(el).removeClass('cvmo-autocomplete-spinner');
            
            // If the list is empty, add an empty item indicator
            if (!data.length) {
                new Element('div', { html:'(No matching results)' }).inject(dropdown);
                
            } else {
                var container = new Element('ul');
                container.inject(dropdown);
                
                // Populate list
                var i=0;
                Array.each(data, function(item) { 

                    // Highlight keywords
                    var txt = item.text;
                    txt = txt.replace(query,'<strong>'+q+'</strong>');
                    
                    // Prepare items
                    var elm = new Element('li', { html: txt }),
                    id=i++;
                    
                    // Bind events
                    elm.addEvent('mousemove', function(e) {
                        select_item(id);
                    });
                    elm.addEvent('click', function(e) {
                        if( select_value( [ elm, item.label, item.attributes ] ) ) {
	                        set_valid(true);
	                        reset_list();
	                        $(el).focus();
                        }
                    });
                    
                    // Store to container
                    $(elm).inject(container)

                    // Push item in the list
                    items.push([ elm, item.label, item.attributes ]);
                });
                
                // Select first item
                select_item(0);
                
            }
            
            // Show list
            show_list();
                
        }, onError: function(data) {
                // Remove spinner
                $(el).removeClass('cvmo-autocomplete-spinner');
                
        }}).get({'query': q });
        
    };
    
    // UI -> Display dropdown
    var show_list = function() {
        var pos = $(el).getPosition(),
            siz = $(el).getSize();
        
        // Align and show
        dropdown.setStyles({
            width: siz.x-2,
            left: pos.x,
            top: pos.y+siz.y,
            display: 'block'
        });
        
    };
    
    // UI -> Perform dropdown sequence
    var do_dropdown = function() {
        reset_list();
        update_list();
    }
    
    // UI -> Select an item from the list
    var select_value = function( item ) {
    	/** 
    	 * Item:
    	 * 	0: element (li)
    	 * 	1: label
    	 * 	2: attributes map
    	 * 		attr_name: attr_value	
    	 */
    	
    	/* Is there callback ? */
    	if( typeof options["onSelectChoice"] == "function" ) {
    		res = options["onSelectChoice"]( item[1], item[2] );
    	} else {
    		res = true;
    	}
    	
    	/* Set value */
    	if( res ) $( el ).set( "value", item[1] );
    	
    	return res;
    }
    
    // Prepare timer var
    var timer=0;
    
    // Register events
    $(el).addEvent('blur', function(e) {
        setTimeout(reset_list, 300);
    });
    $(el).addEvent('keydown', function(e) {
        if (e.code == 13) { /* enter */
            if( index != -1 && select_value( items[index] ) ) {
	            set_valid(true);
	            reset_list();
                $(el).focus();
	            return false;
            }
        } else if (e.code == 40) { /* down arrow */
            return false;
        } else if (e.code == 38) { /* up arrow */
            return false;
        } else if (e.code == 9) { /* tab */
        	/* Do nothing - tab is ignored! */
        } else {
            set_valid(false);
        }        
    });
    $(el).addEvent('keyup', function(e) {
        clearTimeout(timer);
        if (e.code == 40) { // Down
            var value = $(el).get('value');
            if (index == -1) {
                if (value.length>=1) do_dropdown();
            } else {
                index++;
                if (index>=items.length) index=0;
                select_item(index);
            }
        } else if (e.code == 38) { // Up
            var value = $(el).get('value');
            if (index == -1) {
                if (value.length>=1) do_dropdown();
            } else {
                index--;
                if (index<0) index=items.length-1;
                select_item(index);
            }
        } else if (e.code == 13) { /* enter */
            // Passthru
        } else {
            var value = $(el).get('value');
            if (value.length < 1) {
                clearTimeout(timer);
                reset_list();
                set_valid(false);
            } else {
                timer=setTimeout(do_dropdown, 500);
                set_valid(false);
            }
        }
    });
    
    // Invalidate by default
    set_valid(false);
    
};

/**
 * Makes a drop down button from certain CSS selectors. Example of HTML that
 * will become a button toggling a drop down list:
 *
 * <div class="dropdownbutton">
 *   <span>Button label</span>
 *   <ul>
 *     <li>Option 1</li>
 *     <li><a href="http://a-link/">Option 2</a></li>
 *   </ul>
 * </div>
 *
 * Proper transformations are applied at page load.
 *
 */
CVMO.Widgets.MakeDropDown = function( element ) {
    $(element).getChildren('span').addEvent('click', function(evt) {
        evt.stopPropagation();  // avoid trigger close MooTools

        // jQuery used here
        btn = jQuery(this);
        opt = btn.parent().children('ul');

        // Close other dropdowns
        jQuery('.dropdownbutton ul').not(opt).slideUp('fast');

        // Open and position this dropdown
        opt.css('min-width', btn.outerWidth());
        mwth = 150;
        mw = btn.outerWidth()*2.5;
        if (mw < mwth) mw = mwth;
        opt.css('max-width', mw);

        left_wrt_viewport = btn.offset().left + btn.outerWidth()*0.5 -
            jQuery(window).scrollLeft();
        viewport_width = jQuery(window).width();

        if (left_wrt_viewport > viewport_width*0.5) {
            // Right align
            off_right = viewport_width - (btn.offset().left + btn.outerWidth());
            opt.css('right', off_right);
        }
        else {
            // Left align
            opt.css('left', btn.offset().left);
        }

        opt.css('top', btn.offset().top + btn.outerHeight() );
        opt.slideToggle('fast');
    });
};
$(window).addEvent('load', function() {
    $$('.dropdownbutton').each(function(e) {
        var ne = e;
        new CVMO.Widgets.MakeDropDown(ne);
    });
});
$(window).addEvent('click', function() {
    $$('.dropdownbutton ul').each(function(e) {
        jQuery(e).slideUp('fast');
    });
});