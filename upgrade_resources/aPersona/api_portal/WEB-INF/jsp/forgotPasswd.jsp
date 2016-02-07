<%@ page language="java" contentType="text/html; charset=UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn"%>
<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>aPersona ASM - Forgot password</title>
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/fusion.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/style.css">
<link rel="stylesheet" type="text/css"
	href="${pageContext.request.contextPath}/css/ap_style.css">
<link rel="stylesheet" 
	href="${pageContext.request.contextPath}/css/jquery-ui.css" />		
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
<body class="nof-centerBody">
<div style="height:100%; min-height:100%; position:relative;">
	<jsp:include page="header.jsp" />
	<br/>
	<br/>

	<div class="boxLayout" style="width:450px; height:300px;">
      	<h2>aPersona ASM - Reset Password</h2>
              <div class="nof-positioning" style="width:450px;">
          
              <div class="nof-positioning" 
              	style="line-height: 0px; width: 34px; margin-top: 15px; margin-left: 194px; ">
              		<img height="29" width="34" src="${pageContext.request.contextPath}/images/IDHead_1.png" alt="IDHead" title="IDHead" 
              			style="border: 0;">
              </div>
              <div class="nof-clearfix nof-positioning">
                <div class="nof-positioning" style="float: left; display: inline; width: 308px; margin-top: 17px; margin-left: 18px; ">
                  <table border="0" cellspacing="2" cellpadding="2" width="100%" style="background-color: rgb(255,255,255); height: 84px;">
					  
					  <c:if test="${userEmailToRest == null}">
					  <form name="sendOtpForPwdReset" action="sendOtpForPwdReset.ap" method="post">					  
	                     <tr style="height: 22px;">
	                      <td width="110" id="Cell1">
	                        <p style="text-align: right; margin-bottom: 0px;">aP-ASM Admin ID:</p>
	                      </td>
	                      <td width="184" id="Cell16">
	                        <p style="margin-bottom: 0px;"><input required 
	                        	type="email" name="userEmailToRest" value="${userEmail}" size="23" 
	                        				style="white-space: pre; width: 180px;"></p>
	                      </td>
	                    </tr>
	                    <tr style="height: 26px;">
	                      <td id="Cell3">
	                        <p style="margin-bottom: 0px;">&nbsp;</p>
	                      </td>
	                      <td id="Cell18">
	                        <table width=" 100%" border="0" cellspacing="0" cellpadding="0">
	                          <tr>
	                            <td align="center">
	                            	<input type="image" height="26" width="106" src="${pageContext.request.contextPath}/images/ContinueBlue.jpg" 
	                            			alt="ContinueBlue" title="ContinueBlue">
	                            </td>
	                          </tr>
	                        </table>
	                      </td>
	                    </tr>
	                    </form>
	 				  </c:if>

					<c:if test="${userEmailToRest != null}">
					<form name="kvPasswordReset" action="resetPassword.ap" method="post" autocomplete="off">	
                     <tr style="height: 22px;">
                      <td width="110" id="Cell1">
                        <p style="text-align: right; margin-bottom: 0px;">aP-ASM Admin ID:</p>
                      </td>
                      <td width="184" id="Cell16">
                        <p style="margin-bottom: 0px;"><input readonly required type="email" name="userEmailToRest" value="${userEmailToRest}" size="23" 
                        				style="white-space: pre; width: 180px;"></p>
                      </td>
                    </tr>
                    <tr style="height: 22px;">
                      <td id="Cell2">
                        <p style="text-align: right; margin-bottom: 0px;">OTP (sent to email):</p>
                      </td>
                      <td id="Cell17">
                        <p style="margin-bottom: 0px;"><input required type="password" name="otpEntered" autocomplete="off" size="23" style="white-space: pre; width: 180px;"></p>
                      </td>
                    </tr>
                    
                    <tr style="height: 22px;">
                      <td colspan="2"><hr/>
                      </td>
                    </tr>                
                    <tr style="height: 22px;">
                      <td id="Cell2">
                        <p style="text-align: right; margin-bottom: 0px;">Password:</p>
                      </td>
                      <td id="Cell17">
                        <p style="margin-bottom: 0px;"><input required type="password" name="passwd"  autocomplete="off" size="23" style="white-space: pre; width: 180px;"></p>
                      </td>
                    </tr>
                    <tr style="height: 22px;">
                      <td id="Cell2">
                        <p style="text-align: right; margin-bottom: 0px;">Confirm Password:</p>
                      </td>
                      <td id="Cell17">
                        <p style="margin-bottom: 0px;"><input required type="password" name="confirmPasswd"  autocomplete="off" size="23" style="white-space: pre; width: 180px;"></p>
                      </td>
                    </tr>

                    <tr style="height: 26px;">
                      <td id="Cell3">
                        <p style="margin-bottom: 0px;">&nbsp;</p>
                      </td>
                      <td id="Cell18">
                        <table width=" 100%" border="0" cellspacing="0" cellpadding="0">
                          <tr>
                            <td align="center">
                            	<input type="image" height="26" width="106" src="${pageContext.request.contextPath}/images/ContinueBlue.jpg" 
                            			alt="ContinueBlue" title="ContinueBlue" style="border: 0;">
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                    </form>
                    </c:if>
                    <c:if test="${ERR_MESSAGE != null}">
	                   <tr>
	                   		<td></td>
		                   	<td>
	            				<div style="text-align:left; color:red;">${ERR_MESSAGE}</div>
		                   	</td>
	                    </tr>
					</c:if>
                    <c:if test="${ADMIN_ACCT_MESSAGE != null}">
	                   <tr>
	                   		<td></td>
		                   	<td>
	            				<div style="text-align:left; color:green;">${ADMIN_ACCT_MESSAGE}</div>
		                   	</td>
	                    </tr>
					</c:if>
                  </table>
                </div>
                <div style="float: left" class="nof-positioning">
                  <div id="Text109" class="nof-positioning TextObject" style="width: 50px; margin-top: 18px; margin-left: 3px;">
                    <p style="margin-bottom: 0px;"><span style="font-size: 10px;">example:</span></p>
                  </div>
                  <div id="Text110" class="nof-positioning TextObject" style="width: 101px; margin-top: 1px; margin-left: 3px; ">
                    <p style="margin-bottom: 0px;"><span style="font-size: 10px;">yourID@domain.com</span></p>
                  </div>
                </div>
              </div>
<!--               <div id="Text130" class="nof-positioning TextObject" style="width: 200px; margin-top: 2px; margin-left: 127px; ">
                <p style="text-align: center; margin-bottom: 0px;"><a href="forgotPassword.ap">
                		<span style="font-size: 10px; color: rgb(0,102,255);">Forgot your aP-ASM Password?</span></a></p>
              </div>
 -->          
         </div>		
	</div>
	
	<jsp:include page="footer.html" />
</div>
</body>
</html>
