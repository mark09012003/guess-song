# 猜歌王

主持人用的中文猜歌遊戲，純 HTML、CSS 和 JavaScript，透過 YouTube IFrame API 播放。

## 功能

- 隨機抽歌、不重複，試聽 5／15／30／60 秒。
- 再聽一次：回到同一首、同一段落並重新倒數。
- 揭露歌名與歌手；獨立主持人答案視窗。
- 手動新增具名歌單，支援三欄 CSV／TSV：歌名、歌手、YouTube 連結。
- 333 筆內建曲目，同一影片合併後可抽 332 首；部分為原唱現場版本。

## 本機執行

在專案資料夾執行：

```bash
python -m http.server 8000
```

瀏覽器開啟 http://localhost:8000/ 。YouTube 播放需要網路，直接雙擊 HTML 可能因來源資訊而無法播放。

Windows 可雙擊 `windows/GuessSong.exe`，自動啟動 localhost:8000 並開啟瀏覽器，不需 Python。保留服務視窗，關閉即停止。若 8000 已使用，先停止其他服務。執行檔使用 Windows 內建 PowerShell；尚未在 Windows 實機驗證。

## Windows 啟動器重建

```bash
python windows/build.py
```

會把目前 `index.html` 與 `songs.json` 合併並內建到 `windows/GuessSong.exe`，同時輸出可檢視的 `windows/launcher.ps1`。

## 歌單保存

自訂歌單存在瀏覽器 localStorage（key：`guessSong.manualPlaylists.v1`），不寫回專案檔案，也不跨裝置同步。網址的協定、主機或連接埠改變會使用不同儲存區。請保留匯入用 CSV。

## Discord 直播

只分享遊戲主視窗，勿分享主持人答案視窗或整個螢幕。影片播放器在頁面最下方，直播時保持在上方遊戲區。展開題庫或新增歌單表單會看到答案，請在直播前設定。

## 靜態託管

把 `index.html` 與 `songs.json` 放在同一個公開目錄即可，不需要後端或 API key。可使用 GitHub Pages；本專案上傳本身不會自動啟用 Pages。

影片由 YouTube 提供，可能包含廣告、地區限制或禁止嵌入；遇到問題使用「跳過」。專案沒有下載或提供音樂檔案。
