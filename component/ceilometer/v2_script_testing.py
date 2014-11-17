#!/usr/bin/python

import subprocess
import time

adm_token = " MIIRJgYJKoZIhvcNAQcCoIIRFzCCERMCAQExCTAHBgUrDgMCGjCCD3wGCSqGSIb3DQEHAaCCD20Egg9peyJhY2Nlc3MiOiB7InRva2VuIjogeyJpc3N1ZWRfYXQiOiAiMjAxNC0xMS0xNVQxNToxOToxNS4zODI2MTQiLCAiZXhwaXJlcyI6ICIyMDE0LTExLTE1VDE2OjE5OjE1WiIsICJpZCI6ICJwbGFjZWhvbGRlciIsICJ0ZW5hbnQiOiB7ImRlc2NyaXB0aW9uIjogImFkbWluIHRlbmFudCIsICJlbmFibGVkIjogdHJ1ZSwgImlkIjogIjNkZjE1YzQ0M2VhZDRkYWM4YTZkYTJiMTEzNGU3NGJmIiwgIm5hbWUiOiAiYWRtaW4ifX0sICJzZXJ2aWNlQ2F0YWxvZyI6IFt7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzQvdjIvM2RmMTVjNDQzZWFkNGRhYzhhNmRhMmIxMTM0ZTc0YmYiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo4Nzc0L3YyLzNkZjE1YzQ0M2VhZDRkYWM4YTZkYTJiMTEzNGU3NGJmIiwgImlkIjogIjBhNWVkMmM1YWE3ZDQwZDhiZGVlZDA5ODM1YmZmZTFjIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo4Nzc0L3YyLzNkZjE1YzQ0M2VhZDRkYWM4YTZkYTJiMTEzNGU3NGJmIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImNvbXB1dGUiLCAibmFtZSI6ICJub3ZhIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6OTY5Ni8iLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo5Njk2LyIsICJpZCI6ICI4NzVkNTFiNzg0MjQ0YWZhYTBkN2QwNTg3YzUyMGQyMiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6OTY5Ni8ifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAibmV0d29yayIsICJuYW1lIjogIm5ldXRyb24ifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo4Nzc2L3YyLzNkZjE1YzQ0M2VhZDRkYWM4YTZkYTJiMTEzNGU3NGJmIiwgInJlZ2lvbiI6ICJSZWdpb25PbmUiLCAiaW50ZXJuYWxVUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3Ni92Mi8zZGYxNWM0NDNlYWQ0ZGFjOGE2ZGEyYjExMzRlNzRiZiIsICJpZCI6ICIwYWE2NTlkMmRkMjQ0YmM5ODY0NjIzNWNmYmI0MTRmMCIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3Ni92Mi8zZGYxNWM0NDNlYWQ0ZGFjOGE2ZGEyYjExMzRlNzRiZiJ9XSwgImVuZHBvaW50c19saW5rcyI6IFtdLCAidHlwZSI6ICJ2b2x1bWV2MiIsICJuYW1lIjogImNpbmRlcnYyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3NC92MyIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzQvdjMiLCAiaWQiOiAiMGQ0MWNjMGFjNTQ4NDJiZTk0Mzg4YmIzMDNiY2I3MzYiLCAicHVibGljVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzQvdjMifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiY29tcHV0ZXYzIiwgIm5hbWUiOiAibm92YXYzIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODA4MCIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3OjgwODAiLCAiaWQiOiAiMzFmY2RhY2M4NDI4NDFjMTk5ZmMzYjNiZWQyZTk1MzYiLCAicHVibGljVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3OjgwODAifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiczMiLCAibmFtZSI6ICJzd2lmdF9zMyJ9LCB7ImVuZHBvaW50cyI6IFt7ImFkbWluVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3OjkyOTIiLCAicmVnaW9uIjogIlJlZ2lvbk9uZSIsICJpbnRlcm5hbFVSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo5MjkyIiwgImlkIjogIjRkYWY0NzVkZGE0ZjQ4Yjk4YmVkNzAwM2E4MDYzMzBiIiwgInB1YmxpY1VSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo5MjkyIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImltYWdlIiwgIm5hbWUiOiAiZ2xhbmNlIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3NyIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzciLCAiaWQiOiAiNjlmNWE1YTU2ZDA1NDdjM2E4NDhlMmNiZDM0MWZlZmMiLCAicHVibGljVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzcifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAibWV0ZXJpbmciLCAibmFtZSI6ICJjZWlsb21ldGVyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3Ni92MS8zZGYxNWM0NDNlYWQ0ZGFjOGE2ZGEyYjExMzRlNzRiZiIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzYvdjEvM2RmMTVjNDQzZWFkNGRhYzhhNmRhMmIxMTM0ZTc0YmYiLCAiaWQiOiAiMjVjYjEyZTM3ZDBiNGU3MmJiYjdhMzU5OTFlODUwYmUiLCAicHVibGljVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzYvdjEvM2RmMTVjNDQzZWFkNGRhYzhhNmRhMmIxMTM0ZTc0YmYifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAidm9sdW1lIiwgIm5hbWUiOiAiY2luZGVyIn0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODc3My9zZXJ2aWNlcy9BZG1pbiIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzMvc2VydmljZXMvQ2xvdWQiLCAiaWQiOiAiNjI3ZDJjYWUwZjM2NDBiZTliZWQxODIwMjMxYjgyN2QiLCAicHVibGljVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3Ojg3NzMvc2VydmljZXMvQ2xvdWQifV0sICJlbmRwb2ludHNfbGlua3MiOiBbXSwgInR5cGUiOiAiZWMyIiwgIm5hbWUiOiAibm92YV9lYzIifSwgeyJlbmRwb2ludHMiOiBbeyJhZG1pblVSTCI6ICJodHRwOi8vMTkyLjE2OC4xMC4zNzo4MDgwLyIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3OjgwODAvdjEvQVVUSF8zZGYxNWM0NDNlYWQ0ZGFjOGE2ZGEyYjExMzRlNzRiZiIsICJpZCI6ICI2ZTgyZGU3ZmNiNzQ0Mzc4OWZhNmI3NzFjMDdjMGYyOSIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6ODA4MC92MS9BVVRIXzNkZjE1YzQ0M2VhZDRkYWM4YTZkYTJiMTEzNGU3NGJmIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogIm9iamVjdC1zdG9yZSIsICJuYW1lIjogInN3aWZ0In0sIHsiZW5kcG9pbnRzIjogW3siYWRtaW5VUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6MzUzNTcvdjIuMCIsICJyZWdpb24iOiAiUmVnaW9uT25lIiwgImludGVybmFsVVJMIjogImh0dHA6Ly8xOTIuMTY4LjEwLjM3OjUwMDAvdjIuMCIsICJpZCI6ICI4YmE0ZjI4NWYzZmE0MGY3OTdmMGNkMDBkMjU4NmY3MiIsICJwdWJsaWNVUkwiOiAiaHR0cDovLzE5Mi4xNjguMTAuMzc6NTAwMC92Mi4wIn1dLCAiZW5kcG9pbnRzX2xpbmtzIjogW10sICJ0eXBlIjogImlkZW50aXR5IiwgIm5hbWUiOiAia2V5c3RvbmUifV0sICJ1c2VyIjogeyJ1c2VybmFtZSI6ICJhZG1pbiIsICJyb2xlc19saW5rcyI6IFtdLCAiaWQiOiAiNDQxZjBhZWFjM2ExNDk4NWE2MmEyNDk1ODdmYzg1MzYiLCAicm9sZXMiOiBbeyJuYW1lIjogImFkbWluIn1dLCAibmFtZSI6ICJhZG1pbiJ9LCAibWV0YWRhdGEiOiB7ImlzX2FkbWluIjogMCwgInJvbGVzIjogWyI2OWE1MDQ5ZjJkZTQ0OWZlOGJhMDViY2U1M2NiYWUwNyJdfX19MYIBgTCCAX0CAQEwXDBXMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVW5zZXQxDjAMBgNVBAcMBVVuc2V0MQ4wDAYDVQQKDAVVbnNldDEYMBYGA1UEAwwPd3d3LmV4YW1wbGUuY29tAgEBMAcGBSsOAwIaMA0GCSqGSIb3DQEBAQUABIIBADsuGazT2sFgrSWKD-S0r+D0Cs2oFCKYj6yYgyPwMJy2b2IuKfTyteoUyDWjMe3LH9876Lb9rZcTniDHCOCDZ4Fsyp47nW1XoEIa1zLIh6FHTUwQXX7jSwoBoptyxJ9eVGSh67vwoAmx8zh4EKAkI-wdZ4ttB+EMN1qg+Qfi5i41ZhJMkrhZ98mSM2eL1pENzlQUJxLifbvOPvJRCIDrPVAJ0yjW2FeqF9l9TfS2himyYqix2RQbaHq2ZqSzjiflqcsOE3YSahvhb54ezIlpCCrdQW7qDfNoFeUkSfFNxvkt9ty2EYvRT70Z6i0bpoD1h3JNGXPObCRL0fNDr7xbB38="

