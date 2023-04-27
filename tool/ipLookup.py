import ipinfo
import configSetting

def ipLookupByIPInfo(ip)->str:
    handler = ipinfo.getHandler(configSetting.ipinfo_access_token)
    details = handler.getDetails(ip_address=ip)
    return details.country_name