<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>aPersona - User Management</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">
<link rel="stylesheet"
	href="${pageContext.request.contextPath}/css/jquery-ui.css" />
<link href="${pageContext.request.contextPath}/css/theme.default.css" rel="stylesheet">
		<link rel="icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	<link rel="shortcut icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">

<script src="${pageContext.request.contextPath}/js/jquery-1.9.1.js"></script>
<script src="${pageContext.request.contextPath}/js/jquery-ui.js"></script>
<script type="text/javascript" src="${pageContext.request.contextPath}/js/jquery.tablesorter.min.js"></script>

<script>
	$(function() {		
		$( "#tabs" ).tabs();		
		$( "#autoUserRegDt" ).datepicker();
		var selTab = document.tabsName.currentTab.value;
		var selTabIdx = 0;
		if(selTab=='END_USER'){
			selTabIdx = 1;
		}else if(selTab == 'REM_ALL_USERS'){
			selTabIdx = 2;
		}
		$("#tabs").tabs({active: selTabIdx});
	});
</script>

</head>
<body class="nof-centerBody">
	<div style="height: 100%; min-height: 100%; position: relative;">
		<c:set var="selMenu" scope="request" value="userMgmt" />
		<jsp:include page="header.jsp" />

		<div class="nof-centerContent">
			<form name="tabsName">
				<input type="hidden" name="currentTab" value="${SEL_TAB}"/>
			</form>
			<div class="nof-clearfix nof-positioning ">
				<div class="nof-positioning TextObject"
					style="float: left; display: inline; width: 19px;">
					<p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
				</div>
				<div id="Text129" class="nof-positioning TextObject" style="float: left; display: inline; width: 100%; margin-top: 9px; margin-left: 19px; ">
					<p style="margin-bottom: 0px;">
						<b><span style="font-size: 16px; font-weight: bold;">
								aPersona Adaptive Security Manager - User Management</span>
						</b>
					</p>
					<br />
					<p>The aPersona Adaptive Security Manager will only perform multi-factor authentication for Registered Users. The Automatic User Registration option below is an automatic “Opt-In”. If your strategy for multi-factor authentication is to allow users to “Opt-In, then leave this setting set to “Off” and register users one at a time, or by uploading a file, or use the Registration API (coming soon) to enable your users to Opt-In.</p>
				</div>
			</div>

			<div class="nof-positioning" style="width: 100%; margin-left: 8px;">
				<br />
				<div class="boxLayout" style="width: 100%;">
					<h2>End User Management</h2>
					<br />

					<div class="nof-positioning"
						style="width: 95%; margin-top: 13px; margin-left: 28px;">
						<div id="tabs">
							<ul>
								<li><a href="#registerUser">Register End Users</a>
								</li>
								<li><a href="#userSearch">End User Search</a>
								</li>
								<li><a href="#removeAllUsers">Remove All User Registrations</a>
								</li>								
							</ul>

							<div id="registerUser">
								<br />
								<table style="border: 0px;">
									<tr>
										<td>
											<h3>Register a single user:</h3>

											<form name="regNewUser" method="post"
												action="regSingleUser.ap">
												<input required type="email" name="newUserEmail" size="30"
													placeholder="Email address">
												<input name="newLoginId" size="35"
													placeholder="User Login Id (if different than email)">													 
													<input type="submit" class="buttonStyle" value="Add" />
											</form></td>
										<td></td>
									</tr>
									
		                    <c:if test="${USER_ACCT_ERROR_MESSAGE != null}">
			                   <tr>
			                   		
				                   	<td colspan="2">
			            				<div style="text-align:left; color:red;">${USER_ACCT_ERROR_MESSAGE}</div>
				                   	</td>
			                    </tr>
							</c:if>
		                    <c:if test="${USER_ACCT_MESSAGE != null}">
			                   <tr>
				                   	<td colspan="2">
			            				<div style="text-align:left; color:green;">${USER_ACCT_MESSAGE}</div>
				                   	</td>
			                    </tr>
							</c:if>
																		
								</table>
								<br />
								<hr />
								<br />
								<h3>Register users from a text file: (One user per line. ex: emailId@domain.com, userId)</h3>

								<form method="post" enctype="multipart/form-data" action="uploadUsers.ap">
								  File: <input type="file" name="usersFile"/><br/>
								  <input type="submit" class="buttonStyle" value="Register Users" />
								</form>
								