print "List Alarms:"

body = ''
header = {"X-Auth-Token":adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
function = 'GET'
api_path = 'http://192.168.10.37:8777/v2/alarms'

command = "curl -i -X %s -H 'X-Auth-Token: %s' -H 'Content-Type: %s' -H 'Accept: %s' -H 'User-Agent: %s' %s" %(function, header['X-Auth-Token'], header['Content-Type'], header['Accept'], header['User-Agent'], api_path)

out = subprocess.Popen(command, shell=True)
time.sleep(1)
print
print
print

print "List Meters:"

body = ''
header = {"X-Auth-Token":adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
function = 'GET'
api_path = 'http://192.168.10.37:8777/v2/meters'

command = "curl -i -X %s -H 'X-Auth-Token: %s' -H 'Content-Type: %s' -H 'Accept: %s' -H 'User-Agent: %s' %s" %(function, header['X-Auth-Token'], header['Content-Type'], header['Accept'], header['User-Agent'], api_path)

out = subprocess.Popen(command, shell=True)
time.sleep(1)
print
print
print

print "List Resources:"

body = ''
header = {"X-Auth-Token":adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
function = 'GET'
api_path = 'http://192.168.10.37:8777/v2/resources'

command = "curl -i -X %s -H 'X-Auth-Token: %s' -H 'Content-Type: %s' -H 'Accept: %s' -H 'User-Agent: %s' %s" %(function, header['X-Auth-Token'], header['Content-Type'], header['Accept'], header['User-Agent'], api_path)

out = subprocess.Popen(command, shell=True)
time.sleep(1)
print
print
print

meter_id = "3192d3810a81436fbb9a066dd3b1e703"

print "List Samples for Meter[3192d3810a81436fbb9a066dd3b1e703]:"

body = ''
header = {"X-Auth-Token":adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
function = 'GET'
api_path = 'http://192.168.10.37:8777/v2/meters/%s' %(meter_id)

command = "curl -i -X %s -H 'X-Auth-Token: %s' -H 'Content-Type: %s' -H 'Accept: %s' -H 'User-Agent: %s' %s" %(function, header['X-Auth-Token'], header['Content-Type'], header['Accept'], header['User-Agent'], api_path)

out = subprocess.Popen(command, shell=True)
time.sleep(1)
print
print
print

print "List Statistics for Meter[3192d3810a81436fbb9a066dd3b1e703]:"

body = ''
header = {"X-Auth-Token":adm_token, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "python-ceilometerclient"}
function = 'GET'
api_path = 'http://192.168.10.37:8777/v2/meters/%s/statistics' %(meter_id)

command = "curl -i -X %s -H 'X-Auth-Token: %s' -H 'Content-Type: %s' -H 'Accept: %s' -H 'User-Agent: %s' %s" %(function, header['X-Auth-Token'], header['Content-Type'], header['Accept'], header['User-Agent'], api_path)

out = subprocess.Popen(command, shell=True)
time.sleep(1)
print
print
print