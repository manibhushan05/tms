//call function from task status page to append filter html
function taskStatusFilterHtml(role, appendHtmlId) {
    var html = '';
    // html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12 divDateRange" >';
    html += '<div id="dateRange" style="display:none;">';
    html += ' <i class="fa fa-calendar"></i>&nbsp;';
    html += '<span class="dataRangeVal">Select date</span><i class="fa fa-caret-down" style="float:right;"></i>';
    html += '</div>';
    html += '</div>';

    html += '<div class="col-md-2 col-lg-2 col-sm-2 col-xs-12">';
    html += '<div class="item form-group">'
    html += '<select class="form-control employeeRole">';
    html += '<option></option>';
    html += '</select>';
    html += '</div>';
    html += '</div>';

    html += '<div class="col-md-4 col-lg-4 col-sm-4 col-xs-12" >';
    html += '<button class="btn btn-mg btn-success" id="taskStatusSearch">Search</button>';
    html += '<button class="btn btn-mg btn-primary" id="taskSearchClear">Clear</button>';
    html += '</div>';
    $("#" + appendHtmlId + "").html(html);
    employeeRoles();
    selectDaterange()
}

function employeeRoles() {
    $(".employeeRole").select2({
        placeholder: "Select role",
        ajax: {
            url: '/api/employee-roles-list/',
            headers: { "Authorization": localStorage.getItem('token') },
            data: function (params) {
                return {
                    search: params.term
                };
            },
            processResults: function (data) {
                var roleArray = [];
                $.each(data.data, function (key, value) {
                    roleArray.push({ id: value.id, text: value.role })
                });
                return { results: roleArray };
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

$(document).off("click", "#taskSearchClear").on("click", "#taskSearchClear", function (e) {
    $('#dateRange').data('daterangepicker').setStartDate(moment());
    $('#dateRange').data('daterangepicker').setEndDate(moment());
    $('#dateRange span').html('Select date');
    $(".employeeRole").val('').trigger('change');
    //get initial data
    task_status_dt.ajax.url(url).draw();
});
