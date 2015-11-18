<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn" %>

<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - Client Management</title>
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
	<c:set var="selMenu" scope="request" value="clientMgmt"/>
	<jsp:include page="header.jsp" />

	<div class="nof-centerContent">

      <div class="nof-clearfix nof-positioning ">
        <div id="Text140" class="nof-positioning TextObject" style="float: left; display:inline; width: 19px;">
          <p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
        </div>
        <div id="Text129" class="nof-positioning TextObject" style="float: left; display: inline; width: 1000px; margin-top: 9px; margin-left: 0px; ">
          <p style="margin-bottom: 0px;"><b><span style="font-size: 16px; font-weight: bold;">Client and Admin Management</span></b></p>
		  <br/>
          <p>Welcome to the aPersona Adaptive Security Manger. Please use below section(s) to configure clients and administrators for respective clients.</p>
        </div>
      </div>
	  
	  <c:if test="${USER_NOT_SUPER_ADMIN == 'USER_NOT_SUPER_ADMIN'}">
      <div class="nof-positioning" style="width: 100%; margin-left: 8px; ">
	      <br/>	      
	      <div class="boxLayout" style="width:100%;">
	      	<h2>Access Denied</h2>
			<br/>
			<h3>You are not authorized to access this page!</h3>
	  	  </div>
	  </div>	  
	  </c:if>
	  
	  <c:if test="${USER_NOT_SUPER_ADMIN != 'USER_NOT_SUPER_ADMIN'}">
      <div class="nof-positioning" style="width: 100%; margin-left: 8px; ">
	      <br/>	      


	      <div class="boxLayout" style="width:100%;">
	      <div class="boxLayout" style="width:100%;">
	      	<h2>Client Management</h2>
			<br/>
	        <h3>Please select the client to access administration pages for client.</h3>
	        <form name="selProvider" method="post" action="continueToProvider.ap">
	        
	        	<p width="98%" align="left">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Client Name:</b>&nbsp;&nbsp;&nbsp;&nbsp; 
	            <select name="selectedProviderId">
					<c:forEach var="kvProvider" items="${KV_PROVIDERS}" varStatus="loop">
						<option value="${kvProvider.providerId}">${kvProvider.providerName}</option>
					</c:forEach>	          
	          </select>
	          &nbsp;&nbsp;&nbsp;&nbsp;
	          <input type="submit" class="buttonStyle" value="Continue" />
	          </p>
	        </form>
	        
			<hr size="1"/>
			<br/>
			<h3>Add or Modify Clients:</h3>
						<div style="overflow-y:auto; max-height:200px;">
			
			<table class="ap_table" width="98%" align="center" style="font-size: 1px; line-height: 0;">
				<thead class="ap_table_hdr">
					<tr>
						<th>Client Id</th>
						<th>Client Name</th>
						<th>Client URL (For Reference Only.)</th>
						<th>Date Created</th>
						<th>Action</th>
					</tr>
				</thead>
				
				<c:forEach var="kvProvider" items="${KV_PROVIDERS}" varStatus="loop">
							<fmt:formatDate 
                                  		value="${kvProvider.createdAt}"  
						                type="date" 
						                pattern="yyyy-MM-dd HH:mm:ss"
						                var="createdAt" />
						<c:set var="pName" value="${fn:substring(kvProvider.providerName, 0, 28)}" />
						<tr id="div_provider_${loop.index}" 
							class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
							<td width="10%">${kvProvider.providerId}</td>
							<td width="30%" style="margin-left:-100px; text-align:left;">${pName}</td>
							<td width="30%" style="margin-left:-100px; text-align:left;">${kvProvider.providerUrl}</td>
							<td width="15%" style="margin-left:-100px; text-align:left;">${createdAt}</td>
							<td width="15%"><input type="button" class="buttonStyle" value="Edit" onclick="javascript:editProvider(${loop.index});" />
								&nbsp;
								<input type="image" class="clearButtonStyle" value="Delete"
								src="${pageContext.request.contextPath}/images/trash.png"
								 onclick="javascript:deleteProvider(${kvProvider.providerId});" />								
	 						</td>
	 					</tr> 					
	 					
						<tr id="div_provider_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
						<form name="edit_provider_${loop.index}" method="post" action="editProvider.ap">
								<td></td>
								<td  style=" border-left:-10px solid #A0A0A0;">
									<input required type="text" size="40" name="kvProviderName" value="${kvProvider.providerName}"/> </td>
								<td><input required type="text" size="40" name="kvProviderUrl" value="${kvProvider.providerUrl}"/></td>
								<td colspan="2"><input type="hidden" size="18" name="kvProviderId" value="${kvProvider.providerId}" />
		 							<input type="Submit" class="buttonStyle" value="Save"/>
		 							&nbsp;/&nbsp;
		 							<input type="button" value="Cancel" class="buttonStyle" onclick="javascript:cancelProviderEdit(${loop.index});"/></td>		 						
							</form>
						</tr>
					</c:forEach>
			</table>
			</div>
			<table class="ap_table" width="98%" align="center" style="font-size: 1px; line-height: 0;">		
					<tfoot>
						<tr id="new_provider">
							<td colspan="4" align="left"><input class="buttonStyle" style="width:110px; margin-bottom:3px;  margin-top:2px;" 
								type="button" value="Add New Client" onclick="javascript:addNewProvider();"/></td>
						</tr>
						<tr id="new_provider_edit" style="display:none;" class="ap_table_tr_even">
							<form name="new_provider_form" method="post" action="editProvider.ap" class="formStyle">
								<td style="border-right:0px;"><input type="hidden" name="kvProviderId" value="-1" /></td>								
								<td style="border-right:0px;"><input required type="text" size="40" name="kvProviderName" /></td>
								<td style="border-right:0px;"><input required  type="text" size="40" name="kvProviderUrl" style="margin-left:-20px;"/></td>
								<td style="border-right:0px;">
									<input type="Submit"  class="buttonStyle" value="Save"/>
									&nbsp;/&nbsp;
									<input type="button"  class="buttonStyle"
											value="Cancel" onclick="javsscript:cancelAddProvider();"/></td>		 								 						
							</form>
						</tr>										
				<c:if test="${KV_PROVIDER_ERROR_MESSAGE != null}">
						<tr>
							<td colspan="4" align="left"><span class="ap_error">${KV_PROVIDER_ERROR_MESSAGE}</span></td>
						</tr>					
				</c:if>
				<c:if test="${KV_PROVIDER_MESSAGE != null}">
					<tr>
						<td colspan="4" align="left"><span style="color:green;">${KV_PROVIDER_MESSAGE}</span></td>
					</tr>
				</c:if>
			  </tfoot>			
			</table>
			<br/>
			<hr size="1" >
			<br/>
	        <h3>Add or Modify Super Admin Accounts:</h3>
	        
							<table class="ap_table" width="98%" align="center" >
								<thead class="ap_table_hdr">
									<tr>
										<th>Super Admin Account Id</th>
										<th>Is Active</th>
										<th>Force OTP Login</th>
										<th>Re-send OTP</th>
										<th>Action</th>
									</tr>
								</thead>
								<c:forEach var="adminAcct" items="${KV_SUPER_ADMIN_ACCOUNTS}" varStatus="loop">
				
									<tr class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
										<td style="text-align:left;">${adminAcct[0]}</td>
										<td>${adminAcct[5] == "1" ? "Active" : "Not Active"}</td>
										<td>
											<c:if test="${adminAcct[6] == 'N'}">
												<input type="button" class="clearButtonStyle" value="OTP Login is Disabled - Activate now" 
														onclick="javascript:window.location='forceEnhancedLogin.ap?kvAdminUserEmail=${adminAcct[0]}&opt=Y&providerId=0';" />													
											</c:if>
											<c:if test="${adminAcct[6] != 'N'}">
												<input type="button" class="buttonStyle" value="OTP  Login  is  Active  -  Disable now" 
														onclick="javascript:window.location='forceEnhancedLogin.ap?kvAdminUserEmail=${adminAcct[0]}&opt=N&providerId=0';" />													
											</c:if>																					
										</td>
										<td>
