$("#payment_mode").select2({
    placeholder: "Select Payment mode",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
    if ($('#payment_mode').val() !== 'cash') {
        $('#trn-label').text('CHQ/UTR No *');
        $("#trn").prop('required', true);
    }
    else {
        $('#trn-label').text('CHQ/UTR No');
        $("#trn").prop('required', false);
        $('#trn').parsley().validate();
    }
});

$("#customer").select2({
    placeholder: "Select Customer",
    ajax: {
        url: '/api/sme-sme-list/',
        headers: { "Authorization": localStorage.getItem('token') },
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var officeArray = [];
            $.each(data.data, function (key, value) {
                officeArray.push({ id: value.id, text: value.sme_profile.name + ', ' + value.company_code })
            });
            return { results: officeArray };
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$('.date').datepicker({
    format: "dd-M-yyyy",
    todayBtn: "linked",
    autoclose: true,
    todayHighlight: true
}).change(function () {
    $(this).parsley().validate();
});

function resetForm(formid) {
    $(':input', formid).not(':button, :submit, :reset, :hidden').val('')
        .removeAttr('checked').removeAttr('selected');
}

$('#btn-pending-inward-payment').click(function (e) {
    var PENDING_PAYMENT_FORM = $('#pending-inward-payment-form');
    if (!PENDING_PAYMENT_FORM.parsley().isValid()) {
        return true;
    }
    e.preventDefault();

    NProgress.start();
    var data = PENDING_PAYMENT_FORM.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: "/api/team-pending-inward-payment-entry-create/",
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
        }, 1500);

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
$('#btn-credited-inward-payments').click(function (e) {
    var CREDITED_INWARD_PAYMENT = $('#credited-inward-payments');
    if (!CREDITED_INWARD_PAYMENT.parsley().isValid()) {
        return true;
    }
    e.preventDefault(); // Totally stop stuff happening

    NProgress.start();

    var data = new FormData(CREDITED_INWARD_PAYMENT[0]);

    $.ajax({
        url: "/api/team-pending-inward-payment-entry-bulk-create/",
        enctype: 'multipart/form-data',
        data: data,
        processData: false,
        contentType: false,
        cache: false,
        timeout: 600000,
        type: 'POST',
        dataType: 'html',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        $('.right_col').html(response);
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
                className: 'error',
                scroll: true
            });
        }
        NProgress.done();
    });
    return false;
});

$(document).on('click', '#btn-add-receive-payments', function (e) {
    location.reload();
});
