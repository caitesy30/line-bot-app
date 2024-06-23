# -*- coding: utf-8 -*-
"""
Created on Mon Jun 3 02:34:58 2024

@author: user
"""

import os
import pandas as pd
from datetime import datetime
from binance.client import Client

def get_klines_df(symbol, interval):
    # 使用你的 API 密鑰和密鑰來初始化 Client
    api_key = 'DkAIJqRJFkH9HkD9xI5stfTWjIzURm6NUoPAEUxaKNGkOuVPtCnY4tYMDlVkSEcE'
    api_secret = 'NjXXSBkhDHo7gXb7nP2clJf3VV3r11a2UgKt2bycoon4loZlNV36PMWolD9Bg6YA'
    client = Client(api_key, api_secret)

    # 如果不存在 Data 資料夾則創建一個
    if not os.path.exists("Data"):
        os.mkdir("Data")

    # 檢查 CSV 文件是否存在
    file_name = f"Data//{symbol}_{interval}.csv"

    if os.path.exists(file_name):
        # 讀取已存在的文件
        file_data = pd.read_csv(file_name)

        # 獲取最後一行的時間戳
        old_ts = file_data.iloc[-1, 0]  # 修改位置访问

        # 將時間戳轉換為日期字符串
        old_time_str = datetime.fromtimestamp(old_ts / 1000).strftime(
            "%d %b %Y %H:%M:%S"
        )

        # 獲取新數據
        new_data = client.futures_historical_klines(
            symbol, interval, old_time_str
        )

        # 將新數據轉換為 DataFrame
        now_data_df = pd.DataFrame(new_data)

        # 設置列名
        now_data_df.columns = [str(i) for i in now_data_df.columns]

        # 合併舊數據和新數據
        if now_data_df.shape[0] > 0:
            dataframe_data_new = pd.concat([file_data, now_data_df], axis=0)
            dataframe_data_new = dataframe_data_new[
                ~dataframe_data_new["0"].duplicated(keep="last")
            ]
        else:
            dataframe_data_new = file_data.copy()
    else:
        # 獲取自指定日期以來的新數據
        start_str = datetime.strptime(
            "2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        ).strftime("%d %b %Y %H:%M:%S")

        tmp_data = client.futures_historical_klines(
            symbol, interval, start_str
        )

        # 將新數據轉換為 DataFrame
        dataframe_data_new = pd.DataFrame(tmp_data)

    # 將合併後的數據保存到 CSV 文件中
    dataframe_data_new.to_csv(file_name, index=False)

    # 設置列名
    dataframe_data_new.columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ]

    # 添加 datetime 列並設置為索引
    dataframe_data_new["datetime"] = pd.to_datetime(
        dataframe_data_new["open_time"] * 1000000, unit="ns"
    )
    dataframe_data_new.set_index("datetime", inplace=True)

    # 將數據轉換為 float 型
    dataframe_data_new = dataframe_data_new.astype("float")

    return dataframe_data_new
