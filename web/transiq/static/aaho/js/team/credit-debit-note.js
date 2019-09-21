$(function () {
    $('form').parsley('validate');
});

$("#adjusted_bookings").select2({
    maximumSelectionLength: 1,
    placeholder: "Please add Bookings",
    ajax: {
        url: '/api/tiny-manual-booking-list/',
        headers: { "Authorization": localStorage.getItem('token') },
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var custArray = [];
            $.each(data.data, function (key, value) {
                custArray.push({ id: value.id, text: value.booking_id })
            });
            return { results: custArray };
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

// $('.btn-reset').click(function (e) {
//     location.reload();
// });

$('#issueCNCReset').click(function (e) {
    e.preventDefault();
    $('#form-credit-note-customer')[0].reset();
    $('#customer').text('');
    $('#adjusted_bookings').text('');
    $('#credit_note_reason').text('');
});

$('#resetIssueCNS').click(function (e) {
    e.preventDefault();
    $('#form-credit-note-supplier')[0].reset();
    $('#customer').text('');
    $('#adjusted_bookings').text('');
    $('#credit_note_reason').text('');
});
$('#resetIssueDNC').click(function (e) {
    e.preventDefault();
    $('#form-debit-note-customer')[0].reset();
    $('#customer').text('');
    $('#adjusted_bookings').text('');
    $('#debit_note_reason').text('');
});
$('#resetIssueDNS').click(function (e) {
    e.preventDefault();
    $('#form-debit-note-supplier')[0].reset();
    $('#customer').text('');
    $('#adjusted_bookings').text('');
    $('#credit_note_reason').text('');
});

$('#resetIssueDNCA').click(function (e) {
    e.preventDefault();
    $('#form-credit-note-customer-direct-advance')[0].reset();
    $('.customer').text('');
    $('.truck-suppliers').text('');
    $('#adjusted_bookings').text('');
    $('#credit_note_reason').text('');
});


$(".invoice").select2({
    placeholder: "Select Invoice",
    ajax: {
        url: '/team/invoice-number-data/',
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".credit_note_reason").select2({
    placeholder: "Select Reason",
    ajax: {
        url: '/api/credit-debit-note-reason-list/',
        headers: { "Authorization": localStorage.getItem('token') },
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var custArray = [];
            $.each(data.data, function (key, value) {
                custArray.push({ id: value.id, text: value.name })
            });
            return { results: custArray };
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

$('#btn-credit-note-customer').click(function (e) {
    var form_credit_note_customer = $('#form-credit-note-customer');
    if (!form_credit_note_customer.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_credit_note_customer.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/team-credit-note-customer-create/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            // window.location.href = "/api/issue-credit-note-customer-page";
            getAjaxCallFunction('/page/issue-credit-debit-note-page/');
        }, 4000);
    }).fail(function (data, status, error) {
        NProgress.done();
        if (data.status == "401") {
            redirectToLogin(error);
        }
        else {
            $.notify("Failed, Please try again later!!!", "error");
        }
    });
    return false;
});

$('#btn-credit-note-supplier').click(function (e) {
    var form_credit_note_supplier = $('#form-credit-note-supplier');
    if (!form_credit_note_supplier.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_credit_note_supplier.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/team-credit-note-supplier-create/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            // window.location.href = "/api/issue-credit-note-supplier-page/";
            getAjaxCallFunction('/page/issue-credit-debit-note-page/');
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        NProgress.done();
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

    });
    return false;
});


$('#btn-debit-note-customer').click(function (e) {
    var form_debit_note_customer = $('#form-debit-note-customer');
    if (!form_debit_note_customer.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_debit_note_customer.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/team-debit-note-customer-create/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            //  window.location.href = "/api/issue-debit-note-customer-page/";
            getAjaxCallFunction('/page/issue-credit-debit-note-page/');
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        NProgress.done();
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

    });
    return false;
});


$('#btn-debit-note-supplier').click(function (e) {
    var form_debit_note_supplier = $('#form-debit-note-supplier');
    if (!form_debit_note_supplier.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_debit_note_supplier.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/team-debit-note-supplier-create/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            //  window.location.href = "/api/issue-debit-note-supplier-page/";
            getAjaxCallFunction('/page/issue-credit-debit-note-page/');
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        NProgress.done();
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

    });
    return false;
});


$('#btn-credit-note-customer-direct-advance').click(function (e) {
    var form_credit_note_customer_direct_advance = $('#form-credit-note-customer-direct-advance');
    if (!form_credit_note_customer_direct_advance.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = form_credit_note_customer_direct_advance.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    $.ajax({
        url: '/api/team-credit-note-customer-direct-advance-create/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data),
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            //  window.location.href = "/api/issue-credit-note-customer-direct-advance-page/";
            getAjaxCallFunction('/page/issue-credit-debit-note-page/');
        }, 4000);
    }).fail(function (jqXHR, status, error) {
        NProgress.done();
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

    });
    return false;
});


$('#btn-debit-note-supplier-direct-advance').click(function () {
    var form_debit_note_supplier_direct_advance = $('#form-debit-note-supplier-direct-advance');
    if (!form_debit_note_supplier_direct_advance.parsley().isValid()) {
        return true;
    }

    NProgress.start();
    var data = form_debit_note_supplier_direct_advance.serializeJSON();
    $.ajax({
        url: '/team/create-debit-note-supplier-direct-advance/',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(data)
    }).done(function (data, status) {
        NProgress.done();
        $.notify(data['msg'], "success");
        setTimeout(function () {
            window.location.href = "/team/issue-debit-note-supplier-direct-advance-page/";
        }, 4000);
    }).fail(function (data, status) {
        NProgress.done();
        $.notify("Failed, Please try again later!!!", "error");
    });
    return false;
});

