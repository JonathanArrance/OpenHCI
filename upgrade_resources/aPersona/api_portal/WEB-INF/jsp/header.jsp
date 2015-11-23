<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">
		<link rel="icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	<link rel="shortcut icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
<script src="${pageContext.request.contextPath}/js/jquery-1.9.1.js"></script>
<script src="${pageContext.request.contextPath}/js/jquery-ui.js"></script>
	
<style type="text/css">
body {
	margin: 0px;
	text-align: center;
	font-family: Arial;
	font-size: 12px;
	color: rgb(51, 51, 51);
}
</style>

</head>
<body>
	<div>
		<div class="nof-clearfix nof-positioning headerDiv">
		<table width="100%">
		<tr>
		<td><div class="logoDiv">
				<a href="${pageContext.request.contextPath}/logout.ap"><img id="Picture109" height="37"
						width="196" src="${pageContext.request.contextPath}/images/apLogo.jpg"
						alt="aPersona" title="aPersona"	style="border: 0;">
				</a>
			</div>
		</td>
		<td><div class="nof-positioning logoCenter">
				<p><b><span style="color:#455e86; font-size: 16px; font-weight: bold;"><c:out value="${PROVIDER_NAME}"/></span></b></p>
				<c:if test="${USER_EMAIL != null && fn:indexOf(header['User-Agent'],'Chrome') < 0}"><p style="text-align:center;color:blue;"><u>(Please use Chrome browser for better experience.)</u></p></c:if>
			</div>
		</td>
		<td><div class="nof-positioning TextObject logoRight">				
				<p>&nbsp;<c:if test='${USER_EMAIL != null}'>
						Logged in as:&nbsp; <span style="font-weight:bold;"><c:out value="${USER_EMAIL}"/></span>
					</c:if>
				</p>
				<p>
					<a style="color:blue;" href="http://support.apersona.com" target="_blank">Help</a>
						&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
					<c:if test='${USER_EMAIL != null}'>
						<a style="color:blue;" href="${pageContext.request.contextPath}/logout.ap">Logout</a>
					</c:if>					
				</p>
			</div>
		</td>
		
		</tr>
		</table>
		
		</div>

		<div class="menuBar">
			<c:if test='${selMenu != null}'>
			<table class="menu">
				<tr>					
				    <c:if test="${IS_SUPER_ADMIN == 'Y'}">
				    	<td class="${selMenu == 'clientMgmt' ? 'selMenu' : ''}"><a href="superAdminMgmt.ap" title="Client Management">Client Management</a></td>
				    </c:if>				    
                    <c:if test="${PROVIDER_ID != null}">
						<td class="${selMenu == 'kvMgmt' ? 'selMenu' : ''}"><a href="keyvaultMgmt.ap" title="aP-ASM Settings">aP-ASM Settings</a></td>
						<td class="${selMenu == 'apiSrvMgmt' ? 'selMenu' : ''}"><a href="apiServerMgmt.ap" title="Security Policy Mgr">Security Policy Mgr</a></td>
						<td class="${selMenu == 'userMgmt' ? 'selMenu' : ''}"><a href="userMgmt.ap" title="User Mgmt">User Management</a></td>
						<td class="${selMenu == 'loginHist' ? 'selMenu' : ''}"><a href="loginHist.ap" title="Transaction History">Transaction History</a></td>                    
                    </c:if>
<%-- 				    <c:if test="${IS_SUPER_ADMIN == 'Y'}">
				    	<td class="${selMenu == 'analytics' ? 'selMenu' : ''}"><a href="analytics.ap" title="Analytics">Analytics</a></td>
				    </c:if>	 --%>			    
				</tr>
			</table>			
			</c:if>
			
			<%-- <c:if test="${fn:indexOf(header['User-Agent'],'Chrome') < 0}">Please use Chrome browser for better experience.</c:if> --%>
			
		</div>
	</div>
	<br/>
</body>
</html>
