/**
 * Created by mani on 5/5/17.
 */
$(function () {
    $('form').parsley('validate');
});

function resetSupplierForm() {
    $('#register-supplier-form')[0].reset();
    $('#city,#aaho_office,#states').text('');
}

$(document).off('click', '#resetRegisterSupplier').on('click', '#resetRegisterSupplier', function (e) {
    e.preventDefault();
    resetSupplierForm();
});

$(document).off('click', '#btn-register-supplier').on('click', '#btn-register-supplier', function () {
    var REGISTER_SUPPLIER_FORM = $('#register-supplier-form');
    if (!REGISTER_SUPPLIER_FORM.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    console.log(REGISTER_SUPPLIER_FORM.serialize());
    var data = REGISTER_SUPPLIER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/broker-broker-create/",
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

    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(jqXHR['responseText'], {
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
