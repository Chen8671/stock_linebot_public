# 導入 os 模組，該模組提供了與操作系統交互的功能，
import os
# 導入 requests 模組，該模組用於發送 HTTP 請求，
import requests 
# 該模組主要用於解析、建立與操作 XML 數據，
# 是處理 XML 文件的常用工具
import xml.etree.ElementTree as ET
# 從 linebot 套件中導入兩個核心元件
from linebot import LineBotApi, WebhookHandler
#linebot.exceptions 模組中導入 InvalidSignatureError 異常類
from linebot.exceptions import InvalidSignatureError
# 從 linebot.models 模組中導入三個核心元件：
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 從 pymongo 模組中導入 MongoClient，該類用於連接 MongoDB 數據庫
from pymongo import MongoClient
# 導入 pymongo 模組，提供與 MongoDB 數據庫交互的功能
import pymongo
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.models import *

app = Flask(__name__)