<!-- 									<input type="file" id="uploadUsersFile" name="files[]"/>
									<br/> 
								<div id="uploadUsersDiv" style="display:none;">
									<form name="registerUsers" method="post" action="regUsersFromFile.ap">
									<table id="uploadedUsersTable" class="ap_table" style="font-size: 1px; line-height: 0;">
									</table>
									<p id="usersUploadResult"></p>
									</br>
									<input type="submit" class="buttonStyle" value="Register Selected Users" /> <br />
									</form>
									</div>
 -->									<p>
									<div id="uploadUsersErrMsgDiv">
										<span id="busyStatus" class="ap_error"></span>
										<c:if test='${UPLOAD_USERS_ERROR_MESSAGE != null}'>
											<p><span class="ap_error">${UPLOAD_USERS_ERROR_MESSAGE}</span></p>
											<br/>
										</c:if>
										<c:if test='${UPLOAD_USERS_COUNT != null}'>
											<p><span style="color:green;">${UPLOAD_USERS_COUNT} users are successfully registered now.</span></p>
											<br/>
										</c:if>
										<c:if test='${UPLOAD_ERROR_EXISTING_USERS != null}'>
											<p><span class="ap_error">These users are already registered in your aP-ASM: ${UPLOAD_ERROR_EXISTING_USERS}</span></p>
											<br/>
										</c:if>									
										<c:if test='${UPLOAD_ERROR_FAILED_USERS != null}'>
											<p><span class="ap_error">We encountered an issue in registering these users: ${UPLOAD_ERROR_FAILED_USERS}</span></p>
											<br/>
										</c:if>
									</div>									
								<br/>
								<hr />
								<br />

								<!-- TODO -->
								<h3>Automatic User Registration:</h3>
								<form name="autoRegisterForm" action="autoRegister.ap" method="post">
									<select name="autoRegister" style="height: 24px;">
										<option value="N" ${(autoRegister == null || autoRegister == 'N') ? 'selected' : ''}>Off</option>
										<option value="Y" ${autoRegister == 'Y' ? 'selected' : ''}>On</option>
									</select> &nbsp;&nbsp;&nbsp;<b><%-- <u><span
											style="font-weight: bold;">Until:</span>
									</u>
									<fmt:formatDate 
                                  		value="${autoUserRegDt}"  
						                type="date" 
						                pattern="MM/dd/yyyy"
						                var="autoUserRegDtFmt" />									
									</b>&nbsp;&nbsp;&nbsp; --%> <input type="hidden" id="autoUserRegDt" value="${autoUserRegDtFmt}"
										name="autoUserRegDt" size="12" maxlength="13"
										placeholder="mm/dd/yyyy" />
										
										&nbsp;&nbsp;&nbsp; <input type="Submit" value="Save"
										class="buttonStyle" />
										 
									<br /> <br />
									<c:if test="${AUTO_REG_MESSAGE != null}">
			            				<p style="text-align:left; color:green;">${AUTO_REG_MESSAGE}</p>
									</c:if>
									<c:if test="${AUTO_REG_ERR_MESSAGE != null}">
			            				<p style="text-align:left; color:red;">${AUTO_REG_ERR_MESSAGE}</p>
									</c:if>
										
									<p style="text-align: justify; margin-bottom: 0px;">
										<b><i><span style="font-weight: bold;">(If
													&#8220;<u>On</u>&#8221;, the aPersona Adaptive Security Manager will automatically
													register users when a confirmation transaction is sent
													to it. This in effect is an &#8220;automatic
													Opt-In&#8221; for multi-factor authentication.)</span>
										</i>
										</b>
									</p>									
								</form>
								<c:if test="${USER_ACCT_ERROR_MESSAGE != null}">
			                   <tr>			                   	
				                   	<td colspan="2">
			            				<div style="text-align:left; color:red;">${USER_ACCT_ERROR_MESSAGE}</div>
				                   	</td>
			                    </tr>
							</c:if>
								
							</div>
							<div id="userSearch">
								<br />
								<form name="userSearch" method="get" action="searchUsers.ap">
									<input type="text" name="userSearchKey" size="40"
										value="${userSearchKey}"
										placeholder="Type all or part of user Email Address" /> 
									<input type="Submit" class="buttonStyle" value="Search" />
								</form>
								<br />
								<h3>
									<b>Search Results</b>
								</h3>
								<form name="forceEnhanced" method="post"
									action="forceEnhanced.ap">
									<input type="hidden" name="userSearchKey"
										value="${userSearchKey}" />

									<table class="ap_table" width="98%" align="center"
										style="text-align: left;">
										<thead>
											<tr>
												<th>User Email Address
												</th>
												<th>User Login Id
												</th>
												<th>User Verified?
												</th>
												<th>Remove User Registration
												</th>
												<th>Clear All Login Forensic Keys
												</th>
												<th>Force Enhanced Security Across All Servers
												</th>
											</tr>
										</thead>
										<c:forEach var="user" items="${USERS}" varStatus="loop">
											<tr
												class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
												<td style="text-align:left;">${user.email}</td>
												<td style="text-align:left;">${user.userLoginId}</td>
												<td>${user.isVerified=='1' ? 'Yes' : 'No'}</td>
												<td><input type="button" class="clearButtonStyle" value="Remove"
													onClick="javascript:if(confirm('Are you sure you want to remove this user?')){removeUser(${user.userId}, document.userSearch.userSearchKey.value);}" />
												</td>
												<td><input type="button" class="alertButtonStyle" value="Clear Keys"
													onClick="javascript:if(confirm('Are you sure you want to clear all keys for this user?')){clearUserKeys(${user.userId}, document.userSearch.userSearchKey.value);}" />
												</td>
												<td><input type="checkbox" value="${user.userId}"
													name="forceEnhancedUsers" ${user.forceEnhanced== 'Y' ? 'checked' : ''}/>
												</td>
											</tr>
										</c:forEach>
									</table>
									<br/>
									<input type="submit" class="buttonStyle" value="Save" />
								</form>
							</div>
							
							<div id="removeAllUsers">
								<br />
								<h3>Remove All User Registrations</h3>
								<p>If you need to clean up your aP-ASM user database to start fresh, or because you are trying to fully delete a Client aP-ASM Account, you can remove all user registrations here. This action is will remove all registrations for client: <b>${PROVIDER_NAME}</b>.</p>
								<p>There are ${NUM_USERS} users currently registered for this client</p>
									<input type="button" class="clearButtonStyle" value="Remove All User Registrations"
													onClick="javascript:if(confirm('This action will immediatly remove all user registrations for this client. This action is irrevokable! Are you sure you want to remove all user registration from for this client?')){
															if(confirm('LAST WARNING! Are you ABSOLUTELY SURE you want to remove all user registraitions?')){
															removeAllUsers(${PROVIDER_ID});}}" />
									
								</form>
							</div>
							
						</div>
					</div>
				</div>
			</div>
			</div>
			</div>
			
