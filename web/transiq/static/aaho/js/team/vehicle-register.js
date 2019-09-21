/**
 * Created by AmanAgarwal on 19/07/16.
 */
var selectObject1 = {
    allowClear: true,
    placeholder: "Select Owner"
};

var selectObject2 = {
    allowClear: true,
    placeholder: "Select Driver"
};

var selectObject3 = {
    allowClear: true,
    placeholder: "Select Driver App User"
};

var selectObject4 = {
    allowClear: true,
    placeholder: "Select Current City"
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

var selectObject8 = {
    allowClear: true,
    placeholder: "Select Vehicle Status"
};

var selectObject9 = {
    allowClear: true,
    placeholder: "Select Source"
};

var selectObject10 = {
    allowClear: true,
    placeholder: "Select Destination"
};

var selectObject11 = {
    allowClear: true,
    placeholder: "Select State"
};


$(".selectOwner").select2(selectObject1);

$(".selectDriver").select2(selectObject2);

$(".selectDriverAppUser").select2(selectObject3);

$(".selectCurrentCity").select2(selectObject4);

$(".selectVehicleType").select2(selectObject5);

$(".selectSimOperator").select2(selectObject6);

$(".selectStatus").select2(selectObject7);

$(".selectStatus1").select2(selectObject8);

$(".selectSource").select2(selectObject9);

$(".selectDestination").select2(selectObject10);

$(".selectState").select2(selectObject11);

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
