(function($) {
    var SUGGESTION_TEMPLATE = Handlebars.compile(
        "{{owner}}: <strong>{{name}}</strong>"
    );
    var INFO_TEMPLATE = Handlebars.compile(
        "{{owner}}: <strong>{{name}}</strong>"
    ); // not a very nice idea to keep templates here like this!

    /**
     * --------------------
     * Options:
     * --------------------
     *
     * Remote URL
     * --------------------
     * remoteURL: The AJAX call endpoint. Should support `query` GET parameter.
     *
     * Templates
     * --------------------
     * suggestionTmpl: Handlebars template for suggestion
     * infoTmpl: Handlebars template for INFO section
     *
     */

    var methods = {
        init: function(options)
        {
            // Apply defaults
            options = $.extend({
                suggestionTmpl: SUGGESTION_TEMPLATE,
                infoTmpl: INFO_TEMPLATE
            }, options);

            // Validate
            if(!options.remoteURL) {
                $.error("`remoteURL` is a required option");
                return false;
            }

            // Store options
            $(this).data("options", options);

            // Create the Bloodhound engine
            var contexts_engine = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace("name"),
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                remote: options.remoteURL + "?query=%QUERY"
            });
            contexts_engine.initialize();

            // Create the typeahead
            $(".context-selector", this).typeahead(null, {
                name: "context_id",
                valueKey: "id",
                displayKey: "name",
                source: contexts_engine.ttAdapter(),
                templates: {
                    suggestion: options.suggestionTmpl
                }
            });

            // Setup the events
            var that = this;
            $(".context-selector", this).on(
                "typeahead:selected",
                function(e, c, v) {
                    $(that).ContextSelector("thSelected", e, c, v)
                }
            );
            $(".context-selector", this).on(
                "typeahead:autocompleted",
                function(e, c, v) {
                    $(that).ContextSelector("thAutocompleted", e, c, v)
                }
            );

            // Hide the password field by default and disable it (won't be sent with form)
            $(this).find(".context-selector-password").hide().find('input').val('').prop('disabled', true);

            // Apply initial value
            if (options.context) {
                $(this).ContextSelector("select", options.context);
            }
        },

        /*
         * Interface
         */

        select: function(context)
        {
            var options = $(this).data("options");
            if(context.description != "")
                context.description_not_empty = true;
            $(".context-info", this).html(options.infoTmpl(context));
            $(".context-value", this).val(context.id);
            $(".context-selector", this).val(context.name);

            if ( context.is_encrypted ) {
                // TODO: fill with password from Cluster Context definition (when cloning)
                $(this).find('.context-selector-password').show().find('input').val('password').prop('disabled', false);
            }
            else {
                $(this).find('.context-selector-password').hide().find('input').val('').prop('disabled', true);
            }
        },

        reset: function()
        {
            // TODO
            console.log("Reset called");
        },

        /*
         * Typeahead events
         */

        thSelected: function(event, context, value)
        {
            $(this).ContextSelector("select", context);
        },

        thAutocompleted: function(event, context, value)
        {
            $(this).ContextSelector("select", context);
        }
    };

    $.fn.ContextSelector = function(methodOrOptions)
    {
        var argv = arguments;
        return $(this).each(
            function()
            {
                if(methods[methodOrOptions]) {
                    return methods[methodOrOptions].apply(
                        this, Array.prototype.slice.call(argv, 1)
                    );
                } else if (typeof methodOrOptions == "object"
                        || !methodOrOptions) {
                    return methods.init.apply(this, argv);
                } else {
                    $.error(
                        "Method " + methodOrOptions
                        + " does not exist in jQuery.ContextSelector"
                    );
                }
            }
        );
    }
})(jQuery);
