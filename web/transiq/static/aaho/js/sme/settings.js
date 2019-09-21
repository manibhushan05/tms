$('.modal').on('hidden.bs.modal', function (e) {

    $(this)
        .find("input[type!='submit'],textarea,select")
        .val('')
        .end()
        .find("input[type=checkbox], input[type=radio]")
        .prop("checked", "")
        .end();

})

function passwordValidate() {
        var password = document.getElementById("newPassword").value;
        var confirmPassword = document.getElementById("confirmPassword").value;
        if (password != confirmPassword) {
            alert("Passwords do not match.");
            return false;
        }
        return true;
    }

validator.message.date = 'not a real date';

      // validate a field on "blur" event, a 'select' on 'change' event & a '.reuired' classed multifield on 'keyup':
      $('form')
        .on('blur', 'input[required], input.optional, select.required', validator.checkField)
        .on('change', 'select.required', validator.checkField)
        .on('keypress', 'input[required][pattern]', validator.keypress);

      $('.multi.required').on('keyup blur', 'input', function() {
        validator.checkField.apply($(this).siblings().last()[0]);
      });

      $('form').submit(function(e) {
        e.preventDefault();
        var submit = true;

        // evaluate the form using generic validaing
        if (!validator.checkAll($(this))) {
          submit = false;
        }

        if (submit)
          this.submit();

        return false;
      });
// $(document).on('click', '.edit1', function() {
//   $(this).parent().siblings('td.data').each(function() {
//       var content = $(this).html();
//       $(this).html('<input value="' + content + '" />');
//   });
//
//   $(this).siblings('.save1').show();
//   $(this).siblings('.delete').hide();
//   $(this).hide();
// });
//
// $(document).on('click', '.save1', function() {
//
//   $('input').each(function() {
//     var content = $(this).val();
//     $(this).html(content + " ");
//     $(this).contents().unwrap();
//   });
//   $(this).siblings('.edit1').show();
//   $(this).siblings('.delete').show();
//   $(this).hide();
//
// });
//
// $(document).on('click', '.delete', function() {
//   $(this).parents('tr').remove();
// });
//
// $('.add').click(function() {
//   $(this).parents('table').append('<tr><td class="data">Add City</td><td class="data">Add Address</td><td><p class="save1">Save</p><p class="delete">Delete</p> <p class="edit1">Edit</p> </td></tr>');
// });
//
//
//
// $(document).on('click', '.edit', function() {
//   $(this).parent().siblings('td.data').each(function() {
//     var content = $(this).html();
//     $(this).html('<input value="' + content + '" />');
//   });
//
//   $(this).siblings('.save').show();
//   $(this).hide();
// });
//
// $(document).on('click', '.save', function() {
//
//   $('input').each(function() {
//     var content = $(this).val();
//     $(this).html(content + " ");
//     $(this).contents().unwrap();
//   });
//   $(this).siblings('.edit').show();
//   $(this).hide();
// });

// function displayProfile(){
//   var name = document.getElementById('name').value;
//   document.getElementById('nameDisplay').innerHTML = name;
//
//   var username = document.getElementById('username').value;
//   document.getElementById('usernameDisplay').innerHTML = username;
//
//   var constitution = document.getElementById('constitution').value;
//   document.getElementById('constitutionDisplay').innerHTML = constitution;
//
//   var address = document.getElementById('address').value;
//   document.getElementById('addressDisplay').innerHTML = address;
//
//   var pan = document.getElementById('pan').value;
//   document.getElementById('panDisplay').innerHTML = pan;
//
//   var vat = document.getElementById('vat').value;
//   document.getElementById('vatDisplay').innerHTML = vat;
//
// }