<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona - About</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
		<link rel="icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	<link rel="shortcut icon" 
      type="image/png" 
      href="${pageContext.request.contextPath}/images/favicon.png">
	
</head>
<body class="nof-centerBody">
<div style="height:100%; min-height:100%; position:relative;">
	<c:set var="selMenu" scope="request" value="about"/>
	<jsp:include page="header.jsp" />
	<br/>
	<br/>
	
	  <div style="text-align:left; margin-left:150px;">
        <div>
          <p style="margin-bottom:0px;"><b><span style="font-size: 16px; font-weight: bold;">aPersona Adaptive Security Manager</span></b></p>
		  <br/>		  
          <p>Version:<c:out value="${AP_VERSION}"></c:out></p>
          <p>Copyright 2015 aPersona Inc. All rights reserved.
          	 <br/><br/>
          	 
			 Please refer to <a href=" http://www.apersona.com/#!terms/c6yc" target="_blank">Licensing Terms and Conditions</a>
			<br/><br/>
			This product includes GeoLite data created by MaxMind, available from <a href="http://www.maxmind.com" target="_blank">
			http://www.maxmind.com</a>
			</p>
		</div>
      </div>
		<br/><br/><br/><br/>
		<br/><br/><br/><br/>
		<br/><br/><br/><br/>	
	<jsp:include page="footer.html" />
</div>
</body>
</html>
