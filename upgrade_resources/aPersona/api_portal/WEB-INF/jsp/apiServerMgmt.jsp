<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - Security Policy Manager</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">
<!-- <link rel="stylesheet"  -->
<%-- 	href="${pageContext.request.contextPath}/css/jquery-ui.css" />		 --%>
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

<%-- <script src="${pageContext.request.contextPath}/js/jquery-1.9.1.js"></script>
<script src="${pageContext.request.contextPath}/js/jquery-ui.js"></script>
 --%> 	
<script>
	$(function() {
	$( "#tabs" ).tabs();
	$("#tabs").tabs({active: document.tabsName.currentTab.value});
	});
</script>
	
</head>
<body>
<div style="height:100%; min-height:100%; position:relative;">
	<c:set var="selMenu" scope="request" value="apiSrvMgmt"/>
	<jsp:include page="header.jsp" />

	<div class="nof-centerContent">

      <div class="nof-clearfix nof-positioning ">
        <div class="nof-positioning TextObject" style="float: left; display:inline; width: 19px; ">
          <p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
        </div>
        <div id="Text129" class="nof-positioning TextObject" style="float: left; display: inline; width: 100%; margin-top: 9px; margin-left: 19px; ">
          <p style="margin-bottom: 0px;"><b><span style="font-size: 16px; font-weight: bold;">
          		Security Policy Manager</span></b></p>
		  <br/>
          <p>The aPersona Security Policy Manager page enables you to setup and manage the "Policies" that you want to enable for your applications. You assign each Policy an API Key that will be used by your applications. One or more applications can use the same Policy API key or you can setup an multiple Policy Keys for a single application or anything in between. You may create as many Policy keys as are needed to support your security goals.</p>
        </div>
      </div>

      <div class="nof-positioning" style="width: 100%; margin-left: 8px; ">      
	      <div class="boxLayout" style="width:100%;">
	      	<h2>aPersona Security Policy Key Manager</h2>
			<br/>
				<div class="nof-positioning" style="width:98%; margin-top: 0px; margin-left: 10px;">
				<form name="tabsName">
					<input type="hidden" name="currentTab" value="${SEL_TAB=='GROUPS' ? '1' : '0'}"/>
				</form>						
				<div id="tabs">
           			<ul>
						<li><a href="#apiServers">Add/Manage Security Policy API Keys</a></li>
						<!-- <li><a href="#apiServerList">Create/Manage Server Domain Security Groups</a></li> -->
               		</ul>                    	
	
                 	<div id="apiServers">
						<h3>Configured Security Policies</h3>
						<p>(Applicaitons must include a valid Security Policy API Key when sending in transactions to the aPersona Adaptive Security Manager.)</p>			
						<table class="ap_table"  width="100%" align="center" >
							<thead class="ap_table_hdr">
								<tr>
									<th>Policy Label</th>
									<th>Service Name</th>
									<th>IP / Domain</th>
									<!-- <th>Private IP</th> -->
									<!-- <th>Licensed Thru</th> -->
									<th>Policy API Key</th>
									<th>Settings</th>
									<th>Action</th>
								</tr>
							</thead>
							<c:forEach var="apiLic" items="${API_SERVERS}" varStatus="loop">
			
								<tr id="div_lic_${loop.index}" style="font-size: 11px;"
									class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
									<td>${apiLic.serverLabel}</td>
									<td>${apiLic.svrServiceName}</td>
									<td>${apiLic.serverPublicNatIp}</td>
									<%-- <td>${apiLic.expiryDate}</td> --%>
									
									<td>${apiLic.apiKey}</td>
									<td><input type="button" value="View/Edit" class="buttonStyle" style="font-size: 10px;"
									 onclick="javascript:editApiSettings(${apiLic.serverId});" />
									</td>									
									<td><input type="button" value="Delete Policy" class="clearButtonStyle" style="font-size: 10px;"
											onclick="javascript:deleteServer(${apiLic.serverId});" />
									</td>									
			 					</tr>			 					
							</c:forEach>
						</table>
						<br/>
						<input type="button" value="Add New Policy" onclick="javascript:addNewApiServer();" class="buttonStyle"/> 			
					</div>		

