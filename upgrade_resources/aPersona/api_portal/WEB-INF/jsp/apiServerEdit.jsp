<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - Policy Editor</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">	
<link rel="stylesheet" 
	href="${pageContext.request.contextPath}/css/jquery-ui.css" />
		<link rel="icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	<link rel="shortcut icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	
<script src="${pageContext.request.contextPath}/js/jquery-1.9.1.js"></script>
<script src="${pageContext.request.contextPath}/js/jquery-ui.js"></script>

<script>
	$(function() {
		$( "#tabs" ).tabs();
		
		$( "#autoConfirmEndDate" ).datepicker();
	});
</script>
	
</head>
<body class="nof-centerBody">
<div style="height:100%; min-height:100%; position:relative;">
	<c:set var="selMenu" scope="request" value="apiSrvMgmt"/>
	<jsp:include page="header.jsp" />

	<div class="nof-centerContent">

      <div class="nof-clearfix nof-positioning ">
        <div class="nof-positioning TextObject" style="float: left; display:inline; width: 22px; ">
          <p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
        </div>
        <div id="Text129" class="nof-positioning TextObject" style="float: left; display: inline; width: 100%; margin-top: 9px; margin-left: 19px; ">
          <p style="margin-bottom: 0px;"><b><span style="font-size: 16px; font-weight: bold;">
          		aP-ASM - New Security Policy</span></b></p>
		  <br/>
          <p>Please fill in the form below to setup a security policy. The Policy Name and Key information is Required; all the other tabs are optional settings.</p>
        </div>
      </div>

      <div class="nof-positioning" style="width: 100%; margin-left: 8px; ">
	      <div class="boxLayout" style="width:100%;">
	      	<h2>Security Policy Name and Settings</h2>
				<form name="serverEditForm" method="post" action="apiServerEdit.ap" onSubmit="javascript:updServerIp();">
				<input type="hidden" name="serverId" value="${serverId}"/>
				<input type="hidden" name="providerId" value="${providerId}"/>
				
				<div class="nof-positioning" style="width:95%; margin-top: 13px; margin-left: 28px;">				
               	<input type="Submit" class="buttonStyle" style="margin-left: 5px;" value=" Save "/>				
				<input type="button" class="clearButtonStyle" style="margin-left: 28px;" value="Cancel" onclick="javascript:cancelEdit();"/>
				<c:if test="${IS_PRIMARY == 'N'}">
					<br/>
					<br/>
					<p style="margin-left: 28px;">
					<b>NOTE: This Server is a part of a security group. Please select the master server in the security group in order to modify the optional settings.</b></p>
				</c:if>
				<br/><br/>

				<div id="tabs">
           			<ul>
						<li><a href="#serverNameKey">Policy Name &amp; Key</a></li>
						<c:if test="${IS_PRIMARY != 'N'}">						
							<!-- Commenting out as per dev request : ZN8C -->
							<!-- <li><a href="#geoFilter">Geography Filter</a></li> -->
							<li><a href="#confirmMethod">Confirmation Method</a></li>
							<li><a href="#loginForensic">Policy Forensics</a></li>
						</c:if>
						<li><a href="#passcodeVerify">Passcode Verification Settings</a></li>
						<li><a href="#retryTimeout">Confirmation Retry &amp; Time-Out Settings</a></li>
               		</ul>  
               		
               		<div id="serverNameKey" style="display:none;">
                 		<span class="ap_error">*</span>&nbsp;<b>Required Settings</b>
                		<br/><br/>
                 		<table class="ap_table  server_edit" width="100%" align="center">
                 			<tr class="ap_table_tr_odd" >
                 				<td>Policy Label:&nbsp;<span class="ap_error">*</span></td>
                 				<td><input type="text" required name="srvrLabel" value="${server.serverLabel}" placeholder="ex: Websr#1 (PHP)"></td>
                 				<td>Policy Label (Internal Use)</td>
                 			</tr>
                 			<tr class="ap_table_tr_odd">
                 				<td>Service Name:&nbsp;<span class="ap_error">*</span></td>
                 				<td><input required type="text" name="svrServiceName" value="${server.svrServiceName}"
                 						placeholder="ex: MyCompany Web Portal"></td>
                 				<td>Service Name for ID Verifications</td>
                 			</tr>
                 			<tr class="ap_table_tr_odd">
                 				<td>IP/Domain Validation:&nbsp;<span class="ap_error">*</span></td>
                 				<td>
                 				<textarea required name="serverPublicNatIp" id="serverPublicNatIp" 
                 					rows="4"
                 					cols="24"><c:out value="${server.serverPublicNatIp}"/></textarea>
                 				<td>Transactions will only be accepted from the listed IP and or domains.<br/>
                 					Enter the Public (NAT) IP and/or Private IP and/or domain (One per row).<br/>
                 					Example:<br/>
                 					&nbsp;&nbsp;95.34.25.37<br/>
                 					&nbsp;&nbsp;10.5.1.*<br/>
                 					&nbsp;&nbsp;domain.com<br/>
                 				    </td>
                 			</tr>
