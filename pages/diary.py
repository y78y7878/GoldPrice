import streamlit as st

st.set_page_config(
    page_title="開發日誌｜Git 工作流實戰",
    page_icon="📖",
    layout="wide",
)

st.title("📖 開發日誌：從混亂到條理的協作與版控實戰")

st.markdown(
    """
    在這次專案開發中，除了程式碼本身的邏輯，最大的收穫莫過於真正弄懂了 Git 與 GitHub 的協作心法，
    以及如何安全地管理專案的環境變數。這篇日誌紀錄了我在這段期間踩過的坑、釐清的觀念，
    以及最終建立的「開發標準工作流」。

    一開始我常常看著 VS Code 裡的「Sync Changes」發呆，或者被交錯的分支與 Commit 混在一起搞得暈頭轉向。
    但透過實際踩坑、整理紀錄與修正流程，我逐漸建立起一套穩定、可維護、可協作的 Git 工作流。
    """
)

st.subheader("🎯 這份日誌想展現的能力")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("✅ 了解 Git 分支的責任邊界與用途")
with col2:
    st.info("✅ 能處理 Commit、Stash、Rebase、PR 與分支清理")
with col3:
    st.info("✅ 具備環境變數安全管理與協作專案觀念")

st.markdown("---")

st.subheader("🛑 踩坑實錄與 Git 觀念重塑")

st.markdown("### 1. 突破 Master 結界：設定分支保護 (Branch Protection)")
st.markdown(
    """
    剛開始常不小心在 `master` 上改 Code，直到推不上去才發現卡關。這讓我徹底學會了 GitHub 的
    **分支保護機制**。這不是在刁難開發者，而是確保主線程式碼穩定、無 Bug 的終極防線。
    所有進 `master` 的變更都必須經過 PR (Pull Request) 的洗禮，絕不允許任何人單方面硬推。
    """
)

st.success(
    """
    💡 頓悟觀念：`master` 是「唯讀」的櫥窗
    - 錯誤認知：把 `master` 當作開發區。
    - 正確做法：`master` 只放穩定、可上線的成品，不直接手動改檔案。
    - 解法：利用 `git branch feat/xxx` 把不小心寫好的 Commit 移到新分支，接著用 `git reset --hard origin/master` 讓本地主線強制與雲端對齊，最後再把新分支Push出去開 Pull Request。
    """
)

st.markdown("### 2. 精準分岔：改用「Create Branch From...」")
st.markdown(
    """
    以前建立分支時總是無腦點擊「Create Branch」，常常因為當下沒注意自己踩在哪個節點，
    導致新分支包含了不該有的歷史紀錄。現在養成了好習慣，在 VS Code 一律使用
    **「Create Branch From...」**，並明確指定 `origin/master` 作為乾淨的起點，
    確保每一次開發都是從最新的雲端主線出發。
    """
)

st.markdown("### 3. 便條貼哲學：用完即刪與遠端清理")
st.markdown(
    """
    分支的本質是「時間線」而非「資料夾」，就像一張便條貼，完成任務就可以撕掉了。
    * **本地與遠端的差異**：在 VS Code 刪除分支（`Delete branch`）只是清理自己電腦上的紀錄；在 GitHub PR 合併後點擊的刪除，則是清理雲端（`Delete remote branch`）。
    * **黃金守則**：PR 合併完成後，**本地與遠端的分支都要一併刪除**，只保留主線的 Commit 歷史，讓 Git Graph 永遠保持乾淨清爽。
    """
)

st.markdown("### 4. 幽靈檔案：為什麼切換分支時變更會跟著走？")
st.markdown(
    """
    我在開發分支寫到一半時，想切回 `master` 看乾淨版本，卻發現剛剛還沒 Commit 的改動也一起跟著切過去，
    整個工作區變得混亂。當時我以為是 Git 出錯，後來才知道：尚未提交的修改，本質上不屬於任何分支，
    所以只要切換分支，它就會像「背後靈」一樣跟著你走。
    """
)

st.warning(
    """
    💡 頓悟觀念：尚未 Commit 的變更，不屬於任何分支
    - Git 的機制是：只要還沒 Commit，這些修改就會持續存在工作區。
    - 解法：在 VS Code 中採用 `Stash（暫存）`，例如 `git stash -u`，把寫到一半的進度打包收好後再切換分支，等回來後再 `git stash pop` 還原，這樣可避免混亂。
    """
)

st.markdown("### 5. 太早開的空分支，變成凍結的平行時空")
st.markdown(
    """
    早期我為了規劃，第一天就把 `master`、`develop`、`web` 等分支都開好，但後來開始做網頁開發時才發現，
    `web` 分支裡面幾乎是空的，完全沒有前期資料抓取與分析的成果。這讓我理解到：分支不是資料夾，而是「時間軸」和「任務線」。
    """
)

st.success(
    """
    💡 頓悟觀念：分支是時間線，不是資料夾
    - 錯誤認知：提早建好分支，像是在資料夾裡預留位置。
    - 正確做法：採用「即時建立（Just-In-Time）」原則，等要開始實作某個功能時，再從最新的 `master` 切出分支。
    - 好處：分支保持乾淨，不會因為空分支而造成誤判與後續合併混亂。
    """
)

st.markdown("---")

st.subheader("🔐 資安升級：環境變數與機密資訊管理")

