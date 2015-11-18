<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>

<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - aP-ASM Settings</title>
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
<script src="${pageContext.request.contextPath}/js/jquery.min.js"></script>

</head>
<body class="nof-centerBody">
<div style="height:100%; min-height:100%; position:relative;">
	<c:set var="selMenu" scope="request" value="kvMgmt"/>
	<jsp:include page="header.jsp" />

	<div class="nof-centerContent">

      <div class="nof-clearfix nof-positioning ">
        <div id="Text140" class="nof-positioning TextObject" style="float: left; display:inline; width: 19px; ">
          <p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
        </div>
        <div id="Text129" class="nof-positioning TextObject" style="float: left; display: inline; width: 1000px; margin-top: 9px; margin-left: 0px; ">
          <p style="margin-bottom: 0px;"><b><span style="font-size: 16px; font-weight: bold;">aP-ASM Settings for client : <c:out value="${(PROVIDER_NAME != null && PROVIDER_NAME != '') ? (PROVIDER_NAME) : ''}"></c:out></span></b></p>
		  <br/>
          <p>Welcome to the aPersona Adaptive Security Manager. This portal allows you to administer your aPersona ASM. On this page, you can update your aP-ASM license, setup your own SMTP Server for End User Notifications and add additional Administrators to your aP-ASM Server.</p>
        </div>
      </div>

      <div class="nof-positioning" style="width: 100%; margin-left: 8px; ">      
	      <br/>	      
	      <div class="boxLayout" style="width:100%;">
	      	<h2>aP-ASM Settings</h2>
			<br/>
			<h3>This aP-ASM License Key:</h3>
			
			<table class="ap_table" width="98%" align="center" style="font-size: 1px; line-height: 0;">
				<thead class="ap_table_hdr">
					<tr>
						<th>aP-ASM Name</th>
						<th>License Key</th>
						<th>Licensed Thru</th>
						<th>Num of Users</th>
						<th>Action</th>
					</tr>
				</thead>
				
				<c:if test="${fn:length(KV_LICENSES) gt 0}">
					<c:forEach var="kvLic" items="${KV_LICENSES}" varStatus="loop">
					<c:set var="pName" value="${fn:substring(kvLic.keyvaultName, 0, 28)}" />
						<tr id="div_lic_${loop.index}" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
							<td>${pName}</td>
							<td style="text-align:left;">${kvLic.keyvaultLicenseKey}</td>
							<td title="${kvLic.expFlag}" >
									<span class="${kvLic.expFlag == null ? '' : 'ap_error'}">
								<fmt:formatDate 
                                  		value="${kvLic.expDate}"  
						                type="date" 
						                pattern="dd-MMM-yyyy"
						                var="kvExpDate" />${kvExpDate}
								</span>						     
						     </td>
							<td>${kvLic.allowedUsers == '1000000' ? 'Unlimited' : kvLic.allowedUsers}</td>
<%-- 							<td>${kvLic.publicIp}</td>
							<td>${kvLic.privateIp}</td>							
 --%>							<td><input type="button" class="buttonStyle" value="Sync Licensing Info" onclick="window.location='syncKvLicense.ap?kvLicenseId=${kvLic.kvLicenseId}'"/>
								&nbsp;
								<input type="button" class="buttonStyle" value="Edit" onclick="javascript:editRow(${loop.index});" />
								&nbsp;
								<input type="image" class="clearButtonStyle" value="Delete"
								src="${pageContext.request.contextPath}/images/trash.png"
								 onclick="javascript:if(confirm('Are you sure you want to delete this aP-ASM License?')){window.location='removeKvLicense.ap?kvLicenseId=${kvLic.kvLicenseId}'};" />								
	 						</td>
	 					</tr> 					
	 					<c:if test="${INT_NET=='true'}">
							<tr id="div_lichash_${loop.index}" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
								<td colspan="2" style="text-align:left">Offline License Key1 : ${kvLic.licenseHash}</td>
								<td colspan="3" style="text-align:left">Offline License Key2 : ${kvLic.licenseEncKey}</td>		
		 					</tr>
	 					</c:if>
						
						<form name="edit_lic_${loop.index}" id="lic_form_${loop.index}" method="post" action="editKVLic.ap">
						<tr id="div_lic_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
								<td  style="border-left:1px solid #A0A0A0;">
									<input required type="text" size="15" name="kvLicName" value="${kvLic.keyvaultName}"/> </td>
								<td><input required type="text" size="40"  id="kvLicKeyId" style="margin-left:-20px;" name="kvLicKey" value="${kvLic.keyvaultLicenseKey}"/></td>
								<c:if test="${INT_NET=='true'}">
									<td><fmt:formatDate
	                                  		value="${kvLic.expDate}"  
							                type="date" 
							                pattern="dd-MMM-yyyy"
							                var="kvExpDate" />
							                <input required type="text" size="15"  
							                style="margin-left:-20px;" name="kvExpDate"
							                placeholder="dd-mmm-yyyy" 
							                value="${kvExpDate}"/>
							                </td>
									<td><input required type="text" size="15" name="allowedUsers" value="${kvLic.allowedUsers == '1000000' ? 'Unlimited' : kvLic.allowedUsers}"/></td>
								</c:if>
								<c:if test="${INT_NET!='true'}">
									<td><fmt:formatDate 
	                                  		value="${kvLic.expDate}"  
							                type="date" 
							                pattern="dd-MMM-yyyy"
							                var="kvExpDate" />${kvExpDate}</td>
									<td>${kvLic.allowedUsers == '1000000' ? 'Unlimited' : kvLic.allowedUsers}</td>
								</c:if>
								
