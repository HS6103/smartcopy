import json
from gpt_writer import process_news_story
import name2WG
import re
import os
from dotenv import load_dotenv
from tw2us import twd2usd

# Load environment variables from .env file
load_dotenv()
my_name = os.getenv('my_name')

def byLine_enditem_insert(inputSTR):
    if re.search(r'\(By',inputSTR) == None:
        inputSTR += '\n\n(By Name1)'

    if re.search(r'Enditem/', inputSTR) == None:
        inputSTR += '\nEnditem/\n'

    return inputSTR

def reporter_name_insert(inputSTR, reporterLIST=None):
    authorSTR = my_name

    if len(reporterLIST) > 1:
        tmpSTR = ''
        for reporter in reporterLIST:
            if reporter != reporterLIST[-1]:
                tmpSTR += f'{reporter}, '
            else:
                tmpSTR += f'{reporter} and {authorSTR}'

        inputSTR = inputSTR.replace('Name1', tmpSTR)

    else:
        inputSTR = inputSTR.replace('Name1', f'{reporterLIST[0]} and {authorSTR}')

    for reporter in reporterLIST:
        if reporter in reporterDICT.keys():
            inputSTR = inputSTR.replace(reporter, reporterDICT[reporter])
        else:
            pass

    return inputSTR

            

if __name__ == '__main__':
    # with open('test.txt', 'r',encoding='utf-8') as inputFile:
    #     inputSTR = inputFile.read()

    with open('reporter_names.json', 'r', encoding='utf-8') as reporterFile:
        reporterDICT = json.load(reporterFile)
        print("Reporter names loaded.\n")

    with open('test_CN.txt', 'r', encoding='utf-8') as file:
        chinese_article = file.read()
        print("Chinese Article Loaded.\n-----")
        
    english_lead = input("Enter the English lead for the news story: ")
    # word_limit = int(input("Enter the word limit for the news story (default 300): ") or 300)
    auth = input("\nConfirm start writing? (y/n): ")
    if auth.lower() != 'y':
        print("Exiting without generating story.")
        exit(0)
    else:
        print("Generating news story...\n-----\n")
        draft_story = english_lead + "\n\n" + process_news_story(chinese_article, english_lead)
        if not draft_story:
            print("No story generated. Please check the input.")
            exit(1)
        else:
            print("Draft Story Generated\n-----\n")
            print("Inserting byline and enditem...")
            tmpSTR = byLine_enditem_insert(draft_story)
            reporterLIST = input("請輸入每位記者的中文姓名，並以空格分隔！").split(' ')
            print("Inserting reporter names...")
            tmpSTR = reporter_name_insert(tmpSTR, reporterLIST)
            print("Checking for TWD to USD conversion...\n-----\n")
            tmpSTR = twd2usd(tmpSTR)
            print(tmpSTR)


    # with open('test_out.txt', 'w', encoding='utf-8') as outputFile:
    #     outputFile.write(tmpSTR)

