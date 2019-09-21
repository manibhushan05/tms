var date = new Date();
var options = {
    weekday: "short", year: "numeric", month: "short",
    day: "numeric", hour: "2-digit", minute: "2-digit"
};
var lr_generation_dt = $('#lr_generation_DataTable').DataTable({
    "serverSide": true,
    "processing": true,
    "DisplayLength": 25,
    dom: 'Bfrtip',
    lengthMenu: [
        [25, 50, 100, 500, -1],
        ['25 Records', '50 Records', '100 Records', '500 Records', 'All Records']
    ],
    buttons: [
        'pageLength', {
            extend: 'excelHtml5',
            title: 'Generate LR List ' + date.toLocaleTimeString("en-US", options)
        },
        {
            extend: 'csvHtml5',
            title: 'Generate LR List ' + date.toLocaleTimeString("en-US", options)
        }
    ],
    "ordering": false,
    columnDefs: [{
        orderable: false,
        targets: "no-sort",
    }],
    // responsive: {
    //     details: false
    // },

    "ajax": {
        "type": "GET",
        "serverSide": true,
        "url": "/api/team-manual-booking-list/?booking_data_category=loaded_bookings&format=datatables",
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
        { data: "shipment_date" },
        {
            data: "booking_id",
            "render": function (data, type, row) {
                return '<a href="javascript:;" data-id="' + row.id + '"  class="btn btn-default getDetailLRHTML" style="background: darkgray; color:white">' + data + '</a>'
            }
        },
        { data: "customer_placed_order_data.name" },
        { data: "customer_placed_order_data.code" },
        { data: "supplier_data.name" },
        { data: "from_city_fk_data.name" },
        { data: "to_city_fk_data.name" },
        {
            data: null,
            "render": function (data, type, row) {
                return row.vehicle_data.vehicle_number + ', ' + row.vehicle_category_data.type;
            }
        },
        { data: "vehicle_data.vehicle_number", className: 'hidden' },
        { data: "vehicle_category_data.type", className: 'hidden' },
        { data: "id", className: 'hidden' },

    ],
    "language": {
        "processing": "<img class='loadingImage'  src='/static/aaho/images/loader.gif' />"
    }

});


