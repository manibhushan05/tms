var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var reconcile_dt = $('#reconcile_DataTable').DataTable({
    "serverSide": true,
    "processing": true,
    "DisplayLength": 25,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500, -1],
        ['25 Records', '50 Records', '100 Records', '500 Records', 'All Records']
    ],
    buttons: [
        'pageLength'
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort",
    }],
    "ajax": {
        "type": "GET",
        "serverSide": true,
        "url": "/api/team-outward-payment-list/?outward_payment_data_category=reconcile&format=datatables",
        headers: { "Authorization": localStorage.getItem("token") },
        data: function (d) {
            $.extend(d);
            var dt_params = $('.input-sm').val();
            // Add dynamic parameters to the data object sent to the server
            if (dt_params) {
                $.extend(d, { search: dt_params });
            }
        },
        dataSrc: function (json) {
            return json.data;
        },
        error: function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
        }
    },
    columns: [

        { data: "payment_date" },
        { data: "id" },
        {
            data: "bookings_data",
            "render": function (data, type, row, meta) {
                return '<a href="javascript:;" data-id="' + data.id + '" data-url="/api/manual-booking-retrieve/' + data.id + '/"  class="btn btn-default getAjaxPage" style="background: darkgray; color:white">' + data.booking_id + '</a>'
            }
        },
        { data: "lr_numbers" },
        { data: "paid_to" },
        { data: "actual_amount" },
        {
            data: "",
            "render": function (data, type, row, idx) {
                return '<input type="hidden" class="form-control" name="data[' + idx.row + '][id]" value="' + row.id + '" ><input type="text" class="form-control" maxlength="100" name="data[' + idx.row + '][utr]" >'
            }
        },

    ],
    "language": {
        "processing": "<img  src='/static/aaho/images/loader.gif' />"
    },
    "drawCallback": function (settings, json) {
        if (settings.json.summary) {
            $('.noOfPayments').text(settings.json.summary.count);
            $('.amount').text(settings.json.summary.amount);
            if (settings.json.summary.count == 0) {
                $('#reconcile_badge').text('');
                $("#reconciled").attr('disabled', true);
            }
            else {
                $('#reconcile_badge').text(settings.json.summary.count);
                $("#reconciled").attr('disabled', false);
            }
        }
    }

});


$(document).off('click', '#reconciled').on('click', '#reconciled', function (e) {
    var data = $('#reconciled-form').find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    var dataArr = [];
    $.each(data, function (i, v) {
        $.each(v, function (idx, dval) {
            if (dval.utr != undefined) {
                dataArr.push(dval);
            }
        });
    });
    NProgress.start();
    $.ajax({
        url: '/api/team-reconcile-outward-payments/',
        type: 'patch',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(dataArr),
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
        reconcile_dt.draw(true);
        NProgress.done();
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
});

$(document).off('click', '#btn-reconcile-payments').on('click', '#btn-reconcile-payments', function (e) {
    var RECONCILE_BULK_PAYMENTS = $('#form-reconcile-bulk-payments');
    if (!RECONCILE_BULK_PAYMENTS.parsley().isValid()) {
        return true;
    }
    e.preventDefault(); // Totally stop stuff happening

    NProgress.start();

    var data = new FormData(RECONCILE_BULK_PAYMENTS[0]);

    $.ajax({
        url: "/api/team-reconcile-bulk-outward-payments/",
        enctype: 'multipart/form-data',
        data: data,
        processData: false,
        contentType: false,
        cache: false,
        timeout: 600000,
        type: 'POST',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 3000,
            clickToHide: true,
            className: 'success'
        });
        NProgress.done();
        $('#form-reconcile-bulk-payments')[0].reset();
        reconcile_dt.draw(true);
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status === "401") {
            redirectToLogin(error);
        }
        else {
            $.notify(JSON.parse(jqXHR.responseText)['msg'], {
                position: "top center",
                autoHideDelay: 100000,
                clickToHide: true,
                className: 'error',
                scroll: true
            });
        }
        NProgress.done();
    });
    return false;
});

