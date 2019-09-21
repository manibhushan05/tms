/**
 * Created by mani on 1/5/17.
 */
$('.btn-login').click(function () {
    alert("bhjhb");
    if (!$('.btn-login').parsley().isValid()) {
        return true;
    }
    $('#username').parsley().validate();
    $('#password').parsley().validate();
    NProgress.start();
    var data = $('.login-form').serialize();
    $.ajax({
        url: "/authentication/web-login/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        NProgress.done();
        if (response['msg'] === 'team') {
            window.location.href = '/team/fetch-full-booking-data-page/'
        }
        else if (response['msg'] === 'emp_group4') {
            window.location.href = '/team/dashboard/'
        }
        else if (response['msg'] === 'sme') {
            window.location.href = '/company/dashboard'
        }
        else if (response['msg'] === 'admin') {
            window.location.href = '/admin'
        }
        else if (response['msg'] === 'supplier') {
            window.location.href = '/supplier/new-booking-page/'
        }
        else if (response['msg'] === 'm_emp') {
            window.location.href = '/mobile/dashboard/'
        }
        else if (response['msg'] === 'ios') {
            window.location.href = '/m/place-order'
        }
        else {
            window.location.href = '/'
        }
    }).fail(function (jqXHR, status) {
        $('.error-response').text(JSON.parse(jqXHR.responseText)['msg']);
        NProgress.done();
    });
    return false;
});

$('#btn-enquiry').click(function () {
    var enquiry_form = $('#enquiry_form');
    if (!enquiry_form.parsley().isValid()) {
        return true;
    }
    NProgress.start();
    var data = enquiry_form.serialize();
    $.ajax({
        url: "/enquiry/contact-us-landing-page/",
        type: 'POST',
        data: data
    }).done(function (response, status) {
        $.notify('Thank you for the submission. We will get back to you soon.', {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'success'
        });
        $(enquiry_form).each(function () {
            this.reset();
        });
        NProgress.done();
    }).fail(function (jqXHR, status) {
        alert(jqXHR.status);
        $.notify("Oops! looks like some problem in submission, Sorry. Request you to try later", {
            position: "top center",
            autoHideDelay: 1000,
            clickToHide: true,
            className: 'error'
        });
        NProgress.done();
    });
    return false;
});

function initialize() {
    var map;
    var bounds = new google.maps.LatLngBounds();
    var mapOptions = {
        mapTypeId: 'roadmap',
        maxZoom: 18,
        minZoom: 5,
        zoom: 10,
        mapTypeControl: false
    };

    // Display a map on the page
    map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
    map.setTilt(45);

    // Multiple Markers
    var markers = [
        [21.315746, 81.6341611, 'Raipur', "C/O Inc 36,  2nd Floor, City Centre Mall, Pandri, Raipur - 492004"],
        [17.7266086, 83.3145841, 'Visakhapatnam', "Flat No. 105 B Block, Navya Nulife Apartments, Dairy hospital Road, Sheela Nagar, Visakhapatnam - 530012, Andhra Pradesh"],
        [19.0784346, 73.0072526, 'Navi Mumbai', "426, 4th Floor, Grohitam Premises, Opp. Mathadi Bhavan, Sector 19, Vashi, Navi Mumbai - 400705"],
        [19.11046, 72.887037, 'Mumbai', "610-611, Shivai Plaza Premises Co-Operative Society Limited, Marol Industrial Estate, Marol, Andheri East, Mumbai - 400059"],
        [22.930408, 72.596619, 'Ahmedabad', "No. 16, 3rd Floor, Shyam Icon, Near HP Petrol Pump, SP Ring Road, Near Aslali Circle, Aslali, Ahmedabad"],
        [22.4308946, 87.283458, 'Haldia', "Sahid Khudiram Colony, Phalguni Block, Plot No. 113, Post-Hatiberia, Haldia, East Medinapur, West Bengal-721657"]
    ];
    var infoWindowContent = new Array(markers.length);
    for (i = 0; i < markers.length; i++) {
        infoWindowContent[i] = ['<div class="office_address">' +
        "<h4>" + markers[i][2] + "</h4>" +
        "<div style='width: 150px'>" + markers[i][3] + "</div>"
        ]
    }

    // Display multiple markers on a map
    var infoWindow = new google.maps.InfoWindow(), marker, i;
    // Loop through our array of markers & place each one on the map
    for (i = 0; i < markers.length; i++) {
        var position = new google.maps.LatLng(markers[i][0], markers[i][1]);
        bounds.extend(position);
        marker = new google.maps.Marker({
            position: position,
            map: map,
            title: markers[i][0],
            icon: {
                url: '../static/aaho/images/map-marker_red.png', // url
                scaledSize: new google.maps.Size(50, 50), // scaled size
            }

        });

        // Allow each marker to have an info window
        google.maps.event.addListener(marker, 'mouseover', (function (marker, i) {
            return function () {
                infoWindow.setContent(infoWindowContent[i][0]);
                infoWindow.open(map, marker);
            }
        })(marker, i));
        google.maps.event.addListener(marker, "click", function () {
            map.panTo(marker.center);
            infoWindow.close();
        });
        // Automatically center the map fitting all markers on the screen
        map.fitBounds(bounds);
    }

    // Override our map zoom level once our fitBounds function runs (Make sure it only runs once)
    var boundsListener = google.maps.event.addListener((map), 'bounds_changed', function (event) {
        google.maps.event.removeListener(boundsListener);
    });

}