/**
 * Created by mani on 18/5/17.
 */

$(function () {
    $('form').parsley('validate');
});

var IS_GST_APPLICABLE = $("#is_gst_applicable");

IS_GST_APPLICABLE.select2({
    placeholder: "Select GST Choice",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
    if ($('#is_gst_applicable').val() === "yes") {
        $('.gstin-div').show();
        $('#gstin-input').prop('required', true);
    }
    else {
        $('.gstin-div').hide();
        $('#gstin-input').removeAttr('required');
    }

});

$(document).off('click', '#btn-update-customer').on('click', '#btn-update-customer', function () {
    var UPDATE_CUSTOMER_FORM = $('#update-customer-form');
    if (!UPDATE_CUSTOMER_FORM.parsley().isValid()) {
        return true;
    }
    var customerId = $("#customerId").val();
    NProgress.start();
    var data = UPDATE_CUSTOMER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/sme-sme-partial-update/" + customerId + "/",
        type: 'PATCH',
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
        }, 3000);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 1000,
                clickToHide: true,
                className: 'error'
            });
        }

        NProgress.done();
    });
    return false;
});