st.markdown(
    """
    在這次合作專案中，我學會了如何優雅且安全地處理 API Key 等私密資訊，這對於未來參與任何商業或開源專案都至關重要：
    """
)

st.markdown("### 1. 打造隱形防護罩：`.env` 與 `.gitignore`")
st.markdown(
    """
    將所有絕對不能公開的私密金鑰全數移入 `.env` 檔案中，並**第一時間將 `.env` 寫入 `.gitignore`**。
    這樣一來，不論怎麼 Commit，這些機密檔案都會被 Git 忽略，絕不會被推送到 GitHub 上。
    """
)

st.markdown("### 2. 動態讀取私密資訊：`python-dotenv` 實戰")
st.markdown(
    """
    捨棄了將金鑰寫死在程式碼裡的危險做法，改用正規的套件處理：
    搭配內建的 `os` 模組，利用 `python-dotenv` 載入設定後，透過 `os.getenv('私密資訊名稱')` 動態讀取 `.env` 內的變數。
    這讓程式碼不僅安全，在不同環境（如我的電腦與夥伴的電腦）執行時也更具彈性。
    """
)

st.markdown("### 3. 團隊協作的貼心舉動：`.env.example`")
st.markdown(
    """
    既然 `.env` 不會上傳，夥伴 clone 專案下來後怎麼會知道需要哪些環境變數呢？
    最佳解法是額外建立一個 **`.env.example`** 檔案，裡面只放變數名稱與假資料（不放真實密碼），並把它 commit 上去：
    """
)

st.code(
    """
    # .env.example 格式範例
    私密資訊名稱=實際內容
    """,
    language="env",
)

st.markdown("---")

st.subheader("🔍 Git 觀念大解析：不再盲目敲指令")

st.markdown("### 1. `git fetch` vs `git pull`：快遞到底放哪裡？")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        📦 `git fetch`
        - 作用：只把遠端最新進度下載到本地的遠端追蹤分支，例如 `origin/master`
        - 特點：不會改動你的工作區，風險低，適合先確認有人更新了什麼
        - 直覺理解：像快遞把包裹送到管理室，但還不會搬進房間
        """
    )
with col2:
    st.markdown(
        """
        📦 `git pull`
        - 作用：等於 `fetch + merge`
        - 特點：會直接把遠端改動合併到當前分支中，若你本地有未提交內容，容易產生衝突
        - 直覺理解：快遞直接拆開包裹搬進你的房間，效率快，但也更容易打亂現狀
        """
    )

st.markdown("### 2. Git Graph 怎麼看？把它當成捷運路線圖")
st.markdown(
    """
    一開始我看 Git Graph 時，總覺得像一團亂麻，但後來我抓住三個關鍵：
    1. 時間軸由下往上：最上面通常是最新狀態。
    2. 主線與側線：一直往上的那條軸是主幹，分岔出去又合回來的是功能分支。
    3. 定位標籤：`@ feat/xxx` 是我現在站在哪個分支；`origin/master` 則代表 GitHub 雲端目前的版本。
    """
)

st.code(
    """
    git checkout master
    git pull origin master
    git checkout -b feat/今日任務
    git add .
    git commit -m "新增資料視覺化與重構"
    git push
    """,
    language="bash",
)

st.markdown("---")

st.subheader("🚀 實戰總結：我的標準開工三部曲")

st.markdown("#### 🟢 Phase 1：準備開工")
st.markdown(
    """
    1. 切換回 `master` 分支
    2. 執行 `git pull origin master`，確保拿到最新程式碼
    3. 立刻建立並切換到新分支：`git checkout -b feat/今日任務`
    """
)

st.markdown("#### 🟡 Phase 2：開發與遇到更新時")
st.markdown(
    """
    - 安心寫 Code，並適時提交 Commit
    - 若開發到一半，別人更新了 `master`：
      1. `git stash -u`
      2. `git fetch origin`
      3. `git rebase origin/master`
      4. `git stash pop`
    """
)

st.markdown("#### 🔴 Phase 3：收尾與清理")
st.markdown(
    """
    1. `git push` 推送到 GitHub 並建立 Pull Request
    2. 審核通過後合併分支
    3. GitHub 上刪除遠端分支
    4. 本地切回 `master`，拉取最新進度，最後執行 `git branch -D feat/今日任務` 清理分支
    """
)

st.markdown("---")

st.subheader("🧠 心得：我學到的不是「會打字」，而是「會管理版本」")

st.markdown(
    """
    這次實作中，我最大的收穫不是會寫出一堆指令，而是理解了 Git 真正的價值：
    它不是單純保存歷史，而是幫助我把工作拆成可驗證、可回溯、可協作的流程。

    在一個專案裡，版本控制不只是「避免資料丟失」，更是讓工程師能清楚表達：
    我做了什麼、為什麼這樣做、何時需要切換分支、如何與同事協作、如何保護穩定版本，
    以及如何安全管理敏感資訊。

    這種能力讓我在專案管理、協作溝通、任務拆解與資訊安全上，都更加有條理，
    也讓我明白：一個好的 Git 流程，不只是工具使用技巧，更是專案成熟度與工程思維的體現。
    """
)

st.caption("開發日誌整理：Git / GitHub 基本觀念、分支管理、衝突處理、Commit 流程、協作邏輯與環境變數安全管理")