<%-- 								<td><input required type="text" size="13" name="kvLicPubIp" width="10px"  value="${kvLic.publicIp}"/></td>
								<td><input type="text" size="13" name="kvLicPriIp" value="${kvLic.privateIp}"/></td>
 --%>								<td><input type="hidden" size="18" name="kvLicenseId" value="${kvLic.kvLicenseId}" />
		 							<input type="button" class="buttonStyle" value="Save" onclick="javascript:updKVLic(${loop.index});"/>
		 							&nbsp;/&nbsp;
		 							<input type="button" value="Cancel" class="buttonStyle" onclick="javascript:cancelEdit(${loop.index});"/></td>		 						

	 					<c:if test="${INT_NET=='true'}">
							<tr	id="div_lichash_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
								<td colspan="2" style="text-align:left">Offline License Key1 : <input required id="kvLicHashId" type="text" size="45" name="licenseHash" value="${kvLic.licenseHash}"/></td>
								<td colspan="3" style="text-align:left">Offline License Key2 : <input required id="kvLicEncId" type="text" size="45" name="licenseEncKey" value="${kvLic.licenseEncKey}"/></td>		
		 					</tr>
	 					</c:if>	 						
						</tr>
						</form>
					</c:forEach>
				</c:if>
				
				<c:if test="${fn:length(KV_LICENSES) eq 0}">
					<tfoot>
						<tr id="new_lic">
							<td colspan="6" align="left"><input class="buttonStyle" style="width:110px; margin-bottom:3px;  margin-top:2px;" type="button" value="Add License" onclick="javascript:addNewLic();"/></td>
						</tr>
						<form name="new_lic_form" method="post" action="editKVLic.ap" class="formStyle">
						<tr id="new_lic_edit" style="display:none;" class="ap_table_tr_even">
								<td style=" border-left:2px solid #A0A0A0;"><input required type="text" size="15" name="kvLicName" /></td>
								<td><input required  type="text" size="40" name="kvLicKey" style="margin-left:-20px;"/></td>
								<c:if test="${INT_NET=='true'}">
									<td><input required type="text" size="15"  
							                id="kvLicExpDateId" style="margin-left:-20px;" name="kvExpDate"
							                placeholder="dd-mmm-yyyy"/>
							                </td>
									<td><input required type="text" size="15" name="allowedUsers"/></td>
								</c:if>
								<c:if test="${INT_NET != 'true'}">
									<td></td>
									<td></td>
								</c:if>
