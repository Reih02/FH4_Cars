// jQuery functionality for all forms (except delete), to stop double submits

// disable submit button after first click to avoid spam clicks
  $(document).ready(function() {
      // define fields as variables
      var submit_button = $('input#submit');
      var form = $('form#signupform')
      // on submit, disable submit button
      form.submit(function() {
          if (form) {
              submit_button.prop('disabled', true);
          }
      });
  });