<%--                  			<tr class="ap_table_tr_even">
                 				<td>Private IP:&nbsp;<span class="ap_error">*</span></td>
                 				<td><input required type="text" name="serverPrivateIp" value="${server.serverPrivateIp}" 
                 						placeholder="x.x.x.x"></td>
                 				<td>Enter the Private IP Address of this server. </td>
                 			</tr>
 --%>
                 			<tr class="ap_table_tr_odd">
                 				<td>Server Time Zone:</td>
                 				<td><select name="serverTimeZone" style="height: 24px;">
                                              <option value="EDT" ${server.serverTimeZone == 'EDT' ? 'selected' : ''}>(UTC-05:00) Eastern Time (US & Canada)</option>
                                              <option value="CDT" ${server.serverTimeZone == 'CDT' ? 'selected' : ''}>(UTC-06:00) Central Time (US & Canada)</option>
                                              <option value="MDT" ${server.serverTimeZone == 'MDT' ? 'selected' : ''}>(UTC-07:00) Mountain Time (US & Canada)</option>
                                              <option value="PDT" ${server.serverTimeZone == 'PDT' ? 'selected' : ''}>(UTC-08:00) Pacific Time (US & Canada)</option>
                                            </select>
                 				</td>
                 				<td>This time zone will be used when logging any failed transaction confirmations for this policy.</td>
                 			</tr>
                 			<tr class="ap_table_tr_odd">
                 				<td>Policy API Key:&nbsp;<span class="ap_error">*</span></td>
                 				<td><input required type="text" name="apiKey" value="${server.apiKey}" 
                 						placeholder="Please paste lic key here"></td>
                 				<td>Create a strong API Policy Key.</td>
                 			</tr>
                 		</table>
               		</div>               		
               		<div id="geoFilter" style="display:none;">