<%-- 											<input type="button" class="buttonStyle" 
													value="${(adminAcct[7] == "1"||adminAcct[7] == null) ? "Re-send Welcome OTP" : "Re-send   Login   OTP"}" 
													onclick="javascript:window.location='resendOtp.ap?kvAdminUserEmail=${adminAcct[0]}';" />													
 --%>									
 										<c:if test="${(adminAcct[7] eq '1' || adminAcct[7] eq null)}">
	 										<a class="linkHoverStyle" style="color:blue;" href="resendOtp.ap?kvAdminUserEmail=${adminAcct[0]}&providerId=0">
 												<b>Re-send Welcome OTP</b>
 											</a>
 										</c:if>
 										</td>
										<!-- remove user role id  -->
										<td>
										<input type="image" class="clearButtonStyle" value="Delete"
											src="${pageContext.request.contextPath}/images/trash.png"
											 onclick="javascript:if(confirm('Are you sure you want to delete this Super Admin user?')){window.location='removeKvAdminAcct.ap?kvAdminUserId=${adminAcct[0]}&providerId=0'};" />								
										</td>
				 					</tr>
								</c:forEach>
								
								<tfoot>
									<tr id="new_admin_acct">
										<td colspan="5" align="left"><input style="align:left;  margin-bottom:3px;  margin-top:2px;" type="button" value="Add New Super Admin"  class="buttonStyle" 
										onclick="javascript:addNewAdmin();"/></td>
									</tr>
									<c:if test='${ADMIN_ACCT_ERROR_MESSAGE != null}'>
										<tr id="adminAcctMsg" ><td colspan="6" style="text-align:center;">
													<span class="ap_error">${ADMIN_ACCT_ERROR_MESSAGE}</span>
										</td></tr>
									</c:if>
									<c:if test='${ADMIN_ACCT_MESSAGE != null}'>
										<tr id="adminAcctMsg"><td colspan="5" style="text-align:center;">
													<span class="ap_success">${ADMIN_ACCT_MESSAGE}</span>
										</td></tr>
									</c:if>

									<tr id="new_admin_acct_edit" style="display:none;" class="ap_table_tr_even">										
										<form name="new_email_form" method="post" action="addNewAdminAcct.ap">																		
											<td  style=" border-left:2px solid #A0A0A0;"  colspan="1">
											<input type="hidden" name="providerId" value="0"/>
											<input type="hidden" name="isSuperAdmin" value="Y"/>
											<input required size="25" type="email" name="adminEmail" /></td>
											<td colspan="2">
					 							<input type="Submit"  class="buttonStyle" value="Add"/>
					 							&nbsp;/&nbsp;
					 							<input type="button" value="Cancel"  class="buttonStyle" onclick="javascript:cancelNewAdminAcct();"/></td>		 						
										</form>
									</tr>					
								</tfoot>				
							</table> 		
	        
			<br/>
			<hr size="1" >
			<br/>
				        
	        <!-- Start of Email configuration -->
			<h3>Admin Email Settings:</h3>
			
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
				
				<c:if test="${fn:length(ADMIN_MAIL_SETTING) gt 0}">
				
					<c:forEach var="adminEmail" items="${ADMIN_MAIL_SETTING}" varStatus="loop">
	
						<tr id="email_${loop.index}" 
							class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
							<td>${adminEmail.smtpoutUrl}</td>
							<td>${adminEmail.portNumber}</td>
							<td>${adminEmail.loginId}</td>
							<td>********</td>
							<td>${adminEmail.protocol}</td>
							<td>${adminEmail.smtp}</td>
							<td>${adminEmail.fromAddr}</td>
		 					<td>
								<a class="linkHoverStyle" style="color:blue;" href="testEmailSettings.ap?emailServiceId=${adminEmail.emailServiceId}&adminSettings=true">
									<b>Test Settings</b>
								</a>
							</td>
							<td><input type="button" value="Edit" class="buttonStyle"
								onclick="javascript:editEmailSettingRow(${loop.index});" />
								&nbsp;  &nbsp;
								<input type="image" class="clearButtonStyle" value="Delete"
								src="${pageContext.request.contextPath}/images/trash.png"
								 onclick="javascript:if(confirm('Are you sure you want to delete Email Service Settings?')){window.location='removeEmailSetting.ap?emailServiceId=${adminEmail.emailServiceId}&adminSettings=true'};" />
	 						</td>
	 					</tr> 				
	 					
						<tr id="email_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
						<form name="edit_email_${loop.index}" method="post" action="editAdminEmailConfig.ap">
							
							<td style="padding:0px; border-left:1px solid #A0A0A0;"><input style="padding:0px;" required type="text" name="smtpoutUrl" value="${adminEmail.smtpoutUrl}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" required size="5" type="text" name="portNumber" value="${adminEmail.portNumber}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" type="text" name="loginId" value="${adminEmail.loginId}"/></td>
							<td style="padding:0px;"><input style="padding:0px;" size="12" type="password" name="password" value="${adminEmail.password}"/></td>
							<td style="padding:0px;"><select name="protocol">
                                              <option value="ssl" ${adminEmail.protocol == 'ssl' ? 'selected' : ''}>SSL</option>
                                              <option value="tls" ${adminEmail.protocol == 'tls' ? 'selected' : ''}>TLS</option>
                                              <option value="none" ${adminEmail.protocol == 'none' ? 'selected' : ''}>NONE</option>
                                            </select>
                            </td>
							<td style="padding:0px;"><select name="smtp">
                                              <option value="smtp" ${adminEmail.smtp == 'smtp' ? 'selected' : ''}>SMTP</option>
                                              <option value="smtps" ${adminEmail.smtp == 'smtps' ? 'selected' : ''}>SMTPS</option>
                                            </select>
                            </td>
							<td style="padding:0px;"><input style="padding:0px;" required size="12" type="text" name="fromAddr" value="${adminEmail.fromAddr}"/></td>
							<td colspan="2"><input type="hidden" name="emailServId" value="${adminEmail.emailServiceId}" />
	 							<input   type="Submit"  class="buttonStyle" value="Save"/>
	 							&nbsp;/&nbsp;
	 							<input type="button" value="Cancel"  class="buttonStyle" onclick="javascript:cancelEmailEdit(${loop.index});"/>
	 						</td>	 						
							</form>
						</tr>
					</c:forEach>
					
				</c:if>
				
				<c:if test="${fn:length(ADMIN_MAIL_SETTING) eq 0}">
					<tfoot>
						<tr id="new_email_config">
							<td colspan="9" align="left"><input style="align:left; margin-bottom:3px;  margin-top:2px;" class="buttonStyle" type="button" value="Add Email Config" onclick="javascript:addNewEmailConfig();"/></td>
						</tr>
						<tr id="new_email_config_edit" style="display:none;" class="ap_table_tr_even">
							<form name="new_email_form" method="post" action="editAdminEmailConfig.ap" >								
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
	        
	        
	   </div>
	      	<h2>Installation ID</h2>
			<br/>
	        <h3>Please enter the Installation ID from your License Account.</h3>
	        <form id="installKeyForm" method="post" action="editIntsllationTracker.ap">
	        
	        	<p width="98%" align="left">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Installation ID:</b>&nbsp;&nbsp;&nbsp;&nbsp;
	        	<input size="40" name="intsllationTracker" id="intsllationTrackerId" value="${intsllationTracker}" /> 
		          <input type="button" class="buttonStyle" value="Save" onclick="javascript:updInstallKey();"/>
	          </p>
	        </form>
			<c:if test="${INSTALLATION_MSG != null}">
					<p width="98%" align="left">
						<span style="color:green;">${INSTALLATION_MSG}</span>
					</p>
			</c:if>	        
