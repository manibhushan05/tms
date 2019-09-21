html_response="""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head id="Head1"><title>
	GPS TRACKING
</title><meta http-equiv="content-type" content="text/html; charset=UTF-8" /><meta http-equiv="CACHE-CONTROL" content="NO-CACHE" /><meta http-equiv="EXPIRES" content="0" />
    <!-- ---CSS ------ -->
    <link rel="stylesheet" href="css/MainSite.css" type="text/css" media="screen" /><link rel="stylesheet" href="css/menu.css" type="text/css" media="screen" /><link rel="stylesheet" href="css/sticky.css" type="text/css" media="screen" /><link rel="stylesheet" href="css/jquery-ui.css" type="text/css" media="screen" /><link rel="stylesheet" href="css/basic.css" type="text/css" media="screen" /><link rel="stylesheet" href="css/jquery.dataTables.min.css" type="text/css" media="screen" />

    <!-- IE6 "fix" for the close png image -->
    <!--[if lt IE 7]>
<link type="text/css" href="css/basic_ie.css" rel="stylesheet" media="screen" />
<![endif]-->

    <!-- ---End  Site------ -->
    <style type="text/css">
        .bgcolor {
            background-color: blue;
        }


        body {
            margin: 0px;
            padding: 0px;
            margin-top: 5px;
            overflow-y: hidden;
            min-width: 1020px;
            background: #FFF url(images/bg_body_default.gif) repeat-x top left;
            /*  overflow: hidden;  */
        }

        #pnlLeft {
            overflow: auto;
            float: left;
            margin-right: 3px;
            pading-left: 2px;
            border-right: solid 1px #BDBDBD;
        }

        #pnlRight {
            overflow: auto;
            position: relative;
        }

        .labels {
            color: #000;
            background-color: white;
            font-family: "Arial";
            font-size: 12px;
            border: 1px solid gray;
            white-space: nowrap;
        }

        #mapAngle {
            position: absolute;
            bottom: 20px;
            left: 10px;
            z-index: 99;
        }

        #divMapLatLngt {
            bottom: 0px;
            position: absolute;
            margin-left: 80px;
            padding: 2px;
            z-index: 99;
            background-color: rgba(255,255,255, 0.8);
        }

        .custom-combobox {
            position: relative;
            display: inline-block;
        }

        .custom-combobox-toggle {
            position: absolute;
            top: 0;
            bottom: 0;
            margin-left: -1px;
            padding: 0;
            /* support: IE7 */
            *height: 1.7em;
            *top: 0.1em;
        }

        .custom-combobox-input {
            margin: 0;
            padding: 0.3em;
        }

        .ui-widget-content.ui-dialog {
            border: 2px solid brown;
        }

        /* Increase calendar container z index so it will not ovarlap by combobox */
        .ajax__calendar_container {
            z-index: 1000;
        }
        /* ========================= */

        #tblData a {
            text-decoration: none;
            cursor: pointer;
        }

        #tblData thead input {
            width: 100%;
            padding: 5px;
            box-sizing: border-box;
            color: #FFFFFF;
        }

        #tblData thead a {
            text-decoration: none;
            cursor: pointer;
            color: #FFFFFF;
        }

        .onleave td {
            background-color: orange !important;
        }

        .onnightshift td {
            background-color: #8FD8D8 !important;
        }
    </style>
<link href="/WebResource.axd?d=cARzYWS-DQWlHldiRP6h-pjJVekIdpY30GjD4A19DNLdHZ_ITVAbH8bJDr0L0sBANZORIS1_hvUSYBM3GXuWXAZEyVxSwlUVuSqJwJLSzbwnfg5lPFIyuov2_9pLBWitYLBg7GDfwUIWYlH8tzyAlmL_TMzhSkgvgbDmSjOQLSw1&amp;t=636165667728096102" type="text/css" rel="stylesheet" /><link href="/WebResource.axd?d=gHd2GQPhjEPW5Hob4WCXQo4whM9SINkmlDagu5Py-nTuzEft7SHjuIg3KpZA_7EWgzkAHfyHuWMkpb3RK24EZS_On_fXvmuSUrVokK7fmANznyAIlebFtgTMzsTeEVhoYGoIRuoT3HPYXb13-ljh21NxB3hjMnLawc9bF8WDt0g1&amp;t=636165667728096102" type="text/css" rel="stylesheet" /></head>

<body>
    <div id="divToolTip" class="tooltip"></div>

    <!-- -------------------------------- -->
    <form method="post" action="./newHome.aspx" id="Form1">
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKLTU2Njc3ODcwMw9kFgICAw9kFkICBQ8PFgQeCEltYWdlVXJsBSt+L2ltYWdlcy9Qcm92aWRlcl9Mb2dvL3dheSB0cmFja2VyIF8yMTIucG5nHgdWaXNpYmxlZ2RkAgYPFgQeBGhyZWYFNmphdmFzY3JpcHQ6c2hvd01vZGFsRGlhbG9nKCdjb21wYW55dmVodHlwZXMuYXNweCcsJycpOx8BZ2QCBw8PFgIeBFRleHQFEiAgV2VsY29tZSBwcmlob20gIGRkAgkPFgIfA2VkAhEPFgIfAWdkAhIPEA8WAh8BaBYCHghvbmNoYW5nZQUQRmlsdGVyVmVoaWNsZXMoKRAVAhFBbnkgVmVoaWNsZXMgVHlwZQdWZWhpY2xlFQIAAVYUKwMCZ2cWAWZkAhMPEA9kFgIfBAUQRmlsdGVyVmVoaWNsZXMoKQ8WBWYCAQICAgMCBBYFEAUDQW55ZWcQBQZNb3ZpbmcFAVJnEAUIU3RvcHBhZ2UFAVNnEAUJT3ZlcnNwZWVkBQFPZxAFC1VucmVhY2hhYmxlBQFVZ2RkAhUPZBYCZg9kFggCBQ9kFgICAQ8QZGQWAGQCCQ8PZBYCHgVzdHlsZQUNZGlzcGxheTpub25lO2QCDw8WAh4JaW5uZXJodG1sBZICMjxpbWcgc3JjPSdpbWFnZXMvb24uZ2lmJyBhbGlnbj0nYWJzbWlkZGxlJyBib3JkZXI9MCB0aXRsZT0nTW92aW5nJyAvPiZuYnNwOyZuYnNwOzc8aW1nIHNyYz0naW1hZ2VzL29mZi5naWYnIGFsaWduPSdhYnNtaWRkbGUnIGJvcmRlcj0wIHRpdGxlPSdJZGxlJyAvPiZuYnNwOyZuYnNwOzI8aW1nIHNyYz0naW1hZ2VzL05vdFJwdC5naWYnIGFsaWduPSdhYnNtaWRkbGUnIGJvcmRlcj0wIHRpdGxlPSdVbnJlYWNoYWJsZScgLz4mbmJzcDsmbmJzcDsgPHNwYW4+ID0gMTEgPC9zcGFuPmQCEQ8WAh8GBZoPeyJkdCI6W3sibGEiOiIyMS4yNzYzMTMiLCJsbiI6IjgxLjU5NTAzNSIsInZpZCI6IjQiLCJ2biI6IkNHLTA0LUxXLTk0NDgiLCJ2YyI6IiNGRkU3NjYiLCJhbiI6IjQ4IiwiaWMiOiIyIiwiZ2lkIjoiMyIsInZzIjpudWxsLCJubCI6IkphcndheSBBbGlhcyBIaXJhcHVyLVJhaXB1ci1DaGhhdHRpc2dhcmgoMS4wMiBLTSkifSx7ImxhIjoiMjEuMzc4OTc1IiwibG4iOiI4MS42NDU3OTgiLCJ2aWQiOiI1Iiwidm4iOiJDRy0wNC1MWC0wNDQ3IiwidmMiOiJwYWxlZ3JlZW4iLCJhbiI6IjI4NSIsImljIjoiMiIsImdpZCI6IjMiLCJ2cyI6bnVsbCwibmwiOiJVbm5hbWVkIFJvYWQtTXVucmV0aGktMi1SYWlwdXItQ2hoYXR0aXNnYXJoLUluZGlhIn0seyJsYSI6IjIyLjg0NTg4OCIsImxuIjoiODIuMzc3Mzk1IiwidmlkIjoiNiIsInZuIjoiQ0ctMDQtTFctOTQ1MSIsInZjIjoiI0ZGRTc2NiIsImFuIjoiMjMyIiwiaWMiOiIyIiwiZ2lkIjoiMyIsInZzIjpudWxsLCJubCI6IkpoaW5wdXJpLUtvcmJhLUNoaGF0dGlzZ2FyaCgxMS4yNiBLTSkifSx7ImxhIjoiMjQuNzgwNjMiLCJsbiI6Ijg0LjM0OTgyNSIsInZpZCI6IjciLCJ2biI6IkNHLTA0LUxYLTI5MTgiLCJ2YyI6InJlZCIsImFuIjoiMTM0IiwiaWMiOiIyIiwiZ2lkIjoiMyIsInZzIjpudWxsLCJubCI6Ik1hbmp1cmFoaS1BdXJhbmdhYmFkLUJpaGFyKDAuNjEgS00pIn0seyJsYSI6IjIyLjg0NjE0MyIsImxuIjoiODIuMzc2NjEiLCJ2aWQiOiI4Iiwidm4iOiJDRy0wNC1MWC0yOTE2IiwidmMiOiIjRkZFNzY2IiwiYW4iOiIzNDAiLCJpYyI6IjIiLCJnaWQiOiIzIiwidnMiOm51bGwsIm5sIjoiSmhpbnB1cmktS29yYmEtQ2hoYXR0aXNnYXJoKDExLjMyIEtNKSJ9LHsibGEiOiIyMS4zMTcyMzMiLCJsbiI6IjgxLjU2MDI5IiwidmlkIjoiOSIsInZuIjoiQ0ctMDQtTFgtMDQ0NiIsInZjIjoiI0ZGRTc2NiIsImFuIjoiMjI3IiwiaWMiOiIyIiwiZ2lkIjoiMyIsInZzIjpudWxsLCJubCI6IkJhbmEtMi1SYWlwdXItQ2hoYXR0aXNnYXJoKDEuMDggS00pIn0seyJsYSI6IjIxLjMxNzUxIiwibG4iOiI4MS41NjAxMzUiLCJ2aWQiOiIxMCIsInZuIjoiQ0ctMDQtTFctOTQ1MiIsInZjIjoiI0ZGRTc2NiIsImFuIjoiMjg1IiwiaWMiOiIyIiwiZ2lkIjoiMyIsInZzIjpudWxsLCJubCI6IkJhbmEtMi1SYWlwdXItQ2hoYXR0aXNnYXJoKDEuMDcgS00pIn0seyJsYSI6IjIzLjM3Mzc3NyIsImxuIjoiODIuODIyODk0IiwidmlkIjoiMiIsInZuIjoiQ0ctMDQtSkQtNDc4OSIsInZjIjoiI0ZGRTc2NiIsImFuIjoiMjQzIiwiaWMiOiIyIiwiZ2lkIjoiMSIsInZzIjpudWxsLCJubCI6IlNpcmFpLVN1cmd1amEtQ2hoYXR0aXNnYXJoKDQuMTUgS00pIn0seyJsYSI6IjIxLjI2MzQ5NyIsImxuIjoiODEuNTY4ODk3IiwidmlkIjoiMSIsInZuIjoiQ0ctMDQtSkQtNDg4OSIsInZjIjoicmVkIiwiYW4iOiIyOTciLCJpYyI6IjIiLCJnaWQiOiIxIiwidnMiOm51bGwsIm5sIjoiUmluZyBSb2FkLU5hbmRhbnZhbiBSb2FkLVRyYW5zcG9ydCBOYWdhci1SYWlwdXItUmFpcHVyLUNoaGF0dGlzZ2FyaC1JbmRpYSJ9LHsibGEiOiIyMy42MjAzMDEiLCJsbiI6IjgzLjYyNjQ2OSIsInZpZCI6IjMiLCJ2biI6IkNHLTA0LUpELTgxODkiLCJ2YyI6InBhbGVncmVlbiIsImFuIjoiMTcyIiwiaWMiOiIyIiwiZ2lkIjoiMSIsInZzIjpudWxsLCJubCI6Ik5hdGlvbmFsIEhpZ2h3YXkgMzQzLUJhbHJhbXB1ci1TdXJndWphLUNoaGF0dGlzZ2FyaC1JbmRpYSJ9LHsibGEiOiIyMS4yNTU4MTEiLCJsbiI6IjgxLjU3MDA1IiwidmlkIjoiMCIsInZuIjoiQ0ctMDQtSkQtODI4OSIsInZjIjoiI0ZGRTc2NiIsImFuIjoiMCIsImljIjoiMiIsImdpZCI6IjEiLCJ2cyI6bnVsbCwibmwiOiJOYXRpb25hbCBIaWdod2F5IDYtVHJhbnNwb3J0IE5hZ2FyLVRhdGliYW5kaC1SYWlwdXItUmFpcHVyLUNoaGF0dGlzZ2FyaC1JbmRpYSJ9XX1kAhgPFgIfAWcWAgIBD2QWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFBG5hbWUeDkRhdGFWYWx1ZUZpZWxkBQhncm91cF9pZB4LXyFEYXRhQm91bmRnFgIfBAUPRmlsbFZlaGljbGVzKCk7EBUDDFNlbGVjdCBHcm91cA9Qcml5YSBUcmFuc3BvcnQFTkVXQUsVAwEwATEBMxQrAwNnZ2dkZAIZDxAPFgYfBwULc2Vuc29yX25hbWUfCAUJc2Vuc29yX2lkHwlnZBAVAwhJZ25pdGlvbgdCYXR0YXJ5BUVuZ2luFQMCMTECMTICMTMUKwMDZ2dnZGQCGg8QDxYGHwcFC3NlbnNvcl9uYW1lHwgFCXNlbnNvcl9pZB8JZ2QQFQEERlVFTBUBAjIxFCsDAWdkZAIbDxAPFgYfBwULc2Vuc29yX25hbWUfCAUJc2Vuc29yX2lkHwlnZBAVAQtCYXR0LiBWb2x0LhUBAjMxFCsDAWdkZAIfDw8WAh4JTWF4TGVuZ3RoZmRkAiEPFhoeGUN1bHR1cmVEZWNpbWFsUGxhY2Vob2xkZXIFAS4eDklucHV0RGlyZWN0aW9uCymDAUFqYXhDb250cm9sVG9vbGtpdC5NYXNrZWRFZGl0SW5wdXREaXJlY3Rpb24sIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0xNi4xLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0yOGYwMWIwZTg0YjZkNTNlAB4LQ3VsdHVyZU5hbWUFBWVuLUdCHhZDdWx0dXJlVGltZVBsYWNlaG9sZGVyBQE6HgpBY2NlcHRBbVBtaB4bQ3VsdHVyZVRob3VzYW5kc1BsYWNlaG9sZGVyBQEsHhZDdWx0dXJlQU1QTVBsYWNlaG9sZGVyBQVBTTtQTR4OQWNjZXB0TmVnYXRpdmULKX9BamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdFNob3dTeW1ib2wsIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0xNi4xLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0yOGYwMWIwZTg0YjZkNTNlAB4MRGlzcGxheU1vbmV5CysFAB4TT3ZlcnJpZGVQYWdlQ3VsdHVyZWgeFkN1bHR1cmVEYXRlUGxhY2Vob2xkZXIFAS8eEUN1bHR1cmVEYXRlRm9ybWF0BQNETVkeIEN1bHR1cmVDdXJyZW5jeVN5bWJvbFBsYWNlaG9sZGVyBQLCo2QCIg8PFgIfCmZkZAIjDxYYHwwLKwQAHxILKwUAHw4FATofFwUCwqMfFGgfDQUFZW4tR0IfEwsrBQAfEAUBLB8WBQNETVkfEQUFQU07UE0fFQUBLx8LBQEuZAIkDw8WAh8KZmRkAiYPFhofCwUBLh8MCysEAB8NBQVlbi1HQh8OBQE6Hw9oHxAFASwfEQUFQU07UE0fEgsrBQAfEwsrBQAfFGgfFQUBLx8WBQNETVkfFwUCwqNkAicPDxYCHwpmZGQCKA8WGB8MCysEAB8SCysFAB8OBQE6HxcFAsKjHxRoHw0FBWVuLUdCHxMLKwUAHxAFASwfFgUDRE1ZHxEFBUFNO1BNHxUFAS8fCwUBLmQCLQ8WAh8BZ2QCLg8PFgQfAwUISWduaXRpb24fAWdkZAIvDxYCHwFnZAIwDw8WBB8DBQdCYXR0YXJ5HwFnZGQCMQ8WAh8BZ2QCMg8PFgQfAwUFRW5naW4fAWdkZAI5DxYCHwFnZAI6Dw8WBB8DBQRGVUVMHwFnZGQCPQ8WAh8BZ2QCPg8PFgQfAwULQmF0dC4gVm9sdC4fAWdkZAJAD2QWAmYPZBYEAgUPEGQPFgRmAgECAgIDFgQQBQlIb21lIFNpdGUFATFnEAULQ2xpZW50IFNpdGUFATJnEAUPUmVzdHJpY3RlZCBTaXRlBQEzZxAFCk90aGVyIFNpdGUFATRnZGQCDQ88KwARAwAPFgQfCWceC18hSXRlbUNvdW50ZmQBEBYAFgAWAAwUKwAAZAJBD2QWAmYPZBYCAhEPPCsAEQIBEBYAFgAWAAwUKwAAZAJCD2QWAmYPZBYEAgcPEGRkFgBkAhMPPCsAEQIBEBYAFgAWAAwUKwAAZBgEBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WBQUHY2JzZW4xMQUHY2JzZW4xMgUHY2JzZW4xMwUHY2JzZW4yMQUHY2JzZW4zMQUKZ3ZSb3V0ZVNtcw9nZAUIZ3ZSb3V0ZXMPZ2QFB2d2U2l0ZXMPPCsADAEIZmS+F7wiK3QR008uRKGBFZANIBL4aNRUIdxbcbWK0gkHjg==" />


<script src="/ScriptResource.axd?d=sGfFBR2m1JzOLIGVDtP0PbmybL7dcYmUvf4-rvfqlMuT33dzChc8EvXUnbe1d6oXTRO88HK5K7nZCS0UXywhYw2-UdXP1SFQL224qE95UeYHk_n6dFkKgb_rgnd1DSRKITBa2_MeplTCRb3QyBqQjMidSWBwXnyYduDgv1wASJw1&amp;t=72e85ccd" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=OE5ppbLN5np9ftULK0seXMq0AuFchwHDPutjmOaZ2Bg0CUgPQ4Bgced9Zgn8O9jcyujcoVhsPUnQGXK6dCanNX4yleyKWjKmFekAWdvTlhyj_9qzw9MTnnX67uv1qot79oE4P0rk8m-LipOtEAQzZdxyFn2oK1lE5PwVAT5ven41&amp;t=72e85ccd" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=NMo-hmL2PyAKfzX6niwG7L_vx5sJbUfgtihVAAeANHZwbn5jyjuerOodDIjcKFkjYCylPOGv5HKRIiwDxT5v-ADyo6KCH8dPZBgu-986WBBbbPxUMENj83dD6MNRQN9aoPFLH-vfWiYwOmjlUO0_ZA2&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=_yDATiYMYwb4WOWpc6hmpOSDbJiQ6hbAnFlKEuXTPxBpSppbJo-mLrTAhxpUgyQFFljnpJTFsWpXbkspjbujT1Q1iGSlD5-eMNMxXfJgBVNsUmrZw2e_5pYsJ1gkX9-10&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=F-xuba0zZs7wOX_IzB7yy6byx15zB08ZPSuDuy5TvOHOXJpjm6mfTtUu7-5uQR_nd6Ci7LcEUCZdTAm32mDx7XwIsB3DAOcsGXRlz2AFw2WueenG_8l1knpVVQWD94Ye0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=KLobl_ceOXQ3chiAVfBM5t3JG7hT9obZ9SB1HqLnXsaamhwYuYYz9DKtq9f2JqOmlQQNAF6XwJ6HiSRAMgfcRTcXHjTrmRpXH51A6vk6eu-a3xqfDNmuOZa-xJnKJ-mj0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=h-BncPwi3TuPbob24MzYxoYzTnl3jp5Pyh9Wjfp-Zrota-SI4JooVPb_404BU5HER2S1QbVhy2kAlXDUb7jzq_JmoYVyAB0MUeaxxkxYupQ7CeLBbImNIEg4gwr0SLbM0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=rP-SIcLgnty-XS69C2rEoFLTs6NsIemzmnYZ7pbnD64-B4XKdHKxjIdSeHREeLimoB6og4VusFIfT8vOnX26LM4VJ5n24JY46QJbq5AEeKHdwSaCF6HpBHRqAIH4x8fQP_U-1hG2olVJNTlD2lPj5A2&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=Cd5MLMIoia7C-5GhaLYNS3sTvHAJ1LEwJiFFBExGTQlU5KUhEidJURa0cG502ePQ3V8iFWOlWSmuNUbmjUe5HMeC81XoO2stIW6aLm83zV5OpBHGOKFhQwox3nHckREZ0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=IyImPgu3xaPUCMkAM5ImLI4TkO6ZqFxqDaAcj-BwvVNCmS11EstkmCb6uwJfdonaAy0f1dD3ZCbQbO-EiRe9drUBQxLLyiPEFlOb5pTZr2J7noqH5pUD65apgUoH2iX10&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=QY9QQe9DfUPdnmzYWs5_6g7ISXh9lJIaBjOJfKav5Q6_7K1S7X0o-8m5FDb845mck-IW_lA3ctvPPptnvbri_1qCytH8XrQAEmf5TxtP7kOGTozO2vmI19PPQtSvKCmH0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=PbG0NCF_0_m59JNYp57NHAC_vovZN_tWbZ-JjvsR3Qp2pAu_U8AV_rL6kkyTVmUe2eo3FE0EWTfm5v_4o2eBPbxa-7pKvqpn2cEXbngx-wb5scNSaBiZvrzC4B_7j3l-X6PP2BfhuoH5Z_TY7QL3LQ2&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=8hViVUhbSMGSu7VD6ZDcmd-RVF1WjFVLVCkIqHQ7lTmYiG627pMduQZneZwU1u_88gPA1waqpoRjzy9ScOm4C-kNv5VUFTqLNnlYbaAyE3ng25Ze45X2OczIco9EYpUT0&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=xxDUhHsDaNAkfZKPAIYd6oFsBLad7vBFJr9jPLyAVRGGk3SFXFQSmdXacS_pyQzFFois-9oQONqJ99O_jRGhpPFKCUW7MikfAmwYM2V5cT8PuH_aD83ICX1A8FZF83enIzhUvugz6iEKtkTN5er9eg2&amp;t=76554e0d" type="text/javascript"></script>
<script src="/ScriptResource.axd?d=PttqugBhNDPW_sv9FOCUHOJ7TzGjhReI-xpirT1JxjH1mOjrj-PWl6rk68-pLqbdbG885R4s29-3acT8ZGUbRsPeRIvmSRnWxJINm8s-4YFjOwDPvx-K6TIbr9Y1bv3g0&amp;t=76554e0d" type="text/javascript"></script>
<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="6A593159" />
        
        <input type="hidden" name="hfSpecialMenu" id="hfSpecialMenu" value=",,stoppage,,tstime,,tsloc,,tssite,,overspeed," />
        <input type="hidden" name="hfSpec" id="hfSpec" value="1" />
        <input type="hidden" name="hfSites" id="hfSites" value="1" />
        <input type="hidden" name="hfRouteMap" id="hfRouteMap" value="1" />

        <div id="wrapper">
            <table id="container" width="100%">
                <tr>
                    <td id="tdheader">
                        <div style="float: left; height: 60px; padding-top: 10px;">
                            <img id="imgLogo" class="toplogo" src="images/Provider_Logo/way%20tracker%20_212.png" />
                        </div>
                        <div style="float: right; width: auto;">
                            <div style="margin: 10px; text-transform: capitalize;" align="right">
                                <a href="javascript:showModalDialog('companyvehtypes.aspx','');" id="lnkCompanyVehTypes" style="font-size: 12px; font-weight: bold; color: darkblue; text-decoration: none">
                                    <span id="Span1">Update Vehicle types for Better performance </span>
                                </a>
                                &nbsp;&nbsp;&nbsp;&nbsp;                            
                            
                              
                                &nbsp;&nbsp; 
                                <span id="lblUserName"><b>  Welcome prihom  </b></span>&nbsp; | &nbsp;
                                <a href="logout.aspx"><b>Logout </b></a>
                            </div>
                            <div id="divPrintMenu" style="display: none;" align="right">
                                <table border="0" style="border-color: #FFFFFF;">
                                    <tr>
                                        <td style="word-wrap: break-word; max-width: 350px;">
                                            
                                        </td>
                                        <td id="divVehStatus"></td>
                                        <td>
                                            <div class="btn_pdf">
                                                <input type="button" value="Pdf" class="button_pep" onclick="PrintPdf('','',1,hdnrptName.value);" />
                                            </div>

                                            <div style="margin-left: 5px;" class="btn_excel">
                                                <input type="button" value="Excel" class="button_pep" onclick="PrintExcel('', '', 1,hdnrptName.value);" />
                                            </div>

                                            <div style="margin-left: 5px;" class="btn_print">
                                                <input type="button" value="Print" class="button_pep" onclick="return CallPrint('','images/Provider_Logo/way tracker _212.png    ');" />
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td align="left" id="tdmenu">
                        <table cellpadding="0" cellspacing="0" border="0" width="100%">
                            <tr>
                                <td width="65%">
                                    <div id="divMenu" class="ddsmoothmenu">
                                        <ul>
                                            <li><a href="javascript:showHome();">Home</a></li>
                                            <li><a href='#'>Sensors</a><ul><li><a href="javascript:showReport('sensor','ignition');">Sensor Status Report</a></li><li><a href="javascript:showReport('unauthsensor');">Unauthorized Sensor Usage</a></li><li><a href="javascript:showReport('acrun');">Sensor Usage Analysis</a></li><li><a href="javascript:showReport('tssen');">Trip Summary(Sensor)</a></li><li><a href="javascript:showReport('fleetsensorsummary');">Fleet Sensor Summary</a></li><li><a href="javascript:showReport('workinghours');">Working Hours Report</a></li></ul></li><li><a href='#'>Reports</a><ul><li><a href="javascript:showReport('eventlog');">Event Log</a></li><li><a href='#'>Basic Reports</a><ul><li><a href="javascript:showReport('stoppage');">Stoppage</a></li><li><a href="javascript:showReport('overspeed');">Overspeed</a></li></ul></li><li><a href='#'>Trip Summaries</a><ul><li><a href="javascript:showReport('tssite');">Trip Summary(Site)</a></li><li><a href="javascript:showReport('tsloc');">Trip Summary(Location)</a></li><li><a href="javascript:showReport('tstime');">Trip Summary(Time)</a></li><li><a href="javascript:showReport('prdsummary');">Period Summary</a></li><li><a href="javascript:showReport('ntssite');">New Trip Summary(Site)</a></li></ul></li><li><a href='#'>Site Visits</a><ul><li><a href="javascript:showReport('vehsitevisited');">Vehicle Site Visited</a></li><li><a href="javascript:showReport('vehsitenotvisited');">Vehicle Site Not Visited</a></li></ul></li><li><a href='#'>Performance Reports</a><ul><li><a href="javascript:showWindow('newreports.aspx?flag=vp');">Vehicle Performance</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=kmsummary');">KMS Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=fdwkmsum');">Fleet Day Wise Kms Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=ksdw');">Month Wise Kms Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=fdwsum');">Fleet Day Wise KMS Summary with Location</a></li></ul></li><li><a href='#'>Other Reports</a><ul><li><a href="javascript:showReport('locality');">Locality</a></li><li><a title='maintenancereport.aspx' class='basic' href='#'>Maintenance Report</a></li><li><a title='vehtmpreport.aspx' class='basic' href='#'>Vehicle Report For Uploaded Data</a></li></ul></li><li><a href='#'>Movement Reports</a><ul><li><a href="javascript:showWindow('newreports.aspx?flag=vehtriprpt');">Vehicle Trip Report</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=detdailyutil');">Detail Daily Utilisation</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=vehlogrpt');">Vehicle Log Report</a></li></ul></li><li><a href='#'>MIS Report</a><ul><li><a href="javascript:showReport('customerdailysummary');">Daily Summary</a></li></ul></li><li><a href='#'>Consignment Reports</a><ul><li><a href="javascript:showWindow('newreports.aspx?flag=sitevehcnt');">Site Vehicle Count</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=arrprojection');">Arrival Projection</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=totsiteentry');">Total Site Entry</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=vehsitevst');">Vehicles Site Visits</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=consignts');">Consignment Trip Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=ldtripsum');">Load Trip Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=fltutil');">Fleet Utilisation</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=consgnidlerpt');">Fleet Idling Report</a></li><li><a href="javascript:showReport('fltsummary');">Fleet Summary</a></li><li><a href="javascript:showWindow('newreports.aspx?flag=ldtimerpt');">Loading Time Report</a></li><li><a href="javascript:showReport('fltsummary1');">New Fleet Summary</a></li><li><a href="javascript:showReport('tripsummaryworkshop');">Trip Summary Work Shop</a></li></ul></li></ul></li><li><a href='#'>Map</a><ul><li><a href="javascript:showReport('routemap');">Route Mapper</a></li><li><a href="javascript:showReport('sites');">Site Details</a></li><li><a href="javascript:showReport('historytrack');">History Tracking</a></li></ul></li><li><a href='#'>Fuel</a><ul><li><a href="javascript:showReport('fuelfill');">Fuel Fill</a></li><li><a href="javascript:showReport('fuelremoval');">Fuel Removal</a></li><li><a title='Fuelodograph.aspx' class='basic' href='#'>Fuel Distance Graph</a></li><li><a title='Fueltimegraph.aspx' class='basic' href='#'>Fuel Time Graph</a></li><li><a title='fuelreport.aspx' class='basic' href='#'>Fuel Report</a></li></ul></li><li><a href='#'>Routes</a><ul><li><a title='Addroutetable.aspx' class='basic' href='#'>Add Route</a></li><li><a href="javascript:showReport('routeprogress');">Route Progress 2</a></li><li><a href="javascript:showReport('routes');">Route List</a></li><li><a title='addroute.aspx?flag=restroutes' class='basic' href='#'>Add Restricted Route</a></li><li><a title='Routeprogress.aspx' class='basic' href='#'>Route Progress</a></li></ul></li><li><a href='#'>Admin</a><ul></ul></li>
                                            
                                            <li>
                                                <div id="HelpIcon" style="border: solid 1px gray; background-color: #4C83F8; border-radius: 50%; cursor: pointer; width: 25px; margin-left: 10px; margin-top: 2px;"
                                                    title="Help Information"
                                                    onclick="showHelp('home_Vehicle');">
                                                    <span style="font-size: 20px; color: White; font-weight: bold; padding: 0px 7px 0px 7px;">
                                                        <i>i</i> </span>
                                                </div>
                                            </li>

                                        </ul>
                                    </div>
                                </td>
                                <td width="35%">
                                    <div align="right" style="margin-right: 10px;">
                                        <span id="divHome1">
                                            <img src="images/textView.png" alt="Text View" class="hoverPointer" onclick="javascript: showHideMap(0);" title="Text View" />
                                            &nbsp;&nbsp;
                                    <img src="images/mapView.png" alt="Text View" class="hoverPointer" onclick="javascript: showHideMap(1);" title="Map View" />
                                            &nbsp;&nbsp;&nbsp;
                                    <img src="images/bothView.png" alt="Text View" class="hoverPointer" onclick="javascript: showHideMap(-1);" title="Text & Map View" />
                                            &nbsp;&nbsp;                                                                                   
                                             
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            <div id="content">
                <div id="pnlLeft">
                    <div id="lblHeading" class="heading1" style="display: none">
                    </div>
                    <div id="divHome">
                        <input type="hidden" name="txtSensor1" id="txtSensor1" value="1" />
                        <input type="hidden" name="txtSensor2" id="txtSensor2" value="1" />
                        <div id="updProg1" style="display:none;">
	
                                <div align="center">
                                    <img src="images/ajax-loader.gif" alt="Loading" />
                                </div>
                            
</div>

                        <div id='basic-modal'>
                            <div id="divHomeGroups" style="margin: 5px; padding-left: 10px;">
                                <b>Select Group : </b>
                                <select name="lstHomeGroups" id="lstHomeGroups" onchange="ChangeHomeGroup();">
	<option selected="selected" value="0" class="selectHead">All Group</option>
	<option value="1">Priya Transport</option>
	<option value="3">NEWAK</option>

</select>
                            </div>
                            <div class="processMessage" align="center" id="divWait2" style="display: none">
                                <img src="images/ajax-loader.gif" alt="Loading..." />
                            </div>

                            <div id='divHomeData'>
                                
                                <table id="divFilters" style="margin: 5px; min-width: 1000px; " width="100%">
                                    <tr>
                                        <th align="right"><b>Filter : </b>
                                        </th>
                                        <td>
                                            
                                        </td>

                                        <td>Status : 
                                                <select name="lstVehStatus" id="lstVehStatus" onchange="FilterVehicles()">
	<option value="">Any</option>
	<option value="R">Moving</option>
	<option value="S">Stoppage</option>
	<option value="O">Overspeed</option>
	<option value="U">Unreachable</option>

</select>
                                        </td>
                                        <td>
                                            <input type="checkbox" id="chkVehMarker" checked />Marker with Vehicle Name                                          
                                        </td>
                                        <th align="right">Color Scheme : </th>
                                        <td><span style="background-color: palegreen; width: 10px; display: inline-block">&nbsp;</span> Moving &nbsp;&nbsp;</td>
                                        <td>
                                            <span style="background-color: Yellow; width: 10px; display: inline-block">&nbsp;</span> Idle &nbsp;&nbsp;
                                        </td>
                                        
                                        <td>
                                            <span style="background-color: Red; width: 10px; display: inline-block">&nbsp;</span> Unreachable &nbsp;&nbsp;
                                        </td>
                                        
                                    </tr>
                                </table>
                                
                                <div id="UpdatePanel2">
	
                                        <div align="right">
                                            
                                        </div>
                                        <div style="display: none" id="divHomeDataHeading">
                                            <h3> Vehicle Status 07 Nov 2017 15:39 &nbsp; &nbsp;  : Moving=2, Idle=7, Unreachable=2</h3>
                                        </div>
                                        
                                        <span id="Timer2" style="display:none;"></span>

                                        &nbsp;<input type="submit" name="btnVehDetails" value="" id="btnVehDetails" class="button1 del" style="display:none;" />

                                        <input name="hdChkHomeIds" type="hidden" id="hdChkHomeIds" />
                                        <input name="hdSngVehicleId" type="hidden" id="hdSngVehicleId" />
                                        <div id="hdAllVehStatus" style="display: none" class="del">2<img src='images/on.gif' align='absmiddle' border=0 title='Moving' />&nbsp;&nbsp;7<img src='images/off.gif' align='absmiddle' border=0 title='Idle' />&nbsp;&nbsp;2<img src='images/NotRpt.gif' align='absmiddle' border=0 title='Unreachable' />&nbsp;&nbsp; <span> = 11 </span></div>
                                        <div id="txtJson" style="display: none" class="del">{"dt":[{"la":"21.276313","ln":"81.595035","vid":"4","vn":"CG-04-LW-9448","vc":"#FFE766","an":"48","ic":"2","gid":"3","vs":null,"nl":"Jarway Alias Hirapur-Raipur-Chhattisgarh(1.02 KM)"},{"la":"21.378975","ln":"81.645798","vid":"5","vn":"CG-04-LX-0447","vc":"palegreen","an":"285","ic":"2","gid":"3","vs":null,"nl":"Unnamed Road-Munrethi-2-Raipur-Chhattisgarh-India"},{"la":"22.845888","ln":"82.377395","vid":"6","vn":"CG-04-LW-9451","vc":"#FFE766","an":"232","ic":"2","gid":"3","vs":null,"nl":"Jhinpuri-Korba-Chhattisgarh(11.26 KM)"},{"la":"24.78063","ln":"84.349825","vid":"7","vn":"CG-04-LX-2918","vc":"red","an":"134","ic":"2","gid":"3","vs":null,"nl":"Manjurahi-Aurangabad-Bihar(0.61 KM)"},{"la":"22.846143","ln":"82.37661","vid":"8","vn":"CG-04-LX-2916","vc":"#FFE766","an":"340","ic":"2","gid":"3","vs":null,"nl":"Jhinpuri-Korba-Chhattisgarh(11.32 KM)"},{"la":"21.317233","ln":"81.56029","vid":"9","vn":"CG-04-LX-0446","vc":"#FFE766","an":"227","ic":"2","gid":"3","vs":null,"nl":"Bana-2-Raipur-Chhattisgarh(1.08 KM)"},{"la":"21.31751","ln":"81.560135","vid":"10","vn":"CG-04-LW-9452","vc":"#FFE766","an":"285","ic":"2","gid":"3","vs":null,"nl":"Bana-2-Raipur-Chhattisgarh(1.07 KM)"},{"la":"23.373777","ln":"82.822894","vid":"2","vn":"CG-04-JD-4789","vc":"#FFE766","an":"243","ic":"2","gid":"1","vs":null,"nl":"Sirai-Surguja-Chhattisgarh(4.15 KM)"},{"la":"21.263497","ln":"81.568897","vid":"1","vn":"CG-04-JD-4889","vc":"red","an":"297","ic":"2","gid":"1","vs":null,"nl":"Ring Road-Nandanvan Road-Transport Nagar-Raipur-Raipur-Chhattisgarh-India"},{"la":"23.620301","ln":"83.626469","vid":"3","vn":"CG-04-JD-8189","vc":"palegreen","an":"172","ic":"2","gid":"1","vs":null,"nl":"National Highway 343-Balrampur-Surguja-Chhattisgarh-India"},{"la":"21.255811","ln":"81.57005","vid":"0","vn":"CG-04-JD-8289","vc":"#FFE766","an":"0","ic":"2","gid":"1","vs":null,"nl":"National Highway 6-Transport Nagar-Tatibandh-Raipur-Raipur-Chhattisgarh-India"}]}</div>
                                        <table id='tblData' width='100%' cellpadding='1' cellspacing='0' border='1' class='tablesorter tdesign' bordercolor='lightgrey' style='border: solid #999999 1px; width: 100%; border-collapse: collapse;'><thead><tr style='color: White; background-color: Black; font-weight: bold;max-height:18px'><th>SN</th><th class='del'><input type='checkbox' id='chkAll' onclick='toggleChecked(1,this.checked)' /></th><th style='min-width: 85px;' tfilter='true' >Group</th><th style='min-width: 85px;'  tfilter='true' >Vehicle</th><th style='min-width: 100px;'  tfilter='true' >Last Seen</th><th style='' >1</th><th style='' >1</th><th style=''  class='del' >Info</th><th style='min-width: 150px;'  tfilter='true' >Nearest Site</th><th style='min-width: 150px;'  tfilter='true' >Nearest Location</th><th style=''  tfilter='true' >Speed (km/h)</th><th style=''  tfilter='true' >Idle Time(HH:MM:SS)</th><th style=''  class='del' >Specifications</th></tr></thead><tbody><tr id='0' vt='V' vs='S' onmouseover='toggleBounce(0,1,48);' onmouseout='toggleBounce(0,2,48);'><td>1</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='0' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(21.276313,81.595035,'357454074067289','2','CG-04-LW-9448',this);">CG-04-LW-9448 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','21.276313,81.595035');">07 Nov 2017 15:34</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>28</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LW-9448&gimei=357454074067289&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=4&vehicle=CG-04-LW-9448")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=4&vehicle=CG-04-LW-9448")'>Jarway Alias Hirapur-Raipur-Chhattisgarh(1.02 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=4&vehicle=CG-04-LW-9448")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=4&vehicle=CG-04-LW-9448")'>00:35:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LW-9448&gimei=357454074067289'> Specifications </a></td></tr> 
<tr id='1' vt='V' vs='R' onmouseover='toggleBounce(1,1,285);' onmouseout='toggleBounce(1,2,285);'><td>2</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='1' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:palegreen'><a title='Live Track' onclick="showLiveTrack(21.378975,81.645798,'357454073859470','2','CG-04-LX-0447',this);">CG-04-LX-0447 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','21.378975,81.645798');">07 Nov 2017 15:33</td><td align='center' style='color:GREEN'><b>ON</b></td><td align='center' style='color:'><b>41</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LX-0447&gimei=357454073859470&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=5&vehicle=CG-04-LX-0447")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=5&vehicle=CG-04-LX-0447")'>Unnamed Road-Munrethi-2-Raipur-Chhattisgarh-India</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=5&vehicle=CG-04-LX-0447")'>7</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=5&vehicle=CG-04-LX-0447")'>00:00:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LX-0447&gimei=357454073859470'> Specifications </a></td></tr> 
<tr id='2' vt='V' vs='S' onmouseover='toggleBounce(2,1,232);' onmouseout='toggleBounce(2,2,232);'><td>3</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='2' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(22.845888,82.377395,'357454073858225','2','CG-04-LW-9451',this);">CG-04-LW-9451 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','22.845888,82.377395');">07 Nov 2017 14:44</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>63</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LW-9451&gimei=357454073858225&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=6&vehicle=CG-04-LW-9451")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=6&vehicle=CG-04-LW-9451")'>Jhinpuri-Korba-Chhattisgarh(11.26 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=6&vehicle=CG-04-LW-9451")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=6&vehicle=CG-04-LW-9451")'>00:20:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LW-9451&gimei=357454073858225'> Specifications </a></td></tr> 
<tr id='3' vt='V' vs='U' onmouseover='toggleBounce(3,1,134);' onmouseout='toggleBounce(3,2,134);'><td>4</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='3' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:red'><a title='Live Track' onclick="showLiveTrack(24.78063,84.349825,'357454074091529','2','CG-04-LX-2918',this);">CG-04-LX-2918 </a></td><td style='background-color:red' title='Save Site' align='center' onclick="showReport('sites','24.78063,84.349825');">05 Nov 2017 15:15</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>72</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LX-2918&gimei=357454074091529&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=03/11/2017&tdate=07/11/2017 15:39:34&vehicleid=7&vehicle=CG-04-LX-2918")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=03/11/2017&tdate=07/11/2017 15:39:34&vehicleid=7&vehicle=CG-04-LX-2918")'>Manjurahi-Aurangabad-Bihar(0.61 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=03/11/2017&tdate=07/11/2017 15:39:34&vehicleid=7&vehicle=CG-04-LX-2918")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=03/11/2017&tdate=07/11/2017 15:39:34&vehicleid=7&vehicle=CG-04-LX-2918")'>00:51:10</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LX-2918&gimei=357454074091529'> Specifications </a></td></tr> 
<tr id='4' vt='V' vs='S' onmouseover='toggleBounce(4,1,340);' onmouseout='toggleBounce(4,2,340);'><td>5</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='4' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(22.846143,82.37661,'357454073862615','2','CG-04-LX-2916',this);">CG-04-LX-2916 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','22.846143,82.37661');">07 Nov 2017 15:39</td><td align='center' style='color:GREEN'><b>ON</b></td><td align='center' style='color:'><b>104</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LX-2916&gimei=357454073862615&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=8&vehicle=CG-04-LX-2916")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=8&vehicle=CG-04-LX-2916")'>Jhinpuri-Korba-Chhattisgarh(11.32 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=8&vehicle=CG-04-LX-2916")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=8&vehicle=CG-04-LX-2916")'>00:00:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LX-2916&gimei=357454073862615'> Specifications </a></td></tr> 
<tr id='5' vt='V' vs='S' onmouseover='toggleBounce(5,1,227);' onmouseout='toggleBounce(5,2,227);'><td>6</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='5' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(21.317233,81.56029,'357454074079201','2','CG-04-LX-0446',this);">CG-04-LX-0446 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','21.317233,81.56029');">07 Nov 2017 15:36</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>56</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LX-0446&gimei=357454074079201&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=9&vehicle=CG-04-LX-0446")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=9&vehicle=CG-04-LX-0446")'>Bana-2-Raipur-Chhattisgarh(1.08 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=9&vehicle=CG-04-LX-0446")'>0</a></td><td align='right' style='background-color:Aqua'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=9&vehicle=CG-04-LX-0446")'>02:42:17</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LX-0446&gimei=357454074079201'> Specifications </a></td></tr> 
<tr id='6' vt='V' vs='S' onmouseover='toggleBounce(6,1,285);' onmouseout='toggleBounce(6,2,285);'><td>7</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='6' onclick='toggleChecked(0,this.checked)' /></td><td>NEWAK</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(21.31751,81.560135,'357454073860783','2','CG-04-LW-9452',this);">CG-04-LW-9452 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','21.31751,81.560135');">07 Nov 2017 15:36</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>57</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-LW-9452&gimei=357454073860783&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=10&vehicle=CG-04-LW-9452")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=10&vehicle=CG-04-LW-9452")'>Bana-2-Raipur-Chhattisgarh(1.07 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=10&vehicle=CG-04-LW-9452")'>0</a></td><td align='right' style='background-color:Aqua'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=10&vehicle=CG-04-LW-9452")'>03:37:35</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-LW-9452&gimei=357454073860783'> Specifications </a></td></tr> 
<tr id='7' vt='V' vs='S' onmouseover='toggleBounce(7,1,243);' onmouseout='toggleBounce(7,2,243);'><td>8</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='7' onclick='toggleChecked(0,this.checked)' /></td><td>Priya Transport</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(23.373777,82.822894,'356173062596452','2','CG-04-JD-4789',this);">CG-04-JD-4789 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','23.373777,82.822894');">07 Nov 2017 15:28</td><td align='center' style='color:GREEN'><b>ON</b></td><td align='center' style='color:'><b>75</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-JD-4789&gimei=356173062596452&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=2&vehicle=CG-04-JD-4789")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=2&vehicle=CG-04-JD-4789")'>Sirai-Surguja-Chhattisgarh(4.15 KM)</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=2&vehicle=CG-04-JD-4789")'>24</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=2&vehicle=CG-04-JD-4789")'>00:00:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-JD-4789&gimei=356173062596452'> Specifications </a></td></tr> 
<tr id='8' vt='V' vs='U' onmouseover='toggleBounce(8,1,297);' onmouseout='toggleBounce(8,2,297);'><td>9</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='8' onclick='toggleChecked(0,this.checked)' /></td><td>Priya Transport</td><td id='tdv' style='background-color:red'><a title='Live Track' onclick="showLiveTrack(21.263497,81.568897,'356173066467924','2','CG-04-JD-4889',this);">CG-04-JD-4889 </a></td><td style='background-color:red' title='Save Site' align='center' onclick="showReport('sites','21.263497,81.568897');">03 Nov 2017 04:04</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>49</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-JD-4889&gimei=356173066467924&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=01/11/2017&tdate=07/11/2017 15:39:34&vehicleid=1&vehicle=CG-04-JD-4889")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=01/11/2017&tdate=07/11/2017 15:39:34&vehicleid=1&vehicle=CG-04-JD-4889")'>Ring Road-Nandanvan Road-Transport Nagar-Raipur-Raipur-Chhattisgarh-India</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=01/11/2017&tdate=07/11/2017 15:39:34&vehicleid=1&vehicle=CG-04-JD-4889")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=01/11/2017&tdate=07/11/2017 15:39:34&vehicleid=1&vehicle=CG-04-JD-4889")'>15:48:26</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-JD-4889&gimei=356173066467924'> Specifications </a></td></tr> 
<tr id='9' vt='V' vs='R' onmouseover='toggleBounce(9,1,172);' onmouseout='toggleBounce(9,2,172);'><td>10</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='9' onclick='toggleChecked(0,this.checked)' /></td><td>Priya Transport</td><td id='tdv' style='background-color:palegreen'><a title='Live Track' onclick="showLiveTrack(23.620301,83.626469,'356173062383463','2','CG-04-JD-8189',this);">CG-04-JD-8189 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','23.620301,83.626469');">07 Nov 2017 15:32</td><td align='center' style='color:GREEN'><b>ON</b></td><td align='center' style='color:'><b>46</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-JD-8189&gimei=356173062383463&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=3&vehicle=CG-04-JD-8189")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=3&vehicle=CG-04-JD-8189")'>National Highway 343-Balrampur-Surguja-Chhattisgarh-India</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=3&vehicle=CG-04-JD-8189")'>29</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=3&vehicle=CG-04-JD-8189")'>00:00:00</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-JD-8189&gimei=356173062383463'> Specifications </a></td></tr> 
<tr id='10' vt='V' vs='S' onmouseover='toggleBounce(10,1,0);' onmouseout='toggleBounce(10,2,0);'><td>11</td><td class='del'><input type='checkbox'  checked='checked' name='chkHome' value='10' onclick='toggleChecked(0,this.checked)' /></td><td>Priya Transport</td><td id='tdv' style='background-color:#FFE766'><a title='Live Track' onclick="showLiveTrack(21.255811,81.57005,'356173061888538','2','CG-04-JD-8289',this);">CG-04-JD-8289 </a></td><td style='background-color:' title='Save Site' align='center' onclick="showReport('sites','21.255811,81.57005');">07 Nov 2017 15:35</td><td align='center' style='color:RED'><b>OFF</b></td><td align='center' style='color:'><b>48</b></td><td align='center' class='del'><a style='color:Blue;' href='#' class='basic' lang='sensor' title='sensorinfo.aspx?vehicle=CG-04-JD-8289&gimei=356173061888538&cid=10423'><b><i>i</i></b></a></td><td class='wordBreak' style='max-width:350px;background-color:'><a href='javascript:getPageDataInline("report.aspx?flag=tssite&&isinline=1&cid=10423&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=0&vehicle=CG-04-JD-8289")'>No Site Nearby</a></td><td class='wordBreak' style='max-width:350px;background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=tsloc&isinline=1&cid=10423&grade=5&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=0&vehicle=CG-04-JD-8289")'>National Highway 6-Transport Nagar-Tatibandh-Raipur-Raipur-Chhattisgarh-India</a></td><td align='center'><a href='javascript:getPageDataInline("report.aspx?flag=overspeed&isinline=1&cid=10423&rtime=60&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=0&vehicle=CG-04-JD-8289")'>0</a></td><td align='right' style='background-color:'> <a href='javascript:getPageDataInline("report.aspx?flag=stoppage&isinline=1&cid=10423&rtime=10&fdate=05/11/2017&tdate=07/11/2017 15:39:34&vehicleid=0&vehicle=CG-04-JD-8289")'>00:58:26</a></td><td align='center' class='del'><a href='#' class='basic ViewLocSave' title='vsp.aspx?cid=10423&vehicle=CG-04-JD-8289&gimei=356173061888538'> Specifications </a></td></tr> 
</tbody></table>

                                        <div style="margin: 14px; display: none;" id="divSessionMsg" class="del">
                                            &nbsp;  <b>Note : </b>Your session has expired. Please logout and then re-login.
                                        </div>
                                        <div align="center">
                                            <span id="lblError"><b><font color="Red"></font></b></span>
                                        </div>
                                    
</div>
                            </div>
                        </div>
                    </div>

                    <div id="UpdateProgress4" style="display:none;">
	
                            <div align="center">
                                <img src="images/ajax-loader.gif" alt="Loading..." />
                            </div>
                        
</div>

                    <div id='divAltPanel1' style="display: none;">
                        <div id="upAltPanel1">
	
                                
                                <input type="submit" name="btnAltPanel" value="Show All" id="btnAltPanel" style="display: none" />
                            
</div>
                    </div>

                    <div id="divReport" style="display: none;">
                        <input type="hidden" id="hdFlag1" name="hdFlag1" />
                        <input type="hidden" id="hdFlag2" name="hdFlag2" />
                        <table border="0" style="margin-left: 5px;">
                            <tr id="trGroups">
	<td>Groups
                                </td>
	<td>
                                    <div class="styled-select">
                                        <select name="lstGroups" id="lstGroups" onchange="FillVehicles();">
		<option selected="selected" value="0" class="selectHead">Select Group</option>
		<option value="1">Priya Transport</option>
		<option value="3">NEWAK</option>

	</select>
                                    </div>
                                </td>
</tr>

                            <tr id="trSenT1">
                                <td>Sensors
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbSenT1" id="cmbSenT1">
	<option value="11">Ignition</option>
	<option value="12">Battary</option>
	<option value="13">Engin</option>

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr id="trSenT2">
                                <td>Sensors
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbSenT2" id="cmbSenT2">
	<option value="21">FUEL</option>

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr id="trSenT3">
                                <td>Sensors
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbSenT3" id="cmbSenT3">
	<option value="31">Batt. Volt.</option>

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr id="trVehicles">
                                <td>Vehicles
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbVehicles" id="cmbVehicles">
	<option value="2">CG-04-JD-4789</option>
	<option value="1">CG-04-JD-4889</option>
	<option value="3">CG-04-JD-8189</option>
	<option value="0">CG-04-JD-8289</option>
	<option value="4">CG-04-LW-9448</option>
	<option value="6">CG-04-LW-9451</option>
	<option value="10">CG-04-LW-9452</option>
	<option value="9">CG-04-LX-0446</option>
	<option value="5">CG-04-LX-0447</option>
	<option value="8">CG-04-LX-2916</option>
	<option value="7">CG-04-LX-2918</option>

</select>
                                    </div>
                                </td>
                            </tr>

                            <tr id="trAllVehicles" style="display: none;">
                                <td>All Vehicles
                                </td>
                                <td>

                                    <input type="checkbox" id="chkRptAll" onclick='chkAllVeh(this);' />
                                    <input type="hidden" id="hdnChkAll" value="0" />
                                </td>
                            </tr>
                            <tr id="trCoSties" style="display: none;">
                                <td>Sites
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbCoSties" id="cmbCoSties">

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr id="trRoutes" style="display: none;">
                                <td>Route
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="cmbRoute" id="cmbRoute">

</select>
                                    </div>
                                </td>
                            </tr>

                            <tr id="trRuntime1">
                                <td>Run Time
                                </td>
                                <td>
                                    <span>Fast</span>
                                    &nbsp;
                                    <span id="slider1" style="display: inline-block; width: 150px;"></span>
                                    &nbsp;
                                    <span>Slow</span>
                                </td>
                            </tr>
                            <tr id="trStartDate">
                                <td id="lblStartDate">Start Date
                                </td>
                                <td>
                                    <table style="padding: 0; margin: 0 0 0 -3px; border: none;">
                                        <tr>
                                            <td>
                                                <div class="styled-input-m">
                                                    <input name="txtFromDate" type="text" value="07/11/2017" id="txtFromDate" class="m" Size="11" />
                                                    
                                                    <input type="hidden" name="MaskedEditExtender1_ClientState" id="MaskedEditExtender1_ClientState" />
                                                </div>
                                            </td>
                                            <td>
                                                <img src="images/spacer.gif" alt="" width="5" height="1" align="middle" style="float: left;" /><div
                                                    class="styled-input-s">
                                                    <input name="txtFMin" type="text" value="00:00" id="txtFMin" class="s" Size="5" />
                                                </div>
                                                <input type="hidden" name="MaskedEditExtender11_ClientState" id="MaskedEditExtender11_ClientState" />
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr id="trEndDate">
                                <td id="lblEndDate">End Date
                                </td>
                                <td>
                                    <table style="margin: 0 0 0 -3px; padding: 0; border: none;">
                                        <tr>
                                            <td>
                                                <div class="styled-input-m">
                                                    <input name="txtToDate" type="text" id="txtToDate" class="m" Size="11" />
                                                </div>
                                                
                                                <input type="hidden" name="MaskedEditExtender2_ClientState" id="MaskedEditExtender2_ClientState" />
                                            </td>
                                            <td>
                                                <img src="images/spacer.gif" alt="" width="5" height="1" align="middle" style="float: left;" />
                                                <div class="styled-input-s">
                                                    <input name="txtTMin" type="text" value="23:59" id="txtTMin" class="s" Size="5" />
                                                </div>
                                                <input type="hidden" name="MaskedEditExtender21_ClientState" id="MaskedEditExtender21_ClientState" />
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr id="trRuntime">
                                <td>
                                    <span id="lblRuntime">Stoppage (Minutes) </span>
                                </td>
                                <td>
                                    <input type="text" id="txtRunTime" size="15" value="60" />
                                </td>
                            </tr>
                            <tr id="trGrade">
                                <td>
                                    <span id="lblGrade">Grade (Location) </span>
                                </td>
                                <td>
                                    <div class="input-l">
                                        <input name="txtGrade" type="text" value="5" id="txtGrade" Size="5" />
                                    </div>
                                </td>
                            </tr>
                            <tr id="trSite1">
                                <td>Site 1 (Optional)
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="lstSite1" id="lstSite1" onKeyUp="this.blur();">
	<option selected="selected" value="-1" class="selectHead">All Sites Selected</option>

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr id="trSite2">
                                <td>Site 2 (Optional)
                                </td>
                                <td>
                                    <div class="styled-select">
                                        <select name="lstSite2" id="lstSite2" onKeyUp="this.blur();">
	<option selected="selected" value="-1" class="selectHead">All Sites Selected</option>

</select>
                                    </div>
                                </td>
                            </tr>
                            <tr valign="top" id="trInterval">
                                <td>
                                    <span id="lblInterval">Interval in</span>
                                </td>
                                <td>
                                    <div>
                                        <input type="radio" name="rdInterval" id="rdMinutes" value="m" /><b>Minutes</b>
                                        &nbsp;
                                    <input type="radio" name="rdInterval" id="rdHours" value="h" checked="checked" /><b>Hours</b>
                                    </div>
                                    <div class="input-l">
                                        <input name="txtInterval" type="text" value="6" id="txtInterval" class="l" Size="5" />
                                    </div>
                                </td>
                            </tr>
                            <tr id="trPause">
                                <td>Pause
                                </td>
                                <td>
                                    <div class="input-l">
                                        <input type="text" id="txtPause" size="3" class="l" value="3" />
                                    </div>
                                </td>
                            </tr>
                            <tr id="trFreq">
                                <td>Frequency
                                </td>
                                <td>
                                    <div class="input-l">
                                        <input type="text" id="txtFreq" size="3" class="l" value="2" />
                                    </div>
                                </td>
                            </tr>
                            <tr id="trRouteMap">
                                <td colspan="2">
                                    <table width="100%" cellpadding="2" cellspacing="0">
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbStoppage" />
                                                Stoppage
                                            </td>
                                            <td>
                                                <div>
                                                    <input type="text" id="tbStoppage" size="5" value="10" />
                                                    (Min)
                                                </div>
                                            </td>
                                        </tr>

                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbtime" value="1" />
                                                Time interval
                                            </td>
                                            <td>
                                                <div>
                                                    <input type="text" id="tbTimeInt" size="5" value="6" />
                                                    (Hours)
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbOverSpeed" />
                                                OverSpeed
                                            </td>
                                            <td>
                                                <div>
                                                    <input type="text" id="tbOverSpeed" value="60" size="5" />
                                                    KMPH
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbLocation" />
                                                Location
                                            </td>
                                            <td>
                                                <div>
                                                    <input type="text" id="tbLocation" value="4" size="5" />
                                                    Grade
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbSite" />
                                                Site
                                            </td>
                                            <td>
                                                <input type="checkbox" id="cbLocality" />
                                                Locality
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input name="cbsen11" type="checkbox" id="cbsen11" />
                                                <span id="lblsen11">Ignition</span>
                                            </td>
                                            <td>
                                                <input name="cbsen12" type="checkbox" id="cbsen12" />
                                                <span id="lblsen12">Battary</span>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input name="cbsen13" type="checkbox" id="cbsen13" />
                                                <span id="lblsen13">Engin</span>
                                            </td>
                                            <td>
                                                
                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                
                                                
                                            </td>
                                            <td>
                                                
                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input name="cbsen21" type="checkbox" id="cbsen21" />
                                                <span id="lblsen21">FUEL</span>
                                            </td>
                                            <td>
                                                
                                                
                                            </td>
                                        </tr>                                                                              
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="cbNotReach" />
                                                Not Reachable
                                            </td>
                                            <td>
                                                <input name="cbsen31" type="checkbox" id="cbsen31" />
                                                <span id="lblsen31">Batt. Volt.</span>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr id="trBusRoute" style="display: none">
                                <td colspan="2">
                                    <table width="100%" cellpadding="2" cellspacing="0">
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="chk_Br_timeDeviate" />
                                                Time Deviation
                                            </td>
                                            <td>
                                                <input type="text" id="txt_Br_timeDeviate" size="5" value="30" maxlength="5" />
                                                (Min)                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="chk_Br_distDeviate" />
                                                Distance Violation
                                            </td>
                                            <td>
                                                <input type="text" id="txt_Br_distDeviate" size="5" value="1000" maxlength="7" />
                                                (Meters)                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="chk_Br_Stoptime" />
                                                Stoppage Violation
                                            </td>
                                            <td>
                                                <input type="text" id="txt_Br_Stoptime" size="5" value="30" maxlength="5" />
                                                (Min)                                                
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>
                                                <input type="checkbox" id="chk_Br_speed" />
                                                Speed Violation
                                            </td>
                                            <td>
                                                <input type="text" id="txt_Br_Speed" size="5" value="10" maxlength="5" />
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr id="trIdleTime">
                                <td>Idle Time(Minutes)</td>
                                <td>
                                    <input type="text" id="txtIdleTime" maxlength="5" />
                                </td>
                            </tr>
                            <tr id="trConsignor">
                                <td>Consignor</td>
                                <td>
                                    <input type="text" id="txtConsignor" size="20" />
                                </td>
                            </tr>
                            <tr id="trConsignee">
                                <td>Consignee</td>
                                <td>
                                    <input type="text" id="txtConsignee" size="20" />
                                </td>
                            </tr>
                            <tr id="trForwarder">
                                <td>Forwarder</td>
                                <td>
                                    <input type="text" id="txtForwarder" size="20" />
                                </td>
                            </tr>

                            <tr>
                                <td></td>
                                <td>
                                    <input type="button" value="View" class="button1" onclick="SearchReport();" />
                                    <input type="hidden" name="hdnrptName" id="hdnrptName" />
                                </td>
                            </tr>
                        </table>
                    </div>
                    <div id="divSites" style="display: none;">
                        <div id="upSites">
	
                                <div id="uprogesSites" style="display:none;">
		
                                        <div class="processMessage" align="center">
                                            <img src="images/ajax-loader.gif" alt="Loading..." />
                                        </div>
                                    
	</div>
                                <table border="0" style="border-color: #FFFFFF; margin-left: 5px;" width="100%">
                                    <tr>
                                        <td style="padding-right: 5px;">Site Name
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtSite" type="text" maxlength="30" id="txtSite" Size="25" style="margin-left: 5px;" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Type
                                        </td>
                                        <td>
                                            <div class="styled-select">
                                                <select name="lstSiteType" id="lstSiteType">
		<option value="1">Home Site</option>
		<option value="2">Client Site</option>
		<option value="3">Restricted Site</option>
		<option value="4">Other Site</option>

	</select>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td></td>
                                        <td>
                                            <input type="submit" name="btnSiteAdd" value="Add" onclick="return chkAddEditSite();" id="btnSiteAdd" class="button1" />
                                            &nbsp;
                                        <input type="submit" name="btnSiteUpdate" value="Update" onclick="return chkAddEditSite();" id="btnSiteUpdate" class="button1" />&nbsp; &nbsp;
                                            <input type="button" value="Clear Map" onclick="clearMap()" class="button1" />
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="2" style="color: Red;" align="center">
                                            <span id="ltrSiteMsg"><b></b></span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="2">
                                            <div>

	</div>
                                        </td>
                                    </tr>
                                </table>
                                <input type="hidden" name="hdOldSiteId" id="hdOldSiteId" value="-1" />
                                <input type="hidden" name="hdSiteLatLngt" id="hdSiteLatLngt" />
                            
</div>
                    </div>
                    <div id="divRoutes" style="display: none">
                        <div id="upRoutes">
	
                                <div id="UpdateProgress2" style="display:none;">
		
                                        <div class="processMessage" align="center">
                                            <img src="images/ajax-loader.gif" alt="Loading..." />
                                        </div>
                                    
	</div>
                                <input type="submit" name="btnRouteReferesh" value="View" id="btnRouteReferesh" class="button1" style="display: none" />
                                <input name="hdRouteType" type="hidden" id="hdRouteType" />
                                <input type="hidden" name="hdRouteLatLngt" id="hdRouteLatLngt" />
                                <div style="margin: 5px;">
                                    <div>
                                        Route Name : 
                                    <input name="txtRouteName" type="text" maxlength="30" id="txtRouteName" Size="25" />
                                    </div>
                                    <div>
                                        Distance(KM) : 
                                    <input name="txtRouteDist" type="text" maxlength="5" id="txtRouteDist" Size="7" />
                                    </div>
                                    <div align="center" style="margin: 5px;">
                                        <input type="submit" name="btnAddRouteMap" value="Add Route" onclick="return chkAddEditRoute();" id="btnAddRouteMap" class="button1" />
                                        &nbsp;                                        
                                            <input type="button" value="Clear Route Map" onclick="clearMap();" class="button1" />
                                    </div>
                                    <div align="center">
                                        <span id="lblRouteMsg" class="message"><b></b></span>
                                    </div>
                                </div>
                                <div>

	</div>
                            
</div>
                    </div>
                    <div id="divRouteSms" style="display: none">
                        <div id="upRouteSms">
	
                                <div id="UpdateProgress3" style="display:none;">
		
                                        <div class="processMessage" align="center">
                                            <img src="images/ajax-loader.gif" alt="Loading..." />
                                        </div>
                                    
	</div>
                                <input type="submit" name="btnRouteSmsReferesh" value="View" id="btnRouteSmsReferesh" class="button1" style="display: none" />
                                <table border="0" style="border-color: #FFFFFF; margin-left: 5px;" width="100%">
                                    <tr>
                                        <td>
                                            <span id="Label15"><font face="Verdana">Route</font></span>
                                        </td>
                                        <td>
                                            <div class="styled-select">
                                                <select name="cmbSmsRoute" id="cmbSmsRoute" onKeyUp="this.blur();">

	</select>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>First Name
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtRouteSmsFirstName" type="text" id="txtRouteSmsFirstName" tabindex="1" class="l" Size="25" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Last Name
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtRouteSmsLastName" type="text" id="txtRouteSmsLastName" tabindex="1" class="l" Size="25" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Class
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtRouteSmsClass" type="text" id="txtRouteSmsClass" tabindex="1" class="l" Size="25" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Prefered Distance
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtRouteSmsDistance" type="text" id="txtRouteSmsDistance" tabindex="1" class="l" Size="25" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Address
                                        </td>
                                        <td>
                                            <div class="input-l">
                                                <input name="txtRouteSmsAddress" type="text" id="txtRouteSmsAddress" tabindex="3" class="l" Size="25" />
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="2">
                                            <div>

	</div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td colspan="2">
                                            <input type="submit" name="btnRouteSmsDel" value="Delete" onclick="javascript:return confirm(&#39;Are you sure you want to delete this record?&#39;);" id="btnRouteSmsDel" class="button1" />
                                            &nbsp;
                                        <input type="submit" name="btnRouteSmsUpdate" value="Update" id="btnRouteSmsUpdate" class="button1" />
                                            &nbsp;
                                        <input type="submit" name="btnRouteSmsView" value="View" id="btnRouteSmsView" class="button1" />
                                            &nbsp;
                                        <input type="submit" name="btnRouteSmsSave" value="Save" id="btnRouteSmsSave" class="button1" />
                                        </td>
                                    </tr>
                                </table>
                                <input type="hidden" name="hdSmsRouteId" id="hdSmsRouteId" />
                                <input type="hidden" name="hdSmsLat" id="hdSmsLat" />
                                <input type="hidden" name="hdSmsLngt" id="hdSmsLngt" />
                                <input type="hidden" name="hdRouteSmsId" id="hdRouteSmsId" />
                            
</div>
                    </div>

                    

                    <div id="pnlDialog">
                    </div>
                </div>
                <div id="pnlRight">
                    <div class="processMessage" align="center" id="divWait" style="display: none">
                        <img src="images/ajax-loader.gif" alt="Loading..." />
                    </div>
                    <div id="divResult" style="display: none">
                    </div>
                    <div id="mapDialog" title="Google Map">
                        <div id="mapCanvas">
                            <div id="divMapSearch" style="position: absolute; top: 8px; right: 50px; z-index: 9; display: none">
                                Search Location :
                                <input type="text" id="txtMapSearch" onkeypress="pressEnter('btnMapSearch', event);" size="12" />
                                <input type="button" id="btnMapSearch" value="Search" onclick="SearchGeocodeAddress();" />
                            </div>
                            
                            <div id="divMapCluster" style="position: absolute; top: 8px; right: 5px; z-index: 9;">
                                <input type="checkbox" id="chkCluster" onclick="CreateMapCluster()" />
                                Density Cluster
                            </div>
                            <div id="divMapSite" style='position: absolute; top: 8px; left: 130px; z-index: 9;'>
                                <input type="text" id="txtMapSiteSearch" size="12" />
                                <input type="button" id="btnMapSiteSearch" value="Show Sites" onclick="createSiteMarker();" />
                            </div>
                            <div id="map" style="width: 100%; height: 100%;">
                            </div>
                            <div id="mapAngle">
                                <img id="picAngle" src="images/arrow1.png" alt="" border="0" />
                            </div>
                            <div id="divMapLatLngt">
                            </div>
                        </div>
                    </div>
                </div>


                
            </div>
        </div>

        <!-- ---JSS ------ -->
        <script type="text/javascript" language="javascript" src="js/commonjs.js"></script>
        <script type="text/javascript" language="javascript" src="js/homepage.js"></script>
        <script type="text/javascript" language="javascript" src="js/jquery.min.js"></script>
        <script type="text/javascript" language="javascript" src="js/jquery-ui.js"></script>
        <script type="text/javascript" language="javascript" src="js/combobox.js">        
        </script>

        <script type="text/javascript" language="javascript" src="js/menu.js"></script>
        <script type="text/javascript" language="javascript" src="js/jqueryRotate.js"></script>
        <script src="js/jquery.stickynote.js" type="text/javascript"></script>
        <script type="text/javascript" src="//maps.googleapis.com/maps/api/js?&key=AIzaSyAvuJRFV9Vmbrqz83iMbBRgqqGuNwRYclk"></script>
        <!-- <script type="text/javascript" src="http://google-maps-utility-library-v3.googlecode.com/svn/trunk/markerclustererplus/src/markerclusterer.js"></script> -->
        <script type="text/javascript" src="https://cdn.rawgit.com/googlemaps/js-marker-clusterer/gh-pages/src/markerclusterer.js"></script>

        <script type="text/javascript" language="javascript" src="js/markerwithlabel.js"></script>
        
        <script type="text/javascript" language="javascript" src="js/jquery.dataTables.min.js"></script>

        <script type='text/javascript' src='js/jquery.simplemodal.js'></script>

        <!-- ------------------------------------------------------------------------->
        <script type="text/javascript" language="javascript">

            var gWidth = 1024, gHeight = 700,gMinWidth = 1020;
            var today = '';     
            var tempTxtSearch = '';
            var tempSearchType = ''; 
            function setScreenWidthHeight() {
                var winW, winH;
                if (self.innerWidth) {
                    winW = self.innerWidth;
                    winH = self.innerHeight;
                } else if (document.documentElement && document.documentElement.clientWidth) {
                    winW = document.documentElement.clientWidth;
                    winH = document.documentElement.clientHeight;
                } else if (document.body) {
                    winW = document.body.clientWidth;
                    winH = document.body.clientHeight;
                }

                //----------- Set Minimum width rule here --------------
                if(winW < gMinWidth)
                    winW = gMinWidth;
                //-----------------------------------------------------
                    
                gWidth = winW - 8;
                gHeight = winH - $("#container").height() - 5; // 128;
            }
    
            jQuery(function ($) {      
                //Jquery contains funcstion is casesensitive so we have made new containsIN for case insensivite search
                $.extend($.expr[":"], {
                    "containsIN": function (elem, i, match, array) {
                        return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
                    }
                });

                $(' .basic').live('click', function (e) {
                    var src = $(this).attr("title");
                    var type = $(this).attr("lang");   
                
                    showModalDialog(src,type)
                    return false;
                });
            });

            function showModalDialog(src,type)
            {
                if(src == "")
                    return;

                var winHeight = 550;
                var winWidth = 950;
                var posLeft = "";
                var posTop = "";
                var backColor = "#000";
                var strOpacity = 50;

                if(gWidth > winWidth)
                    winWidth = gWidth-100;
                if(gHeight>winHeight)
                    winHeight = gHeight - 50;

                if (type == "sensor") {
                    winHeight = 200;
                    winWidth = 800;
                    posLeft = 5;
                    posTop = gHeight - winHeight + 130;
                    backColor = "#FFF";
                    strOpacity = 0;
                }

                $.modal('<iframe id="idDialog" src="' + src + '" height="' + winHeight + '" width="' + winWidth + '" style="background-color:#FFF;border:none;"/>', {
                    //                 closeHTML: "",
                    containerCss: {
                        backgroundColor: "#FFF",
                        border: '2px solid gray',
                        height: winHeight,
                        padding: 4,
                        width: winWidth
                    },
                    opacity: strOpacity,
                    //                   overlayCss: { backgroundColor: backColor },
                    position: [posTop, posLeft],
                    overlayClose: true,
                    onOpen: function (dialog) {
                        dialog.overlay.fadeIn('slow', function () {
                            dialog.container.slideDown('slow', function () {
                                dialog.data.fadeIn('slow');
                            });
                        });
                    },
                    onClose: function (dialog) {
                        dialog.data.fadeOut('fast', function () {
                            dialog.container.slideUp('fast', function () {
                                dialog.overlay.fadeOut('fast', function () {
                                    $.modal.close(); // must call this!
                                });
                            });
                        });
                    }
                });
            }

            function closeModal() {
                $.modal.close(); // must call this!          
            }


            ddsmoothmenu.init({
                mainmenuid: "divMenu", //menu DIV id
                orientation: 'h', //Horizontal or vertical menu: Set to "h" or "v"
                classname: 'ddsmoothmenu', //class added to menu's outer DIV            
                contentsource: "markup" //"markup" or ["container_id", "path_to_menu_file"]
            });

            function showHelp(str) {
                window.open('/Information.aspx?type=' + str, 'Axes', 'toolbar=no, status=yes, menubar=no, resizable=no, scrollbars=yes, width=1000, height=400');
            }

            function showInformation(flag1, flag2) {
                $("#HelpIcon").live('click', function () {
                    if (flag1 == "home") {
                        showHelp('home_Vehicle');
                        return false;
                    }
                    else if (flag1 == "stoppage" || flag1 == "overspeed" || flag1 == "tssite" || flag1 == "ntssite" || flag1 == "tsloc" || flag1 == "lv" || flag1 == "sv") {
                        showHelp(flag1);
                        return false;
                    }
                    else if (flag2 == "ac" || flag2 == "extbat" || flag2 == "intbat" || flag2 == "gpsbox" || flag2 == "upperlid" || flag2 == "lowerlid") {
                        showHelp(flag2);
                        return false;
                    }
                });
            }
            
            function toggleChecked(flg, val) {
                if (flg == 1)
                {
                    //--- Take Action only to visible rows -------------
                    $('#tblData tr:visible input[name=chkHome]').prop('checked', val);
                }                
                ShowHomeData();                
            }

            function SetWidth(leftColWidth) {
                var wt = gWidth - leftColWidth;
                var ht = gHeight;

                if ( $( "#divFooter" ).length ) { 
                    ht = ht- 20; 
                }
                document.getElementById("pnlLeft").style.height = ht + "px";
                document.getElementById("pnlRight").style.height = ht + "px";

                document.getElementById("pnlLeft").style.display = (leftColWidth > 0 ? "block" : "none");
                document.getElementById("pnlLeft").style.width = leftColWidth + "px";

                document.getElementById("pnlRight").style.width = wt + "px";
                document.getElementById("divReport").style.width = "100%";

                //&& document.getElementById("mapCanvas").style.display != "none"
                if (document.getElementById("mapCanvas")) {                        
                    document.getElementById("mapCanvas").style.height = ht + "px";
                    document.getElementById("mapCanvas").style.width = "100%";// wt + "px";
                      
                    if (map)
                        resizeMap();
                }
            }

            var mapShown = false;
            var currentSort = "";
            $(document).ready(function () {
                setScreenWidthHeight();
                SetWidth(700);
                initialize();
                state = 0;
                ShowHomeData();
           
                if(PanelId == 3 || PanelId == 4)
                {
                    BindData_Panel();
                }
                else if(PanelId == 2 || PanelId == 11)
                {
                    setTimeout(function () { showHideMap(0) },300);                    
                }

            });

            $(window).resize(function () {                    
                setScreenWidthHeight();
                SetWidth($("#pnlLeft").width());
            });

            /*  $.tablesorter.addParser({
                  id: 'custdate',
                  is: function (s) {
                      // return false so this parser is not auto detected 
                      return false;
                  },
                  format: function (s) {
                      var timeInMillis = 0;
                      if (s != "")
                          timeInMillis = Date.parse(s);
  
                      return timeInMillis;
                  },
                  // set type, either numeric or text 
                  type: 'numeric'
              });
  
              $.tablesorter.addParser({
                  id: 'custtime',
                  is: function (s) {
                      // return false so this parser is not auto detected 
                      return false;
                  },
                  format: function (s) {
                      var timeInMillis = 0;
  
                      if (s != "") {
                          try {
                              var strtime = s;
                              if (s.indexOf("d") != -1) {
                                  var str = s.split("d");
                                  timeInMillis = (24 * 60) * parseInt(str[0]);
                                  strtime = str[1];
                              }
                              if (strtime != "");
                              {
                                  var str = strtime.split(":");
                                  if (str.length >= 2)
                                      timeInMillis = timeInMillis + (60 * parseInt(str[0])) + parseInt(str[1]);
                              }
                          }
                          catch (err) {
                          }
                      }
                      return timeInMillis;
                  },
                  // set type, either numeric or text 
                  type: 'numeric'
              });
              */
            function tableSorted() {
                // Setup - add a text input to each footer cell
                $('#tblData thead th[tfilter=true]').each( function () {
                    var title = $(this).text();
                    $(this).html( '<input type="text" placeholder="' +title+'" style="min-width:40px" />' );
                } );
 
                // DataTable
                oTable =  $('#tblData').DataTable( {
                    "paging":   false,
                    "ordering": true,
                    "info":     false,
                    "columnDefs": [{
                        "targets"  : 'del',
                        "orderable": false
                    }]
                } );     
                                          
                // Apply the search
                oTable.columns().every( function () {
                    var that = this;
 
                    //Do filter only for textboxes
                    $('input[type=text]', this.header() ).on( 'keyup change', function () {
                        if ( that.search() !== this.value ) {
                            that
                                .search( this.value )
                                .draw();
                        }
                    } );
                } );
           
                /*
                $("#tblData").tablesorter(
                    {
                        dateFormat: 'dd mmm yyyy HH:MM',
                        ignoreCase: true,
                        headers: { 0: { sorter: false }, 1: { sorter: false } },
                        cssAsc: "headerSortDown",
                        cssDesc: "headerSortUp"
                    }
                    );

                //Without it,its create duplicate rows
                $("#tblData").trigger('update');

                if (currentSort != "") {
                    $("#tblData").trigger("sorton", [currentSort]);
                }
                $("#tblData").bind("sortEnd", function (e) {
                    currentSort = e.target.config.sortList;
                });*/
            }

            $(document).ready(function () {
                $("#slider1").slider({
                    ////max: 640, min: 10, step: 10, value: 320,
                    max: 10, min: 1, step: 2, value: 5,
                    stop: function (event, ui) {
                        document.getElementById("txtRunTime").value = ui.value
                        $("#slider1").attr('title', ui.value);
                    }
                });

                $("#divHome").resizable({
                    ghost: false,
                    minWidth: 100,
                    maxWidth: 1150,
                    handles: 'e, w',
                    revert: true,
                    start: function (event, ui) {
                    },
                    resize: function (event, ui) {
                        var tmpWidth = gWidth - 10 - eval(event.target.style.width.replace("px", ""));
                        document.getElementById("pnlLeft").style.width = event.target.style.width;
                        document.getElementById("pnlRight").style.width = tmpWidth + "px";
                        document.getElementById("mapCanvas").style.width = "100%";
                        /*resizeMap(); */
                    },
                    stop: function (event, ui) {
                        resizeMap();
                    }
                });

            });

            function resizeMap() {                
                //  var currCenter = map.getCenter();  //This did not work in safari
                google.maps.event.trigger(map, 'resize');
                //if(currCenter)
                //  map.setCenter(currCenter);
            }

            function closeStickyMsg() {
                $(".jSticky-delete").parent().remove();
            }

                
            function showReport(flag1, flag2) {
                //Set Reports state
                state = 7;

                flag1 = flag1.toLowerCase();
                if (flag1 == 'sites' && "1" == 0) {
                    alert("Insufficient Permission, Access Denied.");
                    return;
                }
                else if (flag1 == 'routemap' && "1" == 0) {
                    alert("Insufficient Permission, Access Denied.");
                    return;
                }

                //Close current open menu
                $("#divMenu ul li ul").css({ display: 'none' });

                //Close opened sticky msg
                closeStickyMsg();

                //Set information link
                showInformation(flag1, flag2);

                $("#divPrintMenu").show();

                //Clear fist map here
                clearMap();
                map.setZoom(7);

                document.getElementById("divHome").style.display = "none";
                document.getElementById("divHome1").style.display = "none";                                             
                document.getElementById("divSites").style.display = "none";

                document.getElementById("mapCanvas").style.display = "none";   
                document.getElementById("divMapSearch").style.display = "none";               
                document.getElementById("divMapCluster").style.display = "none";
                if($("#divMapCustomMarker").length > 0 )
                    $("#divMapCustomMarker").hide();

                document.getElementById("divRoutes").style.display = "none";
                document.getElementById("divRouteSms").style.display = "none";
                document.getElementById("divAltPanel1").style.display = "none";

                if("0" == "1")
                    $("#divWonderDealers").hide();

                if(flag1 == "altpanel1")
                {
                    $("#pnlLeft").width("100%");
                    $("#lblHeading").css("display", "block");
                    $("#lblHeading").html("Alternate Dashboard");
                    document.getElementById("divReport").style.display = "none";
                    document.getElementById("divResult").style.display = "none";
                    document.getElementById("divAltPanel1").style.display = "block";
                        
                    return;
                }
                else
                {
                    document.getElementById("divReport").style.display = "block";
                    document.getElementById("divResult").style.display = "block";
                }

                $("#pnlLeft").css("border-bottom", "solid 5px #404040");
                $('#divResult').html("");
                //---------- Remove All in vehicles list always if its added -------------
                var lstVehicles = document.getElementById("cmbVehicles");
                if (lstVehicles.length > 0 && lstVehicles.options[0].value == "-1") {
                    lstVehicles.remove(0);
                }
                //-------------------------------------------------------------------------                   

                //-------- Set panel left width & Height
                SetWidth(350);

                if (today == '')
                    today = $("#txtFromDate").val();

                $("#txtFromDate").val(today);
                $("#txtToDate").val(today);
                $("#txtFMin").val('00:00');
                $("#txtTMin").val('23:59');

                var reportHeading = "Stoppage";
                $("#lblHeading").css("display", "block");
                $("#lblHeading").html("");

                $("#divMapSite").show();

                var tmpheading = "";
                if (flag1 == "sites") {
                    state = 3;
                    document.getElementById("mapCanvas").style.display = "block";
                    document.getElementById("divSites").style.display = "block";
                    document.getElementById("divMapSearch").style.display = "block";
                    document.getElementById("divReport").style.display = "none";
                    document.getElementById("divResult").style.display = "none";
                    $("#lblHeading").css("display", "none");
                    if (flag2 && flag2.length > 2) {
                        var spliit = flag2.split(",");
                        showSites(spliit[0], spliit[1], 1, 0);
                    }

                    $("#divPrintMenu").hide();
                    if (map)
                        resizeMap();
                    return;
                }
                else if(flag1 == "wonderdealers")
                {
                    $("#lblHeading").html("Wonder Dealers");
                    $("#divWonderDealers").show();
                    
                    $("#divMapSite").hide();
                    $("#divReport").hide();
                    $("#divResult").hide();
                    $("#divPrintMenu").hide();
                    
                    document.getElementById("mapCanvas").style.display = "block";                                        
                    if (map)
                        resizeMap();

                    return;
                }
                else if (flag1 == "routemap") {
                    reportHeading = "Route Mapper";
                    document.getElementById("mapCanvas").style.display = "block";
                    document.getElementById("divResult").style.display = "none";

                    if($("#divMapCustomMarker").length > 0 )
                        $("#divMapCustomMarker").show();
                
                    $("#divPrintMenu").hide();
                    if (map)
                        resizeMap();
                }                
                else if (flag1 == "routes" || flag1 == "restrt") {
                    state = 5;
                    document.getElementById("mapCanvas").style.display = "block";
                    document.getElementById("divRoutes").style.display = "block";
                    document.getElementById("divReport").style.display = "none";
                    document.getElementById("divResult").style.display = "none";
                    $("#divPrintMenu").hide();
                    if (map)
                        resizeMap();

                    $("#lblHeading").html(flag1 == "routes" ? "Route Details" : "Restricated Routes List");

                    $("#hdRouteType").val(flag1);
                    eval("__doPostBack('btnRouteReferesh','')");
                    return;
                }
                else if (flag1 == "routesms") {
                    document.getElementById("mapCanvas").style.display = "block";
                    document.getElementById("divRouteSms").style.display = "block";
                    document.getElementById("divReport").style.display = "none";
                    document.getElementById("divResult").style.display = "none";
                    $("#divPrintMenu").hide();
                    if (map)
                        resizeMap();

                    $("#lblHeading").html("Route SMS");
                    eval("__doPostBack('btnRouteSmsReferesh','')");
                    return;
                }

    document.getElementById("hdFlag1").value = flag1;
    if (flag2)
        document.getElementById("hdFlag2").value = flag2;


    if (flag1 == "")
        flag1 = "stoppage";

                //Show common rows for all reports -------
    $("#trVehicles").show();
    $("#trStartDate").show();
    $("#lblStartDate").html("Start Date");            
    $("#trEndDate").show();
    $("#lblEndDate").html("End Date");
    $("#txtFMin").show();
    $("#txtTMin").show();
                //------------------------------------

                //---------clearmap---------------------------
                $("#trSenT1").hide();
                $("#trSenT2").hide();
                $("#trSenT3").hide();
                $("#trGrade").hide();
                $("#trRuntime").hide();
                $("#trRuntime1").hide();
                $("#trSite1").hide();
                $("#trSite2").hide();
                $("#trInterval").hide();

                $("#trPause").hide();
                $("#trFreq").hide();
                $("#trRouteMap").hide();

                $("#trIdleTime").hide();
                $("#trConsignor").hide();
                $("#trConsignee").hide();
                $("#trForwarder").hide();

                $("#trAllVehicles").hide(); 
                $("#txtRunTime").val('60');
                $("#trCoSties").hide();
                $("#trRoutes").hide();
                $("#trBusRoute").hide();


                tmpheading = " Report";
                $("#lblRuntime").html("Stoppage (Minutes)");
                $("#lblInterval").html("Interval In");
                $("#rdHours").prop("checked",true);
                $("#txtRunTime").val(10);

                if (flag1 == "historytrack") {
                    tmpheading = "";
                    reportHeading = "History Tracking";

                    $("#trEndDate").hide();
                }
                else if (flag1 == "routemap") {
                    tmpheading = "";
                    reportHeading = "Route Mapper";

                    $("#trRuntime1").show();
                    $("#trPause").show();
                    $("#trFreq").show();
                    $("#trRouteMap").show();

                }
                else if (flag1 == "eventlog") {
                    reportHeading = "Event Log";
                    $("#trRouteMap").show();
                }
                else if (flag1 == "stoppage") {
                    reportHeading = "Stoppage";
                    $("#trRuntime").show();
                }
                else if (flag1 == "stoppagelonghalt") {
                    // same as stoppage
                    reportHeading = "Stoppage Long Halt";
                    $("#trRuntime").show();
                }


                else if (flag1 == "overspeed") {
                    reportHeading = "Overspeed";
                    $("#trRuntime").show();
                    $("#trInterval").show();

                    $("#lblRuntime").html("Speed Limit(KMPH)");
                    $("#lblInterval").html("Time Limit");
                    $("#txtRunTime").val(60);    
                    $("#txtInterval").val(5);    
                    $("#rdMinutes").prop("checked",true);
                }
                else if (flag1 == "tssite") {
                    reportHeading = "Trip Summary(Site)";
                    $("#trSite1").show();
                    $("#trSite2").show();
                }
                else if (flag1 == "ntssite") {
                    reportHeading = "New Trip Summary(Site)";
                }
                else if (flag1 == "tsloc") {
                    reportHeading = "Trip Summary(Location)";
                    $("#trGrade").show();
                }
                else if (flag1 == "locality") {
                    reportHeading = "Locality Visited";
                }
                else if (flag1 == "tstime") {
                    reportHeading = "Trip Summary(Time)";
                    $("#trInterval").show();
                }
                else if (flag1 == "vehsitevisited") {
                    reportHeading = "Vehicle Site Visited";
                }
                else if (flag1 == "vehsitenotvisited") {
                    reportHeading = "Vehicle Site Not Visted";
                }
                else if (flag1 == "fuelconsumption") {
                    reportHeading = "Fuel Consumption";
                    $("#trInterval").show();
                    $("#trSenT2").show();
                }
                else if (flag1 == "fuelfill") {
                    reportHeading = "Fuel Fill";
                    $("#trSenT2").show();
                    $("#trGrade").show();
                }
                else if (flag1 == "fuelremoval") {
                    reportHeading = "Fuel Removal";
                    $("#trSenT2").show();
                }                                
                else if (flag1 == "prdsummary") {
                    reportHeading = "Period Summary";
                    //---------- Add All in vehicles list always if its not added -------------
                    AddAllOptionInVehicles();
                    //-------------------------------------------------------------------------

                    $("#trRuntime").show();
                    $("#trSenT1").show();
                }
                else if (flag1 == "acrun") {
                    reportHeading = "Sensor Usage Analysis";
                    $("#trInterval").show();
                    $("#trSenT1").show();
                }       
                else if (flag1 == "fleetsensorsummary") {
                    reportHeading = "Fleet Sensor Summary";
                    $("#trSenT1").show();
                    $("#trInterval").hide();
                    $("#trVehicles").hide();
                }
                else if (flag1 == "sensor") {
                    $("#trSenT1").show();
                    reportHeading = "Sensor Status";
                }
                else if (flag1 == "workinghours") {
                    $("#trSenT1").show();
                    reportHeading = "Working Hours";
                }
                else if (flag1 == "unauthsensor") {
                    $("#trSenT1").show();
                    $("#trRuntime").show();

                    reportHeading = "Unauthorized Sensor Usage";
                }
                else if (flag1 == "tssen") {
                    $("#trSenT1").show();
                    reportHeading = "Trip Summary(Sensor)";
                }
                else if (flag1 == "routedev") {
                    if (flag2 == "all") {
                        reportHeading = "Route Deviation(All)";
                    }
                    else if (flag2 == "spec") {
                        reportHeading = "Route Deviation(Assigned)";
                    }
                    else if (flag2 == "rest") {
                        reportHeading = "Restricated Route Driving ";
                    }
                }
                else if (flag1 == "mileage") {
                    reportHeading = "Mileage";
                }
                else if (flag1 == "fltsummary1") {
                    reportHeading = "New Fleet Summary";

                    $("#trVehicles").hide();
                    $("#trGroups").hide();
                }
                else if (flag1 == "fltsummary") {
                    $("#trStartDate").hide();
                    $("#trVehicles").hide();
                    $("#trEndDate").hide();

                    //========= Special Case =============
                    SetWidth(0);
                    SearchReport();
                    return;
                    //====================================
                }

                else if (flag1 == "routeprogress") {
                    $("#trStartDate").hide();
                    $("#trVehicles").hide();
                    $("#trEndDate").hide();

                    //========= Special Case =============
                    SetWidth(0);
                    SearchReport();
                    return;
                    //====================================
                }                   
                else if (flag1 == "tripsummaryworkshop") {
                    reportHeading = "Trip Summary Work Shop ";
                    $("#trGroups").hide();
                    $("#trConsignor").show();
                    $('#trConsignor').find('td:first').html('Site (Optional)');
                    $('#txtConsignor').val('workshop');
                }
        
                else if (flag1 == "brtripsummary") {    //Bus Route Trip Summary
                    //// reportHeading = "Bus Route Trip Summary ";
                    reportHeading = "Route Exception ";
            
                    $("#trBusRoute").show();
                    $("#trVehicles").hide();
                    $("#trStartDate").hide();
                    $("#trEndDate").find('td:first').html('Date ');
                    $("#txtTMin").hide();
                }
                else if (flag1 == "updowntrip") {   
                    reportHeading = "Trip Arrival Timing ";
            
                }
                else if (flag1 == "bustripupdownsummary") {   
                    reportHeading = "Bus Trip Up Down Summary ";
                    $("#trVehicles").show();
                    $("#trStartDate").hide();
                    $("#trEndDate").find('td:first').html('Date ');
                    $("#txtTMin").hide();
                }
                else if (flag1 == "plantstatus") {  
                    reportHeading = "Plant Status";
           
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
           
                    //AddAllOptionInVehicles();
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
        
                else if (flag1 == "yardstatus") {  
                    reportHeading = "Yard Status";
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
                else if (flag1 == "dailynonconformity" || flag1 == "yarddailynonconformity") {  
                    if (flag1 == "dailynonconformity")
                        reportHeading = "Daily Nonconformity(Plant)";
                    else
                        reportHeading = "Daily Nonconformity(Yard)";
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
                else if (flag1 == "expectedarrivaltime") {  
                    reportHeading = "Expected Arrival Time";
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
                else if (flag1 == "customerstatus") {  
                    reportHeading = "Customer Status";
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                }
                else if (flag1 == "customerdailysummary") {  
                    reportHeading = "Daily Summary";
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
                else if (flag1 == "customerdailynonconformity") {  
                    reportHeading = "Customer Daily Nonconformity";
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                }
                else if (flag1 == "salestypewiseanalysis") {  
                    reportHeading = "Sales Type Wise Analysis";
                    $("#trVehicles").hide();
                    $("#trRuntime").show();
                    $("#lblRuntime").html('Plant');                        
                    $("#txtRunTime").val('');
                }
                else if (flag1 == "transporterperformance") {  
                    reportHeading = "Transporter Performance";
                    $("#trVehicles").hide();
                    $("#trRuntime").show();
                    $("#lblRuntime").html('Plant');                        
                    $("#txtRunTime").val('');
                }
        
                else if (flag1 == "plantperformancereport") {  
                    reportHeading = "Plant Performance";
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                    $("#trVehicles").hide();
                    // FillCoSites();
                    $("#trCoSties").show();

                }
                else if (flag1 == "transporterperformance2") {  
                    reportHeading = "Transporter Performance(%)";
                    $("#trVehicles").hide();
                    $("#trRuntime").show();
                    $("#lblRuntime").html('Plant');                        
                    $("#txtRunTime").val('');
                }
                else if (flag1 == "bustripsroutetimings") {  
                    reportHeading = "Bus Trips Route Timing Report";
                    $("#trAllVehicles").show(); 
                    $("#trVehicles").show();
                    $("#trRoutes").show();
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                }
                else if (flag1 == "bustripsvehicleallocation") {  
                    reportHeading = "Route Wise Vehicle Allocation With Time and KMs";
                    $("#trVehicles").show();
                    //$("#trRoutes").show();
                    $("#trAllVehicles").show(); 
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                }
                else if (flag1 == "bustripsroutewisegeofence") {  
                    reportHeading = "Route Wise Geofence Table";
                    $("#trRoutes").show();
                    $("#trStartDate").hide();
                    $("#trEndDate").hide();
                    $("#trVehicles").hide();
                    $("#trGroups").hide();
                }
                else if (flag1 == "bustriproutesummary") {    //Bus Route Trip Summary
                    reportHeading = "Route Wise Summary";
                    $("#trVehicles").show();
                    $("#trAllVehicles").show(); 
                    $("#trStartDate").hide();
                    $("#trEndDate").find('td:first').html('Date ');
                }
                else if (flag1 == "actempr") {  
                    reportHeading = "AC Temperature";
                    $("#trVehicles").show();
                    $("#trSenT1").show();
                }
                else if (flag1 == "idling") {   
                    reportHeading = "Idling Summary";
                    $("#trRuntime").show();
                    $("#trVehicles").show();
                    $("#trSenT1").show();
                }
                else if (flag1 == "powercutlog") {   
                    reportHeading = "Power Cut Log";
                    $("#trVehicles").hide();
                }
                else if (flag1 == "mobroutetrack") {   
                    reportHeading = "Mobile Route Visiting";            
                    $("#trVehicles").show();
                }
                else if(flag1=="bustripdelay")
                {
                    reportHeading="Bus Trip Delay";
                    $("#trVehicles").hide();
                    $("#txtFMin").hide();
                    $("#txtTMin").hide();
                }
                else if(flag1=="fleethistorytrack")
                {
                    reportHeading="Fleet History Track";
                    $("#trVehicles").hide();
                    $("#trEndDate").hide();
                    $("#trStartDate").find('td:first').html('Date ');
                }
                else if(flag1=="gvktrip")
                {
                    reportHeading="GVK Trip Detail";
                }
    
                    
    $("#lblHeading").html(reportHeading + tmpheading);
    document.getElementById("hdnrptName").value= reportHeading;  //for reports as a name
}


function showHome() {
    //Set information link
    showInformation("home");
    state = 0;
            
    $("#lblHeading").css("display", "none");
    document.getElementById("divReport").style.display = "none"
    document.getElementById("divResult").style.display = "none";;
    document.getElementById("divSites").style.display = "none";                    
    document.getElementById("divRoutes").style.display = "none";
    document.getElementById("divRouteSms").style.display = "none";
    document.getElementById("divAltPanel1").style.display = "none";
    document.getElementById("divHome").style.display = "block";                    
    $("#pnlLeft").css("border-bottom", "none");
    
    document.getElementById("divHome1").style.display = "inline";
    document.getElementById("mapCanvas").style.display = "block";                    
    document.getElementById("divMapCluster").style.display = "block";
    document.getElementById("divMapSearch").style.display = "none";
    
    SetWidth(700);
    BindData(0);  
    
    if(PanelId == 2 || PanelId == 11 || PanelId == 12){
        showHideMap(0);
    }
    else if(PanelId == 3 || PanelId == 4)
    {
        BindData_Panel();
    }
}
function showHideMap(flg,flgBindData) {    
    document.getElementById("pnlLeft").style.display = (flg == 0 || flg == -1 ? "block" : "none");   
    $("#mapCanvas").css("display", (flg == 1 || flg == -1 ? "block" : "none"));
   
    var showData=1;
    if(typeof flgBindData !== "undefined")
        showData = flgBindData;

    if (flg == 0) {
        $("#pnlLeft").width("99%");
        $("#pnlRight").width("0");
        $("#divHome").width("100%");
    }
    else if (flg == 1) {       
        $("#pnlLeft").width("0");
        $("#pnlRight").width("100%");        
        $("#mapCanvas").width("100%");
        if(showData > 0)
            ShowHomeData();
    }
    else {
        SetWidth(700);
        if(showData > 0)
            ShowHomeData();
    }
    if (flg != 0)
        resizeMap();
}

function BindData(fromTimer) {   
               
    tempTxtSearch = '';
    //fromTimer will decide that this function request comes from user action or from timer which used for setting bounds(zoom)    
    ShowVehicleStatusCount();
                                    
    if (typeof oTable == 'undefined' || fromTimer > 0 || PanelId == 12)
    {
        tableSorted();
    }                
    FilterVehicles(0);
            
    if(typeof map !== "undefined" && state == 0)
        ShowHomeData(fromTimer);
}

function ShowVehicleStatusCount() 
{                
    $("#divVehStatus").html($("#hdAllVehStatus").html());          
}

//For Panel Id 3 and 4
function BindData_Panel()
{
    $("#divHome1").hide();
    $("#mapCanvas").hide();
    $("#pnlLeft").width("100%");
    $("#pnlRight").width("0");
    $("#divHome").width("100%");
}

function ChangeHomeGroup()
{
    eval("__doPostBack('Timer2','')");
}

function FillVehicles() {
    var json_data = jQuery.parseJSON(document.getElementById("txtJson").innerHTML);
    if (json_data) {
        var gid = $("#lstGroups").val();
        var selId = "cmbVehicles";
                
        //First Clear first all list 
        $("#" + selId + " > option").remove();
        $.each(json_data.dt, function (index, item) {
            if (item != null) {
                if (item.gid == gid) {
                    $("#" + selId).append('<option value=' + item.vid + '>' + item.vn + '</option>');
                }
                //$("#" + selId).append(new Option(item[14], item[13]));

            } //End if not null
        }); //End for each     
    }//End Json
    var flg1 = document.getElementById("hdFlag1").value;
    if (flg1 == "prdsummary") {
        AddAllOptionInVehicles();
    }
}

function AddAllOptionInVehicles() {
    //---------- Add All in vehicles list always if its not added -------------
    var lstVehicles = document.getElementById("cmbVehicles");
    if (lstVehicles.length > 0 && lstVehicles.options[0].value != "-1") {
        var alloption = document.createElement("option");
        alloption.text = "All";
        alloption.value = "-1";
        lstVehicles.add(alloption, 0);
        lstVehicles.value = -1;
    }
    //-------------------------------------------------------------------------
}       
        </script>

        <!-- Gmap ARa -->
        <script type="text/javascript" language="javascript">
            var PanelId = parseInt("1");
            var geocoder;
            var map,liveTrackImei = "" ,  bounds ,lineSymbol , markerCluster = null , oTable;
            var marker = [],customMarker;
            var sitemarker = [];
            var sitePolyLoc = [];
            var evmarker = [];
            var marloc;
            var lati = 25; // initial latitude
            var longi = 76; // initial longitude
            var latlng = new google.maps.LatLng(lati, longi);
            
            var prev_infowindow = false,mainInfoWindow;        
            var polyloc;
            var i,mcount=0;
            var latmin;
            var latmax;
            var longmin;
            var longmax;
        
            var timer;
            //site formation
            var j = 0;
            var ilat;
            var ilong;
            var flat;
            var flong;
            //routemapper
            var timeouts = [];
            var martimeouts = [];
            var k = 0;
            var eventflag = [];
            var infowindow = [];
            //map state        
            var state = -1;
            var icons = ['images/markers/red-blank.png',
                       'images/markers/grn-blank.png',                        
                       'images/markers/blu-blank.png',                                               
                       'images/markers/pink-blank.png',
                       'images/markers/ltblu-blank.png', 
                       'images/markers/ylw-blank.png',
                       'images/markers/orange-blank.png',    
                       'images/markers/wht-blank.png',
                       'images/markers/placemark_circle.png'];

            var polycols = ['#0000CC', '#CC6600', '#000000', '#990066', '#6699CC', '#336600', '#FF9900', '#FFFFFF'];

            function initialize() {                
                var opt =
                {
                    center: latlng,
                    zoom: 9,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    scaleControl:true
                };
                map = new google.maps.Map(document.getElementById("map"), opt);
                zoom = map.getZoom();
                google.maps.event.addListener(map, 'zoom_changed', function () {
                    var temp = map.getZoom();
                    if ((temp >= 17) && (zoom < 17)) {
                        //   map.setMapTypeId(google.maps.MapTypeId.HYBRID);
                    }
                    if ((temp <= 14) && (zoom > 14)) {
                        map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
                    }
                    zoom = temp;
                });               

                
                google.maps.event.addListener(map,'mousemove',function(point)
                {                                        
                    $('#divMapLatLngt').html(point.latLng.lat().toFixed(6) + ', ' + point.latLng.lng().toFixed(6));
                });

                lineSymbol = {
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
                };
                //strokeColor: '#000624'
                   
                mainInfoWindow = new google.maps.InfoWindow(
                {                           
                    size: new google.maps.Size(50, 50)
                });

                //google.maps.event.addListener(map, 'resize', function () {
                //    if (map)
                //        resizeMap();
                //})
                //google.maps.event.trigger(map, 'resize');

                google.maps.event.addListener(map, 'click', function (event) {
                    if (state == 3 || state == 5) {
                        if (!polyloc) {
                            polyloc = new google.maps.Polyline(polyOpt());
                            polyloc.setMap(map);
                        }

                        var path = polyloc.getPath();
                        path.push(event.latLng);

                        j += 1;
                    }
                });

            }

            //---------- Live Tracking ------------------------------------
            function showLiveTrack(lat, lng, gimei, icon, vehicle, obj) {
                //Map will load when this function calls first Time
                if(PanelId ==2)
                {
                    $("#pnlLeft").width("99%");  
                    $("#pnlRight").width("0");
                    //  showHideMap(0);
                    showMapInDialog();
                }
                else
                {
                    showHideMap(-1);
                }            
                clearMap();
                    
                state = 6;
                latlng = new google.maps.LatLng(lat, lng);

                map.setZoom(14);
                map.setCenter(latlng);

                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);
          
                createMarker(0, 1, -1, 0, vehicle);

                liveTrackImei = gimei;
                liveTrack(gimei, icon, "", vehicle, obj);
            }

            function liveTrack(gimei, icon, lastdt, vehicle, obj) {
                if (state != 6)
                    return;

                var page = "livetrack.aspx?cid=10423&gimei=" + gimei + "&startDate=" + lastdt;                                       
                //alert(page);
                $.ajax( page)
                .done(function(data) {   
                    if(data.length <= 10)
                    {
                        //---Sometimes previous vehicle live track result comes when we switch vehicles 
                        if(liveTrackImei != gimei && liveTrackImei != "")
                            return;
                        //-----------------------------------------------
                    }
                    else
                    {                                         
                        var tmpJson = jQuery.parseJSON(data);  
                        var tmpImei =  tmpJson["imei"];
                        lastdt = tmpJson["dttime"];                  

                        //---Sometimes previous vehicle live track result comes when we switch vehicles 
                        if(liveTrackImei != tmpImei && liveTrackImei != "")
                            return;
                        //-----------------------------------------------

                        var angle =  tmpJson["angle"];                    
                        var speed =tmpJson["speed"];
                        var markerTitle = vehicle;
                        if(speed != "0")
                            markerTitle += " (Speed : " + speed + ")";

                        $.each(tmpJson.loc, function (index, item) {
                            latlng = new google.maps.LatLng(item[0],item[1]);
                            var path = polyloc.getPath();
                            path.push(latlng);
                        });

                        setCenter();

                        if (typeof marloc !== "undefined" && marloc != null)
                            marloc.setMap(null);

                        i = 1;
                        $("#picAngle").rotate(angle);

                        var image;
                        if (icon == '0' || parseInt(icon) >= 10) {
                            image = marImage(icon >= 10 ? (parseInt(icon)-10) : 0);
                        }
                        else {
                            var icol = i;
                            var srtangle = angle * 1 + 11.25;
                            var idir = parseInt(srtangle / 22.5);
                            image = new google.maps.MarkerImage('images/vicons/' + icon + '-' + icol + '-' + idir + '.gif',
                            new google.maps.Size(32, 28),
                            new google.maps.Point(0, 0),
                            new google.maps.Point(16, 14),
                            new google.maps.Size(32, 28)
                            );
                        }

                        marloc = new MarkerWithLabel({
                            position: latlng,
                            flat: true,
                            map: map,
                            icon: image,
                            labelContent: markerTitle,
                            labelAnchor: new google.maps.Point(-7, 32),
                            labelClass: "labels", // the CSS class for the label
                            labelStyle: { opacity: 0.75 }
                        });                        
                    }

                    //--Show info window when idx parameter passed --------------------                      
                    if (typeof obj !== "undefined") {
                        var currow = obj.parentNode.parentNode;
                        google.maps.event.addListener(marloc, 'click', function () {
                            var message = "";
                            var t = document.getElementById('tblData');
                            var tmp;
                            if (t.rows.length > 1) {
                                var collen = t.rows[0].cells.length;
                                for (var j = 2; j < collen; j++) {
                                    var colheading = $(t.rows[0].cells[j]).text();

                                    tmp = $(t.rows[0].cells[j]).find("input");                                    
                                    if(tmp.length > 0)
                                    {                                        
                                        colheading = $(tmp[0]).attr("placeholder");                                                                                                                                                             
                                    }

                                    if (colheading.indexOf("Specifications") == -1 && colheading.indexOf("Info") == -1 && colheading.indexOf("Status") != 0) {
                                        message += colheading + " : " + $(currow.cells[j]).text() + " <br \>";
                                    }
                                }
                            }
                            var infowindow1 = new google.maps.InfoWindow(
                             {
                                 content: message,
                                 size: new google.maps.Size(50, 50)
                             });
                            openInfoWindow(infowindow1, marloc);
                        });
                    }
                    //---------------------------------------------------------------------
                    
                })
                .always(function() {      
                    clearTimeout(timer);
                    var tmpfun = function () { liveTrack(gimei, icon, lastdt, vehicle, obj); };
                    timer = setTimeout(tmpfun, 15000);
                });                   
            }

            function openInfoWindow(infowindow1, strMarker) {
                if (prev_infowindow) {
                    prev_infowindow.close();
                }
                prev_infowindow = infowindow1;
                infowindow1.open(map, strMarker);
            }

            ////function historyTrack(gimei, firstdt, lastdt, vehicle) {
            ////var page = "routetrack.aspx?cid=10423&gimei=" + gimei + "&startDate=" + firstdt + "&lastDate=" + lastdt;
            function historyTrack(gimei, firstdt, lastdt) {
                var page = "routetrack.aspx?gimei=" + gimei + "&startDate=" + firstdt + "&lastDate=" + lastdt;

                $("#divWait").show();
                $.get(page, function (data) {                
                    $("#divWait").hide();

                    var tmp = eval(data);
                    var lt = tmp[0];
                    var lngt = tmp[1];
                    lastdt = tmp[2];

                    var angle = tmp[3];

                    if (lt.length > 0) {
                        showMapInDialog();
                        showRoute(6, lt, lngt, 'Start', 'End');
                    }
                    else
                        alert("Data not found for this date range");
                });
            }

            ////function historyTrack_Bus(gimei, firstdt, lastdt, vehicle) {
            function historyTrack_Bus(company_id, vehicleId, fromdt, todt,fromDate2, toDate2, vehicle) {
                var page = "routetrack.aspx?type=BUS&cid="+company_id+"&vehicleId=" + vehicleId + "&fromdt=" + fromdt + "&todt=" + todt+"&fromDate2="+fromDate2+"&toDate2="+toDate2;
                $.get(page, function (data) {                
                    var tmp = eval(data);
                    var lt = tmp[0];
                    var lngt = tmp[1];
                
                    var sno = tmp[2];
                    var stage = tmp[3];
                    var time = tmp[4];
                    var kms = tmp[5];
                
                    lastdt = tmp[6];
                    var angle = tmp[7];
                    //lastdt = tmp[2];
                    //var angle = tmp[3];

                

                    if (lt.length > 0) {
                        showMapInDialog();
                        showRoute_Bus( 6, lt, lngt, sno,  stage, time, kms, 'Start', 'End');
                    }
                });
            }

            function historyTrack_DashBoard(company_id, vehicleId, toDate, status, tripId) {
                var page = "routetrack.aspx?type=DASHBOARD&cid="+company_id+"&vehicleId=" + vehicleId + "&todate=" + toDate + "&status=" + status + "&tripid="+tripId;
                $.get(page, function (data) {                
                    var tmp = eval(data);
                    var lt = tmp[0];
                    var lngt = tmp[1];
                    var sno = tmp[2];
                    //point==stage
                    var stage = tmp[3];
                    var actAT = tmp[4];
                    var ETOA = tmp[5];
                    var altdAT=tmp[6];
                    var kms = tmp[7];

                    var lat_2 = tmp[8];
                    var long_2 = tmp[9];
                    if (lt.length > 0) {
                        //// 
                        showMapInDialog();
                        //// showRoute_DASHBOARD( 6, lt, lngt, sno,  stage, actAT, ETOA, altdAT, kms, status, 'Start', 'End');
                        showRoute_DASHBOARD( 6, lt, lngt, sno,  stage, actAT, ETOA, altdAT, kms, status,  lat_2, long_2, 'Start', 'End');
                    }
                });
            }

            function clearMap() {
                //alert(state);
                //state =0 home page,1=Show location,2=Show events ,3=Sites & routes,4=route mapper,5=routes list,6=Live track, 7 = Reports
                if (state < 0)
                    return;

                if (timer)
                    clearTimeout(timer);

                if (typeof marker !== "undefined") {
                    for (var i = marker.length - 1; i >= 0 ; i--) {
                        if (typeof marker[i] !== "undefined")
                            marker[i].setMap(null);
                    }

                    //--Clear custom marker                
                    if (typeof customMarker !== "undefined")               
                        customMarker.setMap(null);
                }
           
                marker = [];            

                try {
                    if (typeof marloc !== "undefined" && marloc != null) {
                        marloc.setMap(null);
                        marloc = null;
                    }
                    if (typeof polyloc !== "undefined" && polyloc != null) {
                        polyloc.setMap(null);
                        polyloc = null;
                    }
                }
                catch (err) {
                    //   alert(err);
                }
                marloc = null;
                polyloc = null;

                if (typeof timeouts !== "undefined" && timeouts.length > 0) {
                    for (var i = timeouts.length - 1; i >= 0 ; i--) {
                        clearTimeout(timeouts[i]);
                        clearTimeout(martimeouts[i]);
                    }
                }

                if (typeof infowindow !== "undefined" && infowindow.length > 0) {
                    for (var i = infowindow.length - 1; i >= 0 ; i--) {
                        if (typeof infowindow[i] !== "undefined")
                            infowindow[i].close();
                    }
                }

                //--------Clear marker cluster
                if (typeof markerCluster !== "undefined" && markerCluster != null) {
                    markerCluster.clearMarkers();
                }             

                map.controls[google.maps.ControlPosition.TOP_RIGHT].clear();
                timeouts = [];
                martimeouts = [];
                eventflag = [];
                j = 0;

            }

            var oldShow = false, oldWidth = 500, oldHeight = 500;
            
            function showLocation(lat, lng ,title,showDialog) {
                clearMap();
          
                var mapTitle = "";
                var showInDialog=1;
                if(typeof title !== "undefined")
                    mapTitle = title;

                if(typeof showDialog !== "undefined")
                    showInDialog = showDialog;

                if(showInDialog <= 0)
                {
                    showHideMap(-1,0);
                }

                // state = 1;
                var mapzoom = 14 * 1;
                latlng = new google.maps.LatLng(lat, lng);
                map.setCenter(latlng);
                map.setZoom(mapzoom);
                marloc = new google.maps.Marker({
                    position: latlng,
                    flat: true,
                    title : mapTitle,
                    map: map
                });
                           
                if(showInDialog > 0 )
                {
                    showMapInDialog();
                }               
            }
            function showMapInDialog() {
                if ($("#mapCanvas").is(':hidden'))
                    oldShow = false;
                else
                    oldShow = true;            

                oldWidth = $("#mapCanvas").width();
                oldHeight = $("#mapCanvas").height();
                $("#mapDialog").dialog({
                    closeText: "Close",
                    width: (gWidth / 2 - 20),
                    height: gHeight,
                    position: "right",
                    resizeStop: function (event, ui) { resizeMap(); },
                    open: function (event, ui) {
                        $("#mapCanvas").show();
                        $("#mapCanvas").width((gWidth / 2 - 50));
                        $("#mapCanvas").height(gHeight - 30);
                        resizeMap();
                    },

                    close: function (event, ui) {                   
                        $("#mapCanvas").hide();
                        $("#mapDialog").dialog("destroy");
                        //$(this).removeClass();

                        $(this).removeAttr("style");
                        $(this).appendTo($("#pnlRight"));
                        if (oldWidth > 0)
                            $("#mapCanvas").width(oldWidth);
                        if (oldHeight > 0)
                            $("#mapCanvas").height(oldHeight);
                                        
                        if(state == 0)
                        {      
                            if($("#pnlLeft").width() == "0")
                                showHideMap(1);
                            else if( $("#pnlRight").width() != "0")
                                showHideMap(-1);
                        }

                    }
                });
            }


            function showDivInDialog(id,align) {
                var divAlign="left";
                if (align && align !== undefined ) 
                    divAlign = align;

                var obj = $("#" + id);
                $(obj).dialog({
                    closeText: "Close",
                    width: gWidth / 2,
                    height: gHeight,
                    position: divAlign,
                    close: function (event, ui) {
                        $(obj).dialog("destroy");
                        $(obj).hide();
                    }
                });
            }

            function ShowHomeData(fromTimer) {
                if(typeof map === "undefined")
                    return;

                $("#divPrintMenu").show();
                //Excel report name for Dashboard data
                document.getElementById("hdnrptName").value= "Dashboard";

                clearMap();                        
                state = 0; //Reset its event also

                var json_data = jQuery.parseJSON(document.getElementById("txtJson").innerHTML);
                var fbndflag = 0;
                if (json_data) {
                    //Get list of all selected checkbox values
                    var chkids = ",", chkLen = $('input[name=chkHome]').length; //chklength used becoz this function called before binddata,so we need to check that chkhome created or not

                    // $('input:visible[name=chkHome]:checked').each(function (idx, item1)
                    $('input[name=chkHome]:checked').each(function (idx, item1) {
                        chkids += item1.value + ",";
                    });                

                    var chkFlag = false;
                    var icol;
                    var srtangle;
                    var idir;
                    var image;
                
                    var flgVehNameMarker = true;
                    if($('#chkVehMarker').prop('checked') == false)
                        flgVehNameMarker = false;

                    $.each(json_data.dt, function (index, item) {
                        chkFlag = false;
                        if (chkids.indexOf("," + index + ",") != -1 || chkLen == 0) {
                            chkFlag = true;
                        }

                        //------------- Handle Search Conditions --------------------------------------------
                        var showItem = true;
                        /* if(tempTxtSearch !='' && tempSearchType != "")
                        {
                            var str = '';
                            switch(tempSearchType)
                            {
                                case "vehicle": 
                                    {
                                        str = item.vn.toString().toLowerCase();
                                        break; 
                                    }
                                case "VehSpec": 
                                    {
                                        str = item.vs.toString().toLowerCase();
                                        break; 
                                    }
                                case "nearestlocation": 
                                    {
                                        str = item.nl.toString().toLowerCase();
                                        break; 
                                    }
                                default :
                                    {
                                        break; 
                                    }
                            }                        
                            var n = str.indexOf(tempTxtSearch.toLowerCase());
                            if(parseInt(n)>=0)
                            {
                                showItem = true;                            
                            }
                        }
                        */
                        //---------------------------------------------------------------------------

                        if (item != null && showItem == true) {        
                            if (chkFlag == true && fbndflag == 0) {
                                latmin = item.la * 1;
                                latmax = item.la * 1;
                                longmin = item.ln * 1;
                                longmax = item.ln * 1;
                                fbndflag = 1;
                            }

                            latlng = new google.maps.LatLng(item.la, item.ln);

                            i = 0;
                            if (item.vc == 'palegreen')
                                i = 1;
                            else if (item.vc == '#FFE766')
                                i = 5;

                            var tmpMarkerLabel = "";
                            if(flgVehNameMarker == true)
                                tmpMarkerLabel = item.vn;

                            // createMarker(1, 1, i, index, item.vehicle);
                            if (item.ic == '0' || item.ic == '')
                                createMarker(1, 1, i, index, tmpMarkerLabel);                        
                            else {
                                icol = i;
                                srtangle = item.an * 1 + 11.25;
                                idir = parseInt(srtangle / 22.5);                               

                                if(parseInt(item.ic) >= 10)
                                {                                    
                                    image = marImage(item.ic - 10);
                                }
                                else
                                {
                                    image = new google.maps.MarkerImage('images/vicons/' + item.ic + '-' + icol + '-' + idir + '.gif',
                                    new google.maps.Size(32, 28),
                                    new google.maps.Point(0, 0),
                                    new google.maps.Point(16, 14),
                                    new google.maps.Size(32, 28)
                                    );
                                }

                                marker[index] = new MarkerWithLabel({
                                    position: latlng,
                                    flat: true,
                                    map: map,
                                    icon: image,
                                    labelContent: tmpMarkerLabel,
                                    labelAnchor: new google.maps.Point(-7, 32),
                                    labelClass: "labels", // the CSS class for the label
                                    labelStyle: { opacity: 0.75 }
                                });                                                     
                            }

                            infowin(index, item);

                            if (chkFlag == true) {
                                if (item.la * 1 < latmin) { latmin = item.la * 1; }
                                if (item.la * 1 > latmax) { latmax = item.la * 1; }
                                if (item.ln * 1 < longmin) { longmin = item.ln * 1; }
                                if (item.ln * 1 > longmax) { longmax = item.ln * 1; }
                            }
                            if (chkFlag == false) {                            
                                marker[index].setMap(null);
                            }
                        } //End if not null
                    })//End for each
                
                    //Special case that when its referesh with timer then we will not set its bounds,for other cases we will set its bounds
                    if (fbndflag == 1 && (typeof fromTimer == 'undefined' || fromTimer == 0  ))
                        fitBounds();   

                    CreateMapCluster();

                }  // End json data check null

                function infowin(ijk, item) {               
                    google.maps.event.addListener(marker[ijk], 'mouseover', function () {
                        if (item != null) {
                            var srtangle = item.an * 1;
                            $("#picAngle").rotate(srtangle);
                        }
                    });

                    google.maps.event.addListener(marker[ijk], 'click', function () {
                        var message="";
                   
                        var objRow = $('table#tblData tr#' + ijk + ' td');
                        var t = document.getElementById('tblData');
                        if($(objRow).length > 0 )
                        {
                            $(objRow).each(function(idx) {
                                var strData = $(this).text();
                                if(idx >=2 && strData != "")
                                {
                                    var colheading = $(t.rows[0].cells[idx]).text();
                                    var colHeadingHtml = $(t.rows[0].cells[idx]).html().toLowerCase();
                                    
                                    if(colheading ==''||colheading ==null || colheading== undefined )
                                    {
                                        var xmlString = colHeadingHtml , parser = new DOMParser() 
                                            , doc = parser.parseFromString(xmlString, "text/xml");
                                        doc.firstChild 
                                        $(doc).find("input[type=text]").each(function(ev)
                                        {
                                            colheading= $(this).attr("placeholder");
                                        })
                                    }

                                    if(colHeadingHtml == null || colHeadingHtml  == undefined)
                                        alert(document.getElementById('t.rows[0].cells['+idx+']').placeholder );
                                    if (colHeadingHtml.indexOf("vehicle") != -1)
                                        colheading = "Vehicle";                                        
                                    else if (colHeadingHtml.indexOf("veh spec") != -1) 
                                        colheading = "Specification";
                                    else if (colHeadingHtml.indexOf("last location") != -1 ) 
                                        colheading = "Last Location";                                        

                                    if(colheading.indexOf("Location") != -1)
                                        strData = strData.replace("i  ","");

                                    if (colheading.indexOf("Specifications") == -1 && colheading.indexOf("Info") == -1 && colheading.indexOf("Status") != 0 ) {
                                        message += colheading + " : " +strData + " <br \>";
                                    }
                                }
                            });//End for each
                        }

                        var infowindow1 = new google.maps.InfoWindow(
                        {
                            content: message,
                            size: new google.maps.Size(50, 50)
                        });
                        openInfoWindow(infowindow1, marker[ijk]);
                    });
                }          
            }

            function toggleBounce(id, evtype, srtangle) {
                // typeof marker !== "undefined"
                if (state == 0 && marker[id]) {
                    if (marker[id].getAnimation() == null && evtype == 1) {
                        marker[id].setAnimation(google.maps.Animation.BOUNCE);
                        $("#picAngle").rotate(srtangle);
                    }
                    else if (evtype == 2 && marker[id].getAnimation() != null) {
                        marker[id].setAnimation(null);
                    }
                }
            }

            function showEvents(tblId) {        
                clearMap();

                state = 2;
                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);

                showMapInDialog();
        
                var t = document.getElementById(tblId);
                if (t.rows.length > 1) {
                    var path = polyloc.getPath();
                    bounds = new google.maps.LatLngBounds();

                    for(var i=1; i < t.rows.length; i++)
                    {
                        var collen = t.rows[0].cells.length;
                        currow = t.rows[i];

                        var message = "";
                        for (var j = 1; j < collen; j++) {
                            var colheading = $(t.rows[0].cells[j]).text();

                            if (colheading.indexOf("Map") == -1) {
                                message += colheading + " : " + $(currow.cells[j]).text() + " <br \>";
                            }
                        } //end j
                
                        var objlat =document.getElementById("rptLatLngt" + (i - 1));
                        if(objlat && objlat.value != "")
                        {
                            var strlatlngt = objlat.value.split(",");

                            latlng = new google.maps.LatLng(strlatlngt[0],strlatlngt[1]);
                            path.push(latlng);

                            createMarker(1, 1, 3, i,"Event - " + i);                
                    
                            infowindow[i] = new google.maps.InfoWindow(
                            {
                                content: message,
                                size: new google.maps.Size(50, 50)
                            });

                            google.maps.event.addListener(marker[i],'click', (function(tmpmarker,tmpwindow){ 
                                return function() {
                                    //  infowindow.setContent(content);  infowindow.open(map,marker);
                                    openInfoWindow(tmpwindow,tmpmarker);
                                };
                            })(marker[i],infowindow[i]));
                   
                
                            bounds.extend(latlng);    
                        }
                    }//End i
                    map.fitBounds(bounds);
                }
            }

            function showSites(lat, lng, len, wid) {
                if (len == 0) {
                    //latlng = new google.maps.LatLng(lat, lng);
                    //map.setCenter(latlng);
                    map.setZoom(7);
                    j = 0;
                }
                else if (wid == 0) {
                    latlng = new google.maps.LatLng(lat, lng);
                    map.setCenter(latlng);
                    map.setZoom(13);
                    createMarker(0, 0, -1, 0, '');
                    j = 3;
                }
            }
            function routeMapper(latis, longis, events, mess, errMsg) {                
                clearMap();
                if(errMsg != "")
                {
                    alert(errMsg);
                    return;
                }
                if(latis.length == 0)
                {
                    alert("Data did not found for this search")
                    return;
                }
                
                state = 4;
                eventflag = events;                
                mcount = 0;
                k = 0;                                

                latlng = new google.maps.LatLng(latis[0], longis[0]);
                map.setCenter(latlng);
                map.setZoom(10);

                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);

                createMarker(1, 0, 1, latis.length, 'Start');

                function HomeControl(map) {
                    var controlStartText = document.createElement('DIV');
                    controlStartText.style.margin = "5px";
                    controlStartText.style.backgroundColor = 'white';
                    controlStartText.style.borderStyle = 'solid';
                    controlStartText.style.borderWidth = '1px';
                    controlStartText.style.cursor = 'pointer';
                    controlStartText.style.textAlign = 'center';
                    controlStartText.title = 'Click to start route mapper ';
                    controlStartText.style.fontFamily = 'Arial,sans-serif';
                    controlStartText.style.fontSize = '12px';
                    controlStartText.style.paddingLeft = '4px';
                    controlStartText.style.paddingRight = '4px';
                    controlStartText.innerHTML = 'Start';
                    controlStartText.index = 3;
                    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlStartText);
                    google.maps.event.addDomListener(controlStartText, 'click', timeset);

                    var controlPauseText = document.createElement('DIV');
                    controlPauseText.style.margin = "5px";
                    controlPauseText.style.fontFamily = 'Arial,sans-serif';
                    controlPauseText.style.fontSize = '12px';
                    controlPauseText.style.paddingLeft = '4px';
                    controlPauseText.style.paddingRight = '4px';
                    controlPauseText.innerHTML = 'Pause';
                    controlPauseText.style.backgroundColor = 'white';
                    controlPauseText.style.borderStyle = 'solid';
                    controlPauseText.style.borderWidth = '1px';
                    controlPauseText.style.cursor = 'pointer';
                    controlPauseText.style.textAlign = 'center';
                    controlPauseText.title = 'Click to Stop route mapper ';
                    controlPauseText.index = 2;
                    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlPauseText);

                    google.maps.event.addDomListener(controlPauseText, 'click',pauseRouteMap);

                    var controlLoadText = document.createElement('DIV');
                    controlLoadText.style.margin = "5px";
                    controlLoadText.style.fontFamily = 'Arial,sans-serif';
                    controlLoadText.style.fontSize = '12px';
                    controlLoadText.style.paddingLeft = '4px';
                    controlLoadText.style.paddingRight = '4px';
                    controlLoadText.innerHTML = 'Load All';
                    controlLoadText.style.backgroundColor = 'white';
                    controlLoadText.style.borderStyle = 'solid';
                    controlLoadText.style.borderWidth = '1px';
                    controlLoadText.style.cursor = 'pointer';
                    controlLoadText.style.textAlign = 'center';
                    controlLoadText.title = 'Click to Load All route mapper ';
                    controlLoadText.index = 1;
                    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlLoadText);
                    google.maps.event.addDomListener(controlLoadText, 'click', function () {
                        timeset(1);
                    });
                }

                var sec = document.getElementById("txtRunTime").value;
                var pause = document.getElementById("txtPause").value * 100;                
                autotimer();

                function autotimer() {
                    if ((document.getElementById("txtRunTime").value != sec) || (document.getElementById("txtPause").value * 100 != pause)) {                       
                        setTimeout(timeset, 50);
                    }
                    timer = setTimeout(autotimer, 1000);
                }

                function pauseRouteMap()
                {
                    for (var i = k; i < latis.length; i++) {
                        clearTimeout(timeouts[i]);
                        clearTimeout(martimeouts[i]);
                    }
                    // k = 0; // RT 14.05.2015 It was repeating route map marker when click on start after pause..
                }

                function timeset(flag) {  
                    //Its necessary without it map hanged
                    pauseRouteMap();

                    var loadAll = false;
                    if (flag && flag == 1)
                        loadAll = true;

                    sec = document.getElementById("txtRunTime").value; //user in seconds
                    pause = document.getElementById("txtPause").value * 100; //user in seconds
                    // dt = sec * 100 / latis.length;                    
                    dt=sec * 10;
                    
                    j = 0;

                    var z = 0;
                    for (var i = k; i < latis.length; i++) {
                        if (events[i] > 0) {
                            if (loadAll == true) {                               
                                martimeouts[i] = setTimeout(function () { markerdraw(flag) }, 50 + (i - k));
                            }
                            else
                                martimeouts[i] = setTimeout(markerdraw, (i - k) * dt + j);

                            j = j + pause;
                        }

                        if (loadAll == true) {                            
                            timeouts[i] = setTimeout(pathdraw, 50 + (i - k));
                        }
                        else
                            timeouts[i] = setTimeout(pathdraw, (i - k) * dt + j);
                    }
                }

                function pathdraw() {
                    latlng = new google.maps.LatLng(latis[k], longis[k]);
                    var al = 1 + 300 / dt;
                    /* 
                    //Remove circle marker 
                    if (k % al < 1) {
                        var image = marImage(11);

                        marloc.setMap(null);                        
                        createMarker(0, 0, 11, 0, '');
                    }*/

                    var path = polyloc.getPath();
                    path.push(latlng);
                    setCenter();
                    
                    if (k == latis.length - 1) {
                        if(marker[k])
                            marker[k].setMap(null);

                        latlng = new google.maps.LatLng(latis[k], longis[k]);
                        createMarker(0, 0, 0, 0, 'End');                     
                        
                        if(mess[k]!='' && mess[k]!=null && mess[k]!=undefined)
                        {
                            var infowindow1 = new google.maps.InfoWindow(
                            {
                                content: mess[k],
                                size: new google.maps.Size(50, 50)
                            });
                            google.maps.event.addListener(marloc, 'click', function () {
                                openInfoWindow(infowindow1, marloc);
                            });
                        }
                    }

                    k = k + 1;
                }

                function markerdraw(flag) {
                    var loadAll = false;
                    if (flag && flag == 1)
                        loadAll = true;

                    if (mcount > 0) {
                        if (prev_infowindow) {
                            prev_infowindow.close();
                        }                        
                    }

                    var idx = k; //We are creating new local idx variable becoz l changes outside of this function so only lastinfo window shown
                    latlng = new google.maps.LatLng(latis[idx], longis[idx]);

                    var tmpStr = " " +  (mcount + 1) + " ";
                    createMarker(1, 1, 0, idx,tmpStr);

                    infowindow[idx] = new google.maps.InfoWindow(
                    {
                        content: mess[idx] + "<br /> <a class='ViewLocSave' href=javascript:showReport('sites','" + latis[idx] + "," + longis[idx] + "');>Save Site</a>",
                        size: new google.maps.Size(50, 50)
                    });
                    google.maps.event.addListener(marker[idx], 'click', function () {
                        openInfoWindow(infowindow[idx], marker[idx]);
                    });

                    //Open info window only when its comes with settimeout
                    if (loadAll == false)
                        infowindow[idx].open(map, marker[idx]);
            
                    mcount += 1;
                }

                HomeControl(map);
            }

            function showSitePoly(obj)
            {
                var strjson =  $(obj.parentNode).attr("sitedata");
                if(strjson != "")
                {
                    var objJson = jQuery.parseJSON(strjson);            
                    showRoute(3,objJson[0],objJson[1],"","");
                }        
            }

            function showRoute(intstate, latis, longis, startsite, endsite) {
                clearMap();
                state = intstate;

                latmin = latis[0] * 1;
                latmax = latis[0] * 1;
                longmin = longis[0] * 1;
                longmax = longis[0] * 1;

                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);

                var path = polyloc.getPath();
                for (var i = 0; i < latis.length; i++) {

                    latlng = new google.maps.LatLng(latis[i], longis[i]);
                    path.push(latlng);

                    if (i == 0 && startsite != "") {
                        createMarker(1, 1, 0, i, startsite);
                    }
                    else if (i == latis.length - 1 && endsite != "") {
                        createMarker(1, 1, 0, i, endsite);
                    }
                    else {
                        var image = new google.maps.MarkerImage(icons[8],
                                    new google.maps.Size(18, 18),
                                    new google.maps.Point(0, 0),
                                    new google.maps.Point(9, 9),
                                    new google.maps.Size(18, 18)
                                    );
                        marker[i] = new google.maps.Marker({
                            position: latlng,
                            flat: true,
                            icon: image,
                            map: map,
                            title: i.toString()
                        });

                        /*google.maps.event.addListener(marker[i], 'click', function (event) {
                            marloc.setMap(null);
                            var image = marImage(3);
                            marloc = new google.maps.Marker({
                                position: event.latLng,
                                flat: true,
                                icon: image,
                                map: map
                            });
                        });*/
                    }

                    if (latis[i] * 1 < latmin) { latmin = latis[i] * 1; }
                    if (latis[i] * 1 > latmax) { latmax = latis[i] * 1; }
                    if (longis[i] * 1 < longmin) { longmin = longis[i] * 1; }
                    if (longis[i] * 1 > longmax) { longmax = longis[i] * 1; }
                }

                fitBounds();
            }

            function showRoute_Bus(intstate, latis, longis, sno,  stage, time,  kms,  startsite, endsite) {
                clearMap();
                state = intstate;

                latmin = latis[0] * 1;
                latmax = latis[0] * 1;
                longmin = longis[0] * 1;
                longmax = longis[0] * 1;

                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);

                var path = polyloc.getPath();
                var sn='';
                for (var i = 0; i < latis.length; i++) {

                    latlng = new google.maps.LatLng(latis[i], longis[i]);
                    path.push(latlng);


                    if(sno[i]!=null && sno[i].toString()!='')
                    {
                        if(sn!=sno[i].toString())
                        {
                            sn= sno[i].toString();
                            ////createMarker(1, 1, 0, i, stage[i].toString());
                            createMarker(1, 1, 0, i, '<p>'+stage[i].toString()+'<br/> kms: '+ kms[i].toString()+ '<br/>Time: '+ time[i].toString()+  '</p>');
                        }
                
                    }
            
                        ////if (i == 0 && startsite != "") {
                        ////    createMarker(1, 1, 0, i, startsite);
                        ////}
                        ////else if (i == latis.length - 1 && endsite != "") {
                        ////    createMarker(1, 1, 0, i, endsite);
                        ////}
                    else {
                        var image = new google.maps.MarkerImage(icons[8],
                                    new google.maps.Size(18, 18),
                                    new google.maps.Point(0, 0),
                                    new google.maps.Point(9, 9),
                                    new google.maps.Size(18, 18)
                                    );
                        marker[i] = new google.maps.Marker({
                            position: latlng,
                            flat: true,
                            icon: image,
                            map: map,
                            title: i.toString()
                        });

                        /*google.maps.event.addListener(marker[i], 'click', function (event) {
                            marloc.setMap(null);
                            var image = marImage(3);
                            marloc = new google.maps.Marker({
                                position: event.latLng,
                                flat: true,
                                icon: image,
                                map: map
                            });
                        });*/
                    }

                    if (latis[i] * 1 < latmin) { latmin = latis[i] * 1; }
                    if (latis[i] * 1 > latmax) { latmax = latis[i] * 1; }
                    if (longis[i] * 1 < longmin) { longmin = longis[i] * 1; }
                    if (longis[i] * 1 > longmax) { longmax = longis[i] * 1; }
                }
        
                fitBounds();
            }

            function showRoute_DASHBOARD(intstate, latis, longis, sno,  stage, actAT,  ETOA, altdAT, kms, status, latis_2, longis_2, startsite, endsite) {
                clearMap();
                state = intstate;

                latmin = latis[0] * 1;
                latmax = latis[0] * 1;
                longmin = longis[0] * 1;
                longmax = longis[0] * 1;

                polyloc = new google.maps.Polyline(polyOpt());
                polyloc.setMap(map);

                var path = polyloc.getPath();
                var sn='';
        
                if(status=='Completed')
                {
                    for (var i = 0; i < latis_2.length; i++) {
                        latlng = new google.maps.LatLng(latis_2[i], longis_2[i]);
                        path.push(latlng);
        
                        var image = new google.maps.MarkerImage(icons[8],
                                        new google.maps.Size(18, 18),
                                        new google.maps.Point(0, 0),
                                        new google.maps.Point(9, 9),
                                        new google.maps.Size(18, 18)
                                        );
                        marker[i] = new google.maps.Marker({
                            position: latlng,
                            flat: true,
                            icon: image,
                            map: map,
                            title: i.toString()
                        });
                    }
                }
                        
                for (var i = 0; i < latis.length; i++) {

                    latlng = new google.maps.LatLng(latis[i], longis[i]);
                    ////path.push(latlng);
                    if(status!='Completed')
                    {path.push(latlng);}
            
                    if(sno[i]!=null && sno[i].toString()!='')
                    {
                        if(sn!=sno[i].toString())
                        {
                            sn= sno[i].toString();

                            if(status=='Completed')
                                createMarker(1, 1, 0, i, '<p>'+ (i==0?'-Start-<br />':'')+ (i==latis.length-1?'-End-<br/>':'')+  stage[i].toString()+'<br/>Kms : '+kms[i].toString()+'<br />Act. AT : '+ actAT[i].toString()+ '</p>');
                            else if(status=='Pending')
                                createMarker(1, 1, 0, i, '<p>'+ (i==0?'-Start-<br />':'')+ (i==latis.length-1?'-End-<br/>':'')+ stage[i].toString()+'<br/>Altd. AT : '+ altdAT[i].toString()+ '</p>');
                            else if(status=='Runing')
                            {
                                if(ETOA[i].toString()=='')
                                    createMarker(1, 1, 0, i, '<p>'+ (i==0?'-Start-<br />':'')+ (i==latis.length-1?'-End-<br/>':'')+ stage[i].toString()+'<br/>Kms : '+kms[i].toString()+'<br />Act. AT : '+ actAT[i].toString()+ '</p>');
                                else
                                    createMarker(1, 1, 0, i, '<p>'+ (i==0?'-Start-<br />':'')+ (i==latis.length-1?'-End-<br/>':'')+ stage[i].toString()+'<br/>Kms : '+kms[i].toString()+'<br />ETOA : '+ ETOA[i].toString()+ '</p>');
                            }
                        }
                    }
                    else {
                        var image = new google.maps.MarkerImage(icons[8],
                                    new google.maps.Size(18, 18),
                                    new google.maps.Point(0, 0),
                                    new google.maps.Point(9, 9),
                                    new google.maps.Size(18, 18)
                                    );
                        marker[i] = new google.maps.Marker({
                            position: latlng,
                            flat: true,
                            icon: image,
                            map: map,
                            title: i.toString()
                        });
                    }

                    if (latis[i] * 1 < latmin) { latmin = latis[i] * 1; }
                    if (latis[i] * 1 > latmax) { latmax = latis[i] * 1; }
                    if (longis[i] * 1 < longmin) { longmin = longis[i] * 1; }
                    if (longis[i] * 1 > longmax) { longmax = longis[i] * 1; }
                }
                fitBounds();
            }

            function fitBounds() {
                if(typeof map !== "undefined")
                {
                    var southWest = new google.maps.LatLng(latmin, longmin);
                    var northEast = new google.maps.LatLng(latmax, longmax);
                    bounds = new google.maps.LatLngBounds(southWest, northEast);

                    map.fitBounds(bounds);
                    zoom = map.getZoom();
                    if (zoom > 16) {
                        map.setZoom(16);
                    }
                    // map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
                }
            }

            function distance(x1, y1, x2, y2) {
                var dis = 111200 * Math.sqrt((x1 - x2) * (x1 - x2) + (Math.cos(x1 * 22.0 / 7 / 180) * (y1 - y2)) * (Math.cos(x1 * 22.0 / 7 / 180) * (y1 - y2)));
                return dis;
            }

            function setCenter() {
                bounds = map.getBounds();
                if (bounds.contains(latlng) == 0) {
                    map.panTo(latlng);
                }
            }

            function marImage(posi) {
                var image = new google.maps.MarkerImage(icons[posi],
                            new google.maps.Size(32, 28),
                            new google.maps.Point(0, 0),
                            new google.maps.Point(16, 28),
                            new google.maps.Size(32, 28)
                            );
                return image;
            }

            function polyOpt() {                                       
                var polyOptions = {
                    strokeColor: '#000000',
                    strokeOpacity: 0.7,
                    strokeWeight: 3,
                    icons: [{
                        icon: lineSymbol,
                        offset: '100%'
                    }]
                }
                return polyOptions;
            }

            function createMarker(arrflag, labflag, image, counter, labname) {
                if (arrflag == 1 && labflag == 1 && image >= 0) {
                    marker[counter] = new MarkerWithLabel({
                        position: latlng,
                        flat: true,
                        map: map,
                        icon: marImage(image),
                        labelContent: labname,
                        labelAnchor: new google.maps.Point(-7, 46),
                        labelClass: "labels", // the CSS class for the label
                        labelStyle: { opacity: 0.75 }
                    });
                }
                else if (arrflag == 0 && labflag == 1 && image < 0) {
                    marloc =  new MarkerWithLabel({
                        position: latlng,
                        flat: true,
                        map: map,                
                        labelContent: labname,
                        labelAnchor: new google.maps.Point(-7, 46),
                        labelClass: "labels", // the CSS class for the label
                        labelStyle: { opacity: 0.75 }
                    });
                }                        
                else if (arrflag == 1 && labflag == 0 && image >= 0) {
                    marker[counter] = new google.maps.Marker({
                        position: latlng,
                        flat: true,
                        icon: marImage(image),
                        map: map,
                        title : labname
                    });
                }
                else if (arrflag == 0 && labflag == 0 && image >= 0) {
                    marloc = new google.maps.Marker({
                        position: latlng,
                        flat: true,
                        icon: marImage(image),
                        map: map,
                        title : labname
                    });
                }            
                else if (arrflag == 0 && labflag == 0 && image < 0) {
                    marloc = new google.maps.Marker({
                        position: latlng,
                        flat: true,
                        map: map,
                        title : labname
                    });
                }
                else if (arrflag == -1 && labflag == -1 && image >= -1) {
                    marker[counter] = new google.maps.Marker({
                        position: latlng,
                        flat: true,
                        map: map,
                        title : labname
                    });
                }

            }

            function createImageMarker(labflag,latlng,image, labname) {
                if(labflag > 0 )
                {
                    return new MarkerWithLabel({
                        position: latlng,
                        flat: true,
                        map: map,
                        icon: image,
                        labelContent: labname,
                        labelAnchor: new google.maps.Point(-7, 46),
                        labelClass: "labels", // the CSS class for the label
                        labelStyle: { opacity: 0.75 }
                    });
                }
                else
                {
                    return  new google.maps.Marker({
                        position: latlng,
                        flat: true,
                        icon: image,
                        map: map,
                        title : labname
                    });
                }
            }

            function createSiteMarker() {
                var txtSite = $.trim($("#txtMapSiteSearch").val()).toLowerCase();                
                var flgHide = false;
                if ($("#btnMapSiteSearch").val().indexOf("Show") == -1) {         
                    //----------- Clear sites marker and its polyloc --------------------------------------
                    for (var i = 0; i < sitemarker.length; i++) {
                        sitemarker[i].setMap(null);
                    }
                    sitemarker = [];

                    if (typeof sitePolyLoc !== "undefined" && sitePolyLoc != null) {
                        for (var i = sitePolyLoc.length - 1; i >= 0 ; i--) {
                            if (typeof sitePolyLoc[i] !== "undefined") {
                                sitePolyLoc[i].setMap(null);
                                sitePolyLoc[i] = null;
                            }
                        }
                    }
                    sitePolyLoc = [];
                    //--------------------------------------------------------------------------------------

                    if(state == 7)
                        state = 0;
                }
                else {
                    if(state == 0)
                        state = 7;

                    flgHide = true;            

                    bounds = new google.maps.LatLngBounds();
                    var idx = 0;

                    var strCond = "";
                    if(txtSite != "")
                        strCond = '[sitename*="' + txtSite + '"]';

                    $('#gvSites tbody tr' + strCond).each(function () {
                        var jsonSites =jQuery.parseJSON( $(this).attr("sitedata"));
                        var siteName =  $(this).attr("sitename");                
                        if (jsonSites != null) {                    
                            var image = new google.maps.MarkerImage('images/pushpin.png',
                            new google.maps.Size(32, 32),
                            new google.maps.Point(0, 0),
                            new google.maps.Point(16, 14),
                            new google.maps.Size(32, 32)
                            );
                            var tmpItem = jsonSites[2].toString().split(",");
                            var latlng = new google.maps.LatLng(jsonSites[2][0], jsonSites[2][1]);
                            bounds.extend(latlng);  

                            sitemarker[idx] = new MarkerWithLabel({
                                position: latlng,
                                flat: true,
                                map: map,
                                icon: image,
                                labelContent:siteName ,
                                labelAnchor: new google.maps.Point(7, -10),
                                // labelClass: "labels", // the CSS class for the label
                                labelStyle: { opacity: 0.75 }
                            });
                          
                            google.maps.event.addListener(sitemarker[idx], 'click', function () {     
                                var strPage = "report.aspx?flag=nearsiteveh&isinline=1&cid=10423&sitename=" + siteName;                                
                                getPageDataInline(strPage);                                
                            });

                            //------------Create site poly ------------------------
                            if("0" == "1")
                            {
                                sitePolyLoc[idx] = new google.maps.Polyline(polyOpt());
                                sitePolyLoc[idx].setMap(map);

                                var path = sitePolyLoc[idx].getPath();
                
                                var lati = jsonSites[0],longi = jsonSites[1];
                                $.each(lati, function (index, item) {
                                    latlng = new google.maps.LatLng(lati[index], longi[index]);
                                    path.push(latlng);     
                            
                                    bounds.extend(latlng);  
                                });
                            }
                            //-----------------------------------------------------

                            idx++;    
                    
                        } //End if json sites                   
                    }); //End each

                    if(idx > 0)
                        map.fitBounds(bounds);
                    else
                    {
                        alert("Sites did not found");
                        return;
                    }
                }//End else
        
                if(flgHide == true)
                {            
                    $("#btnMapSiteSearch").val("Hide Sites");
                    $("#txtMapSiteSearch").hide();
                }
                else
                {
                    $("#btnMapSiteSearch").val("Show Sites");
                    $("#txtMapSiteSearch").show();
                }                 
            }
        </script>

        <script language="javascript" type="text/javascript">
            function ignoreEnter(e) {
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                }
            };
            function searchvehicles(e) {
                    
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                    return false; //this will stop the default event triggering 
                }
                    
                var txtsearch = document.getElementById("txtSearch");
                var strcondition = "";
                if (txtsearch.value != "")
                {
                    //strcondition = txtsearch.value.toLowerCase();
                    strcondition = txtsearch.value;
                }

                if (strcondition.length > 0) 
                {
                    $('#tblData tbody tr').hide();                        
                    $('#tblData tbody tr td[id=tdv]:containsIN(' + strcondition + ')').parent().show();

                    tempTxtSearch = strcondition;
                    tempSearchType='vehicle';//vehicle
                }
                else
                {
                    $('#tblData tr').show();
                    tempTxtSearch='';
                }

                /* if (strcondition.length > 0) {
                     $('#tblData tbody tr[id!="' + strcondition + '"]').hide();
                     $('#tblData tr[id*="' + strcondition + '"]').show();
                     tempTxtSearch = strcondition;
                     tempSearchType='vehicle';//vehicle
                 }
                 else{
                     $('#tblData tr').show();
                     tempTxtSearch='';
                 }*/                
            }
                
            function searchvehiclesAlt(e) {
                    
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                    return false; //this will stop the default event triggering 
                }
                    
                var txtsearch = document.getElementById("txtSearchAlt");

                var strcondition = "";
                if (txtsearch.value != "")
                {
                    //   strcondition += txtsearch.value.toLowerCase();
                    strcondition += txtsearch.value;
                }
                if (strcondition.length > 0) {                        
                    $('#tblDataAlt tbody tr').hide();                        
                    $('#tblDataAlt tbody tr td[id=tdv]:containsIN(' + strcondition + ')').parent().show();

                    //     $('#tblDataAlt tbody tr[id!="' + strcondition + '"]').hide();
                    //     $('#tblDataAlt tr[id*="' + strcondition + '"]').show();
                    tempTxtSearch = strcondition;
                    tempSearchType='vehicle';//vehicle
                }
                else{
                    $('#tblDataAlt tr').show();
                    tempTxtSearch='';
                }                
            }

            function searchVehSpec(e) {
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                    return false; //this will stop the default event triggering 
                }

                var txtSearchVehSpec = document.getElementById("txtSearchVehSpec");
                var strcondition = "";
                if (txtSearchVehSpec.value != "")
                {
                    //   strcondition = txtSearchVehSpec.value.toLowerCase();
                    strcondition = txtSearchVehSpec.value;
                }

                if (strcondition.length > 0) {
                    $('#tblData tbody tr').hide();                        
                    $('#tblData tbody tr td[id=tds]:containsIN(' + strcondition + ')').parent().show();

                    //$('#tblData tbody tr[class!="' + strcondition + '"]').hide();
                    //$('#tblData tr[class*="' + strcondition + '"]').show();

                    tempTxtSearch = strcondition;
                    tempSearchType='VehSpec';
                }
                else{
                    $('#tblData tr').show();
                    tempTxtSearch='';
                }                
            }
            
            function searchLastLocation(e) {
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                    return false; //this will stop the default event triggering 
                }

                var txtlastlocation = document.getElementById("txtlastlocation");

                var strcondition = "";
                if (txtlastlocation.value != "")
                {
                    // strcondition = txtlastlocation.value.toLowerCase();
                    strcondition = txtlastlocation.value;
                }
                if (strcondition.length > 0) {
                    $('#tblData tbody tr').hide();                        
                    $('#tblData tbody tr td[id=tdl]:containsIN(' + strcondition + ')').parent().show();
                    //$('#tblData tbody tr[lastloc!="' + strcondition + '"]').hide();
                    //$('#tblData tr[lastloc*="' + strcondition + '"]').show();

                    tempTxtSearch = strcondition;
                    tempSearchType='nearestlocation';
                }
                else{
                    $('#tblData tr').show();
                    tempTxtSearch='';
                }                
            }

            function searchGvSites(e) {
                if (e.keyCode == 13 || e.which == 13) { // enter    
                    e.preventDefault();
                    return false; //this will stop the default event triggering 
                }
                var txtSearch = document.getElementById("txtGvSiteSearch");

                var strcondition = "";
                if (txtSearch.value != "")
                    strcondition += txtSearch.value.toLowerCase();
                
                var tblData = "gvSites";
                if (strcondition.length > 0) {
                    $('#' + tblData + ' tbody tr[sitename!="' + strcondition + '"]').hide();
                    $('#' + tblData + ' tr[sitename*="' + strcondition + '"]').show();

                    tempTxtSearch = strcondition;
                    tempSearchType='gvsites';
                }
                else{
                    $('#' + tblData + ' tr').show();
                    tempTxtSearch='';
                }                
            }
                
            function SearchReport() {
                var cid =parseInt("10423");
                var flg1 = document.getElementById("hdFlag1").value;               
                var grpid = '';
                if ('1' == 1)
                    grpid = $("#lstGroups").val();

                var lstVehicles = document.getElementById("cmbVehicles");
                var txtFromDate = document.getElementById("txtFromDate");
                var txtToDate = document.getElementById("txtToDate");
                var txtRunTime = document.getElementById("txtRunTime");
                var txtGrade = document.getElementById("txtGrade");

                var txtFMin = document.getElementById("txtFMin");
                var txtTMin = document.getElementById("txtTMin");
                var txtInterval = document.getElementById("txtInterval");
                var lstSite1 = document.getElementById("lstSite1");
                var lstSite2 = document.getElementById("lstSite2");

                var vehicle = "";
                if (lstVehicles.length > 0  && $('#trVehicles').is(':visible'))
                    vehicle = lstVehicles.options[lstVehicles.selectedIndex].text;

                var site1 = "";
                if (lstSite1.length > 0)
                    site1 = encodeURIComponent(lstSite1.options[lstSite1.selectedIndex].text);
                var site2 = "";
                if (lstSite2.length > 0)
                    site2 = encodeURIComponent(lstSite2.options[lstSite2.selectedIndex].text);

                var intervalType = (document.getElementById("rdHours").checked == true ? "H" : "M");
                if (lstVehicles.value == "" && $('#trVehicles').is(':visible')) {
                    alert("Please select Vehicles");
                    lstVehicles.focus();
                    return false;
                }
                if (txtFromDate.value == "" && $('#trStartDate').is(':visible')) {
                    alert("Please select start date");
                    txtFromDate.focus();
                    return false;
                }

                if (txtToDate.value == "" && $('#trEndDate').is(':visible')) {
                    alert("Please select end date");
                    txtToDate.focus();
                    return false;
                }

                ////if (txtRunTime.value == "" && $('#trRuntime').is(':visible')) {
                ////    alert("Please enter stoppage value");
                ////    txtRunTime.focus();
                ////    return false;
                ////}
                if (flg1 != "salestypewiseanalysis" && flg1 != "transporterperformance" && flg1 != "transporterperformance2")
                {
                    if (txtRunTime.value == "" && $('#trRuntime').is(':visible')) {
                        alert("Please enter stoppage value");
                        txtRunTime.focus();
                        return false;
                    }
                }

                if (txtGrade.value == "" && $('#trGrade').is(':visible')) {
                    alert("Please enter grade value");
                    txtGrade.focus();
                    return false;
                }

                if (flg1 == "routedev")
                    var flg2 = document.getElementById("hdFlag2").value;
                else
                    var flg2 = document.getElementById("cmbSenT1").value;

                var flg22 = document.getElementById("cmbSenT2").value;

                //---------- Date validation for few reports ------------------
                if ($('#trEndDate').is(':visible') && (flg1 == "prdsummary" || flg1 == "routemap" || flg1 == "eventlog")) {
                    var maxDays = 20;
                    if(cid == 6163 || cid == 12169 || cid == 28787)
                        maxDays =31 ;

                    var tmpsdate = cDate(txtFromDate.value);
                    var tmpedate = cDate(txtToDate.value);
                    if (tmpedate < tmpsdate) {
                        alert("Please select proper date range.");
                        return false;
                    }
                    else if (DateDiff.inDays(tmpsdate, tmpedate) > maxDays) {
                        alert("Please enter a period smaller than " + maxDays + " days");
                        return false;
                    }
                }
                //-------------------------------------------------------------

                var page = "";
                var qrystr = "&cid=10423&vehicleid=" + lstVehicles.value + "&fdate=" + txtFromDate.value + "&fmin=" + txtFMin.value + "&tdate=" + txtToDate.value + "&tmin=" + txtTMin.value + "&rtime=" + txtRunTime.value;              
                if (flg1 == "routemap" || flg1 == "eventlog") {
                    qrystr += "&freq=" + $("#txtFreq").val();

                    if ($("#cbStoppage").is(':checked') == true)
                        qrystr += "&cbstoppage=1&stoppage=" + $("#tbStoppage").val();
                    if ($("#cbOverSpeed").is(':checked') == true)
                        qrystr += "&cboverspeed=1&overspeed=" + $("#tbOverSpeed").val();
                    if ($("#cbLocation").is(':checked') == true)
                        qrystr += "&cbLocation=1&location=" + $("#tbLocation").val();

                    if ($("#cbtime").is(':checked') == true)
                        qrystr += "&cbtime=1&timeint=" + $("#tbTimeInt").val();

                    if ($("#cbSite").is(':checked') == true)
                        qrystr += "&cbsite=1";
                    if ($("#cbLocality").is(':checked') == true)
                        qrystr += "&cblocality=1";
                    if ($("#cbsen11").is(':checked') == true)
                        qrystr += "&cbsen11=1";
                    if ($("#cbsen12").is(':checked') == true)
                        qrystr += "&cbsen12=1";

                    if ($("#cbsen13").is(':checked') == true)
                        qrystr += "&cbsen13=1";
                    if ($("#cbsen14").is(':checked') == true)
                        qrystr += "&cbsen14=1";
                    if ($("#cbsen15").is(':checked') == true)
                        qrystr += "&cbsen15=1";
                    if ($("#cbsen16").is(':checked') == true)
                        qrystr += "&cbsen16=1";

                    if ($("#cbsen21").is(':checked') == true)
                        qrystr += "&cbsen21=1";
                    if ($("#cbsen22").is(':checked') == true)
                        qrystr += "&cbsen22=1";
                    if ($("#cbsen31").is(':checked') == true)
                        qrystr += "&cbsen31=1";
                   
                    if ($("#cbNotReach").is(':checked') == true)
                        qrystr += "&cbnotreach=1";

                    page = "Routemap.aspx?";
                    if (flg1 == "eventlog") {
                        page = "eventlog.aspx?";
                    }
                }
                else if (flg1 == "mileage") {
                    page = "Mileage.aspx?";
                }
                else if (flg1 == "historytrack") {
                    page = "Historytrack.aspx?";
                }                
                else {
                    page = "report.aspx?flag=" + flg1 + "&flag2=" + flg2 + "&flag22=" + flg22;
                    //// qrystr += "&grade=" + txtGrade.value + "&interval=" + txtInterval.value + "&intervaltype=" + intervalType + "&site1=" + site1 + "&site2=" + site2;
                    qrystr += "&grade=" + txtGrade.value + "&interval=" + txtInterval.value + "&intervaltype=" + intervalType + "&site1=" + site1 + "&site2=" + site2 +"&siteWorkShop="+ $("#txtConsignor").val();

                    if (flg1 == "brtripsummary" )
                    {
                        if ($("#chk_Br_timeDeviate").is(':checked') == true)
                            qrystr += "&brtimedeviate=" + $("#txt_Br_timeDeviate").val();
                        if ($("#chk_Br_distDeviate").is(':checked') == true)
                            qrystr += "&brdistdeviate=" + $("#txt_Br_distDeviate").val();
                        if ($("#chk_Br_Stoptime").is(':checked') == true)
                            qrystr += "&brstoptime=" + $("#txt_Br_Stoptime").val();
                        if ($("#chk_Br_speed").is(':checked') == true) 
                            qrystr += "&brspeed=" + $("#txt_Br_Speed").val();
                    }
                }
                page += qrystr + "&vehicle=" + vehicle;
                if (grpid != "")
                    page += "&gid=" + grpid;

                if($("#hdnChkAll").val()==1)
                {
                    page += "&allVeh=1";
                }
                
                if($("#trCoSties").is(":visible")) {
                    //page += "&siteName=cmbCoSties".value;
                    var siteName = document.getElementById("cmbCoSties").value;
                    if(siteName=='-1' || siteName=='Select')
                        siteName='';
                    page += '&sitename='+siteName;
                }

                if (flg1 == "bustripsvehicleallocation" ||
                    flg1 == "bustripsroutewisegeofence" ||
                    flg1 == "bustripsroutetimings"){
                    if($("#trRoutes").is(":visible")) {
                        var routeId = document.getElementById("cmbRoute").value;
                        page += '&routeid='+routeId;
                    }
                }


                // alert(page);
                // document.write(page);
                $("#divWait").show();

                $.get(page, function (data) {
                    document.getElementById("mapCanvas").style.display = "none";                        
                    $("#divWait").hide();

                    data = $.trim(data);
                    if (flg1 == "routemap") {
                        clearMap(); // 15.05.2015
                        $("#mapCanvas").show();
                        SetWidth(350);
                        eval(data);
                        $('#divResult').html("");

                        //case if no Route found for selected vehicle 15.05.2015
                        var tmpp= "";
                        tmpp=data;
                        if(tmpp==null || tmpp=='\r\n'){
                            alert("No Route Found for this Vehicle till date");
                        }
                    }
                    else if (flg1 == "historytrack") {                           
                        if (data != "") {
                            var tmp = eval(data);
                            showLocation(tmp[0], tmp[1], tmp[2],0);
                        }
                        else
                        {                            
                            alert("No data found for this date");
                        }
                    }
                    else {
                        $('#divResult').html(data);
                        $("#divPrintMenu").show();

                        if (trim($('#divResult').text()) == "") {
                            alert("No data found.");
                        }
                    }

                    //$('#divResult a[rel*=facebox]').facebox();
                    //alert('Load was performed.');
                });

            }

            function chkAddEditSite() {
               
                
                var tmpSite = document.getElementById("txtSite");
                if (tmpSite.value == "") {
                    alert("Please enter value for Site Name.");
                    tmpSite.focus();
                    return false;
                }
                else if (polyloc == null || polyloc.getPath().getLength() <= 2) {
                    alert("Please create site first on Map");
                    return false;
                }
                else {
                    document.getElementById("hdSiteLatLngt").value = ConveryPolyToJson(polyloc.getPath().getArray()); // polyloc.getPath().getArray().toString();                                          
                }
               
        }

        function getPageDataInline(strpage) {           
            if(PanelId=3)
            {
                $("#divWait2").show();
            }
            else{
                $("#divWait").show();
            }
            $.get(strpage, function (data) {                      
                $("#divWait").hide();
                $("#divWait2").hide();
                $("#pnlDialog").show();

                $("#pnlDialog").html(data);
                showDivInDialog("pnlDialog");
            });
        }

        function ConveryPolyToJson(arr) {
            var myarray = [];
            var myJSON = "";

            if (arr.length > 0) {
                for (var i = 0; i < arr.length; i++) {
                    var item = {
                        "lat": arr[i].lat(),
                        "lng": arr[i].lng()
                    };
                    myarray.push(item);
                }
                myJSON = JSON.stringify(myarray);
            }
            return myJSON;
        }

        function chkAddEditRoute() {
            var txtroute = document.getElementById("txtRouteName");
            var txtdist = document.getElementById("txtRouteDist");

            if (txtroute.value == "") {
                alert("Please enter route name.");
                txtroute.focus();
                return false;
            }
            else if (txtdist.value == "" || isNaN(txtdist.value) == true) {
                alert("Please enter valid value for distance.");
                txtdist.focus();
                return false;
            }
            else if (polyloc == null || polyloc.getPath().getLength() <= 2) {
                alert("Please create route first on Map");
                return false;
            }
            else {
                document.getElementById("hdRouteLatLngt").value = ConveryPolyToJson(polyloc.getPath().getArray());
            }
}
        </script>

        <script type="text/javascript">
            function LoadAltPanel()
            {
                showReport('AltPanel1');
                eval("__doPostBack('btnAltPanel','')");
            }

            function showToolTip(obj, e, lat, lng) {
                hideToolTip(); //Hide tooltip if any one has opened

                if (lat == 0 || lng == 0)
                    return;

                var oldTitle = $(obj).attr("title");
                if (typeof oldTitle != 'undefined' && oldTitle != "") {
                    return;
                }

                if (!geocoder)
                    geocoder = new google.maps.Geocoder();

                if (geocoder) {
                    latlng = new google.maps.LatLng(lat, lng);
                    geocoder.geocode({ 'latLng': latlng }, function (results, status) {
                        var success = false;
                        var str = "";
                        if (status == google.maps.GeocoderStatus.OK) {
                            $.each(results, function () {
                                // str += this.formatted_address + "-" + this.types.join(", ") + "\n";
                                str += this.formatted_address;
                                return false; //This will work as break in loop,Break command is not working in jquery loop
                            });
                            if (str == "")
                                str = "Address did not found";
                            else
                                success = true;

                        } else {
                            str = "Geocoder failed due to: " + status;
                        }

                        if (str != "") {
                            if (success == true) {
                                //Set object title so it will show auto tooltip,we did not shown our tooltip
                                $(obj).attr("title", str);
                            }
                            else {
                                //------------------   
                                var tip = $("#divToolTip");
                                tip.html(str);
                                moveToolTip(e);
                                tip.show(); //Show tooltip
                                //-----------------
                            }
                        }
                    });
                }
            }
            function hideToolTip() {
                var tip = $("#divToolTip");
                tip.hide(); //Hide tooltip	
            }
            function moveToolTip(e) {
                var tip = $("#divToolTip");
                /*  var mousex = e.pageX + 20; //Get X coodrinates
                  var mousey = e.pageY + 20; //Get Y coordinates
                  var tipWidth = 200; //tip.width(); //Find width of tooltip
                  var tipHeight = 10; //tip.height(); //Find height of tooltip
                  //Distance of element from the right edge of viewport
                  var tipVisX = $(window).width() - (mousex + tipWidth);
                  //Distance of element from the bottom of viewport
                  var tipVisY = $(window).height() - (mousey + tipHeight);
                  if (tipVisX < 20) { //If tooltip exceeds the X coordinate of viewport
                      mousex = e.pageX - tipWidth - 20;
                  } if (tipVisY < 20) { //If tooltip exceeds the Y coordinate of viewport
                      mousey = e.pageY - tipHeight - 20;
                  }                
                  tip.css({ top: mousey, left: mousex });
                  */
                var tooltipoffsets = [20, -10];
                var x = e.pageX + tooltipoffsets[0], y = e.pageY + tooltipoffsets[1]
                var tipw = tip.outerWidth(), tiph = tip.outerHeight(),

                x = (x + tipw > $(document).scrollLeft() + $(window).width()) ? x - tipw - (tooltipoffsets[0] * 2) : x
                y = (y + tiph > $(document).scrollTop() + $(window).height()) ? $(document).scrollTop() + $(window).height() - tiph - 10 : y
                tip.css({ left: x, top: y })
            }

            function SearchGeocodeAddress() {                       
                var address = $("#txtMapSearch").val();
                if(address == "")
                {
                    alert("Please enter text for searching");
                    $("#txtMapSearch").focus();
                    return;
                }

                if (!geocoder)
                    geocoder = new google.maps.Geocoder();

                geocoder.geocode({'address': address }, function(results, status) {
                    if (status == google.maps.GeocoderStatus.OK) {
                        map.setCenter(results[0].geometry.location);
                        map.setZoom(15);

                        var tmpImg = marImage(6);
                        customMarker = createImageMarker(-1,results[0].geometry.location,tmpImg,address);
                    }
                    else {
                        alert("Address did not found : " + status);
                    }
                });
            }

            function ShowAllVehicleMarkers(vehicle_data) {
                $("#divPrintMenu").show();

                clearMap();                  

                var fbndflag = 0;
                var showLoc='no';
                var chkFlag = true;
                if (vehicle_data) {                       
                    $.each(vehicle_data.dt, function (index, item) {                            
                        if (item != null) {        
                            if (chkFlag == true && fbndflag == 0) {
                                latmin = item.latitude * 1;
                                latmax = item.latitude * 1;
                                longmin = item.longitude * 1;
                                longmax = item.longitude * 1;
                                fbndflag = 1;
                            }
                            
                            latlng = new google.maps.LatLng(item.latitude, item.longitude);
                            if(showLoc=='no'){
                                showLocation(item.latitude, item.longitude)
                                showLoc='yes';
                            }
                            else
                            {
                                //showLocation(item.latitude, item.longitude,'',1);
                                createMarker(-1, -1, -1, index, item.vehicle);
                            }
                            showLoc='yes';                         

                            if (chkFlag == true) {
                                if (item.latitude * 1 < latmin) { latmin = item.latitude * 1; }
                                if (item.latitude * 1 > latmax) { latmax = item.latitude * 1; }
                                if (item.longitude * 1 < longmin) { longmin = item.longitude * 1; }
                                if (item.longitude * 1 > longmax) { longmax = item.longitude * 1; }
                            }
                            if (chkFlag == false) {                            
                                marker[index].setMap(null);
                            }
                        } //End if not null
                    })//End for each

                    //Special case that when its referesh with timer then we will not set its bounds,for other cases we will set its bounds
                    if (fbndflag == 1 && (typeof fromTimer == 'undefined' || fromTimer == 0  ))
                        fitBounds();   

                }  // End json data check null                                  
            }

            function chkAllVeh(cb) {
                // alert(cb.checked);
                if(cb.checked==true)
                    $("#hdnChkAll").val(1);
                else
                    $("#hdnChkAll").val(0);
            }

            function pressEnter(btnId,e)
            {
                // button click key press event on textbox.
                var key;
                if(window.event)
                    key = window.event.keyCode;     //IE
                else
                    key = e.which;     //firefox
                if (key == 13)
                {
                    var btn = document.getElementById(btnId);
                    if (btn != null)
                    {
                        btn.click();
                        event.keyCode = 0
                    }
                }
            }

            function FilterTrips(chk)
            {
                if(chk.value == "")
                {
                    $("input[id^=chkTripStatus]").prop('checked',false);
                    chk.checked = true;
                }
                else
                {
                    $("input[id^=chkTripStatus][value='']").prop('checked',false);
                }
                FilterVehicles();
            }

            function FilterVehicles(fromTimer)
            {                
                //Reset Chk All --------
                $("#chkAll").prop('checked',false);                

                //-----------------------------  
                if($("#divFilters").length > 0 || $("#TrTripStatus").length > 0)
                {
                    var conditions = "",str = "";                  
                    if($('#divFilters').is(':visible'))
                    {
                        if($("#lstVehTypes").length  > 0)
                        {
                            var vehtype = $("#lstVehTypes").val();
                            if(vehtype != "")
                                str = "[vt='" + vehtype + "']";
                        }   

                        
                        if($("#lstVehStatus").length  > 0)
                        {
                            var vehstatus = $("#lstVehStatus").val();
                            if(vehstatus != "")
                            {
                                if(conditions != "")
                                    conditions += ",";

                                conditions += "vs*='" + vehstatus + "'";  
                            }
                        }    
                    }                    
                                       
                    if(conditions != "")
                        str += "[" + conditions +"]";
                          
                    var gridId = 'tblData tbody';
                    if(str != "") {                        
                        $('#' + gridId + ' tr').hide();                            
                        $("#" + gridId + " tr" + str ).show(); 
                  
                        //------ Uncheck checkbox for all hidden rows ------------
                        //  $("#" + gridId + " tr:not(" + str +") input[name=chkHome]").prop('checked', false);                            
                    }
                    else {                        
                        $('#' + gridId + ' tr').show();                        
                    }                    
                    //----------------------------------------------------------------------
                 
                    //----Specilal filter for trip status ---------------------------------------                
                    var tripCodes = "";
                    if($("#TrTripStatus").length > 0)
                    {                                            
                        $('input[id^=chkTripStatus]').each(function () {
                            if (this.checked && $(this).val() != "") {                                                       
                                tripCodes += $(this).val() + ",";
                            }
                        });                        
                        if(tripCodes != "")
                        {
                            tripCodes = "," + tripCodes;
                    
                            $("#" + gridId + " tr").each(function (i, row) {
                                var tmpCode = $(this).attr('tc')
                                if (tmpCode != "") {
                                    if(tripCodes.indexOf("," + tmpCode + ",") != -1)
                                        $(this).show();                                    
                                    else 
                                        $(this).hide();                                    
                                }
                            });
                        }
                    }         
                    
                    //------ Uncheck checkbox for all hidden rows ------------
                    if(str !="" || tripCodes != "")
                        $("#" + gridId + " input[name=chkHome]:hidden").prop('checked', false);  
                    
                    //---------------------------------------------------------------------------
                    if(typeof map !== "undefined" && state == 0 &&  typeof fromTimer == 'undefined')
                        ShowHomeData();
                }                                
            }

            function drawCustomMarker()
            {
                if(customMarker)
                    customMarker.setMap(null);

                var str = $("#txtCustomMarker").val().split(",");
                if(str.length != 2)
                {
                    alert("Please enter comma seperated latitude and  longitude value");
                    return;
                }

                var tmpLat = str[0],tmpLong = str[1];
                if(isNaN(tmpLat) == true || isNaN(tmpLong) == true || parseFloat(tmpLat) <= -90 || parseFloat(tmpLat) >= 90 || parseFloat(tmpLong) <= -180 || parseFloat(tmpLong) >= 180)
                {
                    alert("Please enter valid comma seperated latitude and longitude value");
                    return;
                }

                latlng = new google.maps.LatLng(tmpLat, tmpLong);
                map.panTo(latlng);

                var tmpImg = marImage(6);
                customMarker = createImageMarker(-1,latlng,tmpImg,'Custom Marker');
            }

            function CreateMapCluster()
            {                    
                if($("#chkCluster").prop("checked"))
                {
                    var options_markerclusterer = {
                        gridSize: 60,
                        maxZoom: 18,
                        zoomOnClick: false,
                        imagePath: "images/m"
                    };

                    if (typeof markerCluster !== "undefined" && markerCluster != null) {
                        markerCluster.clearMarkers();
                    } 
                    
                    markerCluster = new MarkerClusterer(map, marker , options_markerclusterer);
                    google.maps.event.addListener(markerCluster, 'clusterclick', function(cluster) {
                        var tmpMarkers = cluster.getMarkers();
                        var array = [];
                        var num = 0;

                        var strData = "";                      
                        for (var i = 0; i < tmpMarkers.length ; i++) {                            
                            array.push( (i+1) + ". " + tmpMarkers[i]["labelContent"]);
                        }
                        
                        if (map.getZoom() <= markerCluster.getMaxZoom()) {
                            mainInfoWindow.setContent("" +  array);
                            mainInfoWindow.setPosition(cluster.getCenter());

                            openInfoWindow(mainInfoWindow,'');
                            //mainInfoWindow.open(map);
                        }
                    });

                }
                else
                {
                    if (typeof markerCluster !== "undefined" && markerCluster != null) {                                                  
                        markerCluster.clearMarkers();

                        if(marker != null)
                        {
                            for(var i=0;i<marker.length;i++)
                            {                          
                                marker[i].setMap(map);                     
                            }
                        }
                        
                        //  markerCluster.setMap(null);
                        markerCluster = null;
                    }
                }
            }

            function getVehicleDetails()
            {
                $("#hdSngVehicleId").val($("#lstSngVehicle").val());
                eval("__doPostBack('btnVehDetails','')");
            }
        </script>

        <script type="text/javascript">
            $(function () {
                LoadComboBox();
            });

            function LoadComboBox() {
                $("#cmbVehicles").combobox();

                $("#cmbCoSties").combobox();
                $("#cmbRoute").combobox();

                if("0" == "1")
                {
                    $("#lstSngVehicle").combobox();
                }

                if("1" == "1")
                {
                    $("#lstSite1").combobox();
                }
                if("1" == "1")
                {
                    $("#lstSite2").combobox();
                }
            }

            function ComboLoaded(elem) {
                var evt = elem.attr("onchange");
                if (evt != "") {
                    //On change attributes
                    eval(evt);
                }
            }
        </script>

        <!--Hide this sticky notes for few companies which use proxy server  -->
        

        <!--Reference the SignalR library. -->
        <script src="Scripts/jquery.signalR-2.2.2.min.js"></script>
        <!--Reference the autogenerated SignalR hub script. -->
        <script src="http://107.6.151.38:22018/signalr/hubs"></script>

        <script type="text/javascript">
            function loadStickyNotes()
            {
                try {
                    var userId = "0";
                    var companyId ="10423";
                    //Set the hubs URL for the connection to signalr server
                    $.connection.hub.url = "http://107.6.151.38:22018/signalr";

                    //send the values through query string
                    $.connection.hub.qs = {
                        'grpId': companyId + "_" + userId
                    };

                    // the generated client-side hub proxy
                    var clnt = $.connection.messageHub;
                    //add state to client proxy 
                    clnt.state.userId = userId
                    clnt.state.cmpId = companyId;

                    //init function to establish connection
                    function init() {
                        clnt.server.signalrconnection().done(function (msg) {
                        });
                    }
                    // Add a client-side hub method that the server will call
                    clnt.client.showstickymsg = function (msg) {
                        $("#content").stickynote({
                            size: 'small',
                            text: msg.replace(";#", "<br />"),
                            containment: 'content',
                            color: '#333333',
                            ontop: false,
                            event: 'default'
                        });
                    }

                    // Start the connection
                    $.connection.hub.start().done(init);

                }
                catch (err) {

                }
            }

            $(document).ready(function () {
                setTimeout(loadStickyNotes, 30000);
            });            
        </script>
        
        <!-- ------------------------------------------------------------------------->
    

<script type="text/javascript">
//<![CDATA[
BindData(0);Sys.Application.add_init(function() {
    $create(Sys.UI._Timer, {"enabled":true,"interval":30000,"uniqueID":"Timer2"}, null, null, $get("Timer2"));
});
Sys.Application.add_init(function() {
    $create(Sys.Extended.UI.CalendarBehavior, {"format":"dd/MM/yyyy","id":"CalendarExtender1"}, null, null, $get("txtFromDate"));
});
Sys.Application.add_init(function() {
"""