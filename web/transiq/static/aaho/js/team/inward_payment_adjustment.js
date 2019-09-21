$(function () {
    $('form').parsley('validate');
});
var INWARD_PAYMENT_ADJUSTMENT_FORM = $('#inward-payment-adjustment-form');
$('#btn-pending-inward-payment').click(function (e) {
    if (!($('#total-balance-payment').text() === '0' && $('#total-balance-tds').text() === '0')) {
        alert('Please adjust entire amount before submit.');
        return true;
    }
    if (!INWARD_PAYMENT_ADJUSTMENT_FORM.parsley().isValid()) {
        return true;
    }
    var formData = INWARD_PAYMENT_ADJUSTMENT_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    NProgress.start();
    $.ajax({
        url: "/api/team-pending-inward-payment-bulk-adjust/",
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(formData),
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
            window.localStorage.setItem("functionalityName", "inward_entry");
            $("#homeDashboard").trigger("click");
        }, 2000);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
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
});