var $pickCityCount = 1;
var $dropCityCount = 1;

// $.fn.select2.defaults = $.extend($.fn.select2.defaults, {
//     allowClear: true, // Adds X image to clear select
//     closeOnSelect: true, // Only applies to multiple selects. Closes the select upon selection.
//     placeholder: 'Select...'
// });

function clonePickSelect() {
    $("#cityPickBlock").append($(".cityPickExtend:eq(0)").clone(true));
    var configParamsObj = {
        placeholder: 'Select a city'
    };
    $(".pickup_city:last").select2(configParamsObj);
    $(".cityPickExtend:last").show();
    $(".cityPickExtend:last").find('[id]').each(function () {
        var id = $(this).attr('id');
        var id1 = $(this).attr('id') + '[]';
        $(this).attr('id', id).attr('name', id1);
    });
}

function cloneDropSelect() {
    $("#cityDropBlock").append($(".cityDropExtend:eq(0)").clone(true));
    var configParamsObj = {
        placeholder: 'Select a city'
    };
    $(".drop_city:last").select2(configParamsObj);
    $(".cityDropExtend:last").show();
    $(".cityDropExtend:last").find('[id]').each(function () {
        var id = $(this).attr('id');
        var id1 = $(this).attr('id') + '[]';
        $(this).attr('id', id).attr('name', id1);
    });
}
var configParamsObj = {
    placeholder: 'Select a city'
};
var configParamsObj2 = {
    placeholder: 'Select a truck'
};

$(".pickupCity").select2(configParamsObj);
$(".dropCity").select2(configParamsObj);
$(".truck_select").select2(configParamsObj2);

$(document).ready(function () {

    // $(".select2_single").select2({
    //     placeholder: "Select a City",
    //     allowClear: true
    // });
    //
    //
    // $(".select2_singleTruck").select2({
    //     placeholder: "Select Truck Type",
    //     allowClear: true
    // });
    //
    // $(".select2_group").select2({});
    //
    // $(".select2_multiple").select2({
    //     maximumSelectionLength: 4,
    //     placeholder: "With Max Selection limit 4",
    //     allowClear: true
    // });




    // var $clone;
    $('#multiCheck').change(function () {
        if (this.checked) {
            $pickCityCount = $pickCityCount + 1;
            // var $pick = $('#cityPickExtend');
            // // var $block = $('#cityPickBlock');
            // // $block.removeClass('hide');
            // $clone = $pick.clone().removeClass('hide').removeAttr('id');
            // $('#buttonAdd').removeClass('hide');
            // // Add '2' to all ID values, and set name value to the same.
            // $clone.find('[id]').each(function () {
            //     var id = $(this).attr('id');
            //     var id1 = $(this).attr('id') + '[]';
            //     $(this).attr('id', id).attr('name', id1);
            //     // .attr('name', id1)
            // });

            // $clone.insertAfter($pick);
            $('#buttonAdd').removeClass('hide');
            clonePickSelect();
        }
        else if (!this.checked) { // Check whether we actually have a clone
            //     $clone.remove();
            // alert($('.cityPickExtend').length);
            // for(var i = 1; i < $('.cityPickExtend').length; i++){
                // alert(i);
            $(".cityPickExtend:eq(1)").remove();
            // }
            $pickCityCount = $pickCityCount - 1;
            if ($pickCityCount === 1) {
                $('#multiCheck').prop('checked', false);
                $('#buttonAdd').addClass('hide');
            }
        }
    });


    $('#multiCheck1').change(function () {
        if (this.checked) {
            $dropCityCount = $dropCityCount + 1;
            // var $pick = $('#cityPickExtend');
            // // var $block = $('#cityPickBlock');
            // // $block.removeClass('hide');
            // $clone = $pick.clone().removeClass('hide').removeAttr('id');
            // $('#buttonAdd').removeClass('hide');
            // // Add '2' to all ID values, and set name value to the same.
            // $clone.find('[id]').each(function () {
            //     var id = $(this).attr('id');
            //     var id1 = $(this).attr('id') + '[]';
            //     $(this).attr('id', id).attr('name', id1);
            //     // .attr('name', id1)
            // });

            // $clone.insertAfter($pick);
            $('#buttonAdd1').removeClass('hide');
            cloneDropSelect();
        }
        else if (!this.checked) { // Check whether we actually have a clone
            //     $clone.remove();
            // alert($('.cityPickExtend').length);
            // for(var i = 1; i < $('.cityPickExtend').length; i++){
                // alert(i);
            $(".cityDropExtend:eq(1)").remove();
            // }
            $dropCityCount = $dropCityCount - 1;
            if ($dropCityCount === 1) {
                $('#multiCheck1').prop('checked', false);
                $('#buttonAdd1').addClass('hide');
            }
        }
    });
    // var $clone1;
    // $('#multiCheck1').change(function () {
    //     if (this.checked) {
    //         $dropCityCount = $dropCityCount + 1;
    //         var $pick = $('#cityDropExtend');
    //         $clone1 = $pick.clone().removeClass('hide').removeAttr('id');
    //         $('#buttonAdd1').removeClass('hide');
    //         // Add '2' to all ID values, and set name value to the same.
    //         $clone1.find('[id]').each(function () {
    //             var id = $(this).attr('id');
    //             var id1 = $(this).attr('id') + '[]';
    //             $(this).attr('id', id).attr('name', id1);
    //         });
    //         // Now that the id value are unique, it is OK to add the clone:
    //         $clone1.insertAfter($pick);
    //     } else if ($clone1) { // Check whether we actually have a clone
    //         $clone1.remove();
    //         $dropCityCount = $dropCityCount - 1;
    //         if($dropCityCount === 1){
    //             $('#multiCheck1').prop('checked', false);
    //             $('#buttonAdd1').addClass('hide');
    //         }
    //     }
    // });
});

