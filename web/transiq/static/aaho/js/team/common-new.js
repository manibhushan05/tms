$("#owner_id").select2({
    placeholder: "Select Owner",
    ajax: {
        url: '/api/owner-owner-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
         data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var ownerArray = [];
            $.each(data.data, function (key, value) {
                ownerArray.push({id: value.id, text: value.owner_profile.name + ',' + value.owner_profile.phone})
            });
            return {results: ownerArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#supplier_id").select2({
    placeholder: "Select Supplier",
    ajax: {
        url: '/api/supplier-supplier-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
         data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var supplierArray = [];
            $.each(data.data, function (key, value) {
                supplierArray.push({id: value.id, text: value.name + ',' + value.phone})
            });
            return {results: supplierArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#vehicle_body_type").select2({
    placeholder: "Select Vehicle Body Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#gps_enable").select2({
    placeholder: "Select GPS Enable Status",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$(".truck-category").select2({
    placeholder: "Select Vehicle Category",
    ajax: {
        method: "GET",
        url: '/api/supplier-vehicle-category-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
        data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var catArray = [];
            $.each(data.data, function (key, value) {
                catArray.push({id: value.id, text: value.vehicle_type})
            });
            return {results: catArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#city").select2({
    placeholder: "Select City",
    ajax: {
        url: '/api/utils-city-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
          data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var cityArray = [];
            $.each(data.data, function (key, value) {
                cityArray.push({id: value.id, text: value.name + ',' + value.code + ',' + value.state.name})
            });
            return {results: cityArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }

    },
    allowClear: true,
}).change(function () {
    $(this).parsley().validate();
});

$("#vehicle-number").select2({
    maximumSelectionLength: 100,
    placeholder: "Please add Vehicles",
    ajax: {
        url: '/api/supplier-vehicle-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
          data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var vehicleArray = [];
            $.each(data.data, function (key, value) {
                vehicleArray.push({id: value.id, text: value.vehicle_number_display})
            });
            return {results: vehicleArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#is_gst_applicable").select2({
    placeholder: "Select GST Choices",
    allowClear: true
}).change(function () {
    if ($('#is_gst_applicable').val() === "yes") {
        $('.gstin-div').show();
        $('#gstin-input').prop('required', true);
    }
    else {
        $('.gstin-div').hide();
        $('#gstin-input').removeAttr('required');
    }
        $(this).parsley().validate();
});

$("#aaho_office").select2({
    placeholder: "Select Office",
    ajax: {
        url: '/api/utils-aaho-office-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
          data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var aahoOfcArray = [];
            $.each(data.data, function (key, value) {
                aahoOfcArray.push({id: value.id, text: value.branch_name})
            });
            return {results: aahoOfcArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});
$("#aaho_poc").select2({
    placeholder: "Select Aaho POC",
    ajax: {
        url: '/api/employee-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
          data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var empArray = [];
            $.each(data.data, function (key, value) {
                empArray.push({id: value.id, text: value.emp_name + ',' + value.emp_phone})
            });
            return {results: empArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

$("#states").select2({
    placeholder: "Select State",
    ajax: {
        url: '/api/state-list/',
        headers: {"Authorization": localStorage.getItem('token')},
        delay: 250,
          data: function (params) {
            return {
                search: params.term
            };
        },
        processResults: function (data) {
            var stateArray = [];
            $.each(data.data, function (key, value) {
                stateArray.push({id: value.id, text: value.name + ',' + value.code})
            });
            stateArray.push({id: 'select_all', text: 'All States'});
            return {results: stateArray};
        },
        error: function (jqXHR, status, error) {
            if(jqXHR.status == "401"){
                redirectToLogin(error);
              }
        }
    },
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});