<!-- 								<td><input required type="text" size="13" name="kvLicPubIp" width="10px"/></td>
								<td><input type="text" size="13" name="kvLicPriIp" /></td>
 -->								<td><input type="hidden" name="kvLicenseId" value="-1" />
									<input type="Submit"  class="buttonStyle" value="Save"/>
									&nbsp;/&nbsp;
									<input type="button"  class="buttonStyle"
											value="Cancel" onclick="javsscript:cancelAddNewLic();"/></td>		 								 						
						</tr>		
	 					<c:if test="${INT_NET=='true'}">
							<tr	id="new_lichash_edit" style="display:none;" class="ap_table_tr_even">
								<td colspan="2" style="text-align:left">Offline License Key1 : <input required type="text" size="40" name="licenseHash" value="${kvLic.licenseHash}"/></td>
								<td colspan="3" style="text-align:left">Offline License Key2 : <input required type="text" size="40" name="licenseEncKey" value="${kvLic.licenseEncKey}"/></td>		
		 					</tr>
	 					</c:if>
						</form>
					</tfoot>
				</c:if>
				
				<c:if test="${KV_LIC_ERROR_MESSAGE != null}">
					<tfoot>
						<tr>
							<td colspan="6" align="left"><span class="ap_error">${KV_LIC_ERROR_MESSAGE}</span></td>
						</tr>					
					</tfoot>
				</c:if>
				<c:if test="${KV_LIC_MESSAGE != null}">
					<tfoot>
						<tr>
							<td colspan="6" align="left"><span style="color:green;">${KV_LIC_MESSAGE}</span></td>
						</tr>
					</tfoot>
				</c:if>
				
			</table>			
			
			<br/>
			<hr size="1" >
			<br/>
			
			<!-- Start of Email configuration -->
			<h3>aP-ASM End-User Email Service Settings:</h3>
			
			<table class="ap_table" width="98%" align="center" style="font-size: 1px; line-height: 0;">
				<thead class="ap_table_hdr">
					<tr>
						<th>Host</th>
						<th>Port</th>
						<th>Login Id</th>
						<th>Password</th>
						<th>SSL/TLS?</th>
						<th>SMTP/SMTPS?</th>
						<th>Send Mail As</th>
						<th>Test</th>
						<th>Action</th>
					</tr>
				</thead>
				
				<c:if test="${fn:length(KV_MAIL_SETTING) gt 0}">
				
					<c:forEach var="kvEmail" items="${KV_MAIL_SETTING}" varStatus="loop">
	
						<tr id="email_${loop.index}" 
							class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
							<td>${kvEmail.smtpoutUrl}</td>
							<td>${kvEmail.portNumber}</td>
							<td>${kvEmail.loginId}</td>
							<td>********</td>
							<td>${kvEmail.protocol}</td>
							<td>${kvEmail.smtp}</td>
							<td>${kvEmail.fromAddr}</td>
		 					<td>
								<a class="linkHoverStyle" style="color:blue;" href="testEmailSettings.ap?emailServiceId=${kvEmail.emailServiceId}">
									<b>Test Settings</b>
								</a>
							</td>
							<td><input type="button" value="Edit" class="buttonStyle"
								onclick="javascript:editEmailSettingRow(${loop.index});" />
								&nbsp;  &nbsp;
								<input type="image" class="clearButtonStyle" value="Delete"
								src="${pageContext.request.contextPath}/images/trash.png"
								 onclick="javascript:if(confirm('Are you sure you want to delete Email Service Settings?')){window.location='removeEmailSetting.ap?emailServiceId=${kvEmail.emailServiceId}'};" />
	 						</td>
	 					</tr> 				
	 					
						<tr id="email_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
						<form name="edit_email_${loop.index}" method="post" action="editKVEmailConfig.ap">
							
							<td style="padding:0px; border-left:1px solid #A0A0A0;"><input style="padding:0px;" required type="text" name="smtpoutUrl" value="${kvEmail.smtpoutUrl}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" required size="5" type="text" name="portNumber" value="${kvEmail.portNumber}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" type="text" name="loginId" value="${kvEmail.loginId}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" size="12" type="password" name="password" value="${kvEmail.password}"/></td>
							<td style="padding:0px;"><select name="protocol">
                                              <option value="ssl" ${kvEmail.protocol == 'ssl' ? 'selected' : ''}>SSL</option>
                                              <option value="tls" ${kvEmail.protocol == 'tls' ? 'selected' : ''}>TLS</option>
                                              <option value="none" ${kvEmail.protocol == 'none' ? 'selected' : ''}>NONE</option>
                                            </select>
                            </td>
							<td style="padding:0px;"><select name="smtp">
                                              <option value="smtp" ${kvEmail.smtp == 'smtp' ? 'selected' : ''}>SMTP</option>
                                              <option value="smtps" ${kvEmail.smtp == 'smtps' ? 'selected' : ''}>SMTPS</option>
                                            </select>
                            </td>
							<td style="padding:0px;"><input style="padding:0px;" required size="12" type="text" name="fromAddr" value="${kvEmail.fromAddr}"/></td>
							<td colspan="2"><input type="hidden" name="emailServId" value="${kvEmail.emailServiceId}" />
	 							<input   type="Submit"  class="buttonStyle" value="Save"/>
	 							&nbsp;/&nbsp;
	 							<input type="button" value="Cancel"  class="buttonStyle" onclick="javascript:cancelEmailEdit(${loop.index});"/>
	 						</td>	 						
							</form>
						</tr>
					</c:forEach>
					
				</c:if>
				
				<c:if test="${fn:length(KV_MAIL_SETTING) eq 0}">
					<tfoot>
						<tr id="new_email_config">
							<td colspan="9" align="left"><input style="align:left; margin-bottom:3px;  margin-top:2px;" class="buttonStyle" type="button" value="Add Email Config" onclick="javascript:addNewEmailConfig();"/></td>
						</tr>
						<tr id="new_email_config_edit" style="display:none;" class="ap_table_tr_even">
							<form name="new_email_form" method="post" action="editKVEmailConfig.ap" >								
							<td style="padding:0; border-left:1px solid #A0A0A0;"><input required type="text" name="smtpoutUrl" /></td>
							<td style="padding:0"><input required size="5" type="text" name="portNumber" /></td>
							<td style="padding:0"><input type="text" name="loginId" /></td>
							<td style="padding:0"><input size="12" type="password" name="password" /></td>
							<td style="padding:0"><select name="protocol">
                                              <option value="ssl">SSL</option>
                                              <option value="tls">TLS</option>
                                              <option value="none">NONE</option>
                                            </select></td>
							<td style="padding:0"><select name="smtp">
                                              <option value="smtp">SMTP</option>
                                              <option value="smtps">SMTPS</option>
                                            </select></td>
							<td style="padding:0"><input required size="12" type="text" name="fromAddr"/></td>						
							<td colspan="2"><input   type="hidden" name="emailServId" value="-1" />
	 							<input type="Submit"  class="buttonStyle" value="Save"/>
	 							&nbsp;/&nbsp;
	 							<input type="button" value="Cancel"  class="buttonStyle" onclick="javascript:cancelNewEmailEdit();"/></td>		 						
							</form>
						</tr>					
					</tfoot>
				</c:if>				

				<c:if test="${KV_MAIL_ERROR_MESSAGE != null}">
					<tfoot>
						<tr>
							<td colspan="9" align="left"><span class="ap_error">${KV_MAIL_ERROR_MESSAGE}</span></td>
						</tr>					
					</tfoot>
				</c:if>
				<c:if test="${KV_MAIL_MESSAGE != null}">
					<tfoot>
						<tr>
							<td colspan="9" align="left"><span style="color:green;">${KV_MAIL_MESSAGE}</span></td>
						</tr>
					</tfoot>
				</c:if>
			</table> 

			<br/>
			<hr size="1" >
			<br/>

