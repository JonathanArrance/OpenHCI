<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>aPersona - My Licenses</title>
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

<style>
	a.licHist:hover{ cursor:pointer}
</style>
</head>
<body class="nof-centerBody">
	<div>
		<c:set var="selMenu" scope="request" value="userLic" />
		<jsp:include page="header.jsp" />

		<div class="nof-centerContent">
			<div class="nof-clearfix nof-positioning ">
				<div id="Text140" class="nof-positioning TextObject"
					style="float: left; display: inline; width: 19px;">
					<p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
				</div>
				<div id="Text129" class="nof-positioning TextObject"
					style="float: left; display: inline; width: 1000px; 
					margin-top:9px;">
					<p style="margin-bottom: 10px;">
						<b><span style="font-size: 16px; font-weight: bold;">Welcome</span> </b>
					</p>
        			<p style="margin-bottom: 0px;">Welcome to the aPersona Licensing Server Customer Portal. 
        			You can manage your licenses, check on orders, update your profile, download software 
        			and buy or extend licenses. For any questions relating to your 
        			account please see the <span style="color: rgb(0,102,255);">purchasing and licensing FAQ&#8217;s</span> page. 
        			</p>
				</div>
			</div>
			
			<div class="nof-positioning" style="width: 1058px; margin-left: 8px;">
				<br />
				<div class="boxLayout" style="width: 100%;">
					<h2>aPersona License Management</h2>
					<div class="nof-positioning" style="width:1020px; margin-top: 13px; margin-left: 28px;">
					  <h2> List of Active Licenses</h2> 
			          <table class="ap_table" width="100%">
						<thead class="ap_table_hdr">
							<c:if test="${not empty USER_LIC_ERR_MSG}">
								<tr class="ap_table_tr_odd">
									<td colspan="6"><span class="ap_error">${USER_LIC_ERR_MSG}</span></td>
								</tr>
							</c:if>
							<tr>
								<th>License Key</th>
								<th>Product Type</th>
								<th>Num of Users</th>
								<th>Expiration Date</th>
								<th>Auto-Renew</th>					
								<!-- <th>Public/NAT IP</th> -->
								<th>Actions</th>
							</tr>
						</thead>
						<c:if test="${fn:length(USER_KV_LIST) eq 0}">
							<tr class='ap_table_tr_odd'>
								<td colspan="6">There are no licenses in your account.</td>
							</tr>
						</c:if>
						<c:if test="${fn:length(USER_KV_LIST) gt 0}">
							<c:forEach var="lic" items="${USER_KV_LIST}" varStatus="loop">
								<tr id="KV_lic_${loop.index}" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
									<td title="Click to see full License Key" onClick="javascript:changeVal(this,'${lic.fullLicenseKey}');"
										><u> <font color="blue">${lic.licenseKey}</font></u></td>
									<td>${lic.prodDesc}</td>
									<td style="text-align: right"><c:out value="${lic.numOfUsers == '1000000' ? 'Unlimited' : lic.numOfUsers}"/></td>
									<td>${lic.expirationDate}</td>
									<td>${lic.autoRenew == 'Y' ? 'On': 'Off'}</td>
									<%-- <td>${lic.publicIp}</td> --%>
									<td><input type="button" class="buttonStyle" value="Edit" onclick="javascript:editLic(${loop.index});" />
										&nbsp;
										<input type="button" class="buttonStyle" value="Upgrade Users" onclick="window.location='extendLic.ap?licId=${lic.prodInstanceId}'" />
										&nbsp;
										<input type="button" class="buttonStyle" value="Extend Expiry" onclick="window.location='extendLic.ap?licId=${lic.prodInstanceId}&extExpiry=Y'" />
									</td>
								</tr>
								<tr id="KV_lic_edit_${loop.index}" style="display:none;" class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
									<form name="KV_lic_edit_form_${loop.index}" method="post" action="editKVLic.ap">
										<td>${lic.licenseKey}
											<input type="hidden" name="licKey" value= "${lic.licenseKey}"/>
											<input type="hidden" name="prodInstanceId" value= "${lic.prodInstanceId}"/>
										</td>
										<td>${lic.prodDesc}</td>
										<td style="text-align: right"><c:out value="${lic.numOfUsers == '1000000' ? 'Unlimited' : lic.numOfUsers}"/></td>
										<td>${lic.expirationDate}</td>
										<td><select name="autoRenew">
												<option value="Y" ${lic.autoRenew == 'Y' ? 'selected': ''}>On</option>
												<option value="N" ${lic.autoRenew == 'Y' ? '': 'selected'}>Off</option>
											</select></td>
