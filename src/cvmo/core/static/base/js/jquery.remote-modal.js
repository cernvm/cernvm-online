(function($) {
    /* Templates */
    var MODAL_TEMPLATE = Handlebars.compile(
        "<div class=\"modal remote-modal fade\" id=\"{{id}}\" tabindex=\"-1\"\
    role=\"dialog\" aria-labelledby=\"{{id}}_label\"\
    aria-hidden=\"true\">\
    <div class=\"modal-dialog\">\
        <div class=\"modal-content\">\
            <div class=\"modal-header\">\
                <button type=\"button\" class=\"close\"\
                    data-dismiss=\"modal\" aria-hidden=\"true\">\
                    &times;\
                </button>\
                <h4 class=\"modal-title\" id=\"{{id}}_label\">{{title}}</h4>\
            </div>\
            <div class=\"modal-body\">\
                <iframe frameborder=\"0\" height=\"{{height}}\"\
                    width=\"{{width}}\" src=\"{{remoteURL}}\"></iframe>\
            </div>\
            {{#buttonHTMLNotEmpty}}\
                <div class=\"modal-footer\">{{{buttonHTML}}}</div>\
            {{/buttonHTMLNotEmpty}}\
        </div>\
    </div>\
</div>"
    );
    var BUTTON_TEMPLATE = Handlebars.compile(
        "<a href=\"{{url}}\" class=\"btn {{classes}}\">{{label}}</a>"
    ); // not a very nice idea to keep templates here like this!

    /**
     * --------------------
     * Options:
     * --------------------
     *
     * Dimensions
     * --------------------
     * height: 400 (data-rm-height)
     * width: 600 (data-rm-width)
     *
     * Remote URL
     * --------------------
     * remoteURL: required (data-rm-remote)
     *
     * Override title
     * --------------------
     * title: undefined (data-rm-title)
     *
     * Footer options
     * --------------------
     * footer: [
     *     {
     *         "classes": ["btn-success"],
     *         "url": "http://cern.ch/",
     *         "label": "CERN Homepage"
     *     }
     * ]
     *
     */

    var methods = {
        init: function(options)
        {
            // Apply defaults
            options = $.extend({
                // Dimensions
                height: $(this).data("rm-height") || 400,
                width: $(this).data("rm-width") || 600,
                // Remote URL
                remoteURL: $(this).data("rm-remote") || undefined,
                // Override title
                title: $(this).data("rm-title") || undefined,
            }, options);

            // Validate
            if(!options.remoteURL) {
                $.error("`remoteURL` is a required option");
                return false;
            }

            // Store options
            $(this).data("options", options);

            // Set AJAX call
            $(this).click(
                function(e)
                {
                    e.preventDefault();
                    $(this).remoteModal("handleClick");
                }
            );
        },

        handleClick: function()
        {
            var options = $(this).data("options");
            if(options.modalElement) {
                $(options.modalElement).modal("show");
                return;
            }

            // Create the modal
            var btnHtml = "";
            if(options.footer) {
                for(var btnIdx in options.footer) {
                    var btn = options.footer[btnIdx];
                    btnHtml += BUTTON_TEMPLATE(btn);
                }
            }
            var modalElement = $(
                MODAL_TEMPLATE(
                    $.extend(
                        options,
                        {
                            title: options.title,
                            buttonHTML: btnHtml,
                            buttonHTMLNotEmpty: (btnHtml != "")
                        }
                    )
                )
            );
            $("div.modal-content", modalElement).css(
                "width", (options.width + 40) + "px"
            );
            $("body").append(modalElement);

            // Show modal
            var modal = $(modalElement).modal();
            $(modalElement).modal("show");
            options.modalElement = modalElement;
        }
    };

    $.fn.remoteModal = function(methodOrOptions)
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
                        + " does not exist in jQuery.remoteModal"
                    );
                }
            }
        );
    }
})(jQuery);
