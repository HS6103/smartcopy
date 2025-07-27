#!/user/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import discord
import json
from gpt_writer import process_news_story
import name2WG
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint
from tw2us import twd2usd

from smartcopy_TW.main import askLoki, ARTICUT

# Load environment variables from .env file
load_dotenv()
discord_token = os.getenv("discord_token")
my_name = os.getenv('my_name')

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# def getLokiResult(inputSTR, filterLIST=[]):
#     splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"] #
#     # 設定參考資料
#     refDICT = { # value 必須為 list
#         #"key": []
#     }
#     resultDICT = askLoki(inputSTR, filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT)
#     logging.debug("Loki Result => {}".format(resultDICT))
#     return resultDICT


def byLine_enditem_insert(inputSTR):
    if re.search(r'\(By',inputSTR) == None:
        inputSTR += '\n\n(By Name1)'

    if re.search(r'Enditem/', inputSTR) == None:
        inputSTR += '\nEnditem/\n'

    return inputSTR

def reporter_name_insert(inputSTR, reporterLIST=None):
    # open reporter_names.json
    with open('reporter_names.json', 'r', encoding='utf-8') as reporterFile:
        reporterDICT = json.load(reporterFile)

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

class BotClient(discord.Client):

    def resetMSCwith(self, messageAuthorID):
        '''
        清空與 messageAuthorID 之間的對話記錄
        '''
        templateDICT = {    "id": messageAuthorID,
                             "updatetime" : datetime.now(),
                             "latestQuest": "",
                             "false_count" : 0,
                             "reporterList" : [],
                             "tmpSTR" : "",
                             "resultSTR" : ""
        }
        return templateDICT

    async def on_ready(self):
        # ################### Multi-Session Conversation :設定多輪對話資訊 ###################
        self.templateDICT = {"updatetime" : None,
                             "latestQuest": ""
        }
        self.mscDICT = { #userid:templateDICT
        }
        # ####################################################################################
        print('Logged on as {} with id {}'.format(self.user, self.user.id))

    async def safe_reply(self, message, content):
        """Safely send a reply without exceeding Discord's 2000 character limit, splitting at paragraph breaks (\n\n)."""
        MAX_LENGTH = 2000

        paragraphs = content.split("\n\n")
        parts = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 <= MAX_LENGTH:  # +2 accounts for the \n\n added back
                current += para + "\n\n"
            else:
                if current:
                    parts.append(current.strip())
                if len(para) + 2 > MAX_LENGTH:
                    # Break oversized paragraph into safe chunks
                    for i in range(0, len(para), MAX_LENGTH):
                        parts.append(para[i:i+MAX_LENGTH].strip())
                    current = ""
                else:
                    current = para + "\n\n"

        if current:
            parts.append(current.strip())

        # Send all parts
        await message.reply(parts[0])
        for part in parts[1:]:
            await message.channel.send(part)


    async def on_message(self, message):
        if message.author == self.user:
            return

        if self.user.mentioned_in(message):
            msgSTR = message.content.replace(f"<@{self.user.id}>", "").strip()

            # Quick replies
            if msgSTR.lower() == "ping":
                await self.safe_reply(message, "pong")
                return
            elif msgSTR.lower() == "ping ping":
                await self.safe_reply(message, "pong pong")
                return
            elif msgSTR.lower() in ["哈囉", "嗨", "你好", "您好", "hi", "hello"]:
                # Session check
                if message.author.id in self.mscDICT:
                    timeDIFF = datetime.now() - self.mscDICT[message.author.id]["updatetime"]
                    if timeDIFF.total_seconds() >= 300:
                        self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)
                        await self.safe_reply(message, "嗨嗨，我們好像見過面，但卓騰的隱私政策不允許我記得你的資料，抱歉！")
                    else:
                        await self.safe_reply(message, self.mscDICT[message.author.id]["latestQuest"])
                else:
                    self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)
                    await self.safe_reply(message, msgSTR.title())
                return

            # Run long OpenAI/Loki task in background
            asyncio.create_task(self.handle_semantic_reply(message, msgSTR))

    async def handle_semantic_reply(self, message, msgSTR):
        # Step 1: Send a quick processing message
        await message.reply("正在處理中，請稍候...")

        replySTR = "（預設錯誤訊息）"

        try:
            if message.author.id not in self.mscDICT:
                self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)

            self.mscDICT[message.author.id]["updatetime"] = datetime.now()

            if self.mscDICT[message.author.id]["reporterList"] == [] and self.mscDICT[message.author.id]["latestQuest"] == "":
                replySTR = "請貼給我英文 news lead！"
                self.mscDICT[message.author.id]["latestQuest"] = "initial_quest"
                self.mscDICT[message.author.id]["tmpSTR"] = msgSTR

            elif self.mscDICT[message.author.id]["latestQuest"] == "initial_quest":
                english_lead = msgSTR.strip()
                chinese_article = self.mscDICT[message.author.id]["tmpSTR"]
                draft_story = process_news_story(chinese_article, english_lead)

                if not draft_story.startswith(english_lead):
                    draft_story = english_lead + "\n\n" + draft_story

                self.mscDICT[message.author.id]["latestQuest"] = "draft_story"
                self.mscDICT[message.author.id]["resultSTR"] = draft_story

                resultSTR = byLine_enditem_insert(draft_story)
                loki_result = askLoki(
                    self.mscDICT[message.author.id]["tmpSTR"],
                    refDICT={"name": [], "location": [], "date": []}
                )

                if loki_result and loki_result["name"]:
                    self.mscDICT[message.author.id]["reporterList"] = loki_result["name"]

                if self.mscDICT[message.author.id]["reporterList"]:
                    resultSTR = reporter_name_insert(resultSTR, self.mscDICT[message.author.id]["reporterList"])
                    resultSTR = twd2usd(resultSTR)
                    self.mscDICT[message.author.id]["resultSTR"] = resultSTR
                    replySTR = resultSTR

                self.mscDICT[message.author.id] = self.resetMSCwith(message.author.id)

        except Exception as e:
            replySTR = f"Something went wrong. Please try again.\n{e}"
            logging.error("Error in semantic reply: %s", e, exc_info=True)

        # Step 2: Send the final reply as a new message (or multiple if needed)
        await self.safe_reply(message, replySTR)



if __name__ == "__main__":
    # with open("account.info", encoding="utf-8") as f: #讀取account.info
    #     accountDICT = json.loads(f.read())
    client = BotClient(intents=discord.Intents.default())
    client.run(discord_token)

    
