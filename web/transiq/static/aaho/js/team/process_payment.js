function color_code(payment_date) {
    date = moment(payment_date, 'DD-MMM-YYYY');
    today = moment();
    if (moment(payment_date, 'DD-MMM-YYYY').isBefore(moment().add(-1, 'days'))) {
        return '#8B0000'
    }
    else if (moment(payment_date, 'DD-MMM-YYYY').isAfter(moment())) {
        return '#228B22';
    }
    else {
        return '#A9A9A9';
    }
}

var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var process_payment_dt = $('#process_payment_DataTable').DataTable({
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
        "url": "/api/team-outward-payment-list/?outward_payment_data_category=process_payment_enet&format=datatables",
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
            if (json.summary) {
                $('.noOfPayments').text(json.summary.count);
                $('.amount').text(json.summary.amount);
                if (json.summary.count === 0) {
                    $("#download_payment_file").attr('disabled', true);
                }
                else {
                    $("#download_payment_file").attr('disabled', false);
                }
            }
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
                return '<a href="javascript:;" data-id="' + data.id + '" data-url="/api/manual-booking-retrieve/' + data.id + '/"  class="btn btn-default getAjaxPage" style="background: ' + color_code(row.payment_date) + '; color:white">' + data.booking_id + '</a>'
            }
        },
        { data: "lr_numbers" },
        { data: "paid_to" },
        { data: "actual_amount" },
        { data: 'payment_mode_display' }

    ],
    "language": {
        "processing": "<img  src='/static/aaho/images/loader.gif' />"
    }

});

$(document).off('click', '#download_payment_file').on('click', '#download_payment_file', function (e) {
    NProgress.start();
    $.ajax({
        url: '/api/download-today-payment-file/',
        type: 'get',
        dataType: 'json',
        contentType: 'application/json',
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('Authorization', localStorage.getItem('token'));
        }
    }).done(function (response, status) {
        if (response.msg) {
            window.open(response.msg, "_self", "");
        }
        $.notify('File sent successfully', {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        process_payment_dt.draw(true);
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