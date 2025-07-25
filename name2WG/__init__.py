"""name2WG
外交部中文名字轉拼音
"""

__version__ = "1.0"

import requests
from pyquery import PyQuery
import unicodedata


def _get_ch2en(name):
    payload = {
        "SN": name,
        "sound": 2,
    }
    url = "https://crptransfer.moe.gov.tw/index.jsp"
    res = requests.get(url, params=payload)
    S = PyQuery(res.text)
    
    # Find the row where the heading is 威妥瑪拼音
    for row in S("tr").items():
        if row("th").text().strip() == "威妥瑪拼音":
            result = " ".join(span.text() for span in row("td span").items())
            # print(result)  # Output: wang hsiao ming
    return result

def _clean_wade_giles(name):
    # Lowercase for consistency
    name = name.lower()
    
    # Normalize accented characters (e.g., ü → u)
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8")
    
    return name

def ch2en(name, encode="威妥瑪拼音"):
    if len(name) == 0:
        return ''
    
    elif len(name) > 3:
        raise ValueError("Not supported yet.")
    
    enName = _get_ch2en(name)
    enName = _clean_wade_giles(enName)

    return enName