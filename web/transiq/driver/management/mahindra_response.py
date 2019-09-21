html_response="""
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head id="Head1">
    <!--Google Analytics -->
     <script src="Scripts/GoogleAnalytics.js"></script> 
        <script  type="text/javascript">
           var BusinessType= '4'; 
            googleanalytics(BusinessType);
        </script> 

    <!--Google Analytics -->
    <title>
	Mahindra DiGiSEnSE :: LocationServices
</title>
    <script type = "text/javascript" >
        history.pushState(null, null, document.URL);
        window.addEventListener('popstate', function () {
            history.pushState(null, null, document.URL);
        });
</script>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <!--[if lt IE 9]>
        <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <!-- Start Stylesheet-->
    <link rel="shortcut icon" href="Images/favicon.ico" type="image/x-icon" /><link rel="stylesheet" type="text/css" href="Styles/style.css" /><link rel="stylesheet" type="text/css" href="Styles/alertify.min.css" /><link rel="stylesheet" type="text/css" href="Styles/jquery.gridster.css" /><link rel="stylesheet" type="text/css" href="Styles/basic.css" />
    <!-- End Stylesheet-->

    <!-- Start Script Jquery Library -->

    
  
     <script src="https://maps.googleapis.com/maps/api/js?v=3.exp&signed_in=false&libraries=places&key=AIzaSyDb9bc0m8Wg_lUjKh66S8zc4UI53u-HCzQ"></script>   
    <script type="text/javascript" src="Scripts/jquery.min.js"></script>
    <script type="text/javascript" src="Scripts/jquery-1.7.min.js"></script>
    <script type="text/javascript" src="Scripts/jquery-ui-1.10.3.custom.min.js"></script>
    <script type='text/javascript' src='Scripts/alertify.js'></script>
    <script type="text/javascript" src="Scripts/store.min.js"></script>

    <script src="Scripts/jquery.simplemodal.js"></script>
    
    <script type="text/javascript" src="Scripts/jquery.gridster.js"></script>
    <script type="text/javascript" src="Scripts/EmergencyPopup.js"></script>

    <!-- End Script Jquery Library-->
    <!-- Start Script For Google Map Track  -->

    <script type="text/javascript" src="Scripts/VehicleLocation.js"></script>
    
    <script type="text/javascript" src="Scripts/infobox.js"></script>
    <!-- End Script For Google Map Track -->
        <!-- session timeout when user click on browser close button -->
    <script   type="text/javascript">
        //<![CDATA[</span />

        var clicked = false;
        function CheckBrowser(e) {
            if (clicked == false) {
                //Browser closed
                alert("browser closed");
              
                var keycode;
                if (window.event)
                    keycode = window.event.keyCode;
                else if (e)
                    keycode = e.which;
                if (keycode == 116) {
                    window.event.returnValue = false;
                    window.event.keyCode = 0;
                    clicked = false;
                }
                else {
                    clicked = true;
                }
                alert(clicked);
               
                /*
                var keyCd = null;

                var altKy = false;

                var ctlKy = false;

                var shiftKy = false;

                keyCd = window.event.keyCode;

                altKy = window.event.altKey;

                ctlKy = window.event.ctlKey;

                shiftKy = window.event.shiftKey;

                if ((window.event.clientX < 0) || (window.event.clientY < 0)) {

                    // Code for your action

                    // [url="http://www.infysolutions.com"]http://www.infysolutions.com[/url]
                    clicked = true;


                }

                else if ((altKy && keyCd == 115) && !ctlKy && !shiftKy && keyCd != 116) {

                    // Code for your action
                    clicked = true;
                }

                else if ((altKy && keyCd == 70) && !ctlKy && !shiftKy && keyCd != 116) {

                    // Code for your action   
                    clicked = true;

                }
                */

            }
            else {
                //redirected 
                alert("browser redirected");
                clicked = true;
            }
        }

        function bodyUnload() {
         
            if (clicked == false)//browser is closed
            {
                var request = GetRequest();
                //Local
                //request.open("POST", "../Signout.aspx", false);

                //server 
                //request.open("POST", "Signout.aspx", false);
                //request.send();
                // alert('This is close');
            }
            else { }
        }
        function GetRequest() {
            var xmlhttp;
            if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
                xmlhttp = new XMLHttpRequest();
            }
            else {// code for IE6, IE5
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
            }
            return xmlhttp;
        }
</script>
    <!-- Start Script Jquery Library -->
     
      <script type="text/javascript">
        var j = jQuery.noConflict();
        var currentroleid = 0;
        j(document).ready(function () {

            //$(window).bind("beforeunload", function () {                
            //    sessLogOut();
            // });

            // FOTA Menu Link target with New Window            
            var menuFotaVar = j(".DynamicMenu ul.menu li.menuItems2 > ul li.secondsubLevelFOTA_Configuration a").text();
            if (menuFotaVar == "FOTA Configuration") {
                j(".DynamicMenu ul.menu li.menuItems2 > ul li.secondsubLevelFOTA_Configuration a").attr('target', '_blank');
            }

            setHelpFileURL();

            j("#lnkbtnLogout").click(function () {
                sessionStorage.clear();
            });
            j("#flip").click(function () {
                j("#panel").slideToggle("slow");
            });

            console.log(currentroleid);

            if (currentroleid == 2) {
                GetReminders();
            }

        });

        var reminderJson = null;

        function GetReminders() {
            $.ajax({
                type: "POST",
                url: "Home.aspx/GetAlertsReminders",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {

                    reminderJson = $.parseJSON(response.d);

                    debugger;
                    if (reminderJson != null) {
                        if (reminderJson.length > 0) {
                            var appendremindertext = null;
                            $.each(reminderJson, function (index, jsonreminderobj) {
                                if (appendremindertext != null) {

                                    appendremindertext = appendremindertext + " | " + jsonreminderobj.AlertName + " for your vehicle registration number " + jsonreminderobj.vehiclenumber;
                                } else {

                                    appendremindertext = jsonreminderobj.AlertName + " for your vehicle registration number " + jsonreminderobj.vehiclenumber;
                                }

                                $("#MarQueeReminders").html(appendremindertext);
                            });


                            //  $("#MarQueeReminders").html(" Insurance Payment Due Reminder# 1 |  Fitness Certification Remider# 1 | Service Due Reminder# 3 for vehicle registration number: 'KA 09 UK 9999'");
                        }
                    }

                },
                failure: function (response) {
                    alert("Error while calling the service");
                }
            });
        }

        function setHelpFileURL() {
            $.ajax({
                type: "POST",
                url: "Home.aspx/GetUserManualFileNameString",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {
                    var fileName = 'UserManual/' + response.d + '.pdf';
                    //alert(fileName);
                    if (fileName != null) {
                        $("#userManualFile").attr("href", fileName);
                    }
                },
                failure: function (response) {
                    alert("Error while calling the service");
                }
            });
        }

        j('#trigger').click(function () {
            j("#this").width(j(".search").width());
        });

        j(function () {
            j("#dialog").dialog({
                autoOpen: false,
                modal: true,
                show: {
                    effect: "blind",
                    duration: 1000
                },
                hide: {
                    effect: "explode",
                    duration: 1000
                }
            });

            j("#dialogTop").dialog({
                autoOpen: false,
                modal: true,
                show: {
                    effect: "blind",
                    duration: 1000
                },
                hide: {
                    effect: "explode",
                    duration: 1000
                }
            });

        });

        //Session TimeOut Code Block
        //Session Code Ends here
    </script>


    <!-- Start Default Menu Select on page navigation -->
    <script type="text/javascript">
        j("document").ready(function () {
            j(function () {
                var url = window.location.href.substr(window.location.href.lastIndexOf("/") + 1);
                j('[href$="' + url + '"]').parents("li").addClass("active");
            });
        });
    </script>
    <!-- End Default Menu Select on page navigation -->
    <!-- Start Right Click is Disabled -->
    <script type="text/javascript">
        var message = "For Security Reason Right Click is Disabled!";
        function clickIE4() {
            if (event.button == 2) {
                alert(message);
                return false;
            }
        }

        function clickNS4(e) {
            if (document.layers || document.getElementById && !document.all) {
                if (e.which == 2 || e.which == 3) {
                    alert(message);
                    return false;
                }
            }
        }

        if (document.layers) {
            document.captureEvents(Event.MOUSEDOWN);
            document.onmousedown = clickNS4;
        }
        else if (document.all && !document.getElementById) {
            document.onmousedown = clickIE4;
        }

        document.oncontextmenu = new Function("alertify.alert('Security Alert!',message).set({ closable: false });return false")

        //function preventBack() { window.history.forward(); }
        //setTimeout("preventBack()", 0);
        //window.onunload = function () { null };
    </script>
    <!-- End Right Click is Disabled -->
    <script>
        j(document).bind('drop dragover', function (e) {
            e.preventDefault();
        });
    </script>
    <!-- Start Alert Button -->
    <script type="text/javascript">
        j(window).load(function () {
            j(".hoverAlert").click(function () {
                j('#notificationContainer').animate({ width: "367px" });
                j('.hoverAlert').hide();
                j('#notificationContainer').hide(500);
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff', 'top', '-2px');
                j('#notificationLink a.hoverAlert').css('border-bottom', 'none');
                j('#notificationLink a.hoverAlert').css('top', '-6px');
                //if (j('#notificationContainer').is(":visible")) {
                //    location.reload(true);
                //}
            });

            j(".nonhoverAlert").click(function () {
                j("#ajaxloader").show();
                j("#notificationContainer").fadeToggle(300);
                //j("#alertDiv").load("Alert.aspx").fadeIn(8000);
                j("#notificationsBody").fadeIn(3000);
                j('#alertDiv').load('Alerts.html', function () {
                    j("#ajaxloader").hide();
                }).fadeIn(10000);
                j('.nonhoverAlert').hide();
                j('.hoverAlert').show();
                j('#notificationLink').css('background-color', 'transparent');
                j('#notificationLink').css('color', '#676867');
                j('.alertName').css('color', '#676867');
                //stopRefresh();
                //intervalon = 0;
                return false;
            });

            j("#innerWrap").click(function () {
                j("#notificationContainerr").hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
                //if (j('#notificationContainer').is(":visible")) {
                //    location.reload(true);
                //}
                // debugger;
                //debugger;
                //if (intervalon == 0) {
                //    startRefresh1();
                //    intervalon = 1;
                //}
            });
            //j(".tablecount").click(function () {
            //    if (j('#notificationContainer').is(":visible")) {
            //        location.reload(true);
            //    }
            //});
            j(".tabArrow").click(function () {
                j("#notificationContainerr").hide();
                j("#notificationContainer").hide();
                j('#page_effect').hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
                //stopRefresh();
                //intervalon = 0;
            });
            j(".tabArrow1").click(function () {
                j("#notificationContainerr").hide();
                j("#notificationContainer").hide();
                j('#page_effect').hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
                //if (intervalon == 0) {
                //    startRefresh1();
                //    intervalon = 1;
                //}
            });

            j("#Content_Div").click(function () {
                j("#notificationContainerr").hide();
                j('#notificationContainer').animate({ width: "367px" });
                j("#notificationContainer").hide();
                j('#page_effect').hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
            });

            j(".headerTopbar").click(function () {
                j("#notificationContainerr").hide();
                j('#notificationContainer').animate({ width: "367px" });
                //if (j('#notificationContainer').is(":visible")) {
                //    location.reload(true);
                //}
                j("#notificationContainer").hide();
                j('#page_effect').hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
            });

            //Document Click hiding the popup 
            j(document).click(function () {
                j("#notificationContainer").hide();
                j('.hoverAlert').hide();
                j('.nonhoverAlert').show();
                j('#notificationLink').css('background-color', '#E01936');
                j('.alertName').css('color', '#fff');
            });

            //Popup on click
            j("#notificationContainer").click(function () {
                return false;
            });
            j('.helpAnchor').on('click', function (e) {
                j('#helpPopup').modal();
                j('#helpPopup').parent().parent().addClass("helpDivStyle");
                e.stopImmediatePropagation();
                return false;
            });

            //j('.helpAnchor').on('click', function (e) {

            //    j('#helpPopup').modal();

            //    j('#helpPopup').parent().parent().addClass("helpDivStyle");
            //    e.stopImmediatePropagation();
            //    //Collape and expand //

            //    LoadFAQ();
            //    var divs = $('.accordion>div').hide(); //Hide/close all containers

            //    var h2s = $('.accordion>h2').click(function () {
            //        h2s.not(this).removeClass('active')
            //        $(this).toggleClass('active')
            //        divs.not($(this).next()).slideUp()
            //        $(this).next().slideToggle()
            //        return false; //Prevent the browser jump to the link anchor

            //    });

            //    //Collape and expand //
            //    return false;
            //});


            j("#secondsubLevel3 a").on("click", function (e) {
                sessionStorage.removeItem(0);
                sessionStorage.removeItem(1);
                sessionStorage.removeItem(2);
                sessionStorage.removeItem(3);
            });
            j(".menu").on("mouseover", function () {
                j("#vehicleDropDown").blur();
                j("#txtFromDate").trigger("blur");
                j("#selectvechicle").trigger("blur");
                if ($("#ui-datepicker-div").is(":visible")) {
                    $("#txtFromDate").datepicker("hide");
                }
            });
        });
    </script>




    <!-- End Alert Button -->
    <!-- End Script-->
    
    <link rel="stylesheet" type="text/css" href="Styles/style.css" />

         
    <link rel="stylesheet" type="text/css" href="Styles/jquery.tooltip.css" />
    <script src="Scripts/gridview-readonly-script.js" type="text/javascript"></script>
    <script type="text/javascript">
        $(function () {
            InitializeToolTip();
      
        });
        function callhighlightMarker(Lattitude, Longitude, VehAlertStatus, Alertid, GpsHeading) {
            var BusinessType = document.getElementById('ContentPlaceHolder1_businessType').value;
            highlightMarker(Lattitude, Longitude, VehAlertStatus, Alertid, BusinessType, GpsHeading);
        }

    </script>
    <style>
        /*.gm-style-iw + div {display: none;}*/
        .gm-style-iw + div {
            display: block !important;
        }

        .jsanchor {
            height: 2px;
            width: auto;
            font-weight: bold;
        }

        .latitude, .longitude,.GpsHeading {
            visibility: hidden;
        }

        .DynamicMenu > ul > li > a {
            color: #676867;
            font-family: "Roboto";
            font-size: 13px;
        }

        .ViewMoreDiv {
            /*display: inline-block;*/
            height: 25px;
            margin: 10px;
            width: 1232px;
            border-radius: 5px;
            height: 30px;
            background-color: #F8F5EE;
        }

        .ViewMoreLink {
            /*display: inline-block;*/
            width:124.594px;
            text-align: center;
            margin-left: 563px;
            font-weight: bold;
            font-size: 14px;
            margin-top: 5px;
            color: red;
            text-decoration: underline;
        }
        #ContentPlaceHolder1_Updatepanel1 {
           height:482px;
           /*overflow-y:auto;*/ 
            width:100%;
        }
        .leftcontainer {
            height:auto;
        }
        .searchSubmit {
            outline:none;
        }
        .autoFillsearch {
            max-height:200px !important;
            overflow-y:auto;
            margin-top:5px;
            font-family:'Roboto';
            font-size:13px;
        }
    </style>

    
    
    <script type="text/javascript">
       
   
     
        j(document).ready(function () {
           




            if (sessionStorage.expanded == "true") {
                expandPanel();
                sessionStorage.expanded = "false";
            }
            j('#trigger').click(function () {
                  



                //console.log(expand);
                collapseExpand();
            });
            j('#trigger').click(function () {
                j("#this").width(j(".search").width());
            });
            function expandPanel() {
                expandAddresspanel();
                j('#activity').hide();
                j('.centerLine').show();
                j('.vehicleCombine').animate({ width: '225px' });
                j('.alertImg').css({ float: 'left' });
                j('.alertImg').css({ "margin-left": '0px' });
                //  j(".alertImg").css("float", "right");
                // j(".alertImg").css("margin-left", "-102px");
                j('table.menuoff').animate({ width: '1245px' });
                j('#sidebar1').animate({ width: '1270px' });
                j('#map_canvas').animate({ width: '1015px' });
                j('.search').animate({ width: '96px', fontSize: '13px', paddingLeft: '35px' });
                j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem').animate({ width: '930px', fontSize: '13px', marginTop: '0px' });
                j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem li').animate({ fontSize: '18px', width: '930px', });
                j('.vehList').animate({ width: '125px' });
                j('.vehType').show();
                j('.lblCss1').show();
                j('.tabArrow1').show();
                j('.tabArrow').hide();
                j(".vehAddress").css("display", "inline-block");
                j(".vehAddress").css("width", "230");
                j(".vehAddress").css("min-height", "1px");
                j(".vehAddress").css("margin-right", "6px");

                j(".VehicleHours").css("display", "inline-block");
                j(".VehicleHours").css("width", "100");
                j(".VehicleHours").css("min-height", "1px");

                j(".CumVehicleHours").css("display", "inline-block");
                j(".CumVehicleHours").css("width", "180");
                j(".CumVehicleHours").css("min-height", "1px");
                
                j(".FuelEfficency").css("display", "inline-block");
                j(".FuelEfficency").css("width", "140");
                j(".FuelEfficency").css("min-height", "1px");

                j(".UreaUsage").css("display", "inline-block");
                j(".UreaUsage").css("width", "80");
                j(".UreaUsage").css("min-height", "1px");

              //  j(".VehicleEngineHours").css("margin-right", "3px");
                
                j('.headTop1').show();
                j('.headTop2').show();
                j('.headTop3').show();
                j('.headTop4').show();
                j('.headTop5').show();
                j('.headTop6').show();
                j('.headTop7').show();
                j('.headTop8').show();
                j('.headLocation').show();
                j("#notificationContainerr").hide();
                //j(".headTop3").css("margin-left", "10px");
                //j(".headTop4").css("margin-left", "120px");
                j(".alertImg").css("top", "-5px");
                j('.vehType').animate({ width: '93px' });
                sessionStorage.expanded = "true";

                document.getElementById('ContentPlaceHolder1_hdfISExpand').value = "1";

                $(".tableCount > table").css('display', 'none');
                // $("#Viewmore").css('display', 'inline-block');

                if ($(".tableCount > table").length > 0) {
                   // debugger;
                    GetRepeaterAddress(1);
                }


                //DisableViewMore();

                //debugger;
               var timer = $find('ContentPlaceHolder1_timerLandingPage');
                if (timer!=null)
                {
                //    console.log(timer);
                    timer._stopTimer();
                }
            }
            function collapsePanel() {
                //debugger;
                j('#activity').animate({ width: '820px' });
                j('#sidebar1').animate({ width: '275px' });
                j('.vehicleCombine').animate({ width: '110px' });
                j('.alertImg').css({ float: 'right' });
                j('#map_canvas').animate({ width: '1015px' });
                j('table.menuoff').animate({ width: '250px' });
                j('.search').animate({ width: '81px', fontSize: '10px', paddingLeft: '35px' });
                j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem').animate({ width: 'auto', fontSize: '13px' });
                j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem li').animate({ width: 'auto', fontSize: '13px' });
                j('.vehType').show();
                j('.lblCss1').hide();
                j('.tabArrow1').hide();
                j('.tabArrow').show();
                j('.vehAddress').hide();
                j(".vehAddress").css("display", "none");

                j('.VehicleHours').hide();
                j(".VehicleHours").css("display", "none");

                j('.CumVehicleHours').hide();
                j(".CumVehicleHours").css("display", "none");
                
                j('.FuelEfficency').hide();
                j(".FuelEfficency").css("display", "none");

                j('.UreaUsage').hide();
                j(".UreaUsage").css("display", "none");

                j('#activity').show();
                j('.centerLine').show();
                j('.headTop1').hide();
                j('.headTop2').hide();
                j('.headTop3').hide();
                j('.headTop4').hide();
                j('.headTop5').hide();
                j('.headTop6').hide();
                j('.headTop7').hide();
                j('.headTop8').hide();
                j('.headLocation').hide();
                j(".alertImg").css("margin-left", "0px");
                j(".alertImg").css("top", "-35px");
                j('.vehType').animate({ width: '140px' });
                sessionStorage.expanded = "false";
                document.getElementById('ContentPlaceHolder1_hdfISExpand').value = "0";

                $(".tableCount > table").css('display', 'inline-block');
                $(".ViewMoreDiv").css('display', 'none');

                var timer = $find('ContentPlaceHolder1_timerLandingPage');
             // console.log(timer);
                //timer._enabled = true;
                if (timer != null)
                {
                    timer._startTimer();
                }
          //      console.log(timer);

               // document.getElementById('ContentPlaceHolder1_btnSearch').click();
            }

            function collapseExpand() {
                if (j("#sidebar1").width() == "275" || j("#sidebar1").width() == "276") {
                    //  if (j("#sidebar1").width() == "275") {
                  
                    expandPanel();
                } else {
                   
                  collapsePanel();
                    // Passed value from backend via hidden variables. As part of this implementation:
                    // hidden variables will get updated in the backend with most recent value, and right after collapsing the vehicle list updated value will be reflected on the map.
                     var zoomValue = document.getElementById('ContentPlaceHolder1_hfZoomLevelLSLanding').value;
                    var latlngValue = document.getElementById('ContentPlaceHolder1_hfLatLngString').value;
                    var vehDetailValue = document.getElementById('ContentPlaceHolder1_hfVehDetailsString').value;
                    loadDefaultmap(zoomValue);
                    var BusinessType= document.getElementById('ContentPlaceHolder1_businessType').value;                    
                    loadMultipleMarkers(latlngValue, vehDetailValue, BusinessType); 
                }
            }

            j("body").on("click", "#Viewmore",
                function () {
                    //j("#Viewmore").click(function () {

                    GetRepeaterAddress(0);

                    //DisableViewMore();
                });


            // Load the data on scroll bar 
          
            var lastScroll = 0;
            $("#divmaster").scroll(
            function () {
              
                //Sets the current scroll position
                var st = $(this).scrollTop();
                //Determines up-or-down scrolling
                if (st > lastScroll) {
                    //Replace this with your function call for downward-scrolling
                    if (sessionStorage.expanded == "true") {
                        GetRepeaterAddress(0);
                    }
                    
                }
               
                //Updates scroll position
                lastScroll = st;
                   
                
            }
            );
           
            // Load the data on scroll bar 

        });

   
   


    </script>

    <script type="text/javascript">
        function expandAddresspanel() {
            if (sessionStorage.expanded == "true") {
                j(".vehAddress").css("display", "inline-block");
                j(".vehAddress").css("width", "230");
                j(".vehAddress").css("min-height", "1px");
                j(".vehAddress").css("margin-right", "6px");
                j('.alertImg').css({ 'float': 'left' });
                j(".alertImg").css("margin-left", "15px");
                j(".vehAddress").css("margin-left", "0px");
                j('.vehList').animate({ width: '120px' });
                j('.menuoff').animate({ width: '1245px' });
                $(".tableCount > table").css('display', 'none');
                //$(".ViewMoreDiv").css('display', 'inline-block');

                j(".VehicleHours").css("display", "inline-block");
                j(".VehicleHours").css("width", "230");
                j(".VehicleHours").css("min-height", "1px");

                j(".CumVehicleHours").css("display", "inline-block");
                j(".CumVehicleHours").css("width", "230");
                j(".CumVehicleHours").css("min-height", "1px");

                j(".FuelEfficency").css("display", "inline-block");
                j(".FuelEfficency").css("width", "150");
                j(".FuelEfficency").css("min-height", "1px");

                j(".UreaUsage").css("display", "inline-block");
                j(".UreaUsage").css("width", "150");
                j(".UreaUsage").css("min-height", "1px");

              //  j(".VehicleEngineHours").css("margin-right", "3px");
              //  j(".VehicleEngineHours").css("margin-left", "0px");
                
                if ($(".tableCount > table").length > 0) {

                    GetRepeaterAddress(1);
                    DisableViewMore();
                }
            }
        }

        function exPandPanelTextChange() {


            expandAddresspanel();
            j('#activity').hide();
            j('.centerLine').show();
            j('.vehicleCombine').animate({ width: '225px' });
            j('.alertImg').css({ float: 'left' });
            j('.alertImg').css({ "margin-left": '0px' });
            //  j(".alertImg").css("float", "right");
            // j(".alertImg").css("margin-left", "-102px");
            j('table.menuoff').animate({ width: '1245px' });
            j('#sidebar1').animate({ width: '1270px' });
            j('#map_canvas').animate({ width: '1015px' });
            j('.search').animate({ width: '96px', fontSize: '13px', paddingLeft: '35px' });
            j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem').animate({ width: '930px', fontSize: '13px', marginTop: '0px' });
            j('ul#ContentPlaceHolder1_txtName_AutoCompleteExtender_completionListElem li').animate({ fontSize: '18px', width: '930px', });
            j('.vehList').animate({ width: '125px' });
            j('.vehType').show();
            j('.lblCss1').show();
            j('.tabArrow1').show();
            j('.tabArrow').hide();
            j(".vehAddress").css("display", "inline-block");
            j(".vehAddress").css("width", "230");
            j(".vehAddress").css("min-height", "1px");
            j(".vehAddress").css("margin-right", "6px");

            j(".VehicleHours").css("display", "inline-block");
            j(".VehicleHours").css("width", "100");
            j(".VehicleHours").css("min-height", "1px");

            j(".CumVehicleHours").css("display", "inline-block");
            j(".CumVehicleHours").css("width", "180");
            j(".CumVehicleHours").css("min-height", "1px");

            j(".FuelEfficency").css("display", "inline-block");
            j(".FuelEfficency").css("width", "140");
            j(".FuelEfficency").css("min-height", "1px");

            j(".UreaUsage").css("display", "inline-block");
            j(".UreaUsage").css("width", "140");
            j(".UreaUsage").css("min-height", "1px");

            //  j(".VehicleEngineHours").css("margin-right", "3px");

            j('.headTop1').show();
            j('.headTop2').show();
            j('.headTop3').show();
            j('.headTop4').show();
            j('.headTop5').show();
            j('.headTop6').show();
            j('.headTop7').show();
            j('.headTop8').show();
            j('.headLocation').show();
            j("#notificationContainerr").hide();
            //j(".headTop3").css("margin-left", "10px");
            //j(".headTop4").css("margin-left", "120px");
            j(".alertImg").css("top", "-5px");
            j('.vehType').animate({ width: '93px' });
            sessionStorage.expanded = "true";

            document.getElementById('ContentPlaceHolder1_hdfISExpand').value = "1";

                $(".tableCount > table").css('display', 'none');
            // $("#Viewmore").css('display', 'inline-block');

                if ($(".tableCount > table").length > 0) {

                    GetRepeaterAddress(1);
                }
            //DisableViewMore();

                //debugger;
                var timer = $find('ContentPlaceHolder1_timerLandingPage');

            //    console.log(timer);
                if (timer != null) {
                    timer._stopTimer();
                }
            //    console.log(timer);

        }

        function pageLoad() {
           // alert('pageLoad');
            var oRows = document.getElementById('rptDiv1').getElementsByTagName('table');
            var iRowCount = oRows.length;

            /////////////////////////////////Cumulative hours Chart/////////////////////////////////////// 
          $('#tblVehicleList tr').each(function (i) {
              var vehList = $(this).find(".vehList").html();
             var hours=$(this).find(".CumVehicleHoursvalue").html().indexOf('h');
             var line1val;
             var line2val;
             var line3val;
             var CumVehicleHours = $(this).find(".CumVehicleHoursvalue").html().substring(0, hours);
                if (CumVehicleHours < 10) {  //set chart legends 
                    CumVehicleHours = CumVehicleHours * 10;
                    line1val = 2; 
                    line2val = 6;
                    line3val = 10;
                }
                else if ((CumVehicleHours >= 10) && (CumVehicleHours < 100))
                {
                    
                   line1val = 20;
                   line2val = 60;
                   line3val = 100;
                }
                else if ((CumVehicleHours >= 100) && (CumVehicleHours < 1000))
                {
                    CumVehicleHours = CumVehicleHours / 10;
                    line1val = 200;
                    line2val = 600;
                    line3val = 1000;
                }
                else if ((CumVehicleHours >= 1000) && (CumVehicleHours < 10000)) {
                    CumVehicleHours = CumVehicleHours / 100;
                    line1val = 2000;
                    line2val = 6000;
                    line3val = 10000;
                }
                else if ((CumVehicleHours >= 10000) && (CumVehicleHours < 100000)) {
                    CumVehicleHours = CumVehicleHours / 1000;
                    line1val = 20000;
                    line2val = 60000;
                    line3val = 100000;
                }
                else if ((CumVehicleHours >= 100000) && (CumVehicleHours < 1000000)) {
                    CumVehicleHours = CumVehicleHours / 10000;
                    line1val = 200000;
                    line2val = 600000;
                    line3val = 1000000;
                }
                var BusinessType = document.getElementById('ContentPlaceHolder1_businessType').value;   
              
              if (BusinessType == 3) {
                  CumVehicleHours = CumVehicleHours * 2;
                  $(this).find(".CumVehicleHours").html('<svg height="60" width="270" style="margin-top: -25px;">' +
                  '<line x1="0" y1="40" x2="330" y2="40" style="stroke:rgb(255,0,0);stroke-width:2" />' +
                   '<line x1="0" y1="37" x2="0" y2="43" style="stroke:rgb(255,0,0);stroke-width:2" />' +
                  '<line x1="40" y1="37" x2="40" y2="43" style="stroke:rgb(255,0,0);stroke-width:2" />' +
                  '<line x1="120" y1="37" x2="120" y2="43" style="stroke:rgb(255,0,0);stroke-width:2" />' +
                  '<line x1="200" y1="37" x2="200" y2="43" style="stroke:rgb(255,0,0);stroke-width:2" />' +
                   '<text x="0" y="50" font-family="Verdana" font-size="8">' +
                  '0' + ' hrs ' +
                  '</text>' +
                  '<text x="40" y="50" font-family="Verdana" font-size="8">' +
                  '' + line1val + ' hrs ' +
                  '</text>' +
                  '<text x="120" y="50" font-family="Verdana" font-size="8">' +
                  ' ' + line2val + ' hrs ' +
                  '</text>' +
                  '<text x="200" y="50" font-family="Verdana" font-size="8">' +
                  '' + line3val + ' hrs' +
                  '</text>' +
                  '<image xlink:href="Images/tractorfarm.png" x=' + CumVehicleHours + ' y="22" height="20px" width="20px"/>' +
                  '</svg>');
              }
              else {
                  $(this).find(".CumVehicleHours").html($(this).find(".CumVehicleHoursvalue").html());
              }
           
            });
            /////////////////////////////////Cumulative hours Chart///////////////////////////////////////
            document.getElementById("totalCount").innerHTML = ('(' + iRowCount + ')');
            if (iRowCount == 0) {

                document.getElementById('rptDiv1').innerHTML = "<div style='align-content:center;float: left;'>No Vehicles Mapped to this Owner.Contact your Dealer/Administrator</div>";
            }

        }
        window.onload = pageLoad;  // invoke pageLoad after all content is loaded
    </script>

    <script type="text/javascript">
        function ItemSelected(sender, args) {

            __doPostBack('ContentPlaceHolder1_txtSearch', "txtSearch_TextChanged");

        }

        var specialKeys = new Array();
        specialKeys.push(8); //Backspace
        specialKeys.push(9); //Tab
        specialKeys.push(46); //Delete
        specialKeys.push(36); //Home
        specialKeys.push(35); //End
        specialKeys.push(37); //Left
        specialKeys.push(39); //Right
        specialKeys.push(32); //Space
        specialKeys.push(13); //Enter
        function IsAlphaNumeric(e) {
            //  
            var valText = $get("ContentPlaceHolder1_txtSearch").value;

            if (valText != "") {

                var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;

                //  var ret = ((keyCode >= 48 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || (keyCode >= 97 && keyCode <= 122) || (specialKeys.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
                var ret = ((keyCode >= 48 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || (keyCode >= 97 && keyCode <= 122) || (specialKeys.indexOf(e.keyCode) != -1)||keyCode ==32);

                if (e.keyCode == 13) {
                    document.getElementById('ContentPlaceHolder1_btnSearch').click();
                }

                return ret;
            }
            else {

                if (e.keyCode == 13) {
                    document.getElementById('ContentPlaceHolder1_btnSearch').click();

                    return true;
                }
            }
        }

    </script>

    <script type="text/javascript">
        function ClearSearchTextBox() {

            document.getElementById("ContentPlaceHolder1_txtSearch").value = "";

        }

        function ClearStorage() {
            sessionStorage.clear();
        }
    </script>



</head>
    
 <body  onbeforeunload="bodyUnload();" onclick="clicked=true;" onload="initSession()" class="post"> 
    

    <script>
        var sess_pollInterval = '10';
        var sess_expirationMinutes = '10';
        var sess_warningMinutes = '18';
        var sess_intervalID;
        var sess_lastActivity;

        function initSession() {
            sess_lastActivity = new Date();
            sessSetInterval();
            $(document).bind('click.session', function (ed, e) {
                sessKeyPressed(ed, e);
            });
        }

        //HitThe Server and Keep session Active - Required for reports 
        setInterval(function () { UpdateActiveSessionDetails(); }, 300000);

        function UpdateActiveSessionDetails() {
            $.ajax({
                type: "POST",
                url: "Home.aspx/UpdateActiveSession",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {

                },
                failure: function (response) {

                }
            });
        }

        function sessSetInterval() {
            sess_intervalID = setInterval('sessInterval()', sess_pollInterval);
        }

        function sessClearInterval() {
            clearInterval(sess_intervalID);
        }

        function sessKeyPressed(ed, e) {
            sess_lastActivity = new Date();
        }

        function sessLogOut() {
            $.ajax({
                type: "POST",
                url: "Home.aspx/ExpireSession",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (response) {
                    window.location.href = 'LoginPage.aspx';
                },
                failure: function (response) {
                    window.location.href = 'LoginPage.aspx';
                }
            });

        }

        function sessInterval() {
            var now = new Date();
            //get milliseconds of differneces 
            var diff = now.getTime() - sess_lastActivity.getTime(); // This will give difference in milliseconds
            var diffMins = Math.round(diff / 60000);

            //get minutes between differences
            var expirymins = sess_expirationMinutes - sess_warningMinutes;

            if (diffMins >= sess_warningMinutes && diffMins < sess_expirationMinutes) {
                alertify.alert('<div class="titlebar">Session Expiry</div>', '<div class="crash_alert"><div class="alertimg"></div><div class="vichleinfo"><p>Your Session will expire in ' + expirymins + ' Minutes. Press Ok to remain logged in.  </p></div></div>', function (e) {
                    if (e) {
                        initSession();
                        sessSetInterval();
                        sess_lastActivity = new Date();
                        return;
                    }
                }).set({ closable: false });
            }
            if (diffMins >= sess_expirationMinutes) {
                sessClearInterval();
                sessLogOut();
            }
        }
    </script>

    <script>
        function breakdownclosurePopup(vehicleID, vehicleType) {

            //var dataValue = "<p><b>Do you want to notify Emergency Alert?</b></p>"
            var dataValue = "<p><b>Do you want to close the status of the breakdown alert of this vehicle " + vehicleID + "?</b></p>"
            alertify.confirm('<div class="titlebar"> Breakdown Alert!! </div>', '<div class="crash_alert"><div class="alertimg"></div><div class="vichleinfo">' + dataValue,

                 function () {
                     alertify.success('CloseNow');
                     UpdatetheBrkdownstatus(vehicleID, vehicleType);
                     location.reload();
                 },
                 function () {
                     alertify.error('Later');
                     location.reload();
                 }).set({ closable: false }).set('labels', { ok: 'Close Now', cancel: 'Later' });

            //  alertify.confirm('<div class="titlebar"> Roadside Assistance</div>', '<div class="crash_alert"><div class="alertimg"></div><div class="vichleinfo"><p>Dealers Name. : <b>ABC Ltd </b></p><p>Dealers Address :</p><p><b>Dummy AddressDummy AddressDummy Address</b></p><p>Phone Number : <b>080-3333333333</b></p></div></div>',

        }
        function UpdatetheBrkdownstatus(vehicleID, vehicleType) {

            var dataToSend = JSON.stringify({ 'vehicleID': vehicleID, 'vehicleType': vehicleType });

            $.ajax({

                type: "POST",

                url: "Home.aspx/CloseBrkdownStatusofVehicle",

                contentType: "application/json; charset=utf-8",
                dataType: "json",
                data: dataToSend,
                success: function (response) {

                    if (response.d == true) {

                        alertify.alert('<div class="titlebar">Breakdown</div>', '<div class="crash_alert"><div class="alertimg"></div><div class="vichleinfo"><p>Your Breakdown alert  have been Closed.</p></div></div>').set({ closable: false });
                    }
                    else {
                        alertify.alert('<div class="titlebar">Breakdown</div>', "Something got wrong...please try again.").set({ closable: false });
                    }
                },
                failure: function (response) {
                    debugger;
                    alert("Error while calling the service");
                }
            });


        }

        // Based on the Role the alert Button Disabled
        function SetAlertBtnVisibility(roleID) {
            currentroleid = roleID;
            if (roleID == 1 || roleID == 3) {
                $(' #notificationLink').hide();
            }
        }

        // Based on the Business Type the Home page,Location Service popup Icons and Fuel Level Enabled and Disabled
        function SetAppImagesBasedOnBusinessType(busineeType) {
            if (busineeType == 1) {
                $('.welcome_cloudlink_Commercial').show();
                $('.vehicleimage_Commercial').show();
                $('.fuellevel').hide();
                $('.roadassitance').css('display', 'block');
                $('.vehicleinfo').css('width', '980px');
                $('#AccordionPane3').css('display,block');
            } else if (busineeType == 2) {
                $('.welcome_cloudlink_Construction_Equipment').show();
                $('.vehicleimage_Construction_Equipment').show();
                $('.fuellevel_others').show();
                $('.roadassitance').hide();
                $('.vehicleinfo').css('width', '910px');
                $('#AccordionPane3').css('display,none');
            } else if ((busineeType == 3)) {
                $('.welcome_cloudlink_Farm').show();
                $('.vehicleimage_Farm').show();
                $('.fuellevel_others').show();
                $('.roadassitance').hide();
                $('.vehicleinfo').css('width', '910px');
                $('#AccordionPane3').css('display,none');
            } else if ((busineeType == 4)) {
                $('.welcome_cloudlink_MTBD').show();
                $('.vehicleimage_MTBD').show();
                $('.fuellevel').hide();
                $('.roadassitance').css('display', 'block');
                $('.vehicleinfo').css('width', '980px');
                $('#AccordionPane3').css('display,block');
            }
        }

        // JSON Menus Calling function
        function CreateDynamicjsonMenu(jSONData) {
            var json = $.parseJSON(jSONData);
            $(".menu").empty();
            $(json).each(function (i, val) {
                var menulistLocal = '';
                var MenuID = val.MenuID;
                var NavigationURL = val.NavigationURL;
                var DisplayIndex = val.ClassName;
                var DisplayText = val.DisplayText;
                var SubmenulistValue = val.SubMenu;
                // Parent Menus
                if (NavigationURL == '') {
                    if (DisplayIndex == 'Feedback_Class') {
                        menulistLocal += "<li class='menuItems" + MenuID + "'><a href='mailto:CoVeCustomerCare@techmahindra.com?subject=Feedback for mahindracloudlink.com&body=Hi Team'><span class='" + DisplayIndex + "'></span><span>" + DisplayText + "</span></a></li>";
                    } else {
                        menulistLocal += "<li class='menuItems" + MenuID + "'><a href='" + "#" + "'><span class='" + DisplayIndex + "'></span><span>" + DisplayText + "</span></a></li>";
                    }
                } else {
                    menulistLocal += "<li class='menuItems" + MenuID + "'><a href='" + NavigationURL + "'><span class='" + DisplayIndex + "'></span><span>" + DisplayText + "</span></a></li>";
                }
                var Submenulist = '';
                var menuItem = 'menuItems' + MenuID;

                if (SubmenulistValue.length > 0) {
                    $(SubmenulistValue).each(function (j, value) {
                        var subNavigationURL = value.NavigationURL;
                        var subDisplayIndex = value.DisplayIndex;
                        var subDisplayText = value.DisplayText;
                        var SuperSubmenu = value.SubMenu;
                        var ClassSubmenu = value.ClassName;
                        // Sub Menus
                        if (subNavigationURL == '') {
                            Submenulist += "<ul class='secondLevel' id='secondLevel" + j + "'><li class='secondsubLevel" + ClassSubmenu + "' id='secondsubLevel" + j + "'><a href='" + "#" + "'><span class='" + ClassSubmenu + "_Menu'></span>" + subDisplayText + "</a>";
                        } else {
                            Submenulist += "<ul class='secondLevel' id='secondLevel" + j + "'><li class='secondsubLevel" + ClassSubmenu + "' id='secondsubLevel" + j + "'><a href='" + subNavigationURL + "'><span class='" + ClassSubmenu + "_Menu'></span>" + subDisplayText + "</a>";
                        }

                        var superSubmenulist = "<ul class='thirdLevel' id='thirdLevel" + j + "'>";
                        var subMenuItem = 'secondLevel' + j;

                        if (SuperSubmenu.length > 0) {
                            $(SuperSubmenu).each(function (k, value) {
                                var subNavigationURL = value.NavigationURL;
                                var subDisplayIndex = value.DisplayIndex;
                                var subDisplayText = value.DisplayText;
                                var subClassName = value.ClassName;
                                superSubmenulist += "<li class='thirdsubLevel' id='thirdsubLevel" + k + "'><a href='" + subNavigationURL + "'><span class='" + subClassName + "_Menu'></span>" + subDisplayText + "</a></li>";
                            });
                            Submenulist = Submenulist + superSubmenulist + "</ul></li></ul>";
                        } else {
                            Submenulist = Submenulist + "</li></ul>";
                        }
                    });
                    menulistLocal = "<li class='menuItems" + MenuID + "'><a href='#'><span class='" + DisplayIndex + "'></span><span>" + DisplayText + "<span class='dropIcon'></span></a></li>";
                    $(".DynamicMenu ul.menu").append(menulistLocal);
                    $(".DynamicMenu ul.menu li." + menuItem).append(Submenulist);
                } else if (SubmenulistValue == null || SubmenulistValue.length == 0) {
                    $(".DynamicMenu ul.menu").append(menulistLocal);
                }
            });
        }
    </script>

    <form method="post" action="./LocationServices.aspx" id="form1">
<div class="aspNetHidden">
<input type="hidden" name="toolkitScriptManager1_HiddenField" id="toolkitScriptManager1_HiddenField" value="" />
<input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value="" />
<input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="" />
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="xgX8pSOuRuVPEMiqsw5GvJAKo7nNo09uVNc/4qnaG2eeA/MasIGVH3foUFmHHkySp5V0jaIwCk6aRWdm6miQBrJUqMhmdudxpuI2EAlzCYwodskb6gXD/78ibG08ki9h4wZHUB58oKbNqKbCotbfLaPtDvZDB0rbt3oFX764wI3VX83inTD6Rlwbs/7Z9qkDqwgp4PcMZl0jDdRPFqHy4titcguX2f36GI2tQMboZEQ4aoiYbcLIFk95dJGMk1aZzU8G90OeVe4h4EoX6SHlRvixj0Psi/2TwE8T+G16w2wZ2kV0q+Shr9tVw2DRqN1fPET37jikTLY/YDTTz0vsEN2XYsLu3mXrchrdHSMs+utX4bSeFMsBhjDSak5K73qSrFDtykytzLBTsDVrKj8CyvNTjjtRi6obCWcmEqbvZON/FEKF8Dd2ntVSQ8KmVtcLu6XCoPwcG0dEoob8V3PHPGv9ye0AX5Bb1XX6naWO4rmRIe3WEOVh/uJ9oWvZN8o17PTh18sxCMYQ0xiYEMgV8cGUFK9lTnoOm0OZEFXoIfo1AvR3ghszkIWQZC4gXvqyvrTK7zxq9Ua9aOOYbVkFnHFPSSTQiT/ZGuwJAGhrXgppgM0LNi3GI5whLPq0nyOsZfySe4cPLD0df0Gx01PgNV2nIu1HKzr2wiPrCKGshBEaCIDEmLX8MXuIjrr5xScb80yl6P5gdFwTF7JCxMqki8HBWAh7tn69I9hj0tCATFZnQJaSxRmhoOVSXyOZJ0qko4apdkUCgpoNqHPV/HmHn5xn9BzJouH2crj0rYhj5fYPU6y9APfGtWAvWj3q0RvzKZtbV+U+ZuLBE/0tXhwBmjWYgL3bYbAd/psJn5VRnbHbxLVLMgvwllyjakxp6dD0vooiFASdxhilc6ZRs3HmX5KljIABWXj1HAMgx7JSMqD3bbQIKs8HiAeQzjH2qmuoXH9+Vko3bkoVVWc7dw5ieWVXQLoEaQ0BSXL5Q+Gb69BvCou7JQdQSYAwj8lt/UWYaNQyt1FcRtbCwuemnRBQSqw867e/0L5OrCT992vMJNI8C9Oku1qyctbr3iNLJMUAsYAGsVT1l6KIoo5coW0dPcDe7ZmdIefp2eB89FKU/ZtSCjTSnRFIt6xI23OCg3/MyaG8b1buxOicMNa8PTrxoWnRr7m07oztH+ZcT5NQwHJ6InyHsPPPRN5ECjJaTco7wBqJgAwB4v8ITRWG8nHIBBAcDFAuSvFYkyf8o6OGvlTQeE1wub03tj5wO6tRuq7chrJzaXTa61SeUvt3QmiPu29pJg3whSsx0pzFO+8kKr2n6BDXHgmijUWRzysH8hB6NzspUj9aTelZLYzNhl7ikGE1b/fzaUP08tyntt+xePjJWgVhmbeXN0beHzgrKdH84dM9WcyRUB/YUWXiaaCKemVIfmk7l/nwiRqN8ico7UvdOuYoVvG3UcohgpmW6xHbLFon9uOkZTzL8S9Y1jXH+Wi/eK5dfh1Cjxpg2SCTJBQoMIvu6veb1Cq+a5+defDVSWr96I3qoEqUdJTEzKCWdk1iWj2H3zJSI6Tg0rV1ZIzWhKdWtkXycOE9ij/pln5JF56H7CEj3mAiAbumSnFBWtlt0YxobzjdaKj6pCgt3MuM8llM1vfN9Tl7Dfx0Jbcec9EFu6RhtcyEmaS3QLI2v3wqhLqOkS3OhhtqtSiCvSDOF/M5voZL1uo+0yKk2O3vrrHpjXU7IaDkSJXNSyo6lPv6aLsGSbbMf0zWUD9D5m+w7OTnFF7peI13Vp6+7lTfIhP6fbR5CYiiSzkSotP6GLM8ZDzkWZqPFVNmiilswZk/QeQeAbclxLH5nlg5+yMSUPw7peNyAp16SlHAa6ChGD0AE2mpd6jOlcOaYMAxQCcRM+i0CazDK++lMl0UgFDqlWntADYlfH5BuTn227slzUdCvMMqCNCGj9FR8C6ocs7mzBAyS4VOzj2r+8pqJtQqpNnKgYZFvK7O9QLF866KvdAGE1Jr1V+Mar+O8i+OSwc/DCNyhJQbEwUnNvgFhrBV8MvEY9rlb/jx13T/ykVRa3sq2IxjuAQoVlbHUM7lB1j/Owd1kETivfv88vB5ARlVaRDkYYtpCYx2mi3Ww0Idi40OJs1Rc7d77FR6t874Rp1nQ9i2dadeTBCWULR+bU5I5aOz822bOmrpmvQk1taziORT/JCoBtxERP8ENiKlDEpqGTLHR5dvvBdP8t6XVihMEL9BXabggL3Hf7I1uoVx/XM9rozEerOYkfw21BVy+PJgAV0hrTySwfbxAGJn6D0OZjj/9fgDGq3ce+xuzPLjdMc5JBPx5Si1v29GLw5o3ls92HmNOoAN1gjO/qJ+lXzqpIMfzGrEQptnV26O87viMX/ySPNUu+Uu9xloq8jFQHyu397d/BnXlKGel0GpN6rrBQ+z/0JeLPLB5qBw+WAa+2BdCbfHW2jTOoRFB8rE74lkyh1xMbU1B03H75i3tn8Eb8hsXNvA8CxJa9sBUdkzFvbuSYOaGHOR79A34r8fipzEQrWqfBPo017l0NYpTOH5LVsDGKoE7bktc8gmhe4xsmbGao55DgrbMQG9aLENMmw6oA8yEOnkbFCckATFz5vLuB8tvoC3b+jwez3PoDxUoewCvLdgEPnaMCZyelaWhsA+NCnLRtOyDh6lwZWlZKoGfOEBHWUTYxIZUM9++UzWlSdBWYbHF8D6TBnx9rdwcOgmXzMybfSa2rXjPUSQ1hDTT8VTbHNWHfEgLiUdWO+8jL0B1SbYEX/9lvdehxdne2LBMyKQn/gOH1QoY+c0apJz/6LBSVcz2lZJKoZG4OFOMSRPIBpVABe2owKuM8KIQDGUMZlyw+hQwPsMGHtahrtGDV/arxRO6N6ttIsRrTvhxgzfc+hfg0nlcV8QnGknds9StrIOs6q3s/GAsjhicKhmfcx0UK5hkz7a9tUlUNlT0P2wVkslySxrZGxACLdHi6Vn+UjmrY/SLrQDGroe237jX3QytTbWOlle5eaYVQG80NxtrWLDOgCJW3wf+9A0CNFkX0BJfmYgzmy/2b3uRAXh6yQ/6616gNGndpfrjWg+7dnH3J1GbXC1s09IW+yZ8jr1xRcDEvAPr7lvcL/Wsg5FypQj3+o3AumUNgwRfIMhscApCufg3DDJWVfNHOJnvUPLpdSABWEPiIKpGAvgFfLYDI1A0cNe5sBLzUz82Yep2zAcIr6wEriq7xfARzV/KcstTDtiVK5cnUC15l6AgYfCVXhds9audNYa8Xu7EzkYlOrcWTfW5weCP529GZfriKf+iVIXNSBeDw9NHSU0EaV8294ePG0A2EqUrQTfQgsDT0aqi/QGCGyAjwmgaUEj4stmlv/X+7zw+a7yEfgG0hOKwU3a0TuoTCZ2/zmCu3T0dB312YqPKRjC86slY+vQ8br/OIuzZIMwA3jjAyDgwtpnVnSOMiJzozqMtuvNmplLEaEYzbwWqlbKD5XooWPnmlsirydcpKkBV5kQMkG/sPMt1gLa1Btx7HKQ2+A6q/OxidadtZ2HIID9yP2cfppINQDkZc78e4shLxMHe4GMb/dmRpXaO4ocwmGJfHYN8AfSehPwbhBJg7YAtSU96ENX4eY02e1S70z5y/KKiAOC3moUS/ZdJn4WCA9e6yYRWnAPFu9ydBUahWXtfxaRamGIDnfnf6ZNBaRa8+qf1+IUeUDRBFOgk3ToYU+7WNe9om2u339DiMhCSY6Yw42BUwdE6Q4Cjab9fLVdm5LTibJoHVhzZ/uuDhZLLpUJCcf6mSvGs790CIjK0nDrmyGg9P2QovcucJW/F11VLTp3OXJxhK4QZycOlv+syiO3VHiCeUAPjEnYwiY/QRDJl6llfofe8lRGL0G4de7GjrUDdHYCx/aq30yqDV3Zae7qaxFnI42Fm3+H+7F3TG7u69PXwGvKhZpb0lU1Leko7ZqYIbkhMCkghSOnQwzjdb5w0OgGJ3BhLZFAuKyhvJA8ehgkEucXuyRpUEZMkYzmafMaUZw7byCwu95Ay1ggF1VFrDEZbDe3ML/nvwMeutjAadTtVNN8nOEV7Hehb25ccPWJWHKKn8makuzSSOe47tZnv2Sc9W09U8JZEOY=" />
</div>

<script type="text/javascript">
//<![CDATA[
var theForm = document.forms['form1'];
if (!theForm) {
    theForm = document.form1;
}
function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
        theForm.__EVENTTARGET.value = eventTarget;
        theForm.__EVENTARGUMENT.value = eventArgument;
        theForm.submit();
    }
}
//]]>
</script>


<script src="/Release1.0/WebResource.axd?d=4mcy8ZMQKg9KxAc6JdeL1Fyl7gIBLW9NoOQXGjxyTE131U8iv1h12mh6gzzRgDLncMngLOlYWiZPR0Umbj6TZEk8yGw1&amp;t=636355104046607314" type="text/javascript"></script>


<script src="/Release1.0/ScriptResource.axd?d=KoLcuFjtQ5dUcTCnMRnwjWVtJFZJ05OA8dHUSc6wFRv9qVD7dnyo3vBB1KEhvpG8aL9OSXEtr6YjBZoFRUcL_9ol8O6K162m52PuIyByc3jpQJQ40&amp;t=78f0a2d1" type="text/javascript"></script>
<script src="/Release1.0/ScriptResource.axd?d=NoajFtAqOnFyAzSFEnGz7aqQTAsrCHNNnc659fqrgU0a5sAhc9i2r3ZdyhkjriqJtX1kxs5P972xhHm0GHgQD_OuHVogAyZgD2H6ZIeKwPdOhjgGzCzgciRihm8n5f6Qn7iJaQ2&amp;t=78f0a2d1" type="text/javascript"></script>
<script src="/Release1.0/ScriptResource.axd?d=dasn2S_DvGitOX1-XwGmBYahM3ohqbPiwtrnVlcurzx0muX71vPuxH0kkhJx7AZm9ub8m-vb2kctSb--3ybOVe7-e7u45wHpUSS5OFq7DNSHWaqsxAkQpR5-YEAIh4Qkl6C87w2&amp;t=78f0a2d1" type="text/javascript"></script>
<script src="/Release1.0/LocationServices.aspx?_TSM_HiddenField_=toolkitScriptManager1_HiddenField&amp;_TSM_CombinedScripts_=%3b%3bAjaxControlToolkit%2c+Version%3d3.5.60623.0%2c+Culture%3dneutral%2c+PublicKeyToken%3d28f01b0e84b6d53e%3aen-IN%3a834c499a-b613-438c-a778-d32ab4976134%3a5546a2b%3a475a4ef5%3ad2e10b12%3aeffe2a26%3a37e2e5c9%3a5a682656%3a12bbc599" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[
var PageMethods = function() {
PageMethods.initializeBase(this);
this._timeout = 0;
this._userContext = null;
this._succeeded = null;
this._failed = null;
}
PageMethods.prototype = {
_get_path:function() {
 var p = this.get_path();
 if (p) return p;
 else return PageMethods._staticInstance.get_path();},
GetNames:function(prefixText,count,succeededCallback, failedCallback, userContext) {
return this._invoke(this._get_path(), 'GetNames',false,{prefixText:prefixText,count:count},succeededCallback,failedCallback,userContext); },
AddVehicleDetailsToSession:function(sVehicleDetails,succeededCallback, failedCallback, userContext) {
return this._invoke(this._get_path(), 'AddVehicleDetailsToSession',false,{sVehicleDetails:sVehicleDetails},succeededCallback,failedCallback,userContext); }}
PageMethods.registerClass('PageMethods',Sys.Net.WebServiceProxy);
PageMethods._staticInstance = new PageMethods();
PageMethods.set_path = function(value) { PageMethods._staticInstance.set_path(value); }
PageMethods.get_path = function() { return PageMethods._staticInstance.get_path(); }
PageMethods.set_timeout = function(value) { PageMethods._staticInstance.set_timeout(value); }
PageMethods.get_timeout = function() { return PageMethods._staticInstance.get_timeout(); }
PageMethods.set_defaultUserContext = function(value) { PageMethods._staticInstance.set_defaultUserContext(value); }
PageMethods.get_defaultUserContext = function() { return PageMethods._staticInstance.get_defaultUserContext(); }
PageMethods.set_defaultSucceededCallback = function(value) { PageMethods._staticInstance.set_defaultSucceededCallback(value); }
PageMethods.get_defaultSucceededCallback = function() { return PageMethods._staticInstance.get_defaultSucceededCallback(); }
PageMethods.set_defaultFailedCallback = function(value) { PageMethods._staticInstance.set_defaultFailedCallback(value); }
PageMethods.get_defaultFailedCallback = function() { return PageMethods._staticInstance.get_defaultFailedCallback(); }
PageMethods.set_enableJsonp = function(value) { PageMethods._staticInstance.set_enableJsonp(value); }
PageMethods.get_enableJsonp = function() { return PageMethods._staticInstance.get_enableJsonp(); }
PageMethods.set_jsonpCallbackParameter = function(value) { PageMethods._staticInstance.set_jsonpCallbackParameter(value); }
PageMethods.get_jsonpCallbackParameter = function() { return PageMethods._staticInstance.get_jsonpCallbackParameter(); }
PageMethods.set_path("LocationServices.aspx");
PageMethods.GetNames= function(prefixText,count,onSuccess,onFailed,userContext) {PageMethods._staticInstance.GetNames(prefixText,count,onSuccess,onFailed,userContext); }
PageMethods.AddVehicleDetailsToSession= function(sVehicleDetails,onSuccess,onFailed,userContext) {PageMethods._staticInstance.AddVehicleDetailsToSession(sVehicleDetails,onSuccess,onFailed,userContext); }
//]]>
</script>

<div class="aspNetHidden">

	<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="8E2E2A24" />
	<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="fBDd/6Mh8bGYTflyOJkfH+WjZWfYvcIa+IXGB++LDGojBWN/O6NSBLh8FXs46wKiZz8OA6W3x0ZBE/oro1Xw/Pd+PK/nn6uM5DgpAmvZv173kMHM5cOo0AFDGJ0k+giVD6qklVjzwpPVX+nHZv6WZe1RnObJ4gy/7S0fXGlT2I/HzuDFU9HarFJiVjkmN6U1XIseNVKJGz2x044VJ5XLFKjyUm6vU91PC4n7tJCMhOS3vbuLpYi+wTQIP3b/K5j4zOPST/waHiTl6GNFTzaSytSFQjvebqIhTFDlTP9P2uMuY5+zLzE2Csi6KFUJGMOEWzcmOyS2F2mAETjh3dtkui5/vkJt/P3+qnIQTWMDwEA5dDfIRk64czhDH+0rWN9YAJyHhWiX1Y3213mj+b5Ah3XbHfeMp3jrD1GIVbAMStzOyJBeRExn6MbB8G6epjHgy4TVvA==" />
</div>
        <script type="text/javascript">
//<![CDATA[
Sys.WebForms.PageRequestManager._initialize('ctl00$toolkitScriptManager1', 'form1', ['tctl00$ContentPlaceHolder1$Updatepanel1','ContentPlaceHolder1_Updatepanel1','tctl00$ContentPlaceHolder1$UpdatepanelMap','ContentPlaceHolder1_UpdatepanelMap'], ['ctl00$ContentPlaceHolder1$timerLandingPage','ContentPlaceHolder1_timerLandingPage'], [], 90, 'ctl00');
//]]>
</script>

        

        <input type="hidden" name="ctl00$Refreshrate" id="Refreshrate" value="1" />
        <input type="hidden" name="ctl00$hdfBusinessType" id="hdfBusinessType" value="4" />
        <input type="hidden" name="ctl00$hdfEmrgURL" id="hdfEmrgURL" value="https://www.mahindradigisense.com/EmergencyServices/Service1.svc/" />
        <div id="wrapper">
            <!-- Header Start-->
            <header>
                <div class="headerTopbar">
                    <div class="headerContent">
                        <div id="logo">
                            <img alt="Cloudlink" src="Images/logo.png" width="192" height="40" ondragstart="return false;" />
                        </div>

                        <!-- active  Nav Start-->
                        <nav>
                            <!-- JSON Menu Section-->
                            <div class="DynamicMenu">
                                <ul class="menu"></ul>
                            </div>

                        </nav>
                        <!-- Nav End-->
                        <div id="welcome">

                            <div class="welcomeTop">
                                <div class="headUser">
                                    <h6>
                                        
                                        Welcome <span class="userName" id="ProfileName">Rohit </span>|
                                        <span id="lbluser" style="font-weight:bold;"></span>
                                    </h6>
                                </div>
                                <div class="headUser_profile">
                                    <ul>
                                        <li>My Account
                                        <ul class="submyaccount">
                                            <li><a href="MyProfile.aspx"><span class='myProfile_Menu'></span>My Profile</a></li>
                                            
                                            <li style="border-bottom: none"><a href="PasswordChange.aspx"><span class='changePassword_Menu'></span>Change Password</a></li>
                                        </ul>


                                        </li>
                                    </ul>
                                    <span style="font-weight: bold">|</span>

                                </div>

                                
                                <div class="headUser_Help">
                                    <ul>
                                        <li>Help
                                        <ul class="submyaccounthelp">
                                            <li><a href="#" class="helpAnchor">Help</a></li>
                                            <li style="border-bottom: none"><a href="FAQ.aspx">FAQ</a></li>
                                        </ul>
                                        </li>
                                    </ul>
                                    <span style="font-weight: bold">|</span>
                                </div>
                                

                                
                                <div class="headLog">
                                    <p class="userName">
                                       <a id="lnkbtnLogout" class="button" href="javascript:__doPostBack(&#39;ctl00$lnkbtnLogout&#39;,&#39;&#39;)">Log Out</a>
                                    </p>

                                </div>
                            </div>
                            <div class="welcomeBottom">
                                <div class="navAlert">
                                    
                                    <div id="notificationLink" class="alertenablefarmmaster">

                                        <a href="#" id="notificationLink alertbtn" class="nonhoverAlert">
                                            <span class="alertName">Alerts</span>
                                        </a>

                                        <a href="#" id="notificationLink" class="hoverAlert" style="display: none;">
                                            <span class="alertName">Alerts</span>
                                        </a>
                                    </div>
                                    
                                </div>
                            </div>
                            <div id="notificationContainer">
                                <div id="notificationsBody" class="notifications">
                                    <div class="loader"></div>
                                    <div id="alertDiv"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>
            <!-- Header End-->
            <div id="Content_Div" style="height: 545px">
                <div id="helpPopup">
                    <!-- modal content -->
                    <div id="helpContent">
                        <div class="helPDiv">
                            <p>
                                In case of any queries please contact 
                            </p>
                            <p>
                                
                                Your nearest Mahindra Dealer. 
                            </p>
                            
                            <p>Email Id:  digisense.ccm@mahindra.com</p>

                            <p>Website: <a href="#" style="text-decoration: underline; color: blue" target="_blank">www.mahindradigisense.com</a></p>

                            <p>Download <a href="#" id="userManualFile" target="_blank" download="UserManual.pdf" style="text-decoration: underline; color: blue">User Manual </a></p>
                        </div>
                    </div>
                </div>
                <marquee id="RemindersMarQue"><span id="MarQueeReminders" style="color: red;">  </span></marquee>

                
    <input type="hidden" name="ctl00$ContentPlaceHolder1$hdfISExpand" id="ContentPlaceHolder1_hdfISExpand" />
    <input name="ctl00$ContentPlaceHolder1$businessType" type="hidden" id="ContentPlaceHolder1_businessType" value="4" />
    <span id="ContentPlaceHolder1_timerLandingPage" style="visibility:hidden;display:none;"></span>

    <div id="innerWrap">

        <div id="main">
            <div id="ember">
                <div id='sidebar1' class="leftcontainer">

                    <div class="searchLeft">
                        <input name="ctl00$ContentPlaceHolder1$txtSearch" type="text" maxlength="15" id="ContentPlaceHolder1_txtSearch" class="autosearch" autocomplete="on" onkeypress="return IsAlphaNumeric(event);" />
                        <input type="submit" name="ctl00$ContentPlaceHolder1$btnSearch" value="" id="ContentPlaceHolder1_btnSearch" class="searchSubmit" />
                        
                    </div>

                    <div id="rptDiv">
                        <div class="headVehicle">
                            <h4>ALL VEHICLES</h4>
                            <span class="allVeh">
                                <div id="totalCount" onload="pageLoad()"></div>
                            </span>
                        </div>
                        <table class="headLocation">
                            <tr>
                                <th class="headTop1">Vehicle Reg No</th>
                                <th class="headTop2">Vehicle Type </th>
                                <th class="headTop3">Vehicle Address</th>
                                <th class="headTop4">Vehicle Status</th>
                              
                                <th class="headTop5">Running Hours</th>
                                <th class="headTop6">Cumulative Engine Hours</th>
                                
                                <th class="headTop7">Fuel Efficiency TripA</th>                                
                                <th class="headTop8">Fuel Efficiency TripB</th>
                                
                            </tr>
                        </table>
                        <div id="divmaster" style="height:482px;width:100%;overflow:scroll;"">
                        <div id="ContentPlaceHolder1_Updatepanel1">
	
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$hdfToogleStatus" id="ContentPlaceHolder1_hdfToogleStatus" value="2" />
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$hfZoomLevelLSLanding" id="ContentPlaceHolder1_hfZoomLevelLSLanding" value="10" />
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$hfLatLngString" id="ContentPlaceHolder1_hfLatLngString" value="19.8424216666667,83.4482661111111#19.8388486111111,83.4520733333333#18.7860258333333,83.4278211111111#" />
                                <input type="hidden" name="ctl00$ContentPlaceHolder1$hfVehDetailsString" id="ContentPlaceHolder1_hfVehDetailsString" value="DH 01 H 9368|0|01-12-2017 15:13:49||2|MTBD|Stopped|0|02h:18m:00s|1|Non Tipper|360^DH 01 H 9366|0|01-12-2017 15:02:52||3|MTBD|Idle|0|03h:23m:00s|1|Non Tipper|360^DH 01 H 9493|0|01-12-2017 14:53:30||2|MTBD|Stopped|0|00h:00m:00s|1|Non Tipper|360^" />
                                <div id="rptDiv1">
                                    <div class="tableCount">

                                        

                                         
                                                <table id="tblVehicleList" style="width: 250px; margin-top: 5px; z-index: 0; border-bottom: 1px solid #e1e2e5;" class="menuoff" onmouseover="className='menuon';" onmouseout="className='menuoff';">
                                                    <tr>
                                                        <td>
                                                              <a id="ContentPlaceHolder1_rptControl_LinkButton1_0" class="lnkbtnCss1" onmouseout="return callout();" onmouseover="callhighlightMarker(19.8424216666667,83.4482661111111,0,2,360 );" href="javascript:__doPostBack(&#39;ctl00$ContentPlaceHolder1$rptControl$ctl00$LinkButton1&#39;,&#39;&#39;)"><div class='vehList gridViewToolTip'>DH 01 H 9368</div><div id='tooltip' style='display: none;'><div >MA1PHAPHDH6H49368</div></div><div  class='vehType'>Non Tipper</div><div  class='vehAddress'> </div><div  class='alertImg'><span class='StatusName'>Stopped</span><div class='red'><span class='circle'></span></div></div><div  class='VehicleHours'> 02h:18m:00s</div><div  class='CumVehicleHours'></div><div id='tooltip' style='display: none;'><div >121h:00m:00s</div></div><div  class='FuelEfficency'> 0 KMPL</div><div  class='UreaUsage'> 0 KMPL</div><div id='lat'  class='latitude'>19.8424216666667</div><div  class='longitude'>83.4482661111111</div><div  class='GpsHeading'>360</div></a>
                                                            
                                                              
                                                           
                                                                 <div class='CumVehicleHoursvalue' style="display:none;width: 3px;">121h:00m:00s</div> 
                                                        </td>
                                                    </tr>

                                                </table>
                                            
                                                <table id="tblVehicleList" style="width: 250px; margin-top: 5px; z-index: 0; border-bottom: 1px solid #e1e2e5;" class="menuoff" onmouseover="className='menuon';" onmouseout="className='menuoff';">
                                                    <tr>
                                                        <td>
                                                              <a id="ContentPlaceHolder1_rptControl_LinkButton1_1" class="lnkbtnCss1" onmouseout="return callout();" onmouseover="callhighlightMarker(19.8388486111111,83.4520733333333,0,3,360 );" href="javascript:__doPostBack(&#39;ctl00$ContentPlaceHolder1$rptControl$ctl01$LinkButton1&#39;,&#39;&#39;)"><div class='vehList gridViewToolTip'>DH 01 H 9366</div><div id='tooltip' style='display: none;'><div >MA1PHAPHDH6H49366</div></div><div  class='vehType'>Non Tipper</div><div  class='vehAddress'> </div><div  class='alertImg'><span class='StatusName'>Idle</span><div class='yellow'><span class='circle'></span></div></div><div  class='VehicleHours'> 03h:23m:00s</div><div  class='CumVehicleHours'></div><div id='tooltip' style='display: none;'><div >128h:00m:00s</div></div><div  class='FuelEfficency'> 0 KMPL</div><div  class='UreaUsage'> 0 KMPL</div><div id='lat'  class='latitude'>19.8388486111111</div><div  class='longitude'>83.4520733333333</div><div  class='GpsHeading'>360</div></a>
                                                            
                                                              
                                                           
                                                                 <div class='CumVehicleHoursvalue' style="display:none;width: 3px;">128h:00m:00s</div> 
                                                        </td>
                                                    </tr>

                                                </table>
                                            
                                                <table id="tblVehicleList" style="width: 250px; margin-top: 5px; z-index: 0; border-bottom: 1px solid #e1e2e5;" class="menuoff" onmouseover="className='menuon';" onmouseout="className='menuoff';">
                                                    <tr>
                                                        <td>
                                                              <a id="ContentPlaceHolder1_rptControl_LinkButton1_2" class="lnkbtnCss1" onmouseout="return callout();" onmouseover="callhighlightMarker(18.7860258333333,83.4278211111111,0,2,360 );" href="javascript:__doPostBack(&#39;ctl00$ContentPlaceHolder1$rptControl$ctl02$LinkButton1&#39;,&#39;&#39;)"><div class='vehList gridViewToolTip'>DH 01 H 9493</div><div id='tooltip' style='display: none;'><div >MA1PHAPHDH6H49493</div></div><div  class='vehType'>Non Tipper</div><div  class='vehAddress'> </div><div  class='alertImg'><span class='StatusName'>Stopped</span><div class='red'><span class='circle'></span></div></div><div  class='VehicleHours'> 00h:00m:00s</div><div  class='CumVehicleHours'></div><div id='tooltip' style='display: none;'><div >00h:00m:00s</div></div><div  class='FuelEfficency'> 0 KMPL</div><div  class='UreaUsage'> 0 KMPL</div><div id='lat'  class='latitude'>18.7860258333333</div><div  class='longitude'>83.4278211111111</div><div  class='GpsHeading'>360</div></a>
                                                            
                                                              
                                                           
                                                                 <div class='CumVehicleHoursvalue' style="display:none;width: 3px;">00h:00m:00s</div> 
                                                        </td>
                                                    </tr>

                                                </table>
                                            
                                       
                                       
                                    </div>
                                </div>
                                </div>
                            
</div>
                         </div>
                        <div id="ContentPlaceHolder1_Panel1">

</div>
                        <span id="ContentPlaceHolder1_lblErr"></span>
                    </div>

                    <span class="centerLine">
                        <div class="triggerSide">
                            <a href="#" id="trigger" class="left_arrow">
                                <span class="tabArrow"></span>
                                <span class="tabArrow1" style="display: none;"></span>

                            </a>

                        </div>
                    </span>
                    <div id='activity'>
                        <div id="ContentPlaceHolder1_UpdatepanelMap">
	
                                <div id="map_canvas" style="height: 500px; padding: 0;overflow:hidden;"></div>
                            
</div>
                        <div class="color_exp">
                            
                            <div class="green">
                                <span class="circle"></span>
                                <h5>Running</h5>
                            </div>
                            <div class="red">
                                <span class="circle"></span>
                                <h5>Stopped</h5>
                            </div>
                            <div class="blue">
                                <span class="circle"></span>
                                <h5>Not Used</h5>
                            </div>
                            <div class="yellow">
                                <span class="circle"></span>
                                <h5>Idle</h5>
                            </div>
                            <div class="grey">
                                <span class="circle"></span>
                                <h5>Unknown</h5>
                            </div>
                            <div class="highPriority">                               
                                <h5>High Priority Alert</h5>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <div id="loader" style="margin: 0px; padding: 0px; position: fixed; right: 0px; top: 0px; width: 100%; height: 100%; background-color: #666666; z-index: 30001; opacity: .8; filter: alpha(opacity=70); display: none">
            <p style="position: absolute; top: 30%; left: 45%; color: White;">
                Loading, please wait...<img src="Images/waitCursor.GIF" border="0" />
            </p>
        </div>

    </div>

            </div>

            <footer class="footer_menu">
                <div class="MasterFooter">
                    Copyright &copy; 2016 Mahindra & Mahindra. All rights reserved
                </div>
                <div class="versionFoot">Release 1.1</div>
                <div class="versionMsg">The Application is Best Viewed in Chrome, Firefox and IE version 10 and 11</div>
            </footer>
        </div>
    
<script type='text/javascript'>loadDefaultmap(' 10 ');</script><script type='text/javascript'>loadMultipleMarkers('19.8424216666667,83.4482661111111#19.8388486111111,83.4520733333333#18.7860258333333,83.4278211111111#','DH 01 H 9368|0|01-12-2017 15:13:49||2|MTBD|Stopped|0|02h:18m:00s|1|Non Tipper|360^DH 01 H 9366|0|01-12-2017 15:02:52||3|MTBD|Idle|0|03h:23m:00s|1|Non Tipper|360^DH 01 H 9493|0|01-12-2017 14:53:30||2|MTBD|Stopped|0|00h:00m:00s|1|Non Tipper|360^','4');</script><script type='text/javascript'>InitializeToolTip();</script><script type='text/javascript'>CreateDynamicjsonMenu('[{"MenuID":"1","DisplayText":"Home","ClassName":"Home_Class","NavigationURL":"Home.aspx","SubMenu":[]},{"MenuID":"8","DisplayText":"Registration","ClassName":"Registration_Class","NavigationURL":"","SubMenu":[{"MenuID":"25","DisplayText":"Driver ","ClassName":"RegisterUser_Class","NavigationURL":"RegisterDriver.aspx","SubMenu":[]}]},{"MenuID":"11","DisplayText":"Services","ClassName":"Services_Class","NavigationURL":"","SubMenu":[{"MenuID":"15","DisplayText":"Reports","ClassName":"Reports_Class","NavigationURL":"ReportDashboardFrontPage.aspx","SubMenu":[]},{"MenuID":"22","DisplayText":"Geofence","ClassName":"GeofencePage_Class","NavigationURL":"GeofencePage.aspx","SubMenu":[]},{"MenuID":"23","DisplayText":"Location Services","ClassName":"LocationServices_Class","NavigationURL":"LocationServices.aspx","SubMenu":[]}]},{"MenuID":"16","DisplayText":"Feedback","ClassName":"Feedback_Class","NavigationURL":"Feedback.aspx","SubMenu":[]}]');</script><script type='text/javascript'>SetAlertBtnVisibility('2');</script>
<script type="text/javascript">
//<![CDATA[
(function() {var fn = function() {$get("toolkitScriptManager1_HiddenField").value = '';Sys.Application.remove_init(fn);};Sys.Application.add_init(fn);})();Sys.Application.add_init(function() {
    $create(Sys.UI._Timer, {"enabled":true,"interval":60000,"uniqueID":"ctl00$ContentPlaceHolder1$timerLandingPage"}, null, null, $get("ContentPlaceHolder1_timerLandingPage"));
});
Sys.Application.add_init(function() {
    $create(Sys.Extended.UI.AutoCompleteBehavior, {"completionListCssClass":"autoFillsearch","completionSetCount":1,"delimiterCharacters":"","enableCaching":false,"id":"ContentPlaceHolder1_txtName_AutoCompleteExtender","minimumPrefixLength":1,"serviceMethod":"GetNames","servicePath":"LocationServices.aspx","useContextKey":true}, {"itemSelected":ItemSelected}, null, $get("ContentPlaceHolder1_txtSearch"));
});
//]]>
</script>
</form>
</body>
</html>
"""