<!-- 				<table>
					<tr>
					<td>
 --><!-- 						<div class="nof-positioning"
								margin-top:0px; margin-left: 5px; "> -->
							<h3>aP-ASM Admin Accounts:</h3>
							<table class="ap_table" width="98%" align="center" >
								<thead class="ap_table_hdr">
									<tr>
										<th>Administrator Account Id</th>
										<th>Role</th>
										<th>Is Active</th>
										<th>Force OTP Login</th>
										<th>Re-send OTP</th>
										<th>Action</th>
									</tr>
								</thead>
								<c:forEach var="adminAcct" items="${KV_ADMIN_ACCOUNTS}" varStatus="loop">
				
									<tr class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
										<td style="text-align:left;">${adminAcct[0]}</td>
										<td>${adminAcct[1]}</td>
										<td>${adminAcct[5] == "1" ? "Active" : "Not Active"}</td>
										<td>
											<c:if test="${adminAcct[6] == 'N'}">
												<input type="button" class="clearButtonStyle" value="OTP Login is Disabled - Activate now" 
														onclick="javascript:window.location='forceEnhancedLogin.ap?kvAdminUserEmail=${adminAcct[0]}&opt=Y&providerId=${PROVIDER_ID}';" />													
											</c:if>
											<c:if test="${adminAcct[6] != 'N'}">
												<input type="button" class="buttonStyle" value="OTP  Login  is  Active  -  Disable now" 
														onclick="javascript:window.location='forceEnhancedLogin.ap?kvAdminUserEmail=${adminAcct[0]}&opt=N&providerId=${PROVIDER_ID}';" />													
											</c:if>																					
										</td>
										<td>
