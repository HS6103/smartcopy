import json
import name2WG
import re
from tw2us import twd2usd

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

            

if __name__ == '__main__':
    with open('test.txt', 'r',encoding='utf-8') as inputFile:
        inputSTR = inputFile.read()

    with open('reporter_names.json', 'r', encoding='utf-8') as reporterFile:
        reporterDICT = json.load(reporterFile)

    tmpSTR = byLine_enditem_insert(inputSTR)
    # tmpSTR = reporter_name_insert(tmpSTR)
    tmpSTR = twd2usd(tmpSTR)
    print(tmpSTR)

    with open('test_out.txt', 'w', encoding='utf-8') as outputFile:
        outputFile.write(tmpSTR)