var $cityIndex = 2;
var $clone;
$(document).on('click', '#addBtn', function () {
    // var $position = $(this).parents('.form-group');
    // $cityIndex = $cityIndex + 1;
    $pickCityCount = $pickCityCount + 1;
    // var $pick = $('#cityPickExtend');
    // $clone = $pick.clone().removeClass('hide').removeAttr('id');
    // $clone.find('[id]').each(function () {
    //     var id = $(this).attr('id');
    //     var id1 = $(this).attr('id') + '[]';
    //     $(this).attr('id', id).attr('name', id1);
        // $position.find('#addBtn').hide();
    clonePickSelect();
    // });

    // Now that the id value are unique, it is OK to add the clone:
    // $clone.insertAfter($position);
    // $clone.appendTo('#cityPickBlock');



});

$(document).on('click', '#removeBtn', function () {
    var $pick = $(this).parents('.form-group');
    $pickCityCount = $pickCityCount - 1;
    $pick.remove();
    if($pickCityCount === 1){
        $('#multiCheck').prop('checked', false);
        $('#buttonAdd').addClass('hide');
    }
});

var $cityDropIndex = 2;
var $clone1;
$(document).on('click', '#addBtn1', function () {
    // var $position = $(this).parents('.form-group');
    // $cityDropIndex = $cityDropIndex + 1;
    $dropCityCount = $dropCityCount + 1;
    // var $pick = $('#cityDropExtend');
    // $clone1 = $pick.clone().removeClass('hide').removeAttr('id');
    // $clone1.find('[id]').each(function () {
    //     var id = $(this).attr('id');
    //     var id1 = $(this).attr('id') + '[]';
    //     $(this).attr('id', id).attr('name', id1);
    // });
    // Now that the id value are unique, it is OK to add the clone:
    // $clone1.appendTo('#cityDropBlock');
    cloneDropSelect();
});

$(document.body).on('click', '#reset', function() {
    $("select").val(null).trigger("change");
});

$(document).on('click', '#removeBtn1', function () {
    var $pick = $(this).parents('.form-group');
    $pick.remove();
    $dropCityCount = $dropCityCount - 1;
    if($dropCityCount === 1){
        $('#multiCheck1').prop('checked', false);
        $('#buttonAdd1').addClass('hide');
    }
});


