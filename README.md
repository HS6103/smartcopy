# SmartCopy  
Smartcopy 結合 LLM 生成與符號式 AI 的規則檢查，並整合 Discord chatbot，旨在流線化英文新聞工作流程，並希望能分擔一部分查核工作（如金額換算、人名資訊等）。

> 本專案為個人實驗性質之 prototype，僅供探索與學習使用，並非公司正式產品。

---

## 目前支援功能

- 自動續寫英文草稿（GPT-4)  
- 檢查並轉換「台幣金額」為當日美金匯率 (卓騰Loki)
- 自動插入 by-line（將記者姓名轉為英文）  
- 加入標準結尾格式（Enditem/）

---

## 待加入／待解決項目

- 擷取中文稿人物中英姓名對照  
- 世界常識補充（例如：「2025年總統」→「賴清德」）

---

## 環境設定

1. 依照[步驟](https://ithelp.ithome.com.tw/articles/10350599)設定 DC bot
2. 在根目錄加入 .env 並寫入：

```
    discord_token = 上一步獲得的 bot token
    my_name = 您的英文名
    openai_api_key = 您的 OpenAI API key
```

3. 在 smartcopy_TW 放入您的卓騰 account.info 檔案
4. 在根目錄使用 `pip install -r requirements. txt` 安裝必要套件
5. 在根目錄加入 reporter_names.json 並以中文名為 key / 英文名為 value

## 使用流程

1. 貼上中文原稿  
2. 貼上初步的英文 lead（開頭段落）  
3. 等待草稿自動生成  

SmartCopy 將自動完成以下作業：  

- 延續英文草稿撰寫
- 尋找稿中第一個台幣金額並標註當日美金換算
- 根據記者中文姓名與使用者英文名自動生成 by-line  
- 加入標準結尾格式 Enditem/

---

本工具為支援雙語新聞編輯流程而開發，仍在持續改進中，歡迎交流與指教。
