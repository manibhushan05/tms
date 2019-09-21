/**
 * Created by mani on 4/5/17.
 */
$(function () {
    $('form').parsley('validate');
});
var COMPANY_CODE = $('#company_code');
$("input").change(function () {
    COMPANY_CODE.val(COMPANY_CODE.val().toUpperCase());
});


$('.gstin-div').hide();

function resetCustomerForm() {
    $('#register-sme-form')[0].reset();
    $('#city,#aaho_poc,#aaho_office,#is_gst_applicable').text('');

    $('#is_gst_applicable').append('<option value=""></option>' +
        '<option value="yes">Yes</option>' +
        '<option value="no">Exempted</option>');
}

$(document).off('click', '#resetRegisterCustomer').on('click', '#resetRegisterCustomer', function (e) {
    e.preventDefault();
    resetCustomerForm();
});

$(document).off('click', '#btn-register-sme').on('click', '#btn-register-sme', function () {
    var REGISTER_SME_FORM = $('#register-sme-form');
    if (!REGISTER_SME_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = REGISTER_SME_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();

    $.ajax({
        url: "/api/sme-sme-create/",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
        setTimeout(function () {
            location.reload();
        }, 2000);
    }).fail(function (jqXHR, status,error) {
        if(jqXHR.status === "401"){
            redirectToLogin(error);
          }
          else{
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 5000,
                clickToHide: true,
                className: 'error'
            });
          }
       
        NProgress.done();
    });
    return false;
});

