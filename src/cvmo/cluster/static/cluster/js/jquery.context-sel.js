(function($) {
    var methods = {
        init: function(options)
        {
            if(!options.infoTmpl) {
                $.error("`infoTmpl` is a required option");
                return false;
            }
            if(!options.remoteURL) {
                $.error("`remoteURL` is a required option");
                return false;
            }
            $(this).data("options", options);

            var contexts_engine = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace("name"),
                queryTokenizer: Bloodhound.tokenizers.whitespace,
                remote: options.remoteURL + "?query=%QUERY"
            });
            contexts_engine.initialize();

            $(".context-selector", this).typeahead(null, {
                name: "context_id",
                valueKey: "id",
                displayKey: "name",
                source: contexts_engine.ttAdapter(),
                templates: {
                    suggestion: Handlebars.compile(
                        "{{owner}}: <strong>{{name}}</strong>"
                    )
                }
            });
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

            if(options.context)
                this.ContextSelector("select", options.context);
        },

        /*
         * Interface
         */

        select: function(context)
        {
            var options = $(this).data("options");
            if(context.description != "")
                context.description_not_empty = true;
            jQuery(".context-info", this).html(options.infoTmpl(context));
            jQuery(".context-value", this).val(context.id);
            jQuery(".context-selector", this).val(context.name);
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
            this.ContextSelector("select", context);
        },

        thAutocompleted: function(event, context, value)
        {
            this.ContextSelector("select", context);
        }
    };

    $.fn.ContextSelector = function(methodOrOptions)
    {
        if(methods[methodOrOptions]) {
            return methods[methodOrOptions].apply(
                this, Array.prototype.slice.call(arguments, 1)
            );
        } else if (typeof methodOrOptions == "object" || !methodOrOptions) {
            return methods.init.apply(this, arguments);
        } else {
            $.error(
                "Method " + methodOrOptions
                + " does not exist in jQuery.ContextSelector"
            );
        }
    }
})(jQuery);
