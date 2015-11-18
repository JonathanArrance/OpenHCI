<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>

<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<title>aPersona - Analytics</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/jquery-ui.css" />
<link href="${pageContext.request.contextPath}/css/theme.default.css" rel="stylesheet" type="text/css">

<script type="text/javascript" src="${pageContext.request.contextPath}/js/jquery-1.9.1.js"></script>
<script type="text/javascript" src="${pageContext.request.contextPath}/js/jquery-ui.js"></script>
<script type="text/javascript" src="${pageContext.request.contextPath}/js/jquery.tablesorter.min.js"></script>
    
    <script>
        $(function(){
          $( "#fromDtId" ).datepicker();
          $( "#toDtId" ).datepicker();
        });
    </script>

<style>
	table.fixed { table-layout:fixed;}
</style>
</head>
<body class="nof-centerBody">
	<div style="height: 100%; min-height: 100%; position: relative;">
		<c:set var="selMenu" scope="request" value="analytics" />
		<jsp:include page="header.jsp" />

		<div class="nof-centerContent">
			<div class="nof-clearfix nof-positioning ">
				<div class="nof-positioning TextObject"
					style="float: left; display: inline; width: 19px;">
					<p style="text-align: right; margin-bottom: 0px;">&nbsp;</p>
				</div>
				<div id="Text129" class="nof-positioning TextObject"
					style="float: left; display: inline; width: 1000px; margin-top: 9px; margin-left: 19px;">
					<p style="margin-bottom: 0px;">
						<b><span style="font-size: 16px; font-weight: bold;">
								aPersona Analytics
					</p>
				</div>
			</div>

			<div class="nof-positioning" style="width: 1058px; margin-left: 8px;">
				<br />
				<div class="boxLayout" style="width: 100%;">
					<h2>Analytics</h2>
					<br />
					<table style="border:1px single black">
						<tr>
							<td width ="20%" style="background:#F0F0F0;">
								<table width="100%">
									<tr>
										<td colspan="2">
											<b>Report Type</b>											
											<select>
												<option value="ABC Company">ABC Company</option>
												<option value="ABC Company">ABC Company</option>
												<option value="ABC Company">ABC Company</option>
											</select>
											<br/>											
										</td>
									</tr>
									<tr>
										<td>
											<b>From Date:</b>
											<br/>
											Date1
										</td>
										<td>
											<b>To Date:</b>
											<br/>
											Date2										
										</td>
									</tr>
								</table>
							
							</td>
							<td width="80%" >col2</td>
							
						</tr>
					</table>
				</div>
	</div>
	</div></div>
<%@include file="footer.html" %>	

<script>
	function reqRespSubmit(){
		document.reqRespHist.failedLoginsUserSearchKey.value = document.failedUserLogins.failedLoginsUserSearchKey.value;
		document.reqRespHist.failedLoginsFromDt.value = document.failedUserLogins.failedLoginsFromDt.value;
		document.reqRespHist.failedLoginsToDt.value = document.failedUserLogins.failedLoginsToDt.value;
		return true;
	}
	
	function failedLoginsSubmit(){
		document.failedUserLogins.reqRespUserSearchKey.value = document.reqRespHist.reqRespUserSearchKey.value;
		document.failedUserLogins.reqRespFromDt.value = document.reqRespHist.reqRespFromDt.value;
		document.failedUserLogins.reqRespToDt.value = document.reqRespHist.reqRespToDt.value;
		return true;
	}
	
</script>	
</body>
</html>