<%--                  	<div id="apiServerList">
                 	<br/>
					
						<h3>Server Domain Security Groups</h3>
						<p>(This enables a group of servers to share Login Forensic Keys)</p>			
						<table class="ap_table"  align="center" width="100%">
							<thead class="ap_table_hdr">
								<tr>
									<th>Server Domain Security Group</th>
									<th>Server Group</th>
									<th>Add Server</th>
									<th>Action</th>
								</tr>
							</thead>
							<c:forEach var="srvrGrp" items="${SERVER_GROUP_MAPPINGS}" varStatus="loop">
			
								<tr class="ap_table_tr_odd">
									<td>${srvrGrp.serverGrpName}</td>
									<td style="margin: 0px; padding: 0px;">
										<table class="ap_table_inner">
											<c:forEach var="srvr" items="${srvrGrp.serverDetails}" varStatus="loop2">
											<tr>
												<td style="border-top: 0px; border-bottom: 1px solid #ffffff;"
														class="${srvr[2] == 'Y' ? 'selectedCell' : ''}">${srvr[1]}
												</td>
												<td class="linkHoverStyle" style="border-top: 0px; border-bottom: 1px solid #ffffff; margin-right:5px;padding-right:5px;">
												<a href="deleteServerFromGroup.ap?srvrGroupId=${srvrGrp.serverGrpId}&serverId=${srvr[0]}">
													<img height="10" width="10"
														src="${pageContext.request.contextPath}/images/x.png"
														border="0" alt="Remove" title="Remove"/></a>
												</td>
											</tr>
											</c:forEach>
										</table>
									</td>
									<td>
									<div id="addNewServerButton_${loop.index}">
										<input type="button"  class="buttonStyle" style="font-size:10px;" value="Add Server" onclick="javascript:addServerToGroup(${loop.index});"/>
									</div>
									<form name="addServerToGrp" action= "addServerToGroup.ap">
										<input type="hidden" name="srvrGroupId" value="${srvrGrp.serverGrpId}" />
									<table width="100%" id="newSrvrToGrp_${loop.index}" style="display:none;">
										<tr >
											<td colspan="2" width="100%">
												<select name="newServerToAdd">
												<c:forEach var="newSrvr" items="${ungroupedServers}" varStatus="loop3">
													<option value="${newSrvr.key}">${newSrvr.value}</option>
												</c:forEach>
												</select>
											</td>
										</tr>
										<tr>
											<td colspan="2">
					 							<input type="submit" class="buttonStyle" value="Add" />
					 							&nbsp;/&nbsp;
					 							<input type="button" value="Cancel" class="buttonStyle" onclick="javascript:cancelAddServerToGroup(${loop.index});"/></td>		 						
											</td>
										</tr>					
									</table>
									</form>
									</td>
									<td>
									<input type="button"  class="clearButtonStyle" style="font-size: 10px;" value="Delete Server Group" 
										onclick="javascript:if(confirm('Are you sure you want to delete this server group?')){window.location.href='deleteServerGroup.ap?srvrGroupId=${srvrGrp.serverGrpId}'};"/> 	
			 					</tr>
			 					<tr  class="ap_table_tr_even" > <td colspan = "5" width="100%" style="margin: 0px; padding: 0px;"/> <hr/> </tr>		 					
							</c:forEach>
							<tr id="newServerGroupRow" class="ap_table_tr_odd" style="display:none;">
							<form name="new_server_grp_form" method="post" action="newServerGroup.ap" 
														class="formStyle">
								<td><input type="text" size="30" required name="newServerGroupName" /></td>
								<td><input type="Submit"  class="buttonStyle" value="Add"/>
									&nbsp;/&nbsp;
									<input type="button"  class="buttonStyle"
											value="Cancel" onclick="javsscript:cancelNewServerGroup();"/>		 								 						
								</td>
								<td  colspan="2"></td>							
							</form>
							</tr>
						</table>
						<br/>
						<div id="newServerGroupButton">
							<input type="button" class="buttonStyle"  value="Add Server Domain Security Group" 
								onclick="javsscript:addNewServerGroup();"/> 			
						</div>
					</div>		
 --%>
 
 
 				</div>
			</div>		
		</div>
	  </div>
    </div>
</div>
<%@include file="footer.html" %>

<script>
	function editApiSettings(serverId){
		window.location.href = "apiServerDetails.ap?serverId="+serverId;
	}
	
	function clearApiLoginKeys(serverId){
		window.location.href = "apiServerClearKeys.ap?serverId="+serverId;
	}

	function addNewApiServer(){
		window.location.href = "apiServerDetails.ap?serverId=-1";
	}
	
	function deleteServer(serverId){
		if(confirm('Are you sure you want to delete this security policy? Ensure there are no applications using this policy before you delete it!')){
			window.location.href = "deleteServer.ap?serverId="+serverId;
		}		
	}
	
	function addServerToGroup(idx){		
		$('#newSrvrToGrp_'+idx).show();
		$('#addNewServerButton_'+idx).hide();		
	}

	function cancelAddServerToGroup(idx){		
		$('#newSrvrToGrp_'+idx).hide();
		$('#addNewServerButton_'+idx).show();		
	}
	
	function addNewServerGroup(){
		$('#newServerGroupButton').hide();
		$('#newServerGroupRow').show();				
	}

	function cancelNewServerGroup(){
		$('#newServerGroupButton').show();
		$('#newServerGroupRow').hide();				
	}

</script>
</body>
</html>
	
