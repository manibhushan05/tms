$('#btn-update-contract-booking').click(function (e) {
    var update_contract_booking_rate_form = $('#update_contract_booking_rate_form');
    if (!update_contract_booking_rate_form.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = $('#update_contract_booking_rate_form').serializeJSON();
    $.ajax({
        url: "/api/contract-booking-partial-update/",
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
            autoHideDelay: 1200,
            clickToHide: true,
            className: 'success'
        });

        NProgress.done();
        setTimeout(function () {
             getAjaxCallFunction('/page/update-contract-booking/');
        }, 1500);
    }).fail(function (jqXHR, status,error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify('Failed', {
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

$('#btn-reset').click(function (e) {
     e.preventDefault();
     $('.updateRate').val(0);
});