<%--                		<b>Optional Settings:&nbsp;Country based Geography Filter(Select One)</b>
                 		<br/> <br/>
                 		<table class="ap_table  server_edit confirmationLabel" width="100%" align="center" style="text-align:left;">
                 			<tr class="ap_table_tr_odd">
                 			<td colspan="2" class="${(server.geoFilter == 'NONE' || server.geoFilter==null) ? 'selectedVal' : ''}"><input type="radio"  name="geoFilterType" 
                 								${(server.geoFilter == 'NONE' || server.geoFilter==null) ? 'checked' : ''} value="NONE" />
                 					Allow login transactions from all countries</td>
                 			</tr>
                 			<tr class="ap_table_tr_odd">
                 			<td width="60%" style="border-right: 1px solid #dedede;" 
                 			   class="${(server.geoFilter == 'INCLUDE') ? 'selectedVal' : ''}">
                 			<input type="radio"  name="geoFilterType" 
                 								${(server.geoFilter == 'INCLUDE') ? 'checked' : ''} value="INCLUDE" />
                 					Allow login transactions ONLY from these countries</td>
                 					
                 			<td rowspan="2" width="40%" style="margin:0px; padding 0px;"
                 				class="${(server.geoFilter == 'INCLUDE' || server.geoFilter=='EXCLUDE') ? 'selectedVal' : ''}">
                 			<br/>
                 			<div style= "width:500px; height: 100px; overflow-y: scroll;">
                 			<c:forEach var="ctrFilter" items="${geoFilterList}" varStatus="loop">
			                 		<input style="margin: 0px; padding: 0px;" type="checkbox" value="${ctrFilter[0]}" name="ctrSelectedList"
                                    	${ctrFilter[2] == 'Y' ? 'checked' : ''}/>&nbsp; ${ctrFilter[1]}
                 					<br/>
                 				</c:forEach>
                 			</div>                 			
                 			</td>                 					
                 			</tr>
                 			<tr class="ap_table_tr_odd">
                 			<td class="${(server.geoFilter=='EXCLUDE') ? 'selectedVal' : ''}"
                 					style="border-right: 1px solid #dedede;">                 			
                 			<input type="radio"  name="geoFilterType" 
                 								${(server.geoFilter == 'EXCLUDE') ? 'checked' : ''} value="EXCLUDE" />
                 					BLOCK login transactions from these countries</td>
                 			</tr>
						</table> --%>
               		</div>
               		<div id="confirmMethod" style="display:none;">
                 		<b>Optional Settings:&nbsp;Policy Mode (Select One)</b>
                 		<br/> <br/>
                 		<table class="ap_table  server_edit confirmationLabel" width="100%" align="center" style="text-align:left;">
                 			<tr class="${(server.confirmMethod == 'DEFAULT_LOGIN' || server.confirmMethod == null) ? 'selectedVal' : 'ap_table_tr_odd'}">
                 				<td align="left"><b>Active Forensic Mode:</b></td>
                 				<td align="left"><input type="radio"  name="loginConfirmMethod" 
                 								${(server.confirmMethod == 'DEFAULT_LOGIN' || server.confirmMethod == null) ? 'checked' : ''} value="DEFAULT_LOGIN" /> 
                 						<i>This is the Default mode. All transactions will immediately route to Policy Forensics</i></td>
                 			</tr>
                 			<tr class="${(server.confirmMethod == 'FORENSIC_AFTER_N') ? 'selectedVal' : 'ap_table_tr_odd'}">
                 				<td align="left"><b>Learning Mode - Auto Confirm:</b></td>
                 				<td align="left"><input type="radio" name="loginConfirmMethod" 
                 								${(server.confirmMethod == 'FORENSIC_AFTER_N') ? 'checked' : ''} value="FORENSIC_AFTER_N"/>
                 					
                 					<select name="autoConfirmType" style="height: 24px;">
                                              <option value="UNTIL" ${server.autoConfType == 'UNTIL' ? 'selected' : ''} >Until</option>
                                              <option value="FOREVER" ${server.autoConfType == 'FOREVER' ? 'selected' : ''}>Forever</option>
                                  	</select>
                                  	<fmt:formatDate 
                                  		value="${server.autoConfEndDate}"  
						                type="date" 
						                pattern="MM/dd/yyyy"
						                var="autoConfFmtDate" />
                                  	<input type="name" id="autoConfirmEndDate" 
                                  			name="autoConfirmEndDate" size="6" maxlength="12" 
                                  			value="${autoConfFmtDate}" 
                                  			placeholder="mm/dd/yyyy" style="width: 100px;" >
                 				<i>Re-engage Active Mode after this # of User transactions:</i>
                 				<select name="forensicConfirmAfterLogingNum" style="height: 24px;">
                                              <option value="1" ${server.autoConfLogins == '1' ? 'selected' : ''}>1</option>
                                              <option value="2" ${server.autoConfLogins == '2' ? 'selected' : ''}>2</option>
                                              <option value="3" ${server.autoConfLogins == '3' ? 'selected' : ''}>3</option>
                                              <option value="4" ${server.autoConfLogins == '4' ? 'selected' : ''}>4</option>
                                              <option value="5" ${server.autoConfLogins == '5' ? 'selected' : ''}>5</option>
                                              <option value="10" ${server.autoConfLogins == '10' ? 'selected' : ''}>10</option>
                                              <option value="15" ${server.autoConfLogins == '15' ? 'selected' : ''}>15</option>
                                              <option value="20" ${server.autoConfLogins == '20' ? 'selected' : ''}>20</option>
                                              <option value="0" ${(server.autoConfLogins == null || server.autoConfLogins == '0') ? 'selected' : ''}>N/A</option>
                                            </select>
                 				</td>
                 			</tr>
                 			<tr class="${(server.confirmMethod == 'FORCE_FORENSIC') ? 'selectedVal' : 'ap_table_tr_odd'}">
                 				<td><b>Force Forensic Confirmation Always:</b></td>
                 				<td><input type="radio" name="loginConfirmMethod" 
                 							${(server.confirmMethod == 'FORCE_FORENSIC') ? 'checked' : ''} value="FORCE_FORENSIC"/>
                 				<i>This setting will force a One Time Passcode to be sent to the User for all transactions for this Policy.</i></td>
                 			</tr>
                 			<tr class="${(server.confirmMethod == 'MAINTENANCE_MODE') ? 'selectedVal' : 'ap_table_tr_odd'}">
                 				<td><b>Maintenance Mode - No Confirmations:</b></td>
                 				<td><input type="radio" name="loginConfirmMethod" 
                 							${(server.confirmMethod == 'MAINTENANCE_MODE') ? 'checked' : ''} value="MAINTENANCE_MODE"/>
                 				<i>Warning, this setting disables this Policy.</i></td>
                 			</tr>
                 		</table>                 		                 		           
               		</div>
               		<div id="loginForensic" style="display:none; overflow-y: scroll; height:400px;">
               			<b>Optional Settings:&nbsp;</b>
                 		<br/><br/>                 		
                 		<table class="ap_table leftAlignTable" width="100%" align="center">
