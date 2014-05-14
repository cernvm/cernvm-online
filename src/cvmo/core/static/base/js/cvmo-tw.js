/*
 * Common JavaScript snippets for the new CernVM Online.
 */

//
// Password strength meter
// Code from: http://jsfiddle.net/fh9FP/12/
//

(function($) {

  //
  // Safe scope where we are sure that $ is jQuery
  //

  // Limits. 'score' represents the upper limit (-1 is 'infinite')
  var crack_limits = [
    { score: 26, verdict: 'weak',        pct:  25, cl: 'danger' },
    { score: 40, verdict: 'medium',      pct:  50, cl: 'warning' },
    { score: 50, verdict: 'strong',      pct:  75, cl: 'info'    },
    { score: -1, verdict: 'very strong', pct: 100, cl: 'success' }
  ];

  // Rules. See: http://jsfiddle.net/jquery4u/mmXV5/
  var rules = [

    // Email
    {
      score: -100,
      re: new RegExp(/^([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,6})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,5})?)$/i)
    },

    // Length
    {
      func: function(w) {
        return Math.pow( w.length, 1.4 );
      }
    },

    // Lowercase
    {
      score: 1,
      re: new RegExp(/[a-z]/)
    },

    // Uppercase
    {
      score: 3,
      re: new RegExp(/[A-Z]/)
    },

    // At least one number
    {
      score: 3,
      re: new RegExp(/\d/)
    },

    // At least three numbers
    {
      score: 5,
      re: new RegExp(/[0-9]{3}/)
    },

    // At least one special character
    {
      score: 3,
      re: new RegExp(/[^a-zA-Z0-9]/)
    },

    // At least two special characters
    {
      score: 5,
      re: new RegExp(/[^a-zA-Z0-9]{3}/)
    },

    // Upper/lower combo
    {
      score: 2,
      re: new RegExp(/([a-z].*[A-Z])|([A-Z].*[a-z])/)
    },

    // Letter/number combo
    {
      score: 2,
      re: new RegExp(/([a-zA-Z].*[0-9])|([0-9].*[a-zA-Z])/)
    },

    // Letter/number/char combo
    {
      score: 2,
      re: new RegExp(/([a-zA-Z0-9].*[^a-zA-Z0-9])|([^a-zA-Z0-9].*[a-zA-Z0-9])/)
    }

  ];

  var methods = {

    // This function is the constructor of our object
    init: function() {

      password_sel = $(this).data('password-id');

      if ( password_sel === undefined ) {
        $.error('Progress bar must contain the data-password-id attribute pointing to the password field to validate!');
        return;
      }

      password_sel = '#' + password_sel;

      var that = this;
      $(password_sel).on('input', function() {
        $(that).password_strength_meter('recompute_score');
      });

      $(this).password_strength_meter('recompute_score');

    },

    // Called when pressing a key in the textbox
    recompute_score: function() {

      var score = $(this).password_strength_meter('measure_strength');

      // Find the verdict range. Assumes crack_limits is already ordered
      // by scores.
      for (i=0; i<crack_limits.length; i++) {
        if ( score <= crack_limits[i].score ) {
          break;
        }
      }
      if (i == crack_limits.length) {
        i--;
      }

      // Apply style
      $(this).password_strength_meter('set_progressbar', crack_limits[i], score );

    },

    // Set progress bar class, value and label
    set_progressbar: function(params, score) {

      if ( $(this).find('span').text() == params.verdict ) {
        // Nothing to do: don't waste time redrawing
        return;
      }

      // Remove all classes first
      for (i=0; i<crack_limits.length; i++) {
        $(this).removeClass( 'progress-bar-'+crack_limits[i].cl );
      }

      // Add the correct class
      $(this).addClass( 'progress-bar-'+params.cl );

      // Width
      $(this).css('width', params.pct+'%');

      // Text
      $(this).find('span').text(params.verdict);

    },

    // Measures the password strength
    measure_strength: function() {

      password = $( '#'+$(this).data('password-id') ).val();

      score = 0;

      $.each( rules, function(idx, val) {

        if ( typeof val.func === 'function' ) {

          // Arbitrary function: we call it and add the return value to the score
          score += val.func(password);

        }
        else if (( val.re !== undefined ) && ( val.score !== undefined )) {

          // Regular expression: if it matches we add the specified score
          if ( val.re.test(password) ) {
            score += val.score;
          }

        }
        else {
          $.error( 'Cannot execute validation rule' );
        }

      });

      return score;

    }

  };

  // This property can be called directly on the object
  $.fn.password_strength_meter = function( methodOrOptions ) {

    var argv = arguments;

    if ( methods[methodOrOptions] ) {
      // We are calling a function: iterators not taken into account
      return methods[methodOrOptions].apply( this, Array.prototype.slice.call(argv, 1) );
    }
    else if ( typeof methods[methodOrOptions] == 'object' || !methodOrOptions ) {
      // Called from a jQuery chain: init the object, take iterators into account
      return $(this).each( function() {
        methods.init.apply( this, argv );
      });
    }
    else {
      $.error( 'Method ' + methodOrOptions + ' does not exist in jQuery.password_strength_meter' );
    }

  };

})(jQuery);