<%-- 											<input type="button" class="buttonStyle" 
													value="${(adminAcct[7] == "1"||adminAcct[7] == null) ? "Re-send Welcome OTP" : "Re-send   Login   OTP"}" 
													onclick="javascript:window.location='resendOtp.ap?kvAdminUserEmail=${adminAcct[0]}';" />													
 --%>									
 										<c:if test="${(adminAcct[7] eq '1' ||adminAcct[7] eq null)}">
	 										<a class="linkHoverStyle" style="color:blue;" href="resendOtp.ap?kvAdminUserEmail=${adminAcct[0]}&providerId=${PROVIDER_ID}">
 												<b>Re-send Welcome OTP</b>
 											</a>
 										</c:if>
 										</td>
										<!-- remove user role id  -->
										<td>
										<input type="image" class="clearButtonStyle" value="Delete"
											src="${pageContext.request.contextPath}/images/trash.png"
											 onclick="javascript:if(confirm('Are you sure you want to delete this user?')){window.location='removeKvAdminAcct.ap?kvAdminUserId=${adminAcct[0]}&providerId=${PROVIDER_ID}'};" />								
										</td>
				 					</tr>
								</c:forEach>
								
								<tfoot>
									<tr id="new_admin_acct">
										<td colspan="6" align="left"><input style="align:left;  margin-bottom:3px;  margin-top:2px;" type="button" value="Add New Admin"  class="buttonStyle" 
										onclick="javascript:addNewAdmin();"/></td>
									</tr>
									<c:if test='${ADMIN_ACCT_ERROR_MESSAGE != null}'>
										<tr id="adminAcctMsg" ><td colspan="6" style="text-align:left;">
													<span class="ap_error">${ADMIN_ACCT_ERROR_MESSAGE}</span>
										</td></tr>
									</c:if>
									<c:if test='${ADMIN_ACCT_MESSAGE != null}'>
										<tr id="adminAcctMsg"><td colspan="6" style="text-align:left;">
													<span class="ap_success">${ADMIN_ACCT_MESSAGE}</span>
										</td></tr>
									</c:if>

									<tr id="new_admin_acct_edit" style="display:none;" class="ap_table_tr_even">										
										<form name="new_email_form" method="post" action="addNewAdminAcct.ap">								
											<td  style=" border-left:2px solid #A0A0A0;"  colspan="1">
												<input type="hidden" name="providerId" value="${PROVIDER_ID}"/>
												<input required size="25" type="email" name="adminEmail" /></td>
											<td colspan="2">
					 							<input type="Submit"  class="buttonStyle" value="Add"/>
					 							&nbsp;/&nbsp;
					 							<input type="button" value="Cancel"  class="buttonStyle" onclick="javascript:cancelNewAdminAcct();"/></td>		 						
										</form>
									</tr>					
								</tfoot>				
							</table> 		
<!-- 						</div>
					</td>
 -->					
<!-- 					<td>
		                <div id="Text121" class="nof-positioning TextObject" 
		                	style="width: 323px; margin-top: 9px; margin-left: 88px; ">
							<div id="Text121" class="nof-positioning TextObject" style="width: 323px; margin-top: 9px; margin-left: 88px; ">
		                    	<h3>aPersona Licensing Server Account:</h3>
		                  	</div>		
		                  	<div class="nof-positioning" style="line-height: 0px; 
		                  			width: 219px; margin-top: 10px; margin-left: 104px; ">
		                  			<input type="button" value="Sign in to aPersona Licensing Server"  class="buttonStyle" onclick="javascript:alert('Coming soon!');"/>
		                  	</div>                
		                </div>
		                
					</td>
 --><!-- 					</tr>
				</table> -->			
<!-- 		  </div> -->

			<br/>
			<hr size="1" >
			<br/>