<!--                  			<tr class="ap_table_tr_odd">
                 				<td><b>Login Forensic Key Security Domain:</b></td>
                 				<td colspan="2">
									<select name="compareForensicType" style="height: 24px;">
                                             <option value="COMPARE_ALL_SERVERS" ${server.forensicDomain == 'COMPARE_ALL_SERVERS' ? 'selected' : ''}>
                                             							Compare Forensics across all Servers</option>
                                             <option value="COMPARE_THIS_SERVER_ONLY" ${server.forensicDomain == 'COMPARE_THIS_SERVER_ONLY' ? 'selected' : ''}>
                                             							Compare Foresics for THIS SERVER ONLY</option>
                                             <option value="COMPARE_SERVER_GROUP" ${server.forensicDomain == 'COMPARE_SERVER_GROUP' ? 'selected' : ''}>
                                             							Compare Forensics from a Group of Servers</option>
                                    </select>
								</td>

 							</tr>
 -->                 		
<!--  							<tr class="ap_table_tr_odd">
                 				<td  style="margin: 0px; padding: 0px;" colspan="3"><hr/></td>
                 			</tr>
 -->                 			<tr class="ap_table_tr_odd">
                 				<td width="10%"><b>MITM Checking:</b></td>
                 				<td width="55%">
                 					<select name="mitmChecking" style="height: 24px;">
                                        <option value="Off" ${server.mitmChecking == 'Off' ? 'selected' : ''}>Off</option>
                                        <option value="On"  ${server.mitmChecking == 'On' ? 'selected' : ''}>On</option>
                                    </select>
                 				</td>
                 				<td width="35%" style="font-size: 10px; font-style: italic;">
                 				If set to On, the aPersona ASM will send API response code 203 in an IP Conflict/MITM situation. If set to Off, then IP Conflict/MITM situations will be ignored.
                 				</td>                 				
							</tr>


<!--  							<tr class="ap_table_tr_odd">
                 				<td  style="margin: 0px; padding: 0px;" colspan="3"><hr/></td>
                 			</tr>
 -->                 			<tr class="ap_table_tr_odd">
                 				<td><b>Policy Forensic Level:</b></td>
                 				<td colspan="2">
                 					<select name="loginForensicMethod" style="height: 24px;">
                                        <option value="STANDARD" ${server.forensicMethod == 'STANDARD' ? 'selected' : ''}>
                                        							Level 1 (Device "OR" NAT IP "OR" Cookie Device ID)</option>
                                        <option value="ENHANCED" ${server.forensicMethod == 'ENHANCED' ? 'selected' : ''}>
                                        							Level 2 (Device "AND" ISP Geography) "OR" (Cookie Device ID)</option>
                                    </select>
                                    <br/>
                                    <div style="margin-top: 5px;">
