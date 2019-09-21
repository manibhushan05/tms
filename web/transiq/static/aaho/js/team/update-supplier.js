/**
 * Created by mani on 18/5/17.
 */


$(function () {
    $('form').parsley('validate');
});

$(document).off('click', '#btn-update-supplier').on('click', '#btn-update-supplier', function () {
    var UPDATE_SUPPLIER_FORM = $('#update-supplier-form');
    if (!UPDATE_SUPPLIER_FORM.parsley().isValid()) {
        return true;
    }
    var supplierId = $("#supplierId").val();
    NProgress.start();
    var data = UPDATE_SUPPLIER_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/broker-broker-partial-update/" + supplierId + "/",
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
        if (jqXHR.status === "401") {
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