<%@include file="footer.html" %>			
<script>
	function clearUserKeys(userId, userSearchKey){
		window.location.href = "clearKeys.ap?userId="+userId+"&userSearchKey="+userSearchKey;
	}
	
	function removeUser(userId, userSearchKey){
		window.location="removeUser.ap?userId="+userId+"&userSearchKey="+userSearchKey;
	}
	
	function removeAllUsers(providerId){
		window.location="removeAllUsers.ap?providerId="+providerId;
	}
	
	function handleFileSelect(evt) {
	    evt.stopPropagation();
	    evt.preventDefault();
	
        $('#uploadUsersErrMsgDiv').hide();
	    var files = evt.target.files || evt.dataTransfer.files; // FileList object.
	    var file = files[0];

	    // this creates the FileReader and reads stuff as text
	    var fr = new FileReader();
	    fr.onload = parse;
	    fr.readAsText(file);

	    // parse file and populates the table
	    function parse()
	    {
	        var table = document.getElementById('uploadedUsersTable');
	        var usersList = fr.result.split('\n'); 
	        var c = 0;
	        var rowIdx =0;
	        var content = "<thead class='ap_table_hdr'><tr><th></th><th>User Email Id</th><th>Action</th></tr></thead>";
	        for (var i in usersList)
	        {
	        	c++;
	        	var user = usersList[i];
	        	user = $.trim(user);
	        	// user = trim(user);
	        	if (user != '')
	            {
	                content+= "<tr class='ap_table_tr_odd' id='usr_"+rowIdx+"'>";
//	                content+="<td><input type='checkbox' checked value="+user+"+ name='selUsersToUpload' /></td>";
//	                content+="<td>"+user+"</td>";
	                content+="<td>"+c+"</td>";
	                content+="<td><input type='email' value="+user+" name='selUsersToUpload' /></td>";
	                //content+="<td><input type='button' class='clearButtonStyle' onclick='document.getElementById(\"uploadedUsersTable\").deleteRow("+i");' /></td>";	                
	                content+="<td><input type='image' value='Remove' class='clearButtonStyle' src='${pageContext.request.contextPath}/images/trash.png' onclick='javascript:deleteRow(this); return false;' /></td>";
                	content+="</tr>";
                	rowIdx++;
	            }
	        }
	        table.innerHTML=content;
	        
	        // document.getElementById('usersUploadResult').innerHTML = '<span>Uploaded ' + c + ' users from file: ' + file.name + '</span>';
	        $('#uploadUsersDiv').show();
	    }
	}
	
	function deleteRow(tdObj){
		//var rowElement = document.getElementById('rowId');
		var rowObj = tdObj.parentNode.parentNode;
		//alert(rowObj+" - "+rowObj.rowIndex);		
		document.getElementById("uploadedUsersTable").deleteRow(rowObj.rowIndex);
		return false;
	}
	document.getElementById("uploadUsersFile").addEventListener('change', handleFileSelect, false);
</script>
</body>
</html>