var $num = 0;
function cloning() {
    var dropd = document.getElementById("truck");
    if(dropd.value !== "") {
        $num++;
        $count = $count + 1;
        document.getElementById('truckCount').innerHTML = $count;

        $('#truck option[value = "' + dropd.value + '"]').attr('data-value', $num);

        var remBtn = $('<button></button>', {
            class: 'remBtn glyphicon glyphicon-remove',
            id: dropd.value,
            field: 'truckDetail' + $num
        });

        var truckIn = $('<div></div>', {
            class: 'truckIn'
        });

        var divElem = $('<div></div>', {
            class: 'truckContain col-md-4 col-sm-4 col-xs-6',
            id: '' + $num,
            name: 'truckDetail' + $num
        });

        /*var imgElem = $('<img />', {
            id: 'truckImg' + $num,
            class: 'truckImg'
        });
        imgElem.attr('src', dropd.value);*/

        var pElem = $('<p></p>', {
            id: 'truckName' + $num,
            class: 'truckName',
            text: dropd.options[dropd.selectedIndex].text
        });

        var divBtn = $('<div></div>', {
            class: 'plusMinus',
            id: "plusMinus" + $num
        });

        var minus = $('<input>', {
            type: 'button',
            value: '-',
            class: 'qtyminus',
            id: 'qtyminus' + $num,
            field: $("select option[value =" + "'" + dropd.value + "'" + "]").data('id'),
            onclick: 'truckCountMinus()'
            // disabled: 'disabled'
        });

        var plus = $('<input>', {
            type: 'button',
            value: '+',
            class: 'qtyplus',
            id: 'qtyplus' + $num,
            field: $("select option[value =" + "'" + dropd.value + "'" + "]").data('id'),
            onclick: 'truckCountAdd()'
        });

        var qty = $('<input>', {
            type: 'text',
            name: $("select option[value =" + "'" + dropd.value + "'" + "]").data('id'),
            value: '1',
            class: 'qty',
            id: 'qty' + $num
        });

        divElem.appendTo('#truckType');
        remBtn.appendTo(divElem);
        // imgElem.appendTo(divElem);
        pElem.appendTo(divElem);
        divBtn.insertAfter(pElem);
        minus.appendTo(divBtn);
        qty.insertAfter(minus);
        plus.insertAfter(qty);

        $('#truck option[value = "' + dropd.value + '"]').attr('disabled', true);
        console.log(dropd.value);

    }
}

// This button will increment the value
$(document.body).on('click', '.qtyplus', function (e) {
    // Stop acting like a button
    e.preventDefault();
    // Get the field name
    var fieldName = $(this).attr('field');
    // Get its current value
    var currentVal = parseInt($("input[name='" + fieldName + "']").val());
    // If is not undefined
    if (!isNaN(currentVal)) {
        // Increment
        $('input[name=' + fieldName + ']').val(currentVal + 1);

    } else {
        // Otherwise put a 1 there
        $('input[name=' + fieldName + ']').val(1);
    }
});
// This button will decrement the value till 0
$(document.body).on('click', '.qtyminus', function (e) {
    // Stop acting like a button
    e.preventDefault();
    // Get the field name
    var fieldName = $(this).attr('field');
    // Get its current value
    var currentVal = parseInt($('input[name=' + fieldName + ']').val());
    // If it isn't undefined or its greater than 0
    if (!isNaN(currentVal) && currentVal > 2) {
        // Decrement one
        $('input[name=' + fieldName + ']').val(currentVal - 1);
    } else if(currentVal - 1 === 1){
        $(this).attr('disabled', true);
        $('input[name=' + fieldName + ']').val(1);
        // $(this).attr('disabled', false);
    }
});

var $count = 0;

