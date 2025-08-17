import logging
import requests
import re
from bs4 import BeautifulSoup

url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
res = requests.get(url)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, "html.parser")

def twd2usd(inputSTR):
    """Convert TWD to USD using the exchange rate."""
    search_result = re.search(r'((NT\$[0-9\.,]+) (cents|million|billion|trillion){0,1})', inputSTR)

    if search_result is None:
        logging.debug("**No TWD amount found in the input string.**\n")
        return inputSTR
    else:
        twdSTR = search_result.groups(0)[0]
    # print(twdSTR)

    if twdSTR:
        units = ['cents', 'million', 'billion', 'trillion']
        if any(unit in twdSTR for unit in units):
            match = [unit for unit in units if unit in twdSTR]
            if 'cents' in match:
                twdINT = float(twdSTR.strip().replace('NT$', '').replace(',', '').replace('cents', '')) / 100
            elif 'million' in match:
                twdINT = float(twdSTR.strip().replace('NT$', '').replace(',', '').replace('million', '')) * 1_000_000
            elif 'billion' in match:
                twdINT = float(twdSTR.strip().replace('NT$', '').replace(',', '').replace('billion', '')) * 1_000_000_000
            elif 'trillion' in match:
                twdINT = float(twdSTR.strip().replace('NT$', '').replace(',', '').replace('trillion', '')) * 1_000_000_000_000
            twdINT = int(twdINT)
        else:
            twdINT = int(twdSTR.strip().replace('NT$', '').replace(',', ''))

        usd_rate = _get_usd_rate()
        usd_value = int(twdINT / usd_rate)

        usdSTR = "{:,}".format(usd_value)
        inputSTR = inputSTR.replace(f'{twdSTR}', f'{twdSTR} (US${usdSTR}) ', 1)

    return inputSTR


def _get_usd_rate():
    try:
        # Find the <tr> that contains "美金 (USD)"
        usd_row = None
        for row in soup.select("table tbody tr"):
            if "美金" in row.text:
                usd_row = row
                break
        
        if usd_row:
                # Extract "本行現金賣出" (cash sell rate)
                cash_sell_td = usd_row.find("td", {"data-table": "本行現金賣出"})
                if cash_sell_td:
                    # print("USD Cash Sell Rate:", cash_sell_td.text.strip())
                    return float(cash_sell_td.text.strip())
                else:
                    print("Couldn't find the cash sell cell in USD row.")
        else:
            raise ValueError("Couldn't find the USD row in the table.")

    except Exception as e:
        print(f"An error occurred while fetching the USD rates: {e}")