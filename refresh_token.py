import requests
token = [
    'e01efw5EZw6IVR2wRFGwRwofCiMOLVlJrW8K6XWHCjHnDg1d9w4drwrB7w4LCv1x1TsK1UsK6wrBXw4rCucKUccSBVMK5wrfDul3EhsKswqhjwp7EpcSHwrLCtsKSxITDg8KnRjwWDhIWFA8XGw8ZEhoRFRMVDREVExcPExcRSDfDv2vCuEY9RksvVFxYGVtjZk9eTxlgUFo9R18UGxNHOSZLPUvDisO9w4jCtsOCxIHDhMKEw4jEicOAwptLRUtDw4ERMjzDg8OSF8K9xIUPw4LDixHDi8WBE8OLwrFow5NlaibDicK%2BEC9DRsOERkYfQT5CRERGS0JGL0XDg8KOw5tnaizCvcOGGzZDIj5ERkVERkRGR0JEMEZGOzxESzNGFRUWDhg1R8OHw4LCv8OiREY%3D',
    'e01efw5JacxxHZxAbZRHCjMKJw4RbUmhWwrFkYcKHeMOMWn3DjGbCt3bDgsOEw4DDjE3DjMKRw4bCmMK5wp7CssKywrvCo2bEjMK0xIdVxIJiw71VwqPEpcSMwq%2FCsXBNw4DCqj01FhEPDQ0PHBYYGBIVEA4OFRIQDg4XFA4QEEg8xIJkwrlGQktEMlRXWRJWY2lSZVIZY1FRREdkDRQORzYrRERLw4XEhMK%2FwrvDgsO%2Bwr3CuMOJxInDg8KWRExLQMK%2Fw50vPMOAw48Qw4TEhRTCv8OEEMOLxL4Ow4TCsGjDkGxhHyzDgV44PkbCv0s9IkFBP0s9Rkg%2FPTJFw4DCk8OUamojIcK9UzZAH0U9Rko9PT1GTD9LMUZIQDM9SzBLDhwWERkuSsOHwr3DgsOpPUY%3D',
    'V1R9sgFub6319sVtRuzhobISu07jzewS4~',
    'V1R9sgFub6319sVtRuzhobISq27zvexy0~',
    'V1R9sgFub6319sVtRuzhobISu07jzewS4~',
    'V1R9sgFub6319sVtRuzhobISu56DjTwSk~'
]

refresh_url = 'https://www.zhipin.com/wapi/zppassport/get/zpToken?v=1717381481516'
headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token[2]}'
        }
data = {
            'token': token[2]
        }
response = requests.post(refresh_url, headers=headers, json=data)
if response.status_code == 200:
    token = response.json().get("token")
    print(response.json())
    print(f"Token 刷新成功: {token}")
else:
    raise ValueError("刷新 token 失败")