/**
 * Created by mani on 11/5/17.
 */

$(".billing_type").select2({
    placeholder: "Select Billing Type",
    allowClear: true
}).change(function () {
    $(this).parsley().validate();
});