//create  html and append to respective row
$(document).off("click", ".getDetailLRHTML").on("click", ".getDetailLRHTML", function () {
    var $row = $(this).parent().parent();
    var rowIndex = $($row).index();
    var id = $(this).attr('data-id');
    $(this).parent().parent().addClass('tr_' + id); //add class to row clicked
    var detailLRHtml = $(".detailLRTr_" + id).html();  //check html for detailed lr if not create and append
    if (detailLRHtml == undefined) {
        var detailedLRHtml = "";
        detailedLRHtml += "<div class='x_panel'>";
        detailedLRHtml += "<div class='x_title'>";
        detailedLRHtml += "<h2>LR Details </h2>";
        detailedLRHtml += "<ul class='nav navbar-right panel_toolbox'>";
        detailedLRHtml += "<li><a class='collapse-link getDetailedLRPage' data-row=" + id + "><i id='toggleDetailedLR_" + id + "' class='fa fa-chevron-down'></i></a>";
        detailedLRHtml += "</li>";
        detailedLRHtml += "</ul>";
        detailedLRHtml += "<div class='clearfix'></div>";
        detailedLRHtml += "</div>";
        detailedLRHtml += "<div id='detailedLRContent_" + id + "'>";

        detailedLRHtml += "</div>";
        detailedLRHtml += "</div>";

        detailedLRHtml += "<div id='otherLRDetails_" + id + "' class='x_panel' style='display:block !important;'>";
        detailedLRHtml += "<div class='otherLRContent_" + id + "'>";

        detailedLRHtml += "<div class='panel-body'>";
        detailedLRHtml += " <div class='row'>";

        detailedLRHtml += " <form class='form-horizontal form-label-left'";
        detailedLRHtml += " data-parsley-validate data-parsley-trigger='keyup'";
        detailedLRHtml += " id='create-confirmed-booking-lr-form_" + id + "'>";
        detailedLRHtml += "<input type='hidden'  name='mb_id' value=" + id + " />";
        detailedLRHtml += "<div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += "<label><span class='required'>Party Charged Weight(in Tonnes) *</span></label></br>";
        detailedLRHtml += "<input type='number' class='form-control' name='charged_weight' style='width: 100% !important;' ";
        detailedLRHtml += "data-parsley-min='0' min='0' data-parsley-type='number'  data-parsley-max='1000000' ";
        detailedLRHtml += " placeholder='Charged Weight' required step='0.001' />";
        detailedLRHtml += "</div>";

        detailedLRHtml += "<div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += "<label><span class='required'>Supplier Charged Weight(in Tonnes) *</span></label></br>";
        detailedLRHtml += "<input type='number' class='form-control' name='supplier_charged_weight' style='width: 100% !important;' ";
        detailedLRHtml += " placeholder='Supplier Charged Weight'";
        detailedLRHtml += "data-parsley-min='0' min='0' data-parsley-type='number'  data-parsley-max='1000000' ";
        detailedLRHtml += "required step='0.001' />";
        detailedLRHtml += "</div>";

        detailedLRHtml += " <div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += " <label><span class='required'>Actual Weight(in Tonnes) *</span></label></br>";
        detailedLRHtml += " <input type='number' style='width: 100% !important;' class='form-control' name='loaded_weight' data-parsley-min='0' ";
        detailedLRHtml += "min='0' data-parsley-type='number'  data-parsley-max='1000000' ";
        detailedLRHtml += " step='0.001' placeholder='Actual weight' required>";
        detailedLRHtml += " </div>";

        detailedLRHtml += " <div class='item form-group col-lg-12 col-md-12 col-sm-12 col-xs-12'></div>";

        detailedLRHtml += "<div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += " <label>Number Of LR Required <span class='required'>*</span></label></br>";
        detailedLRHtml += " <input type='number' class='form-control' name='number_of_lr'style='width: 100% !important;' ";
        detailedLRHtml += "  placeholder='Number of LR Per Lorry' required='required' value='1' data-parsley-min='1'";
        detailedLRHtml += "data-parsley-type='number'  data-parsley-max='10' autocomplete='off'>";
        detailedLRHtml += "   </div>";

        detailedLRHtml += "<div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += "<label><span class='required'>Refund *</span></label></br>";
        detailedLRHtml += "<input type='number' style='width: 100% !important;' class='form-control' name='refund_amount' data-parsley-min='0' min='0'";
        detailedLRHtml += "data-parsley-type='number'  data-parsley-max='1000000000' placeholder='Refund Amount' required>";
        detailedLRHtml += "</div>";

        detailedLRHtml += "<div class='item form-group col-lg-4 col-md-4 col-sm-4 col-xs-12'>";
        detailedLRHtml += "<label><span class='required'>GPS Device</span></label></br>";
        detailedLRHtml += "<select class='gps_device form-control' name='gps_device' style='width:100%'> ";
        detailedLRHtml += "<option></option>";
        detailedLRHtml += "</select>";
        detailedLRHtml += "</div>";

        detailedLRHtml += " <div class='item form-group col-lg-12 col-md-12 col-sm-12 col-xs-12'></br></div></br>";

        detailedLRHtml += "<div class='form-group col-lg-2 col-md-2 col-sm-2 col-xs-12'>";
        detailedLRHtml += " <button class='btn btn-success btn-md pull-right create-confirmed-booking-lr' ";
        detailedLRHtml += "data-rowIndex=" + id + " style='width: 100%' name='submit_type' value='generate_finish_lr'> ";
        detailedLRHtml += " Generate LR ";
        detailedLRHtml += " </button> ";
        detailedLRHtml += "</div>";
        detailedLRHtml += "</form>";

        detailedLRHtml += "</div>";
        detailedLRHtml += " </div>"; //panelbodyend

        detailedLRHtml += "</div>";
        detailedLRHtml += "</div>";
        $($row).after('<tr colspan="8" class="lrDetails detailLRTr_' + id + '"><td colspan="8" class="detailLRTd_' + rowIndex + '">' + detailedLRHtml + '</td></tr>');

        setTimeout(function () {
            $('#create-confirmed-booking-lr-form_' + id).parsley();
            $(".gps_device").select2({
                placeholder: "Select GPS Device",
                ajax: {
                    method: "GET",
                    url: '/api/driver-gps-device-list/',
                    headers: { "Authorization": localStorage.getItem('token') },
                    data: function (params) {
                        return {
                            search: params.term
                        };
                    },
                    processResults: function (data) {
                        var gpsArray = [];
                        $.each(data.data, function (key, value) {
                            gpsArray.push({ id: value.id, text: value.device_id + ', ' + value.device_provider_data.name })
                        });
                        return { results: gpsArray };
                    },
                    error: function (jqXHR, status, error) {
                        if (jqXHR.status == "401") {
                            redirectToLogin(error);
                        }
                    }
                },
                allowClear: true
            }).change(function () {
            });
        }, 100);
        $('#generate-lr-form_' + id).parsley('validate');
    }
    else {
        $(".detailLRTr_" + id).remove();
    }
});