<%--                                      <input type="checkbox" value="Y" name="forceForencicCheckBox"
                                    	${server.forceEnhanced == 'Y' ? 'checked' : ''}/>&nbsp;
 --%>                                    	Force Level 2 from here:
	                                    <input type="text" name="forceForencicIpList" size="50" value="${server.forceEnhCidr}" 
	                                    placeholder="Enter IP's separated by commas. e.g. 10.5.1.*, 95.34.45.3"/>
                                    	 <br/>Do not challenge IP's:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
	                                    <input type="text" name="bypassIps" size="50" value="${server.bypass}" 
	                                    placeholder="Enter IP's separated by commas. e.g. 10.5.1.*, 95.34.45.3"/>

                                    </div>
                                   
                 				</td>
                 			</tr>	
<!--                  			<tr class="ap_table_tr_odd">
                 				<td  style="margin: 0px; padding: 0px;" colspan="3"><hr/></td>
                 			</tr>
 -->
 
                  			<tr class="ap_table_tr_odd">
                 				<td><b>Application Defined Fields:</b></td>
                 				<td colspan="1">
                 				<p align="center">
                 				<b>Policy Forensic Level</b>
                 				<br/>
                 				<br/>
                 				<select style="align:center;" name="addForensicLevelCond" style="height: 24px;">
                                        <option value="OR" ${server.addForensicLevelCond == 'OR' ? 'selected' : ''}>
                                        							"OR"</option>
                                        <option value="AND" ${server.addForensicLevelCond == 'AND' ? 'selected' : ''}>
                                        							"AND"</option>
                                    </select>
                                    <hr/>

                                     <input type="checkbox" value="Y" name="applField1Sel"
                                    	${server.applField1Sel == 'Y' ? 'checked' : ''}/>
                                    	&nbsp;&nbsp;
                                    	Application Defined Field 1:   
                                    	&nbsp;&nbsp;&nbsp;&nbsp;
                                    	
                                    	<select style="align:center;" name="applField1Operator" style="height: 24px;">
	                                        <option value="=" ${server.applField1Operator == '=' ? 'selected' : ''}>&nbsp;&nbsp;  =  &nbsp;&nbsp;</option>
	                                        <option value=">" ${server.applField1Operator == '>' ? 'selected' : ''}>&nbsp;&nbsp;  &gt;  &nbsp;&nbsp;</option>
											<option value="<" ${server.applField1Operator == '<' ? 'selected' : ''}>&nbsp;&nbsp;  &lt;  &nbsp;&nbsp;</option>
											<option value="Contains" ${server.applField1Operator == 'Contains' ? 'selected' : ''}>Contains</option>
                                    	</select>
										&nbsp;&nbsp;&nbsp;&nbsp;
	                                    <input type="text" name="applField1Value" size="20" value="${server.applField1Value}" 
	                                    placeholder="Value here"/>
	                                    
			                 			<div align="center">
			                 			<!-- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -->
			                 			<select style="align:center;" name="applFieldsCondition" style="height: 24px;">
			                                        <option value="OR" ${server.applFieldsCondition == 'OR' ? 'selected' : ''}>
			                                        							"OR"</option>
			                                        <option value="AND" ${server.applFieldsCondition == 'AND' ? 'selected' : ''}>
			                                        							"AND"</option>
			                                    </select>
			                            </div>
			                                    
                                     <input type="checkbox" value="Y" name="applField2Sel"
                                    	${server.applField2Sel == 'Y' ? 'checked' : ''}/>
                                    	&nbsp;&nbsp;
                                    	Application Defined Field 2:   
                                    	&nbsp;&nbsp;&nbsp;&nbsp;
                                    	
                                    	<select style="align:center;" name="applField2Operator" style="height: 24px;">
	                                        <option value="=" ${server.applField2Operator == '=' ? 'selected' : ''}>&nbsp;&nbsp;  =  &nbsp;&nbsp;</option>
	                                        <option value=">" ${server.applField2Operator == '>' ? 'selected' : ''}>&nbsp;&nbsp;  &gt;  &nbsp;&nbsp;</option>
											<option value="<" ${server.applField2Operator == '<' ? 'selected' : ''}>&nbsp;&nbsp;  &lt;  &nbsp;&nbsp;</option>
											<option value="Contains" ${server.applField2Operator == 'Contains' ? 'selected' : ''}>Contains</option>
                                    	</select>
										&nbsp;&nbsp;&nbsp;&nbsp;
	                                    <input type="text" name="applField2Value" size="20" value="${server.applField2Value}" 
	                                    placeholder="Value here"/>
	                                    </p>
	                           </td>
                 				<td>"OR" below "Policy Forensic Level" will make the policy less restrictive, "AND" will make the policy more restrictive.
