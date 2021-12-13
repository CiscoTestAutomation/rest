#!/bin/env python
""" Unit tests for the IOS-XE REST implementation """

__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "Maaz Mashood Mohiuddin <mmashood@cisco.com>"

import os
import unittest
import requests_mock

from pyats.topology import loader

from rest.connector import Rest

HERE = os.path.dirname(__file__)

@requests_mock.Mocker(kw='mock')
class test_iosxe_test_connector(unittest.TestCase):
# @requests_mock.Mocker(kw='mock')
# class test_iosxe_test_connector():

    def setUp(self):
        self.testbed = loader.load(os.path.join(HERE, 'testbed.yaml'))
        self.device = self.testbed.devices['eWLC']

    def test_connect(self, **kwargs):
        connection = Rest(device=self.device, alias='rest', via='rest')

        response_text = """<!--
Description: Library wiring of WebUI application
Copyright (c) 2014-2019 by Cisco Systems, Inc.
All rights reserved.
-->
<!doctype html>
<!--[if lt IE 7]>
<html class="no-js lt-ie9 lt-ie8 lt-ie7">
    <![endif]-->
    <!--[if IE 7]>
    <html class="no-js lt-ie9 lt-ie8">
        <![endif]-->
        <!--[if IE 8]>
        <html class="no-js lt-ie9">
            <![endif]-->
            <!--[if gt IE 8]>
            <!-->
            <html class="no-js">
                <!--
                <![endif]-->
                <head>
                    <meta charset="utf-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <title></title>
                    <meta name="description" content="">
                    <meta name="viewport" content="width=device-width">
                    <link rel="icon" type="image/x-icon" href="login/favicon.ico">
                    <script src="common/lib/index1.js">
        </script>
                    <!-- Wire Bootstrap CSS -->
                    <link rel="stylesheet" href="lib/bootstrap/bootstrap.min.css"/>
                    <!-- Wire any Kendo theme from the below location. Here kendo bootstrap look is wired -->
                    <link rel="stylesheet" href="lib/kendo/styles/kendo.common-bootstrap.min.css"/>
                    <link rel="stylesheet" href="lib/kendo/styles/kendo.bootstrap.min.css"/>
                    <link rel="stylesheet" href="lib/kendo/styles/kendo.dataviz.min.css"/>
                    <link rel="stylesheet" href="lib/kendo/styles/kendo.dataviz.bootstrap.min.css"/>
                    <link rel="stylesheet" href="features/notificationPanel/common-styles.css">
                    <link rel="stylesheet" href="lib/c3/c3.min.css"/>
                    <!-- Wire icon font -->
                    <link rel="stylesheet/less" href="assets/fonts/style.css"/>
                    <!-- Wire Font Awesome CSS for icon fonts -->
                    <link rel="stylesheet" href="lib/font-awesome-4.0.3/css/font-awesome.min.css">
                    <!-- This is the custom CSS for WebUI -->
                    <link rel="stylesheet/less" href="assets/styles/polaris_bootstrap_customization.css"/>
                    <link rel="stylesheet/less" href="assets/styles/angular-wizard.css"/>
                    <link rel="stylesheet/less" href="assets/styles/polaris-typography.css"/>
                    <link rel="stylesheet/less" href="assets/styles/polaris_kendo_customization.css" />
                    <link rel="stylesheet" href="common/megamenu/css/style.css">
                    <link rel="stylesheet/less" href="assets/styles/main.css"/>
                    <link rel="stylesheet" href="features/switchView/resource/switch.css">
                    <link rel="stylesheet/less" href="common/directives/jsdiff/diffview.css"/>
                    <!-- The following entry is for vendor specific style changes. 
            Should come from the vendors directory.  -->
                    <link rel="stylesheet/less" href="assets/styles/custom-spec.css"/>
                    <!-- ng-cloak to wait until angular loads -->
                    <style>
            [ng-cloak] {
                display: none !important;
            }
            div.busyLoadingContainer {
                display: none;
            }
            .busy div.busyLoadingContainer {
                position: fixed;
                width: 100%;
                height: 100%;
                background: #000;
                opacity: 0.5;
                filter: alpha(opacity=50);
                display: block;
                z-index: 99999;
                text-align: center;
            }
            div.busyLoadingContainer span.spinner {
                color: #fff;
                font-size: 60px;
                position: relative;
                top: 50%;
            }
        </style>
                </head>
                <!-- Declare the app -->
                <body ng-app="webUiDevApp" class="busy">
                    <div class="busyLoadingContainer">
                        <span class="spinner fa fa-spin fa-spinner"></span>
                    </div>
                    <div class="container main-container">
                        <div class="row" ng-init="initFunction()"  ng-controller="megaMenuCtrl">
                            <div ng-cloak class="top-panel panel-gradient clearfix" ng-init="addClass=false" ng-hide="addClass">
                                <i class="icon-chevron icon-right-arrow-circle" ng-hide="hideMegamenu" title="{{::'header_expand_collapse'|Translate}}" ng-class="{'collapsed': isActive}" ng-click="hideShowMenu()"></i>
                                <div class="logo">
                                    <a href="javascript://" id="companyLogoLink" style="cursor:default">
                                        <img src="assets/images/companylogo.png" alt="{{::'common_logo'|Translate}}">
                                    </a>
                                </div>
                                <span ng-if="loggedIn">
                                    <h1 class="main-title"> Cisco {{brandName}} 
                    
                                        <br/>
                                        <span class="deviceVersion">{{version}}</span>
                                    </h1>
                                </span>
                                <div class="top-panel-tools topPanelIconView topPanelIconClass" ng-show="loggedIn">
                                    <div class="top-panel-section">
                            {{::'header_welcome'|Translate}} 
                                        <i>{{username}}</i>
                                        <div class="loginDetails" ng-show="loginDetails.showLoginDetails">
                                                                {{::'index_last_login' | Translate}} {{loginDetails.last_success_time}}
                                                                
                                            <span class="loginDetailsTooltip">...
                                                                        
                                                <span class="loginDetailsTooltipText">
                                                    <span> {{::'index_last_failure' | Translate}}: {{loginDetails.last_fail_time}} </span>
                                                    <span class="margin-top--10"> {{::'index_time_zone' | Translate}}: {{loginDetails.time_zone}} </span>
                                                    <span class="margin-top--10"> {{::'index_failure_count' | Translate}}: {{loginDetails.fail_count}} </span>
                                                    <span class="margin-top--10"> {{::'index_privilege_changed' | Translate}}: {{loginDetails.privilege_change ? loginDetails.privilege_change : login_no}} </span>
                                                    <span class="margin-top--10" ng-show="loginDetails.login_success_track_conf_time"> {{::'index_success_logins' | Translate}} : {{loginDetails.successful_login_count}} </span>
                                                </span>
                                            </span>
                                        </div>
                                    </div>
                                    <div class="top-panel-section" ng-hide="userType==='lobby'">
                                        <a href="{{home}}" title="{{::'header_home'|Translate}}">
                                            <i class="fa fa-home"></i>
                                        </a>
                                        <a ng-show="isWirelessSupported" id="wirelessSetupSelection" href="javascript://" class="wirelessIcon" ng-click="showWirelessDropdown=true" title="{{::'header_wireless_setup'|Translate}}">
                                            <img class="icon-wireless-setup" ng-src="assets/images/wireless_setup.svg" alt="{{::'header_wireless_setup'|Translate}}"/>
                                        </a>
                                        <!--<a ng-if="isWirelessSupported" title="{{::'header_alerts'|Translate}}" class="avcTableContainer"  ng-init="countOfNewAlerts=0;showAlertsDropdown=false;clickOnAlerts=false" ng-click= "showAlertsDropdown=true;clickOnAlerts=true;clickOnAlertsIcon()"><i class="fa fa-exclamation-triangle"></i><span class="alerts-counter"  ng-model="alertsCount"  ng-show="countOfNewAlerts!==0" >{{countOfNewAlerts}}</span><div class="alerts" click-outside="closeAlertsDropdown()" ng-show="showAlertsDropdown===true" ng-include src="'features/alerts/views/iconAlertsView.html'"></div></a>-->
                                        <!--    <a href="" title="{{::'header_make_awish'|Translate}}" ng-click="showWindow('feedbackWindow')"><i class="fa fa-envelope"></i></a> -->
                                        <a href="" ng-if="isUserPrivilegeBool" title="{{::'saveconfig_saveconfig' | Translate}}" ng-click="showWindow('saveConfigConfirmWindow')">
                                            <i class="fa fa-save"></i>
                                        </a>
                                        <a href="" ng-if="isUserPrivilegeBool" title="{{::'preference_preferences' | Translate}}"  ng-click="showWindow('preferencesWindow')">
                                            <i class="fa fa-gear"></i>
                                        </a>
                                        <a  title="{{selectedLanguage}}" href="javascript://" class="languageIcon" ng-click="showLanguageDropdown=true">
                                            <i class="fa fa-language"></i>
                                        </a>
                                        <a href="javascript://" title="{{::'header_help'|Translate}}" ng-click="openOnlineHelpWindow(currentPage)">
                                            <i class="fa fa-question-circle"></i>
                                        </a>
                                        <a href="javascript://" title="{{::'header_refresh'|Translate}}" ng-click="showWindow('refresh')">
                                            <i class="fa fa-refresh"></i>
                                        </a>
                                        <span id="languageSelector" class="alerts languageSelectorColor" ng-show="showLanguageDropdown">{{::'header_change_language' | Translate}} 
                                            <select  style="width:130px" kendo-drop-down-list="languageSelector" name="languageSelected" id="languageSelected"
                                    ng-model="prefLang"
                                    k-data-source="supportedLanguages"
                                    k-data-text-field="'name'"
                                    k-data-value-field="'value'"
                                    k-change="updateLanguageSelection"
                                    k-ng-delay="prefLang"></select>
                                        </span>
                                        <span id="wirelessSelector" class="alerts languageSelectorColor" ng-show="showWirelessDropdown">{{::'Wireless Setup' | Translate}} 
                            
                                            <select  style="width:130px" kendo-drop-down-list="wirelessSelector" name="wirelessSelected" id="wirelessSelected"
                                    ng-model="wirelessSetupLink"
                                    k-data-source="wirelessSetupLinks"
                                    k-data-text-field="'name'"
                                    k-data-value-field="'value'"
                                    k-change="redirectWirelessSelection"></select>
                                        </span>
                                    </div>
                                    <div kendo-window="loginTimerWindow" k-title="'{{::'time_session_expiry'|Translate}}'" k-modal="true" k-width="500" k-visible="false" k-actions="[]">
                                        <div class="windowContent">
                                {{'session_will_expiry_in' | Translate:loginTimer}}
                                            <br>
                                {{::'do_you_wish_to_extend_the_session' | Translate}}
                            
                                        </div>
                                        <div class="windowButtonContainer">
                                            <button class="btn btn-primary k-button pull-left" ng-click="extendSession()">{{'extend' | Translate}}</button>
                                            <button class="btn btn-primary k-button" ng-click="logOffUser(true)">{{'logoff_now' | Translate}}</button>
                                        </div>
                                    </div>
                                    <div class="top-panel-section" title="{{::'index_supported_browsers' | Translate}}" class="supportedBrowsers" ng-if="!isHTML5SupportedBrowser()">
                                        <a href="javascript://"  ng-click="showConfirmWindow(true,supportedBrowsersWindow)">
                                            <i class="fa fa-times-circle" ></i>
                                        </a>
                                    </div>
                                    <div class="top-panel-section withoutRightBorder">
                                        <a href="" title="{{::'header_logout' | Translate}}" ng-click="showWindow('logoutConfirmWindow')">
                                            <i class="fa fa-sign-out"></i>
                                        </a>
                                    </div>
                                    <div style="display:none">
                                        <!-- Window for Make a wish -->
                                        <!--    <div kendo-window="feedbackWindow" k-title="'{{::'header_make_awish'|Translate}}'" k-modal="true" k-resizable="false" k-width="600" k-visible="false"><div ng-include src="'features/feedback/feedback.html'"></div></div> -->
                                        <!-- Window for System Information -->
                                        <div kendo-window="systemInfoWindow" k-title="'{{::'header_system_information'|Translate}}'" k-modal="true" k-resizable="false" k-width="500" k-visible="false">
                                            <div ng-include src="'features/system-information/sysinfo.html'"></div>
                                        </div>
                                        <!-- Window for Preferences -->
                                        <div kendo-window="preferenceWindow" class="noPadding" k-title="'{{::'preference_preferences' | Translate}}'" k-modal="true" k-resizable="false" k-width="600" k-visible="false">
                                            <div ng-include src="'features/preferences/preference.html'"></div>
                                        </div>
                                        <div kendo-window="showDiffWindow" class="noPadding" k-title="'{{::'header_save_configuration_diff' | Translate}}'" k-modal="true" k-resizable="false" k-width="1200" k-height="600" k-scrollable="true" k-visible="false">
                                            <div ng-hide="!LoadDiffSpinner" class="customDialogCss" id="testDiv" >
                                                <div class="diffMenuOptions pull-right"   download-content="startupConf" style="left:29%;top:5px;">
                                                    <em class="fa fa-download margin-right-10" title="{{::'header_download_startup_config' | Translate}}" ng-click="downloadLog('startupConf')"></em>
                                                </div>
                                                <div class="diffMenuOptions pull-right"  scroll-to-table-diff-block>
                                                    <!--em class="fa fa-download margin-right-10" title="Download Log" ng-click="downloadLog()"></em-->
                                                    <em class="fa fa-arrow-up margin-right-10" title="{{::'header_previous_diff_section' | Translate}}" ng-click="scrollElement(true)"></em>
                                                    <em class="fa fa-refresh margin-right-10" title="{{::'header_refresh' | Translate}}" ng-click="diffRefresh()" ></em>
                                                    <em class="fa fa-arrow-down" title="{{::'header_next_diff_section' | Translate}}"  ng-click="scrollElement(false)"></em>
                                                </div>
                                                <div class="diffMenuOptions pull-right"  download-content="runningConf" style="left:79.3%;top:5px;">
                                                    <em class="fa fa-download margin-right-10" title="{{::'header_download_running_config' | Translate}}" ng-click="downloadLog('runningConf')"></em>
                                                </div>
                                                <jsdifflib previous="first" current="second" previousheading="previoushead" currentheading="currenthead" ng-init="first = '';second='';previoushead=''; currenthead=''"></jsdifflib>
                                            </div>
                                            <div ng-hide="!LoadDiffSpinner" class="windowButtonContainer">
                                                <button kendo-button="showDiffWindowCancelButton" class="btn btn-primary" ng-click="showDiffAction(false,showDiffWindow)">
                                                    <i class="fa pl-cancel"></i>
                                             {{::'common_cancel' | Translate}}
                                                </button>
                                                <button kendo-button="showDiffWindowOKButton" class="btn btn-primary primaryActionButton" ng-click="showDiffAction(true,showDiffWindow)">
                                                    <i class="icon-save-device"></i>
                                             {{::'common_save_and_apply' | Translate}}
                                                </button>
                                            </div>
                                            <div ng-hide="LoadDiffSpinner" class="diffSpinner">
                                                <em class="fa fa-spinner fa-spin fa-3x"></em>
                                            </div>
                                        </div>
                                        <!--Window for Supported Browsers Action-->
                                        <div kendo-window="supportedBrowsersWindow" k-title="'{{::'index_supported_browsers' | Translate}}'" k-modal="true" k-width="500" k-visible="false">
                                            <div class="windowContent">
                                                <div class="title">
                                            {{::'index_supported_browsers' | Translate}}
                                        </div>
                                                <div>
                                                    <label>{{::'index_ie' | Translate}}</label>
                                                    <span>&gt;10</span>
                                                </div>
                                                <div>
                                                    <label>{{::'index_google_chrome' | Translate}}</label>
                                                    <span>>=59</span>
                                                </div>
                                                <div>
                                                    <label>{{::'index_mozilla' | Translate}}</label>
                                                    <span>>=54</span>
                                                </div>
                                                <div>
                                                    <label>{{::'index_safari' | Translate}}</label>
                                                    <span>>=10</span>
                                                </div>
                                            </div>
                                            <div class="windowButtonContainer">
                                                <button kendo-button="supportedBrowsersCancelButton" class="btn btn-primary " ng-click="showConfirmWindow(false,supportedBrowsersWindow)">
                                            {{::'common_ok' | Translate}}
                                        </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="main"  ng-cloak  ng-init="getPlatform();addClass=false" ng-class="{'dayzerobgcolor': addClass}">
                                <span kendo-notification="notification" k-options="notificationOptions"></span>
                                <span kendo-notification="notificationLonger" k-options="notificationLongerOptions"></span>
                                <!-- Including Left Mega menu-->
                                <div ng-include="'common/megamenu/helper/menus.html'" ng-cloak class="megamenu" ng-class="{'collapsed': isActive}" ng-init="isActive = false" ng-hide="hideMegamenu"></div>
                                <div class="webui-container">
                                    <div ng-if="!blockwithText && !blockFullwithText" class="blockUIContainer" ng-style="blockUI?{display:'block'}:{display:'none'}">
                                        <span ng-style="isActive?{left:'50%'}:{left:'40%'}" class="spinner fa fa-spin fa-spinner"></span>
                                    </div>
                                    <div ng-if="blockFullwithText" class="blockFullContainer" ng-style="blockUI?{display:'block'}:{display:'none'}">
                                        <span class="addEllipses textFormatting">{{blockText}}</span>
                                    </div>
                                    <ul class="breadcrumbNavigationBar" >
                                        <li ng-repeat="pathName in breadcrumbPath track by $index" ng-class="{'SelectedPage': $last}">
                                            <a ng-show="!$last && $index!=1" href="javascript:void(0);"class="breadcrumbLink" ng-click="onBreadCrumbClick()">{{pathName}}</a>
                                            <a ng-show="!$last && $index!=0" href="javascript:void(0);"class="breadcrumbLink breadCrumbDropdownElement"ng-click="showBreadCrumbDropdown()" >{{pathName}}</a>
                                            <span ng-show="$last">{{pathName}}</span>
                                            <ul class="breadcrumbDropdownDiv breadcrumbPath" ng-if="!$last && $index!=0 && breadcrumbDropdownFlag" >
                                                <li class="parentElement breadcrumbPath">
                                                    <img class="breadcrum-menu-icon breadcrumbPath" ng-src="common/megamenu/{{breadcrumbLinks.icon}}"  alt="image" title="{{breadcrumbLinks.nlskey | Translate}}">{{breadcrumbLinks.nlskey | Translate}}
                                                </li>
                                                <li class="breadcrumbPath" ng-repeat="linkName in breadcrumbLinks.submenus track by $index">
                                                    <a class="breadCrumbDropdownElement" href="{{linkName.url}}" title="{{linkName.nlskey | Translate}}">{{linkName.nlskey | Translate}}</a>
                                                </li>
                                            </ul>
                                        </li>
                                    </ul>
                                    <div ng-view=""></div>
                                    <!-- The view is filled via routes -->
                    
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- use the css class no-js on top to get the exact container width -->
                    <!-- Scripts wired in Angular, D3, Boostrap -->
                    <script src="assets/styles/variables.js"></script>
                    <script src="lib/less/less.js"></script>
                    <script src="lib/d3/d3.min.js"></script>
                    <script src="lib/angular-kendo/jquery.min.js"></script>
                    <script src="lib/angular/angular.min.js"></script>
                    <script src="lib/angular-resource/angular-resource.min.js"></script>
                    <script src="lib/angular-cookies/angular-cookies.min.js"></script>
                    <script src="lib/angular-sanitize/angular-sanitize.min.js"></script>
                    <script src="lib/angular-route/angular-route.min.js"></script>
                    <script src="lib/kendo/kendo.all.min.js"></script>
                    <script src="lib/kendo/jszip.min.js"></script>
                    <script src="lib/angular-kendo/angular-kendo.js"></script>
                    <script src="lib/bootstrap/bootstrap.min.js"></script>
                    <script src="lib/c3/c3.min.js"></script>
                    <script src="lib/ngCsv/ng-csv.min.js"></script>
                    <script src="lib/clickoutside/clickOutsideDirective.js"></script>
                    <script src="lib/ngDraggable/ngDraggable.js"></script>
                    <script src="lib/scrypt-1.2.0/scrypt.js"></script>
                    <script src="lib/csvimport/angular-csv-import.js"></script>
                    <!-- Green FE wiring Framework Files-->
                    <script src="lib/cisco/dbal.js"></script>
                    <script src="lib/cisco/dbal_helper.js"></script>
                    <script src="lib/tdl/tdllib.js"></script>
                    <script src="lib/tdl/dbal_greencore_js.js"></script>
                    <script src="lib/tdl/tdllib_ec.js"></script>
                    <script src="lib/tdl/btrace_eventq_db_js.js"></script>
                    <script src="lib/tdl/ewlc_common_js.js"></script>
                    <script src="lib/tdl/ewlc_green_config_db_js.js"></script>
                    <script src="lib/tdl/ewlc_green_oper_alt_db_js.js"></script>
                    <script src="lib/tdl/ewlc_green_oper_db_js.js"></script>
                    <script src="lib/tdl/sm_common_js.js"></script>
                    <script src="lib/tdl/sm_green_config_db_js.js"></script>
                    <script src="lib/tdl/ewlc_green_oper_emul_db_js.js"></script>
                    <script src="lib/tdl/ios_oper_db_js.js"></script>
                    <script src="lib/tdl/mdt_oper_db_js.js"></script>
                    <!-- Angular App, Controller and any other script wired here -->
                    <script src="app.js"></script>
                    <script src="common/filters/translateFilter.js"></script>
                    <script src="common/filters/commonFilters.js"></script>
                    <script src="common/directives/wizard/angular-wizard.js"></script>
                    <script src="common/directives/deviceMapDirective.js"></script>
                    <script src="common/directives/toggleButtonDirective.js"></script>
                    <script src="common/directives/applyButtonDirective.js"></script>
                    <script src="common/directives/leftTabsDirective.js"></script>
                    <script src="common/directives/frontPanelDirective.js"></script>
                    <script src="common/directives/stackedSwitchDirective.js"></script>
                    <script src="common/directives/errorNavigator.js"></script>
                    <script src="common/directives/uploadDirective.js"></script>
                    <script src="common/directives/downloadDirective.js"></script>
                    <script src="common/directives/commonDirectives.js"></script>
                    <script src="features/dashboard/dashlet/dashletDirectives.js"></script>
                    <script src="lib/lodash/lodash.compat.js"></script>
                    <script src="common/services/gridOptionsService.js"></script>
                    <script src="features/applicationVisibility/avcDirective.js"></script>
                    <script src="common/directives/tagsInputDirective.js"></script>
                    <script src="common/directives/addEditDirective.js"></script>
                    <!-- Add services here -->
                    <script src="common/services/greenFeService.js"></script>
                    <script src="common/services/greenFeService_new.js"></script>
                    <script src="common/services/datasourceService.js"></script>
                    <script src="common/services/validationService.js"></script>
                    <script src="common/services/onlineHelpService.js"></script>
                    <script src="common/services/httpEndPointService.js"></script>
                    <script src="features/preferences/preferencesService.js"></script>
                    <script src="common/services/rbacProvider.js"></script>
                    <script src="common/services/getTabsJSONService.js"></script>
                    <script src="common/services/leftTabsHelperService.js"></script>
                    <script src="common/services/vendorService.js"></script>
                    <script src="features/dayzero/StepCtrls/dayZeroStepService.js"></script>
                    <script src="features/wlan/wlanService.js"></script>
                    <script src="features/smartCallHome/smartCallHomeService.js"></script>
                    <script src="common/megamenu/megaMenu/megaMenuCtrl.js"></script>
                    <script src="features/logicalInterface/logicalService.js"></script>
                    <script src="features/alerts/alertsService.js"></script>
                    <script src="common/megamenu/megaMenu/megaMenuGetJSONService.js"></script>
                    <script src="features/portUtilization/portUtilizationService.js"></script>
                    <script src="features/snmp/snmpService.js"></script>
                    <script src="features/physicalInterface/physicalService.js"></script>
                    <script src="features/ap360View/ap360ViewService.js"></script>
                    <!--wireless scripts starts -->
                    <script src="lib/tdl/ewlc_rogued_common_js.js"></script>
                    <script src="lib/tdl/ewlc_green_rogued_db_js.js"></script>
                    <script src="lib/tdl/ios_config_db_js.js"></script>
                    <script src="features/management/technicalSupport/coreDumpService.js"></script>
                    <script src="features/flexProfile/flexProfileController.js"></script>
                    <script src="features/dashboard/clientsAP/clientsAPService.js"></script>
                    <script src="features/management/technicalSupport/apCrashService.js"></script>
                    <script src="features/dashboard/accesspoint/apController.js"></script>
                    <script src="features/atf/atfService.js"></script>
                    <script src="features/atf/atfService.js"></script>
                    <script src="features/rrm/rrm5000/rrm5000Controller.js"></script>
                    <script src="features/rrm/rrm24ghz/rrm24Controller.js"></script>
                    <script src="features/rrm/fra/fraController.js"></script>
                    <script src="features/802dot11bgn/scripts/parameters24ghzController.js"></script>
                    <script src="features/rogue/rougeApController.js"></script>
                    <script src="features/cleanair/scripts/cleanAirConfigController5g.js"></script>
                    <script src="features/cleanair/scripts/cleanAirConfigController24g.js"></script>
                    <script src="features/network/scripts/highThroughput24ghzCtrl.js"></script>
                    <script src="features/network/scripts/highThroughputCtrl.js"></script>
                    <script src="features/network/scripts/highThroughputService.js"></script>
                    <script src="features/network/scripts/networkController.js"></script>
                    <script src="features/network24ghz/scripts/network24Controller.js"></script>
                    <script src="features/rrm/mediaparams/scripts/mediaParamsController5g.js"></script>
                    <script src="features/rrm/mediaparams/scripts/mediaParamsController24g.js"></script>
                    <script src="features/accessPointConfiguration/accessPointConfigQuickSetupCtrl.js"></script>
                    <script src="features/loadBalance/loadBalanceController.js"></script>
                    <script src="features/threatDefense/policyService.js"></script>
                    <script src="features/threatDefense/threatDefenseCtrl.js"></script>
                    <script src="features/threatDefense/umbrellaController.js"></script>
                    <script src="features/atf/atfConfigController.js"></script>
                    <script src="features/atf/atfController.js"></script>
                    <script src="features/atf/atfStatisticsController.js"></script>
                    <script src="features/wirelessInterface/wirelessInterfaceController.js"></script>
                    <script src="features/rfProfile/rfProfileController.js"></script>
                    <script src="features/management/technicalSupport/coreDumpCtrl.js"></script>
                    <script src="features/telemetryMonitoring/telemetryMonitoringController.js"></script>
                    <script src="features/fabricMonitoring/fabricMonitoringController.js"></script>
                    <script src="features/mesh/meshService.js"></script>
                    <script src="features/wlanProfile/wlanConfigController.js"></script>
                    <script src="features/wlanProfile/wlanService.js"></script>
                    <script src="features/apJoinProfile/apJoinController.js"></script>
                    <script src="features/policyProfile/policyProfileController.js"></script>
                    <script src="features/tags/policyTagController.js"></script>
                    <script src="features/tags/siteTagController.js"></script>
                    <script src="features/tags/rfTagController.js"></script>
                    <script src="features/tags/apTagController.js"></script>
                    <script src="features/tags/apFilterController.js"></script>
                    <script src="features/dashboard/cpuUtilization/cpuUtilizationController.js"></script>
                    <script src="features/management/technicalSupport/apCrashCtrl.js"></script>
                    <script src="features/dashboard/clientDeviceTypes/clientDeviceTypesController.js"></script>
                    <script src="features/dashboard/clientsAP/clientsAPController.js"></script>
                    <script src="features/dashboard/memoryUtilization/memoryUtilizationContoller.js"></script>
                    <script src="features/troubleshooting/apPacketCaptureController.js"></script>
                    <script src="features/troubleshooting/radioactiveTraceController.js"></script>
                    <script src="features/localProfiling/localProfilingController.js"></script>
                    <script src="features/dashboard/networkSummary/networkSummaryController.js"></script>
                    <!--wirelesss scripts ends -->
                    <script src="features/aaa/aaaService.js"></script>
                    <script src="features/trustSec/trustSecService.js"></script>
                    <script src="features/qos/qosService.js"></script>
                    <script src="features/localPolicies/localPoliciesService.js"></script>
                    <script src="features/statistics/statisticsService.js"></script>
                    <script src="features/managementUtilization/managementUtilizationService.js"></script>
                    <script src="features/802dot11anac/scripts/parametersService.js"></script>
                    <script src="common/megamenu/megaMenu/megaMenuService.js"></script>
                    <script src="features/acl/aclController.js"></script>
                    <script src="features/acl/aclService.js"></script>
                    <script src="features/dashboard/frontpanel/FrontPanelService.js"></script>
                    <script src="features/management/technicalSupport/controllerCrashService.js"></script>
                    <script src="features/applicationVisibility/applicationVisibilityService.js"></script>
                    <script src="features/applicationVisibility/applicationVisibilityTaxonomyService.js"></script>
                    <script src="features/applicationVisibility/avcServiceabilityService.js"></script>
                    <script src="features/avcConfig/avcConfigService.js"></script>
                    <script src="features/SoftwareUpgrade/softwareUpgradeService.js"></script>
                    <script src="features/switchView/switchService.js"></script>
                    <script src="common/services/httpSecurityService.js"></script>
                    <script src="common/services/httpInterceptorService.js"></script>
                    <script src="common/services/httpErrorHandler.js"></script>
                    <script src="common/services/utilsService.js"></script>
                    <script src="features/mdm/masterView/autoDiscoverService.js"></script>
                    <!-- Add controllers here -->
                    <script src="features/iox/test.js"></script>
                    <script src="features/iox/IoxController.js"></script>
                    <script src="features/login/loginController.js"></script>
                    <script src="features/preferences/preferenceController.js"></script>
                    <script src="features/dayzeroWireless/dayzeroController.js"></script>
                    <script src="features/dayzero/dayzeroController.js"></script>
                    <script src="features/dayzero/StepCtrls/step1Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step2Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step3Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step4Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step5Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step6Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step7Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/step8Ctrl.js"></script>
                    <script src="features/dayzero/StepCtrls/switchwide.js"></script>
                    <script src="features/dayzero/StepCtrls/summaryScreenCtrl.js"></script>
                    <script src="common/megamenu/megaMenu/megaMenuHandler.js"></script>
                    <script src="features/alerts/alertsController.js"></script>
                    <script src="features/dayzero/leftTabsController.js"></script>
                    <script src="features/routingProtocols/staticRouting/staticRoutingController.js"></script>
                    <script src="common/services/capabilityService.js"></script>
                    <script src="features/dashboard/systemInformation/systemInformationCtrl.js"></script>
                    <script src="features/dashboard/temperature/temperatureCtrl.js"></script>
                    <script src="features/dashboard/CPUAndMemoryUtilization/CPUAndMemoryUtilizationController.js"></script>
                    <script src="features/eigrp/eigrpController.js"></script>
                    <script src="features/eigrp/summaryWidget.js"></script>
                    <script src="features/802dot11anac/scripts/parametersController.js"></script>
                    <script src="features/portUtilization/portUtilizationController.js"></script>
                    <script src="features/notificationPanel/notifPanelDirective.js"></script>
                    <script src="features/managementUtilization/managementUtilizationController.js"></script>
                    <script src="features/managementUtilization/managementUtilizationController.js"></script>
                    <script src="features/dashboard/topApplication/topApplicationController.js"></script>
                    <script src="features/dashboard/topApplication/topAppService.js"></script>
                    <script src="features/management/technicalSupport/controllerCrashCtrl.js"></script>
                    <script src="features/logs/logsController.js"></script>
                    <script src="features/dashboard/dashlet/DashletController.js"></script>
                    <script src="features/dashboard/dashlet/DashletService.js"></script>
                    <script src="features/system-information/sysinfoController.js"></script>
                    <script src="features/applicationVisibility/applicationVisibilityCtrl.js"></script>
                    <script src="features/applicationVisibility/wirelessAvcCtrl.js"></script>
                    <script src="features/applicationVisibility/switchavcController.js"></script>
                    <script src="features/applicationVisibility/avcServiceabilityCtrl.js"></script>
                    <script src="features/diagnostic/diagnosticCtrl.js"></script>
                    <script src="features/radioActiveTracing/radioActiveTracingController.js"></script>
                    <script src="common/lib/index2.js"></script>
                    <script src="features/preferences/preferencesService.js"></script>
                    <script src="features/switchView/switchController.js"></script>
                    <script src="features/feedback/feedbackController.js"></script>
                    <script src="features/dashboard/networkSummary/networkSummaryController.js"></script>
                    <script src="features/customApplication/customAppController.js"></script>
                    <script src="features/troubleshooting/troubleshootingController.js"></script>
                    <script src="features/troubleshooting/testWanConnection.js"></script>
                    <script src="features/troubleshooting/pingAndTraceController.js"></script>
                    <script src="features/troubleshooting/packetCaptureController.js"></script>
                    <script src="features/troubleshooting/coreDumpCaptureController.js"></script>
                    <script src="features/troubleshooting/webServerLogController.js"></script>
                    <script src="features/troubleshooting/debugBundleController.js"></script>
                    <script src="features/troubleshooting/auditController.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage1Controller.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage2Controller.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage3Controller.js"></script>
                    <script src="features/statmc/statmcCtrl.js"></script>
                    <script src="lib/jsdifflib/difflib.js"></script>
                    <script src="lib/jsdifflib/diffview.js"></script>
                    <script src="common/directives/jsdiff/jsdifflibDirective.js"></script>
                    <script src="features/dashboard/poe/poeDashletCtrl.js"></script>
                    <script src="features/OSPF/ospfAddressFamily.js"></script>
                    <script src="features/mdm/masterView/masterviewCtrl.js"></script>
                    <script src="features/mdm/template/templateController.js"></script>
                    <script src="features/mdm/masterView/addDeviceController.js"></script>
                    <script src="features/stpMonitoring/stpMonitoringController.js"></script>
                    <script src="features/rlan/rlanController.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage1MDMCtrl.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage2MDMCtrl.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage3MDMCtrl.js"></script>
                    <script src="features/troubleshooting/auditing/auditpage4MDMCtrl.js"></script>
                    <script src="features/troubleshooting/auditMDMController.js"></script>
                </body>
            </html>
"""
        kwargs['mock'].get('https://198.51.100.3:443/', text=response_text)
        output = connection.connect(verbose=True).text
        self.assertEqual(output, response_text)
        return connection

    def test_get(self, **kwargs):
        connection = self.test_connect()

        response_text = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": [
        {
            "profile-name": "default-ap-profile",
            "description": "default ap profile",
            "hyperlocation": {
                "pak-rssi-threshold-detection": -50
            },
            "halo-ble-entries": {
                "halo-ble-entry": [
                    {
                        "beacon-id": 0
                    },
                    {
                        "beacon-id": 1
                    },
                    {
                        "beacon-id": 2
                    },
                    {
                        "beacon-id": 3
                    },
                    {
                        "beacon-id": 4
                    }
                ]
            }
        }
    ]
}
"""

        kwargs['mock'].get('https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile', text=response_text)
        output = connection.get('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile', verbose=True).text
        self.assertEqual(output, response_text)
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post(self, **kwargs):
        connection = self.test_connect()

        payload = """
        {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_post_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, text=response_text)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_post_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].post(url, status_code=204)
        try:
            output = connection.post('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_patch(self, **kwargs):
        connection = self.test_connect()

        payload = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_patch_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, text=response_text)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_patch_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile'
        kwargs['mock'].patch(url, status_code=204)
        try:
            output = connection.patch('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=default-ap-profile', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_put(self, **kwargs):
        connection = self.test_connect()

        payload = """{
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": true,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
"""
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_put_dict_payload_without_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        response_text = ""

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, text=response_text)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_json_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='json', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)

    def test_put_dict_payload_with_xml_content_type(self, **kwargs):
        connection = self.test_connect()

        payload = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": {
        "profile-name": "test-profile",
        "description": "test-profile",
        "hyperlocation": {
            "hyperlocation-enable": True,
            "pak-rssi-threshold-detection": -50
        },
        "halo-ble-entries": {
            "halo-ble-entry": [
                {
                    "beacon-id": 0
                },
                {
                    "beacon-id": 1
                },
                {
                    "beacon-id": 2
                },
                {
                    "beacon-id": 3
                },
                {
                    "beacon-id": 4
                }
            ]
        }
    }
}
        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles'
        kwargs['mock'].put(url, status_code=204)
        try:
            output = connection.put('/restconf/data/site-cfg-data/ap-cfg-profiles', payload, content_type='xml', verbose=True).text
        except AssertionError as e:
            self.assertEqual(str(e), 'content_type parameter required when passing dict')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


    def test_delete(self, **kwargs):
        connection = self.test_connect()

        url = 'https://198.51.100.3:443/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile'
        kwargs['mock'].delete(url, status_code=204)
        output = connection.delete('/restconf/data/site-cfg-data/ap-cfg-profiles/ap-cfg-profile=test-profile', verbose=True).text
        self.assertEqual(output, '')
        connection.disconnect()

        self.assertEqual(connection.connected, False)


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.WARNING, format="%(asctime)s [%(levelname)8s]:  %(message)s")
    logger = logging.getLogger('rest')
    logger.setLevel(logging.DEBUG)
    unittest.main()
