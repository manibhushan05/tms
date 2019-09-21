/**
 * Created by AmanAgarwal on 19/07/16.
 */
var selectObject1 = {
    allowClear: true,
    placeholder: "Select City"
};

var selectObject2 = {
    allowClear: true,
    placeholder: "Select Id Proof"
};

var selectObject3 = {
    allowClear: true,
    placeholder: "Select Account Type"
};

var selectObject4 = {
    allowClear: true,
    placeholder: "Select Taxation Id"
};

var selectObject5 = {
    allowClear: true,
    placeholder: "Select Vehicle type"
};

var selectObject6 = {
    allowClear: true,
    placeholder: "Select Sim Operator"
};

var selectObject7 = {
    allowClear: true,
    placeholder: "Select Status"
};


$(".selectCity").select2(selectObject1);

$(".selectId").select2(selectObject2);

$(".selectAccount").select2(selectObject3);

$(".taxationId").select2(selectObject4);

$(".selectVehicleType").select2(selectObject5);

$(".selectSimOperator").select2(selectObject6);

$(".selectStatus").select2(selectObject7);

$(document).ready(function () {

    $('#registrationDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'YYYY'
    });
    $('#permitDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#insuranceDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#registrationDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#registerValidityDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#fitnessDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#fitnessValidDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#pucDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
    $('#pucValidDateTimePicker').datetimepicker({
        viewMode: 'years',
        format: 'DD/MM/YYYY'
    });
});
