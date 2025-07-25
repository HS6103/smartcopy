import json
import name2WG
import re
import tw2us

def byLine_enditem_insert(inputSTR):
    if re.search(r'\(By',inputSTR) == None:
        inputSTR += '\n\n(By Name1)'

    if re.search(r'Enditem/', inputSTR) == None:
        inputSTR += '\nEnditem/\n'

    return inputSTR
        
def reporter_name_insert(inputSTR):
    reporterLIST = input('Enter each reporter last name-first name with space between: ').split(' ')

    if len(reporterLIST) > 2:
        pass
    else:
        inputSTR = inputSTR.replace('Name1', f'{reporterLIST[0]} and {reporterLIST[1]}')

        for reporter in reporterLIST:
            if reporter.replace('-','') in reporterDICT.keys():
                inputSTR = inputSTR.replace(reporter, reporterDICT[reporter.replace('-','')])
            else:
                try:
                    surname = name2WG.ch2en(reporter.split('-')[0],encode='威妥瑪拼音').title()
                    given_name = name2WG.ch2en(reporter.split('-')[1],encode='威妥瑪拼音').capitalize().replace(' ', '-',1).replace(' ', '')
                    inputSTR = inputSTR.replace(reporter, surname + ' ' + given_name)

                except Exception as e:
                    print(f"Error converting reporter name: {reporter}. Error: {e}")
                    break
    
    return inputSTR

def twd2usd(inputSTR):
    """Convert TWD to USD using the exchange rate."""
    search_result = re.search(r'((NT\$[0-9\.,]+) (cents|million|billion|trillion){0,1})', inputSTR)
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
        usdSTR = "{:,}".format(tw2us.twd2usd(twdINT))
        inputSTR = inputSTR.replace(f'{twdSTR}', f'{twdSTR} (US${usdSTR}) ', 1)

        
    return inputSTR

if __name__ == '__main__':
    with open('test.txt', 'r',encoding='utf-8') as inputFile:
        inputSTR = inputFile.read()

    with open('reporter_names.json', 'r', encoding='utf-8') as reporterFile:
        reporterDICT = json.load(reporterFile)

    tmpSTR = byLine_enditem_insert(inputSTR)
    tmpSTR = reporter_name_insert(tmpSTR)
    tmpSTR = twd2usd(tmpSTR)
    print(tmpSTR)

    with open('test_out.txt', 'w', encoding='utf-8') as outputFile:
        outputFile.write(tmpSTR)