<%-- 			<h3>aP-ASM Encryption Keys:</h3>
			<br/>
			<div width="80%" align="left" style="padding-left:20px;">
				<h4>Instructions:</h4>
				<ul>
					<li>Encryption keys will be grerated in the temporary holding folder:  ${ENC_KEY_LOCATION} and will overwrite any previously generated keys in this temporary folder.</li>
					<li>To make the new keys Active you must:
						<br/>
						&nbsp;&nbsp;&nbsp;&nbsp;1. Copy the API encryption key (CLIENT_ENC_${PROVIDER_ID}.key) to all API servers
						<br/>
						&nbsp;&nbsp;&nbsp;&nbsp;2. Copy the aP-ASM encryption key (KV_ENC_${PROVIDER_ID}.key) to aP-ASM server
					</li>
					<li>Your previous keys will remain active until the new keys are copied.</li>
				</ul>
				<input type="button" value="Generate Encryption Keys" onclick="javascript:generateEncKeys();" class="buttonStyle"/>
				<br/>
				<br/>
				<c:if test="${SUCCESS_MESSAGE_KV_ENC_KEYS != null}">
					<p><span class="ap_success">${SUCCESS_MESSAGE_KV_ENC_KEYS}</span></p>
				</c:if>

				<c:if test="${ERR_MESSAGE_KV_ENC_KEYS != null}">
					<p><span class="ap_error">${ERR_MESSAGE_KV_ENC_KEYS}</span></p>
				</c:if>
								
			</div>
 --%>			

	  </div>
	</div>
	<br/>		
</div>
</div>
<%@include file="footer.html" %>
<script>

function generateEncKeys(){
	if(confirm('Are you sure you want to generate new encryption keys? \nThis will over-write any previously generated keys in the temporary directory. To use thse new keys, they must be copied into the aP-ASM Production Key Folder and also to all API Servers.')){
		window.location.href = "genEncKeys.ap";
	}
}

function editRow(rowId){
	$('#div_lic_'+rowId).hide();
	$('#div_lic_edit_'+rowId).show();

	$('#div_lichash_'+rowId).hide();
	$('#div_lichash_edit_'+rowId).show();
	
/* 	var editRow = document.getElementById("div_lic_edit_"+rowId);	
	var parentRow = document.getElementById("div_lic_"+rowId);
	parentRow.hide();
	alert("test..:"+editRow);
	parentRow.style.display = 'none';
	editRow.style.display = 'block';	
	$(parentRow).children().style('display', 'none');
 */}
 
 function cancelEdit(rowId){
	$('#div_lic_edit_'+rowId).hide();
	$('#div_lic_'+rowId).show();		 
	$('#div_lichash_edit_'+rowId).hide();
	$('#div_lichash_'+rowId).show();		 

 } 
 
 function addNewLic(){
		$('#new_lic').hide();
		$('#new_lic_edit').show();		 	 
		$('#new_lichash_edit').show();		 	 
 }
 
 function cancelAddNewLic(){
		$('#new_lic').show();
		$('#new_lic_edit').hide();
		$('#new_lichash_edit').hide();
 }
 
 function editEmailSettingRow(rowId){
		$('#email_'+rowId).hide();
		$('#email_edit_'+rowId).show();		 	 
}
 
 function cancelEmailEdit(rowId){
		$('#email_'+rowId).show();
		$('#email_edit_'+rowId).hide();		 	 
 }

 function addNewEmailConfig(){
		$('#new_email_config').hide();
		$('#new_email_config_edit').show();		 	 
 }

 function cancelNewEmailEdit(){
		$('#new_email_config').show();
		$('#new_email_config_edit').hide();		 	 
 }
 
 function addNewAdmin(){
		$('#new_admin_acct').hide();
		$('#new_admin_acct_edit').show();
		$('#adminAcctMsg').hide();
 }
 
 function cancelNewAdminAcct(){
 		$('#new_admin_acct_edit').hide();
		$('#new_admin_acct').show();
 }

 function updKVLic(rowId){
	var kvLicKeyVal = $('#kvLicKeyId').val();
	if(kvLicKeyVal){
		if(kvLicKeyVal.indexOf("***") != -1){
			alert("Please enter complete license key.");
			return false;
		}
	}
	if($('#kvLicHashId')){
		var kvLicKeyVal = $('#kvLicHashId').val();
		if(kvLicKeyVal){
			if(kvLicKeyVal.indexOf("***") != -1){
				alert("Please enter complete value for license hash.");
				return false;
			}
		}		
	}
	if($('#kvLicEncId')){
		var kvLicKeyVal = $('#kvLicEncId').val();
		if(kvLicKeyVal){
			if(kvLicKeyVal.indexOf("***") != -1){
				alert("Please enter complete value for license enc key.");
				return false;
			}
		}		
	}

	$('#lic_form_'+rowId).submit();
	return true;
 }
 
</script>
</body>
</html>