$(document.body).on('click', '.remBtn', function (e) {
    e.preventDefault();
    var fieldName = $(this).attr('field');
    // $('div[name = ' + fieldName + ']').remove();
    // $('#truck option[value = "' + dropd.value + '"]').attr('disabled', true);
    $('#truck option[value = "' + $(this).attr('id') + '"]').attr('disabled', false);
    console.log($(this).attr('id'));
    var id = '#qty' + $('#truck option[value = "' + $(this).attr('id') + '"]').data('value');
    console.log(id);
    var value = $(id).val();
    console.log(value);
    $count = $count - parseInt(value);
    console.log($count);
    document.getElementById('truckCount').innerHTML = $count;
    $('div[name = ' + fieldName + ']').remove();
    console.log($num);
    // $num --;
    // var $num1 = $num + 1
    // if ($('#qty' + $num1).length == 0) {
    //     $num = $num;
    // }
    // else {
    //     $num = $num + 1;
    // }
    console.log($num);
});
// var $truckCount = 1;
function truckCountAdd(){
    var $truckCount = 1;
    for(var $i = 1; $i <= $num; $i++){
        var id = '#qty' + $i;
        console.log(id);
        var value = $(id).val();
        console.log(value);
        console.log($truckCount);
        if(value){
            $truckCount = $truckCount + parseInt(value);
        }
   }
    $count = $truckCount;
    document.getElementById('truckCount').innerHTML = $count;
};

function truckCountMinus(){
    var $truckCount = 1;
    for(var $i = 1; $i <= $num; $i++){
        var id = '#qty' + $i;
        console.log(id);
        var value = $(id).val();
        console.log(value);
        console.log($truckCount);
        $truckCount = $truckCount - parseInt(value);
   }
    $count = -$truckCount;
    document.getElementById('truckCount').innerHTML = $count;
};

validator.message.date = 'not a real date';

// validate a field on "blur" event, a 'select' on 'change' event & a '.reuired' classed multifield on 'keyup':
$('form')
    .on('blur', 'input[required], input.optional, select.required', validator.checkField)
    .on('change', 'select.required', validator.checkField)
    .on('keypress', 'input[required][pattern]', validator.keypress);

$('.multi.required').on('keyup blur', 'input', function () {
    validator.checkField.apply($(this).siblings().last()[0]);
});

function display() {
    $('.messageDisplay').stop().fadeIn(400).delay(10000).fadeOut(400); //fade out after 3 seconds
};

$('.form_datetime').datetimepicker({
    language: 'en',
    weekStart: 1,
    todayBtn: 1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    forceParse: 0,
    showMeridian: 1
});
$('.form_date').datetimepicker({
    language: 'en',
    weekStart: 1,
    todayBtn: 1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 2,
    minView: 2,
    forceParse: 0
});
$('.form_time').datetimepicker({
    language: 'en',
    weekStart: 1,
    todayBtn: 1,
    autoclose: 1,
    todayHighlight: 1,
    startView: 1,
    minView: 0,
    maxView: 1,
    forceParse: 0
});




// <body>Single select example
// <a href="#">Add more</a>
//     <div class="selectRow" style="display: none;">
//         <select class="singleSelectExample">
//             <option></option><!-- Needed to show X image to clear the select -->
//             <option value="1">Option 1</option>
//             <option value="2">Option 2</option>
//             <option value="3">Option 3</option>
//             <option value="4">Option 4</option>
//             <option value="5">Option 5</option>
//         </select>
//     </div>
// </body>



// Setting default configuration here or you can set through configuration object as seen below
// $.fn.select2.defaults = $.extend($.fn.select2.defaults, {
//     allowClear: true, // Adds X image to clear select
//     closeOnSelect: true, // Only applies to multiple selects. Closes the select upon selection.
//     placeholder: 'Select...',
//     minimumResultsForSearch: 15 // Removes search when there are 15 or fewer options
// });
//
//
// function cloneRow() {
//   $("body").append($(".selectRow:eq(0)").clone(true));
//   var configParamsObj = {
//     placeholder: 'Select an option...', // Place holder text to place in the select
//     minimumResultsForSearch: 3 // Overrides default of 15 set above
//   };
//   $(".singleSelectExample:last").select2(configParamsObj);
//   $(".selectRow:last").show();
// }
//
// $(document).ready(
// function () {
// $("a").on("click", function(e){
// e.preventDefault();
// cloneRow();
// });
//
//     // Single select example if using params obj or configuration seen above
//     cloneRow();
// });

//
// .selectRow {
//     display : block;
//     padding : 20px;
// }
// .select2-container {
//     width: 200px;
// }