<br/>
NOTES: IF af1 OR af2 are null or missing, ASM WILL ACT AS IF THE APPLICATION DEFINED FIELD IS UNCHECKED. THIS ENABLES A SINGLE SECURITY POLICY TO BE USED FOR BOTH LOGIN AND POST LOGIN (HIGHER RISK) VALIDATIONS. Simply leave af1 & af2 blank at login; include af1 &/or af2 post login.
                 				</td>
                 			</tr>	

                  			<tr class="ap_table_tr_odd">
                 				<td><b>Policy &#8220;Time to Live&#8221;:</b></td>
                 				<td><table class="innerTable" style="margin:0px; padding:0px;">
                 						<tr>
                 							<td></td>
                 							<td colspan="3">Days between Trans.</td>
                 							<td></td>
                 						</tr>
                 						<tr>
                 							<td></td>
                 							<td>1st</td>
                 							<td>2nd</td>
                 							<td>3rd-Nth</td>
                 							<td></td>                 							
                 						</tr>
                 						<tr>
                 							<td style="text-align:right;">PC:</td>
                 							<td><input type="text" name="forensicTimeLivePcFirst" 
                 								size="4" maxlength="10"	value="${server.pcTimeout1==null ? '15' : server.pcTimeout1}"></td>
                 							<td><input type="text" name="forensicTimeLivePcSecond" 
                 								size="4" maxlength="10"	value="${server.pcTimeout2==null ? '30' : server.pcTimeout2}"></td>
                 							<td><input type="text" name="forensicTimeLivePcThird" 
                 								size="4" maxlength="10"	value="${server.pcTimeout3==null ? '45' : server.pcTimeout3}"></td>
                 							<td><a style="color:blue;" href="javascript:setPcTimeoutDefaults();">defaults</a>	
                 						</tr>
										<tr>
											<td style="text-align:right;">Mobile/Tablet:</td>
                 							<td><input type="text" name="forensicTimeLiveMobileFirst" 
                 								size="4" maxlength="10"	value="${server.mobileTimeout1==null ? '7' : server.mobileTimeout1}"></td>
                 							<td><input type="text" name="forensicTimeLiveMobileSecond" 
                 								size="4" maxlength="10"	value="${server.mobileTimeout2==null ? '15' : server.mobileTimeout2}"></td>
                 							<td><input type="text" name="forensicTimeLiveMobileThird" 
                 								size="4" maxlength="10"	value="${server.mobileTimeout3==null ? '30' : server.mobileTimeout3}"></td>
                 							<td><a style="color:blue;" href="javascript:setMobileTimeoutDefaults();">defaults</a>									
										</tr>                 						
                 					</table>
                 				</td>

                 				<td style="font-size: 10px; font-style: italic;">
                 				&nbsp;If the numbers entered are 15,30, 45, then: After the first detection of a new Device and/or Network, the Poplicy Forensics will be kept for 15 days. If the User logs in a 2nd time from the same Device and/or Network within 15 days, then the Policy Forensics will be kept for 30 days, and so on. Settings are provided for both PC and Mobile type devices.
                 				</td>
                 			</tr>

                 			</tr>
                 		</table>                 		                 	
               		</div>
               		
               		<div id="passcodeVerify" style="display:none;">
               		<b>Optional Settings:&nbsp;</b>
               		<br/><br/>
	               		<table class="ap_table leftAlignTable" width="100%">
	               			<tr class="ap_table_tr_odd">
	               				<td><b>One Time Passcode Length:</b></td>
	               				<td>
	               					<select name="otpLength" style="height: 24px;">
                                         <option value="4" ${server.otpLength == '4' ? 'selected' : ''}>4</option>
                                         <option value="5" ${server.otpLength == '5' ? 'selected' : ''}>5</option>
                                         <option value="6" ${server.otpLength == '6' ? 'selected' : ''}>6</option>
                                         <option value="7" ${server.otpLength == '7' ? 'selected' : ''}>7</option>
                                         <option value="8" ${server.otpLength == '8' ? 'selected' : ''}>8</option>                                         
                                    </select>                                    
	               				</td>
	               				<td colspan="2">Select the length of the One Time Passcode. Default value is '4'.
	               				</td>
	               			</tr>

	               			<tr class="ap_table_tr_odd">
	               				<td><b>End User OTP Verification Method Priority:</b></td>
	               				<td colspan="2">
	               					<select name="passwdVerifyFirstMethod" style="height: 24px;">
                                         <option value="EMAIL" ${server.otpVerifyMethod1 == 'EMAIL' ? 'selected' : ''}>User Email Address</option>
                                         <option value="AUTO_ACCEPT" ${server.otpVerifyMethod1 == 'AUTO_ACCEPT' ? 'selected' : ''}>Monitor Mode/OTP Accept</option>
                                    </select>                                    
	               				</td>
	               				<td>Select the delivery methods for One-Time-Passcodes.</td>			               				
	               			</tr>
	               			<tr class="ap_table_tr_odd">
	               				<td><b>Template text for OTP ID Verification:</b></td>
	               				<td colspan="3">
	               					<table class="ap_table_inner">
	               						<tr>
	               							<td style="border: 0px;"><b>Subject:</b></td>
	               							<td style="border: 0px;">
		               							<input type="text" name="passwdVerifySubject" 
		               								size="77" value="${(server.otpVerifySubject == null || server.otpVerifySubject == '') ? 'ID Code for [ServiceName]: [OTPCode]' : server.otpVerifySubject}"/>
	               							</td>
	               						</tr>
	               						<tr>
	               							<td style="border: 0px;"><b>Body:</b></td>
	               							<td style="border: 0px;">
												<p style="margin-bottom: 0px;">
												<!-- TODO -->
												<input type="hidden" name="passwdVerifyBodyText" />
												<c:set var="defaultBody" value='Enter your ID Code: <b><span style="color:white; background:green;">[OTPCode]</span></b> to verify your access.
