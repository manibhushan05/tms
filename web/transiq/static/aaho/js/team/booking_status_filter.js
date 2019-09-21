//call function from booking status page to append html for filter
function bookingStatusFilterHtml(role, appendHtmlId) {
    var html = '';
    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12 divDateRange" >';
    html += '<div id="dateRange" style="">';
    html += ' <i class="fa fa-calendar"></i>&nbsp;';
    html += '<span class="dataRangeVal">Select date</span><i class="fa fa-caret-down" style="float:right;"></i>';
    html += '</div>';
    html += '</div>';

    if (role != "City Head") {
        html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12">';
        html += '<div class="item form-group">'
        html += '<select class="form-control sourceOffice">';
        html += '<option></option>';
        html += '</select>';
        html += '</div>';
        html += '</div>';
    }

    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12">';
    html += '<div class="item form-group">'
    html += '<select class="form-control destinationOffice">';
    html += '<option></option>';
    html += '</select>';
    html += '</div>';
    html += '</div>';

    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12">';
    html += '<div class="item form-group">'
    html += '<select class="form-control customer">';
    html += '<option></option>';
    html += '</select>';
    html += '</div>';
    html += '</div>';

    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12">';
    html += '<div class="item form-group">'
    html += '<select class="form-control supplier">';
    html += '<option></option>';
    html += '</select>';
    html += '</div>';
    html += '</div>';

    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12" >';
    html += '<button class="btn btn-mg btn-success" id="bookingStatusSearch">Search</button>';
    html += '<button class="btn btn-mg btn-primary" id="bookingSearchClear">Clear</button>';
    html += '</div>';
    $("#" + appendHtmlId + "").html(html);
    sourceOffice();
    destinationOffice();
    customer();
    supplier();
    selectDaterange()
}


function sourceCity() {
    $(".sourceCity").select2({
        placeholder: "Source City",
        ajax: {
            url: '/api/utils-city-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var cityArray = [];
                $.each(data.data, function (key, value) {
                    cityArray.push({ id: value.id, text: value.name + ',' + value.code + ',' + value.state.name })
                });
                return { results: cityArray };
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
}

function destinationCity() {
    $(".destinationCity").select2({
        placeholder: "Destination City",
        ajax: {
            url: '/api/utils-city-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var cityArray = [];
                $.each(data.data, function (key, value) {
                    cityArray.push({ id: value.id, text: value.name + ',' + value.code + ',' + value.state.name })
                });
                return { results: cityArray };
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
}

function sourceOffice() {
    $(".sourceOffice").select2({
        placeholder: "Source Office",
        ajax: {
            method: "GET",
            url: '/api/utils-aaho-office-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var officeArray = [];
                $.each(data.data, function (key, value) {
                    officeArray.push({ id: value.id, text: value.branch_name })
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
    });
}


function destinationOffice() {
    $(".destinationOffice").select2({
        placeholder: "Destination Office",
        ajax: {
            method: "GET",
            url: '/api/utils-aaho-office-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var officeArray = [];
                $.each(data.data, function (key, value) {
                    officeArray.push({ id: value.id, text: value.branch_name })
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
    });
}

function customer() {
    $(".customer").select2({
        placeholder: "Select Customer",
        ajax: {
            url: '/api/sme-sme-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var custArray = [];
                $.each(data.data, function (key, value) {
                    custArray.push({ id: value.id, text: value.sme_profile.name + ' ,' + value.company_code })
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
    });
}

function supplier() {
    $(".supplier").select2({
        placeholder: "Select Supplier",
        ajax: {
            url: '/api/broker-broker-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var brokerArray = [];
                $.each(data.data, function (key, value) {
                    brokerArray.push({ id: value.id, text: value.profile.name + ' ' + value.profile.phone })
                });
                return { results: brokerArray };
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
}

function selectDaterange() {
    var start = moment().subtract(29, 'days');
    var end = moment();
    function cb(start, end, label) {
        if (label == "Clear") {
            $('#dateRange').data('daterangepicker').setStartDate(moment());
            $('#dateRange').data('daterangepicker').setEndDate(moment());
            $('#dateRange span').html('Select date');
        }
        else if (start == null) {
            $('#dateRange').data('daterangepicker').setStartDate(moment());
            $('#dateRange').data('daterangepicker').setEndDate(moment());
        }
        else {
            $('#dateRange span').html(start.format('YYYY-MM-DD') + ' To ' + end.format('YYYY-MM-DD'));
        }
    }

    $('#dateRange').daterangepicker({
        startDate: moment().startOf('hour'),
        endDate: moment().startOf('hour').add(1, 'days'),
        ranges: {
            'Clear': [null, null],
            'Today': [moment(), moment()],
            'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        "showDropdowns": true,
        "minDate": "01/01/2010",
        "maxDate": moment()
    }, cb);
    cb(null, null);
}

$(document).off("click", "#bookingSearchClear").on("click", "#bookingSearchClear", function (e) {
    $('#dateRange').data('daterangepicker').setStartDate(moment());
    $('#dateRange').data('daterangepicker').setEndDate(moment());
    $('#dateRange span').html('Select date');
    $('.sourceCity').val('').trigger('change');
    $('.destinationCity').val('').trigger('change');
    $('.customer').val('').trigger('change');
    $('.supplier').val('').trigger('change');
    //to get initial data
    booking_status_dt.ajax.url(url).draw();
});
