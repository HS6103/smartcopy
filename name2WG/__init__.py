"""name2WG
外交部中文名字轉拼音
"""

__version__ = "1.0"

import requests
from pyquery import PyQuery


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



def ch2en(name, encode="威妥瑪拼音"):
    if len(name) == 0:
        return ''
    
    elif len(name) > 3:
        raise ValueError("Not supported yet.")
    
    enName = _get_ch2en(name)

    return enName