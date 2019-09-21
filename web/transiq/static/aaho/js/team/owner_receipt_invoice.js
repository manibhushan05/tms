/**
 * Created by mani on 7/10/16.
 */
$(document).ready(function () {
    $('#lrdate').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#shipmentdate').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#party_invoice_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
        console.log(start.toISOString(), end.toISOString(), label);
    });
});
$(document).ready(function () {
    $('#insurance_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $(".select2_single").select2({
        placeholder: "Select a city",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".username").select2({
        placeholder: "Select a Customer",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".delivery_office").select2({
        placeholder: "Select Delivery Office",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".billing_type").select2({
        placeholder: "Select a Billing Type",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".consignor_city").select2({
        placeholder: "Select a Consignor City",
        allowClear: true
    });
    $(".select2_group").select2({});
});
$(document).ready(function () {
    $(".consignee_city").select2({
        placeholder: "Select a Consignee City",
        allowClear: true
    });
    $(".select2_group").select2({});
});

$('.form_datetime').datetimepicker({
    format: "dd MM yyyy - HH:ii P",
    language: 'en',
    weekStart: 1,
    todayBtn: true,
    autoclose: true,
    todayHighlight: 1,
    startView: 2,
    forceParse: 0,
    showMeridian: true,
});

$(document).ready(function () {
    $(".select2_single").select2({
        placeholder: "select booking id",
        allowClear: true
    });
    $(".select2_group").select2({});
    $(".select2_multiple").select2({
        maximumSelectionLength: 1,
        placeholder: "Please add all associated LR(s)",
        allowClear: true
    });
});
// initialize the validator function
validator.message.date = 'not a real date';

// validate a field on "blur" event, a 'select' on 'change' event & a '.reuired' classed multifield on 'keyup':
$('form')
    .on('blur', 'input[required], input.optional, select.required', validator.checkField)
    .on('change', 'select.required', validator.checkField)
    .on('keypress', 'input[required][pattern]', validator.keypress);

$('.multi.required').on('keyup blur', 'input', function () {
    validator.checkField.apply($(this).siblings().last()[0]);
});

$('form').submit(function (e) {
    e.preventDefault();
    var submit = true;

    // evaluate the form using generic validaing
    if (!validator.checkAll($(this))) {
        submit = false;
    }

    if (submit)
        this.submit();

    return false;
});
$(document).ready(function () {
    $('#loading_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $('#unloading_date').daterangepicker({
        singleDatePicker: true,
        calender_style: "picker_4"
    }, function (start, end, label) {
    });
});
$(document).ready(function () {
    $("#tds_certificate").select2({
        placeholder: "Select status",
        allowClear: true
    });
});

$(document).ready(function () {
    $("input").change(function () {
        var rate = parseInt($('#rate').val());
        var loading_charge = parseInt($('#loading_charge').val());
        var unloading_charge = parseInt($('#unloading_charge').val());
        var detention_charge = parseInt($('#detention_charge').val());
        var other_charge = parseInt($('#other_charge').val());
        var weight = parseInt($('#weight').val());
        var commission = parseInt($('#commission').val());
        var lr_cost = parseInt($('#lr_cost').val());
        var deduction_for_advance = parseInt($('#deduction_for_advance').val());
        var deduction_for_balance = parseInt($('#deduction_for_balance').val());
        var other_deduction = parseInt($('#other_deduction').val());
        var freight_to_owner = rate * weight;
        var advance_paid = parseInt($('#advance_paid').val());
        var total_payable_amount = freight_to_owner + loading_charge + unloading_charge + detention_charge + other_charge - lr_cost - deduction_for_advance - deduction_for_balance - other_deduction;
        var balance =total_payable_amount - advance_paid;
        // $("#other_deduction").val(lr_cost+deduction_for_advance+deduction_for_balance+other_deduction);
        $("#total_payable_amount").val(total_payable_amount);
        $("#lorry_freight").val(freight_to_owner);
        $("#balance").val(balance);
        if (balance <0){
            alert("Balance is negative");
        }

    });
});