<p>This transaction originated from: [IPGEO].<br/>(If you are not accessing [ServiceName], you should reset your password immediately.)</p>'/>
												<textarea name="passwdVerifyBodyTextArea" rows="5" cols="75" style="font-size: 11px;"><c:out value="${(server.otpVerifyBody != null && server.otpVerifyBody != '') ?server.otpVerifyBody : defaultBody}"/></textarea>
												
	               							</td>	               						
	               						</tr>
	               					</table>
	               				</td>
	               			</tr>
	               		</table>
               		</div>
               		

               		
               		<div id="retryTimeout" style="display:none;">
                 		<b>Optional Settings:&nbsp;</b>
                 		<br/><br/>
	               		<table class="ap_table leftAlignTable" width="100%">
	               			<tr class="ap_table_tr_odd">
	               				<td><b>Trans. Confirmation Retry Limit:</b></td>
	               				<td><select name="loginConfirmRetryTimes" style="height: 24px;">
                                                  <option value="1" ${server.otpConfRetry == '1' ? 'selected' : ''}>1</option>
                                                  <option value="2" ${server.otpConfRetry == '2' ? 'selected' : ''}>2</option>
                                                  <option value="3" ${(server.otpConfRetry == '3' || server.otpConfRetry == null) ? 'selected' : ''}>3</option>
                                                </select>
                                      (Times)                         
	               				</td>
	               				<td><b>On Failure to Confirm:</b>
										<select name="loginRetryFailureToConfirm" style="height: 24px;">
                                             <option value="LOG_FAIL_KVDB" ${server.otpConfRetryNotify == 'LOG_FAIL_KVDB' ? 'selected' : ''}>Log Failure in aP-ASM DB</option>
                                             <option value="LOG_FAIL_KVDB_ADMIN" ${server.otpConfRetryNotify == 'LOG_FAIL_KVDB_ADMIN' ? 'selected' : ''}>Log Failure in aP-ASM DB &amp; Email Admin</option>
                                             <option value="LOG_FAIL_KVDB_ADMIN_USER" ${server.otpConfRetryNotify == 'LOG_FAIL_KVDB_ADMIN_USER' ? 'selected' : ''}>Log Failure in aP-ASM DB &amp; Notify Admin &amp; User</option>
                                        </select>
	               				</td>
	               			</tr>

	               			<tr class="ap_table_tr_odd">
	               				<td><b>Trans. Confirmation Time-Out (in Seconds):</b></td>
	               				<td><input type="number" name="loginConfirmTimeoutLimit" 
	               							size="5" maxlength="10" value="${(server.otpConfTimeout == null) ? '300' : server.otpConfTimeout}">                                                
                                      (Seconds)                         
	               				</td>
	               				<td><b>On Failure to Confirm:</b>
										<select name="loginRetryTimoutToConfirm" style="height: 24px;">
                                             <option value="LOG_FAIL_KVDB" ${server.otpConfTimeoutNotify == 'LOG_FAIL_KVDB' ? 'selected' : ''}>Log Failure in aP-ASM DB</option>
                                             <option value="LOG_FAIL_KVDB_ADMIN" ${server.otpConfTimeoutNotify == 'LOG_FAIL_KVDB_ADMIN' ? 'selected' : ''}>Log Failure in aP-ASM DB &amp; Email Admin</option>
                                             <option value="LOG_FAIL_KVDB_ADMIN_USER" ${server.otpConfTimeoutNotify == 'LOG_FAIL_KVDB_ADMIN_USER' ? 'selected' : ''}>Log Failure in aP-ASM DB &amp; Notify Admin &amp; User</option>
                                        </select>
	               				</td>
	               			</tr>
	               			<tr class="ap_table_tr_odd">
	               				<td><b>Template text for Failed Transaction Notification:</b></td>
	               				<td colspan="2">
	               					<table>
	               						<tr>
	               							<td  style="border: 0px;"><b>Subject:</b></td>
	               							<td  style="border: 0px;">
		               							<input type="text" name="failedLoginSubject" 
		               								size="77" value="${(server.otpConfSubject == null || server.otpConfSubject == '') ? 'Failed Verification for [ServiceName]' : server.otpConfSubject}"/>
	               							</td>
	               						</tr>
	               						<tr>
	               							<td  style="border: 0px;"><b>Body:</b></td>
	               							<td  style="border: 0px;">
												<p style="margin-bottom: 0px;">
												<input type="hidden" name="failedLoginBodyText" />
												<c:set var="defaultBodyFailedLogin" value='There was a failed transaction attempt for user: [UserEmail]
