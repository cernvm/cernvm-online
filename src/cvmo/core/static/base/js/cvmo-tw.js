/*
 * Common JavaScript snippets for the new CernVM Online.
 */

//
// Password strength meter
// Code from: http://jsfiddle.net/fh9FP/12/
//

(function($) {

  // Safe scope where we are sure that $ is jQuery

  // Days required to crack a MD5 password with 1000 cores (on a 2014 computer):
  // those limits are used to calculate the "strength"
  var crack_limits = [
    { days:   400, verdict: 'weak',        pct:  25, cl: 'danger'  },
    { days: 20000, verdict: 'medium',      pct:  50, cl: 'warning' },
    // { days: 20000, verdict: 'strong',      pct:  75, cl: 'info'    },
    { days: 30000, verdict: 'very strong', pct: 100, cl: 'success' }
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
      $(password_sel).on('keyup', function() {
        $(that).password_strength_meter('recompute_score');
      });

      $(this).password_strength_meter('recompute_score');

    },

    // Called when pressing a key in the textbox
    recompute_score: function() {

      var score = $(this).password_strength_meter('measure_strength');

      // Find the verdict range
      for (i=0; i<crack_limits.length; i++) {
        if ( score <= crack_limits[i].days ) {
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

      // Remove all classes first
      for (i=0; i<crack_limits.length; i++) {
        $(this).removeClass( 'progress-bar-'+crack_limits[i].cl );
      }

      // Add the correct class
      $(this).addClass( 'progress-bar-'+params.cl );

      // Width
      $(this).css('width', params.pct+'%');

      // Text
      $(this).find('span').text(params.verdict + "**" + Math.floor(score));

    },

    // Measures the password strength.
    // Code from: http://jsfiddle.net/fh9FP/12/
    measure_strength: function() {

      password = $( '#'+$(this).data('password-id') ).val();

      // init character classes
      var numEx = /\d/;
      var lcEx = /[a-z]/;
      var ucEx = /[A-Z]/;
      var syEx = /\W/;
      var meterMult = 1;
      var character_set_size = 0;
      
      // loop over each char of the password and check it per regexes above.
      // weight numbers, upper case and lowercase at .75, 1 and .25 respectively.
      if (numEx.test(password)) {
        character_set_size += 10;
      }
      if (ucEx.test(password)) {
        character_set_size += 26;
      }
      if (lcEx.test(password)) {
        character_set_size += 26;
      }
      if (syEx.test(password)) {
        character_set_size += 32;
      }

      // Strenght represents the number of possibilities
      var strength = Math.pow(character_set_size, password.length);

      // Rate to crack a MD5 pwd (hashes/second) --> it's the fastest
      // all numbers from slowest computer here http://hashcat.net/oclhashcat-plus/
      var rateMd5 = 1333000000; 
      // var rateSHA1 = 433000000;
      // var rateMd5crypt = 855000;
      // var rateBcrypt = 604;

      // Score: number of days required to crack the MD5 password with 10000 cores
      var score = strength / rateMd5 / (10000 * 86400);

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