$(document).off("click", ".create-confirmed-booking-lr").on("click", ".create-confirmed-booking-lr", function (e) {
    var rowIndex = $(this).attr("data-rowindex");
    var lrForm = $('#create-confirmed-booking-lr-form_' + rowIndex);
    if (!lrForm.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var data = lrForm.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();
    var generateLrCount = $("#lr_generation_badge").text();

    $.ajax({
        url: "/api/create-confirmed-booking-lr/",
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
            autoHideDelay: 30000,
            clickToHide: true,
            className: 'success'
        });

        NProgress.done();
        $('.tr_' + rowIndex).remove();
        $('.detailLRTr_' + rowIndex).remove();
        lr_generation_dt
            .draw(true);
        if (parseInt(generateLrCount) == 1) {
            $("#lr_generation_badge").text('');
        }
        else {
            var lrCount = parseInt(generateLrCount) - 1;
            $("#lr_generation_badge").text(lrCount);
        }
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    //return false;
});

//get detail other lr page and append to detailed row html
$(document).off("click", ".getDetailedLRPage").on("click", ".getDetailedLRPage", function () {
    var row = $(this).attr('data-row');
    $('#toggleDetailedLR_' + row).toggleClass("fa fa-chevron-up fa fa-chevron-down");

    if ($('#toggleDetailedLR_' + row).hasClass("fa-chevron-up")) {
        NProgress.start();
        $.ajax({
            url: '/page/team-manual-booking-detailed-lr/' + row + '/',
            type: 'GET',
            dataType: 'html',
            headers: { "Authorization": localStorage.getItem('token') },
            contentType: 'application/json',
        }).done(function (response, status, request) {
            NProgress.done();
            $('#detailedLRContent_' + row).html(response);

        }).fail(function (jqXHR, status, error) {
            if (jqXHR.status == "401") {
                redirectToLogin(error);
            }
            $('#error-response').text(JSON.parse(jqXHR.responseText)['msg']);
            NProgress.done();
        });
    }
    else {
        $('#detailedLRContent_' + row).html('');

    }
    $('#otherLRDetails_' + row).toggle();
});


$(document).off("click", ".detailed-lr-finish").on("click", ".detailed-lr-finish", function (e) {
    var id = $(this).attr('data-id');
    var generate_lr_and_finish = $('#detailedLRContent_' + id).find("#detailed-booking-form");
    if (!generate_lr_and_finish.parsley().isValid()) {
        return true;
    }
    e.preventDefault();
    NProgress.start();
    var generateLrCount = $("#lr_generation_badge").text();
    var data = generate_lr_and_finish.find(':input').filter(function () {
        return $.trim(this.value).length > 0
    }).serializeJSON();

    $.ajax({
        url: "/api/create-confirmed-booking-lr/",
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
        $('.tr_' + id).remove();
        $('.detailLRTr_' + id).remove();
        lr_generation_dt
            .draw(true);
        if (parseInt(generateLrCount) == 1) {
            $("#lr_generation_badge").text('');
        }
        else {
            var lrCount = parseInt(generateLrCount) - 1;
            $("#lr_generation_badge").text(lrCount);
        }
    }).fail(function (jqXHR, status, error) {
        if (jqXHR.status == "401") {
            redirectToLogin(error);
        }
        $.notify(response['msg'], {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});