Service Name: [ServiceName]
Transaction originated from [IPGEO]
Action may be needed.'/>
												<textarea name="failedLoginBodyTextArea" rows="4" cols="75" style="font-size: 11px;">
<c:out value="${(server.otpConfBody != null && server.otpConfBody != '') ? server.otpConfBody :defaultBodyFailedLogin}"/>
</textarea></p>
											</td>	               						
	               						</tr>
	               					</table>
	               				</td>
	               			</tr>
	               		</table>                 		
               		</div>               		
				</div>
				</div>							
			</form>
          </div>
      </div>
      
    </div>
</div>
<%@include file="footer.html" %>
<script>
	function setPcTimeoutDefaults(){
		serverEditForm.forensicTimeLivePcFirst.value="15";
		serverEditForm.forensicTimeLivePcSecond.value="30";
		serverEditForm.forensicTimeLivePcThird.value="45";		
	}

	function setMobileTimeoutDefaults(){
		serverEditForm.forensicTimeLiveMobileFirst.value="7";
		serverEditForm.forensicTimeLiveMobileSecond.value="15";
		serverEditForm.forensicTimeLiveMobileThird.value="30";		
	}
	
	function cancelEdit(){
		window.location.href = "apiServerMgmt.ap";
	}
	
	function updServerIp(){
		var serverPubIpVal = $(serverPublicNatIp).val();
		if(serverPubIpVal){
			if(serverPubIpVal.indexOf("127.0.0.1") != -1){
				alert("Transactions will not be allowed from restricted IP 127.0.0.1");
				// $(serverPublicNatIp).val(serverPubIpVal.replace("127.0.0.1",""));
				return false;
			}
			if(serverPubIpVal.indexOf("localhost") != -1 || serverPubIpVal.indexOf("localdomain") != -1){
				alert("Transactions will not be allowed from generic hostnames containing localhost or localdomain");
				return false;
			}
		}
		return true;
	}
</script>
</body>
</html>