<%-- 										<td><input name="publicIp" value="${lic.publicIp}"/>
										</td>
 --%>										 
										<td><input type="Submit" class="buttonStyle" value="Save"/>
											&nbsp;
											<input type="button" class="buttonStyle" value="Cancel" onclick="javascript:cancelEditLic(${loop.index});" />
										</td>										
									</form>
								</tr>	
							</c:forEach>	
						</c:if>	
					</table>
					</div>
					
				<br/>
				<hr size="1" >
			  <div class="nof-positioning" style="width: 1020px; margin-top: 13px; margin-left: 28px;">	
				  <h2> List of Expired Licenses</h2> 
		          <table class="ap_table" width="100%">
					<thead class="ap_table_hdr">
						<tr>
							<th>License Key</th>
							<th>Product Type</th>
							<th>Num of Users</th>
							<th>Expiration Date</th>
							<th>Auto-Renew</th>					
							<!-- <th>Public/NAT IP</th> -->
							<th>Actions</th>
						</tr>
					</thead>
					<c:if test="${fn:length(USER_KV_LIST_EXPIRED) eq 0}">
						<tr class='ap_table_tr_odd'>
							<td colspan="6">There are no expired licenses in your account.</td>
						</tr>
					</c:if>
					<c:if test="${fn:length(USER_KV_LIST_EXPIRED) gt 0}">
						<c:forEach var="lic" items="${USER_KV_LIST_EXPIRED}" varStatus="loop">
							<tr class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
								<td title="Click to see full License Key" onClick="javascript:changeVal(this,'${lic.fullLicenseKey}');"
										><u> <font color="blue">${lic.licenseKey}</font></u></td>
								<td>${lic.prodDesc}</td>
								<td style="text-align: right"><c:out value="${lic.numOfUsers == '1000000' ? 'Unlimited' : lic.numOfUsers}"/></td>
								<td>${lic.expirationDate}</td>
								<td>${lic.autoRenew == 'Y' ? 'On': 'Off'}</td>
								<%-- <td>${lic.publicIp}</td> --%>
								<td><input type="button" class="buttonStyle" value="Upgrade Users" onclick="window.location='extendLic.ap?licId=${lic.prodInstanceId}'" />
									&nbsp;
									<input type="button" class="buttonStyle" value="Extend Expiry" onclick="window.location='extendLicExpiry.ap?licId=${lic.prodInstanceId}'" />
								</td>
							</tr>
						</c:forEach>	
					</c:if>	
					</table>
				  </div>


				<br/>
				<hr size="1" >
			  	<div class="nof-positioning" style="width: 1020px; margin-top: 13px; margin-left: 28px;">	
				  <h2><a id="licHist" href="#" onclick="javascript:toggleLicHist();"><label id="viewChangesId"><b>+</b>  View Changes to Licenses (Audit History)</label></a></h2> 
		          <table class="ap_table" id="viewChangesTableId" width="100%" style="display:none;">
					<thead class="ap_table_hdr">
						<tr>
							<th>License Key</th>
							<th>Num of Users</th>
							<th>Expiration Date</th>
							<th>Auto-Renew</th>					
							<!-- <th>Public/NAT IP</th> -->
							<th>Ordered By / Updated By</th>
							<th>Updated At</th>
						</tr>
					</thead>
					<c:if test="${fn:length(USER_AUD_HIST) eq 0}">
						<tr class='ap_table_tr_odd'>
							<td colspan="6">There are no changes made to Licenses in your account.</td>
						</tr>
					</c:if>
					<c:if test="${fn:length(USER_AUD_HIST) gt 0}">
						<c:forEach var="lic" items="${USER_AUD_HIST}" varStatus="loop">
							<tr class="${loop.index % 2 == 0 ? 'ap_table_tr_even' : 'ap_table_tr_odd'}">
								<td title="Click to see full License Key" onClick="javascript:changeVal(this,'${lic.fullLicenseKey}');"
										><u> <font color="blue">${lic.licenseKey}</font></u></td>
								<td style="text-align: right"><c:out value="${lic.numOfUsers == '1000000' ? 'Unlimited' : lic.numOfUsers}"/></td>
								<td>${lic.expirationDate}</td>
								<td>${lic.autoRenew == 'Y' ? 'On': 'Off'}</td>
								<%-- <td>${lic.publicIp}</td> --%>
								<td>${lic.lastUpdatedBy}</td>
								<td>${lic.lastUpdatedTime}</td>
							</tr>
						</c:forEach>	
					</c:if>	
					</table>
				  </div>
				                      		
				</div>
			</div>			
		</div>
	</div>
	<%@include file="footer.html" %>
</body>
<script>
function editLic(rowId){
	//alert("test:"+rowId);
	//alert("inside editLic..");
	var isAllow = true;
	$('*[id*=KV_lic_edit_]:visible').each(function() {		
		//alert('display' + $(this).css('display'));
		if($(this).css('display') != 'none'){
			alert("Please Save/Calcel before editing next license.");
			isAllow = false;
		}
	});
	if(isAllow){
		$('#KV_lic_'+rowId).hide();
		$('#KV_lic_edit_'+rowId).show();		
	}else{
		return false;
	}
}

function cancelEditLic(rowId){
	$('#KV_lic_'+rowId).show();
	$('#KV_lic_edit_'+rowId).hide();
}

function toggleLicHist(){
	var hist = $('#viewChangesTableId');
	if ($(hist).css("display") == 'none')
	{
	     $(hist).show();
	     $('#viewChangesId').html('<b>-</b>  Hide Changes to Licenses (Audit History)');
	}else{
	     $(hist).hide();
	     $('#viewChangesId').html('<b>+</b>  Show Changes to Licenses (Audit History)');		
	}
 }

 function changeVal(obj, val){
	obj.innerHTML = val;
 }
 
</script>
</html>
