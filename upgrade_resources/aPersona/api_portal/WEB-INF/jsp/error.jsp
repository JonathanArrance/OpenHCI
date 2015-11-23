<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - Error</title>
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

</head>
<body>
<div style="height:100%; min-height:100%; position:relative;">
	<c:set var="selMenu" scope="request" value="error"/>
	<jsp:include page="header.jsp" />		
		
	<div class="nof-centerContent">
         <p style="margin-bottom: 0px;"><b><span style="font-size: 16px; font-weight: bold;">
         		Error in processing request</span></b></p>
		  <br/>
         <p>We encountered an error in processing request, please contact support for immediate assistance
         <br/>
         You can continue using the application using the menu options. 
         </p>
		<%@include file="footer.html" %>
    </div>
</body>
</html>
	