<!-- 	          <hr/>
	          <p> FOR TESTING ONLY <br/>
	          		<a href="http://localhost:8080/apkv/sendLicLog.kv" target="_blank">Click here</a> to send aP-ASM logs to Licensing Server
	          	</p>
	        
			<hr size="1"/>
 -->			<br/>
		</div>

	   </div>
	   </c:if>
	</div>
	<br/>		
</div>
<%@include file="footer.html" %>
<script>

function editProvider(rowId){
	$('#div_provider_'+rowId).hide();
	$('#div_provider_edit_'+rowId).show();
}
 
 function cancelProviderEdit(rowId){
	$('#div_provider_edit_'+rowId).hide();
	$('#div_provider_'+rowId).show();		 
 } 
 
 function addNewProvider(){
		$('#new_provider').hide();
		$('#new_provider_edit').show();		 	 
 }
 
 function cancelAddProvider(){
		$('#new_provider_edit').hide();
		$('#new_provider').show();		 	 
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

function deleteProvider(providerId){
	if(confirm('Please note that all setting for the client(Key Valut, servers, users, email configuration) should be deleted before deleting the client. Are you sure you want to proceed?')){
		window.location='removeProvider.ap?providerId='+providerId;
	}	
}

function updInstallKey(){
	var installKey = $(intsllationTrackerId).val();
	if(installKey){
		if(installKey.indexOf("***") != -1){
			alert("Please enter full installation id.");
			return false;
		}
	}
	$('#installKeyForm').submit();
	return true;
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

</script>
</body>
</html>