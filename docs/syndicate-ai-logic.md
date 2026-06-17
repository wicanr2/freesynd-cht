# 《Syndicate》(1993) 的 AI 邏輯 ── 從 Bullfrog 到 FreeSynd 的考古

> 一篇給 30 年後同代玩家的回信，也是給寫過遊戲 AI 的人的技術筆記。
>
> 本文所有「程式怎麼跑」的斷言，都附上 FreeSynd 引擎原始碼的 `檔名:行號`。
> FreeSynd 是 1993 年原版《Syndicate》的開源重製（reimplementation），
> 它的 kernel 是目前最完整、可被閱讀的「Syndicate AI 還原本」，
> 因此本文把它當作真相之源（source of truth）來引用。

---

## 目錄

- [一、背景：1993 年，為什麼這款 AI 重要](#background)
- [二、IPA 三屬性系統 ── Syndicate 的招牌 AI/RPG 混血](#ipa)
- [三、行為元件架構 (Behaviour Components)](#components)
- [四、狀態機與動作鏈 ── 一個敵人怎麼決定要不要開槍](#statemachine)
- [五、平民恐慌與說服 ── 讓人群活起來的兩個機制](#crowd)
- [六、1993 的限制 vs 現代 ── FreeSynd 補了什麼](#modern)
- [附錄：給自己接手的人](#appendix)

---

<a name="background"></a>
## 一、背景：1993 年，為什麼這款 AI 重要

還記得嗎？1993 年，Bullfrog 把《Populous》《Theme Park》那套「上帝視角看一堆小人各過各的日子」的世界觀，
塞進了一座賽博龐克的霓虹都市裡，然後遞給你一支電擊棒，叫你去**洗腦路人**。這就是《Syndicate》。

那時候我們在 14 吋 CRT、320×200、Sound Blaster 的機器前，第一次看到一件很難形容的事：
**畫面上的小人不是擺設**。等距視角（isometric）的街道上，行人會走來走去，會在你掏槍的瞬間四散尖叫；
警察會聞風而來；敵方企業特工會包抄。整個城市是即時運轉的（real-time），不是回合制 ── 這在 1993 年的戰術遊戲裡是稀罕貨。

更狠的是那把**說服器（Persuadertron）**。你不必把路人全殺光，你可以走過去、按一下，
把他「收編」成你的隨從。被收編的人會跟著你跑、會去撿地上的槍、會替你擋子彈、甚至替你開槍。
一個任務打到後面，你可能帶著一條三十人的隊伍在街上行軍 ── 這種「一個人變成一支軍隊」的爽感，
靠的全是底層那套讓每個小人**各自做決定**的 AI。

老玩家絕對記得：那時候沒有 GameFAQ、沒有 Discord、沒有 wiki，
你對遊戲機制的理解全靠《電腦玩家》《軟體世界》《PC Game》三大誌的拆解，跟 BBS 攻略板上前輩的口耳相傳。
而 Syndicate 的 AI 之所以難解，是因為它把**即時戰術**、**群眾模擬**，跟一套**藥物驅動的數值系統**綁在一起 ──
那套系統就是底下要講的 IPA。

要懂這套 AI 為什麼長這樣，得先回到它的三條彩色長條：智力、感知、腎上腺素。

---

<a name="ipa"></a>
## 二、IPA 三屬性系統 ── Syndicate 的招牌 AI/RPG 混血

每個特工底部都有三條會自己變動的彩條：**Intelligence（智力）/ Perception（感知）/ Adrenaline（腎上腺素）**，
合稱 **IPA**。這不是裝飾。Syndicate 把每個小人的「神經系統」抽象成這三條會隨時間流動的數值，
而你可以靠注射藥物去推動它們 ── 這是 1993 年罕見的「AI 即 RPG 數值」的設計。

FreeSynd 把這套系統封裝成 `IPAStim` 類別（`kernel/include/fs-kernel/model/ipastim.h`）。
每個 ped 持有三個 `IPAStim` 物件：`adrenaline_` / `perception_` / `intelligence_`（`ped.cpp:58-60`）。

### 三條 bar 的模型：amount / effect / dependency

原版畫面上每條 IPA 其實是**三段疊在一起**的，FreeSynd 完整保留了這個模型（見 `ipastim.h:111-130` 的註解）：

| 子量 | 螢幕對應 | 意義 | 原始碼 |
|---|---|---|---|
| **amount**（量） | 亮色段，玩家可拉動 | 注射進去的藥量。50% 是中性點。你按鍵就是在動它。 | `ipastim.h:116` |
| **effect**（效果） | 較暗的段 | 藥物**實際生效**的程度。它從 dependency 線往 amount 追，追上後兩者一起往 dependency 線退。 | `ipastim.h:118-124` |
| **dependency**（依賴） | 中性線 | 成癮/耐受度。這條設得越高，effect 持續越短 ── 越依賴，藥效越短命。 | `ipastim.h:125-130` |

這三段不是靜止的。`processTicks()` 每幀被呼叫（`ped.h:390-392` 對三個 IPA 各跑一次），
模擬原版觀察到的流動規律（`ipastim.cpp:96-153` 的註解直接寫了「From observation of the original Syndicate」）：

- **effect 大約每秒走一格**（`effect_timer_(1000)`，`ipastim.cpp:37`）；
- **dependency 走得慢得多**，約 effect 的五、六分之一（`dependency_timer_(4500)`）；
- effect 與 amount 相等後，**兩者一起往 dependency 線退**（`ipastim.cpp:121-128`）；
- dependency 永遠悄悄朝 amount 蠕動（`ipastim.cpp:134-149`）。

換句話說：你猛拉一條 bar 到頂，藥效不會立刻全開（effect 要一格一格追上來），
而且你越常這樣搞，dependency 越往上爬，下一次藥效就越短 ── **這就是成癮的數值化**。

### 一條 bar 怎麼變成一個倍率

AI 真正吃的是 `getMultiplier()`（`ipastim.cpp:49-84`）。它的演算法很乾淨：

1. 取 `magnitude = |amount − dependency|`（`getMagnitude()`，`ipastim.cpp:43-46`）── 偏離中性線多遠；
2. 看方向：amount ≥ dependency 是 **boost**，否則是 **reduce**（`direction()`，`ipastim.h:97-98`）；
3. boost 時回傳 `1 + magnitude/100`，範圍 **1.0 → 2.0**；reduce 時回傳其倒數，範圍 **0.5 → 1.0**。

所以一條 IPA 對外永遠是一個 **0.5x ～ 2.0x** 的乘數，中性時剛好 **1.0x**。
原始碼註解講得很白：一個沒有任何 Mod 的特工，腎上腺素拉滿時移動速度加倍，拉到底時砍半；
中性的腎上腺素 ── 跟一個普通平民走一樣快（`ipastim.cpp:51-64`）。

### 三條 bar 各自餵給哪段行為

這是 IPA 真正「是 AI」而非「是裝飾」的地方 ── 三個乘數分別接到不同的行為參數上：

| IPA | 餵給什麼 | 具體效果 | 原始碼 |
|---|---|---|---|
| **Perception 感知** | 偵測範圍、說服力、命中 | 把基礎警戒半徑乘上 `perception().getMultiplier()`；平民逃跑距離也照此放大；說服有效點數乘上感知 | `behaviour.cpp:213`、`behaviour.cpp:534`、`ped.cpp:1435`、`ped.cpp:794` |
| **Adrenaline 腎上腺素** | 移動速度、反應頻率、開槍間隔 | 速度直接乘上腎上腺素乘數；自衛掃描週期被它除（越高反應越快）；兩次射擊間隔被它除 | `ped.cpp:1249`、`behaviour.cpp:204`、`ped.cpp:577` |
| **Intelligence 智力** | 偵測門檻、開槍間隔微調 | 智力乘數 < 0.6 的敵人「掃描失敗」，根本不會發現你；智力對開槍間隔有一個較小的加成 | `behaviour.cpp:721`、`behaviour.cpp:911`、`ped.cpp:578` |

舉個能直接讀懂的例子 ── **開槍頻率**怎麼算（`ped.cpp:573-580`）：

```cpp
double reaction = kDefaultShootReactionTime
    / adrenaline_.getMultiplier()                          // 腎上腺素越高，反應越快
    / (1.0 + 0.2 * (intelligence_.getMultiplier() - 1.0)); // 智力給一個較小的加成
return reaction + pWeapon->getClass()->reloadTime();
```

腎上腺素拉滿（2.0x）的特工反應時間直接砍半，再疊上智力的小加成，
然後才加上武器的重裝彈時間。命中率那邊也吃 IPA ── 感知拉高使彈道更準，
但腎上腺素拉太高反而讓手抖、散布變大（`ped.cpp:1349-1350`，注意兩條的正負號相反）。

這就是 Syndicate AI 的招牌：**你不是在點技能樹，你是在替一個會上癮的神經系統調藥**。
拉滿全部很爽 ── 跑得飛快、反應極速、看得老遠 ── 但 dependency 跟著爬，藥效越來越短，
而高腎上腺素還會讓你的特工**打不準**。這種「強得有代價」的張力，就是底下行為元件運作的環境。

---

<a name="components"></a>
## 三、行為元件架構 (Behaviour Components)

原版把每個小人的「決策」寫死在一大團邏輯裡。FreeSynd 做了一件很 deep-module 的事：
把每個 ped 的 AI 拆成**可組合的行為元件**（BehaviourComponent）。

一個 `Behaviour` 物件持有一條元件清單 `compLst_`（`behaviour.h:102`）。
每幀，`Behaviour::execute()` 依序跑每個**啟用中**的元件（`behaviour.cpp:94-107`）；
事件來時，`handleBehaviourEvent()` 把事件廣播給**所有**元件（`behaviour.cpp:68-74`）。
這是個經典的 component + event 架構：對外只有「execute / 收事件」兩個窄介面，
內部每個元件各自藏一台小狀態機。一個平民可能只掛 `PanicComponent`，
一個玩家特工掛 `CommonAgent + AgentDefense + Persuader`，一個敵方特工掛 `PlayerHostile`。

### 事件模型

元件之間、以及世界對元件，靠這幾種事件溝通（`behaviour.h:48-65`）：

| 事件 | 何時發出 | 誰在乎 |
|---|---|---|
| `kBehvEvtWeaponOut` | 有人把槍掏出來 | 平民開始恐慌、警察進入警戒、被說服者去找槍 |
| `kBehvEvtWeaponCleared` | 有人收槍 | 平民冷靜、警察重新評估、被說服者收槍 |
| `kBehvEvtHit` | 某個 ped 被打中 | 裝了 Chest v2 Mod 的特工觸發回血 |
| `kBehvEvtActionEnded` | 一個動作鏈跑完 | 各狀態機回到「重新掃描」或「回預設」 |
| `kBehvEvtPersuadotronActivated` / `Deactivated` | 玩家開/關說服器 | `PersuaderBehaviourComponent` 開始/停止收編 |
| `kBehvEvtEnterVehicle` | 特工上車 | 他的隨從跟著上車 |
| `kBehvEvtEjectedFromVehicle` | 駕駛被打中、被踢出車 | 警察走離車身以免擋住射線 |

### 元件清單

| 元件 | 掛在誰身上 | 核心邏輯 | 關鍵原始碼 |
|---|---|---|---|
| **CommonAgentBehaviourComponent** | 所有特工（敵我） | 受傷後若裝有 Chest v2 Mod，週期性回血 1 點 | `behaviour.cpp:137-156` |
| **PersuaderBehaviourComponent** | 我方特工 | 說服器啟用時，掃描範圍內非我方 ped，對其插入一個「說服傷害」 | `behaviour.cpp:271-298` |
| **PersuadedBehaviourComponent** | 被說服者 | 跟隨主人；主人掏槍時，自己有槍就掏、沒槍就去地上找一把帶彈藥的撿起來 | `behaviour.cpp:305-411` |
| **PanicComponent** | 平民 | 預設停用（省 CPU）；有人掏槍才啟用，偵測到附近武裝者就往反方向逃跑 | `behaviour.cpp:437-549` |
| **PoliceBehaviourComponent** | 警察 | 看到非警察的武裝者就警告、逼近、開槍；對方收槍則等一陣子再決定回巡邏 | `behaviour.cpp:557-707` |
| **AgentDefenseBehaviourComponent** | 我方特工 | 自衛：每個掃描週期找最近的武裝敵人，原地開火（不追擊） | `behaviour.cpp:181-262` |
| **PlayerHostileBehaviourComponent** | 敵方特工 | 只打玩家小隊：發現、逼近、射擊、必要時呼叫附近同夥；目標久未現身就放棄追擊 | `behaviour.cpp:715-893` |
| **GuardAreaBehaviourComponent** | 駐守敵人 | 跟 PlayerHostile 類似，但**原地不動**只負責射擊，不會追 | `behaviour.cpp:905-1007` |

幾個值得多看一眼的元件：

**PanicComponent 的省電設計**。它建構時就 `setEnabled(false)`（`behaviour.cpp:434`），
平時完全不跑 ── 一座城市幾十個平民，沒人掏槍時你不希望每幀對每個人做半徑掃描。
只有 `kBehvEvtWeaponOut` 事件才把它喚醒（`behaviour.cpp:469-474`），
等場上武裝者歸零（`numArmedPeds() == 0`）再讓它睡回去（`behaviour.cpp:476-485`）。
這是 1993 年那種「CPU 預算極緊」的思維，被忠實還原下來。

**AgentDefenseBehaviourComponent 的 IPA 串接**。它把腎上腺素接到「反應頻率」上：
掃描週期 `kBaseScanPeriod / adrenaline().getMultiplier()`，夾在 80～500ms 之間
（`behaviour.cpp:204-207`）── 腎上腺素越高，掃得越勤、反應越快。
偵測半徑則乘上感知（`behaviour.cpp:213`）。找敵人時還會做 3D 射線檢查
（`checkBlockedByTile`），牆壁、樓板都會擋住跨層射擊（`behaviour.cpp:256-259`）。

**PlayerHostileBehaviourComponent 的群體警報**。一個敵方特工發現你之後，
不只自己開打，還會呼叫半徑 `kAllyAlertRange`（2048）內的同夥一起上
（`alertNearbyAllies`，`behaviour.cpp:838-851`），被叫到的同夥跳過「警告」直接進入交戰
（`alertToEnemy`，`behaviour.cpp:830-836`）。這讓敵方特工感覺像一個小隊，而不是一盤散沙。

讀完元件清單，你會發現一個漂亮的事實：**同一套事件、同一個 execute 介面，
組合出平民、警察、敵特、隨從四種完全不同的「人格」**。這正是底下狀態機要展開的東西。

---

<a name="statemachine"></a>
## 四、狀態機與動作鏈 ── 一個敵人怎麼決定要不要開槍

行為元件回答「我現在想做什麼」，但「具體一步步怎麼動」交給**動作鏈（action chain）**。
這是兩層：**狀態機**在元件內（決策），**動作**在 ped 上排成鏈（執行）。

以敵方特工為例，`PlayerHostileBehaviourComponent` 的狀態機有四態（`behaviour.h:361-370`）：

```
        ┌──────────────────────────────────────────────┐
        │                                               │
        ▼                                               │
   ┌─────────┐  發現可見的玩家     ┌──────────────────┐  │
   │ Default │ ──(intel≥0.6 + LOS)──▶│ FollowAndShoot   │  │
   │（巡邏） │                     │（逼近並射擊）    │  │
   └─────────┘                     └──────────────────┘  │
        ▲                                  │             │
        │                          目標死亡/             │
        │                          失去視野 4 秒          │
        │                                  ▼             │
   ┌──────────────────┐   等待結束   ┌──────────────────┐ │
   │ CheckForDefault  │ ◀───────────│ PendingEndFollow │ │
   │（還有敵人嗎？）  │             │（等一下）        │ │
   └──────────────────┘             └──────────────────┘ │
        │  還有敵人 → 重新 FollowAndShoot ─────────────────┘
        │  沒敵人 → 收槍、回 Default
        └────────────────────────────────────────────────
```

關鍵細節，逐條對原始碼：

1. **Default → FollowAndShoot 的兩道門**（`behaviour.cpp:715-731`）：
   先過**智力門**（`intelligence().getMultiplier() < 0.6` 直接掃描失敗，笨敵人發現不了你），
   再過**視線門**（`findVisiblePlayerAgent` 內做 `checkBlockedByTile` 射線檢查）。
   偵測半徑由武器射程與感知共同決定（`computeDetectionRange`，`behaviour.cpp:785-795`）。

2. **FollowAndShoot 的放棄追擊**（`behaviour.cpp:732-752`）：
   目標若離開視野，累計 `lostTargetMs_`，超過 `kGiveUpPursuitMs`（4000ms）就放棄，
   進入 PendingEndFollow ── 不會像 1993 原版那樣有時鬼打牆地永遠追下去。

3. **動作鏈本身**（`followAndShootTarget`，`behaviour.cpp:853-892`）。
   進入交戰時，往 ped 的 alt 動作槽塞進一條鏈：

   ```
   WaitBeforeShootingAction → FollowToShootAction → FireWeaponAction → ResetScriptedAction
   ```

   - **WaitBeforeShootingAction**（`actions.cpp:722-751`）：面向目標、選一把有彈藥的射擊武器，
     等 2000ms（`waitTimer_(2000)`）。這就是你被敵人發現後那短短的「喘息空檔」 ──
     而如果開槍的是**警察**、目標是**你的特工**，等待結束時會發出 `PoliceWarningEmittedEvent`
     ── 那句「放下武器」的警告就是這裡來的（`actions.cpp:742-745`）。
   - **FollowToShootAction**（`actions.cpp:480-...`）：逼近到「武器射程的 2/3」才停
     （`followDistance_ = (range()/3)*2`，`actions.cpp:485`）；若貼得太近（< `kMeleeAvoidDistance` = 128）會後退一點，避免貼臉（`actions.cpp:506`）。
   - **FireWeaponAction**（`actions.cpp:753-...`）：真正開火。它會檢查目標沒死、沒有能量護盾、
     射手自己沒在被擊中的硬直裡；警察還多一條規矩 ── **不對沒掏槍的人開火**（`actions.cpp:765-767`）。
     射擊期間若目標移出射程或躲到掩體後，就停火。

警察的狀態機（`PoliceBehaviourComponent`）幾乎是同一套，只多了「目標收槍 → PendingEndFollow 等 1500ms 再決定」
這條人性化的規則（`behaviour.cpp:598-612`），以及上面那句警告。
駐守敵人（`GuardArea`）則砍掉 FollowToShoot 那一段 ── 它**只站著開槍**（`behaviour.cpp:920-923`）。

這裡有個值得學的工程點：**為什麼開槍時還要在元件的 execute 裡持續 `updateShootingTarget`？**
因為自動射擊一旦啟動，移動動作鏈會被掛起，FireWeaponAction 自己沒法追蹤移動中的目標，
所以元件每幀補一刀，更新瞄準點與朝向（`behaviour.cpp:753-758`、`behaviour.cpp:561-566` 都有同樣註解）。
這是「動作鏈」與「狀態機」兩層分工下必然要打的一個補丁。

---

<a name="crowd"></a>
## 五、平民恐慌與說服 ── 讓人群活起來的兩個機制

Syndicate 的城市之所以「活」，靠的就是這兩件事：**人群會怕**，而你**能收編**。

### 平民恐慌（PanicComponent）

平民平時只有一個預設動作：不停地走（`behaviour.h:206-210` 的註解）。
直到有人掏槍 ── `kBehvEvtWeaponOut` 把 `PanicComponent` 喚醒（`behaviour.cpp:469-474`）。
喚醒後，每 500ms 掃一次附近（`scoutTimer_(500)`，`behaviour.cpp:428`），
若 `kScoutDistance`（1500）內有武裝者（`findNearbyArmedPed`，`behaviour.cpp:511-519`），
就 `runAway`：

```cpp
// 朝武裝者的反方向設定逃跑方向
pPed->setDirection(thisPedLoc.x - otherLoc.x,
                   thisPedLoc.y - otherLoc.y);
// 逃跑距離 = 基礎 800 × 感知乘數
int escapeDistance = kBaseDistanceToRun * pPed->perception().getMultiplier();
```
（`behaviour.cpp:525-549`）

注意這裡 ── **感知越高的平民逃得越遠**。一個遲鈍的路人只跑一小段就停下；
一個感知拉高的人會頭也不回地衝出半條街。再加上武裝者一旦死亡或收槍，恐慌立刻解除
（`behaviour.cpp:439-447`、`behaviour.cpp:476-485`），整片人群的「炸開又重新聚攏」就是這麼來的。
1993 年我們看著一聲槍響後滿街人尖叫四散 ── 底層其實只是幾十台這種小狀態機在同步反應。

### 說服器（Persuadertron）

這是 Syndicate 的靈魂機制。它由兩個元件配合：

**收編端**（`PersuaderBehaviourComponent`，掛在玩家特工上，`behaviour.cpp:271-298`）：
玩家按下說服器後，每幀掃描非我方 ped，對能說服的對象插入一個 `kDmgTypePersuasion` 傷害。
能不能說服由 `canPersuade` 判定（`ped.cpp:1423-1442`）── 對方需要的點數，
不能超過你的「總說服點數 × 感知乘數」。所以**感知高的特工能收編更頑固的對象**
（警察、敵方特工要的點數遠高於平民，見 `getRequiredPointsToPersuade`，`ped.cpp:1375-1409`）。

**被收編端**（`PersuadedBehaviourComponent`，`behaviour.cpp:305-411`）：
這是一台五態小狀態機（`behaviour.h:184-195`）。一被收編，它就：

1. 清掉原本的動作，把「跟隨主人」設成新的預設動作（`FollowAction`，`behaviour.cpp:307-313`）；
2. 主人掏槍時（`kBehvEvtWeaponOut`），自己有槍就掏出來，沒槍就進入 `LookForWeapon` 狀態
   ── 每秒掃一次地面，找一把帶彈藥、最近的槍（`findWeaponWithAmmo`，`behaviour.cpp:393-411`），
   找到就走過去撿、撿完自動掛上 warning 讓主人知道可以選它（`behaviour.cpp:314-337`）；
3. 主人上車（`kBehvEvtEnterVehicle`），隨從跟著上車（`behaviour.cpp:377-383`）。

於是你看到的畫面 ── 一條隨從縱隊跟著你跑、你一掏槍他們紛紛去撿地上的槍武裝起來 ──
全是這台狀態機在每個被收編者身上各跑一份。一個人，真的能滾成一支軍隊。

---

<a name="modern"></a>
## 六、1993 的限制 vs 現代 ── FreeSynd 補了什麼

說句公道話 ── 1993 年的原版在當時的硬體上已經是奇蹟。但拿現代眼光看，
有些行為是「礙於預算的妥協」，有些是「沒做到的事」。FreeSynd 在忠實還原的前提下，
補了一層更聰明的可選邏輯。以下是誠實的對照：

| 面向 | 1993 原版的處境 | FreeSynd 的還原 / 改進 |
|---|---|---|
| **視線判定** | 跨樓層、隔牆射擊的判定常有破綻 | 統一走 `checkBlockedByTile` 3D 射線，牆與樓板都擋槍（`behaviour.cpp:256-259`） |
| **追擊邏輯** | 敵人有時會永遠追著消失的目標 | 加入 `kGiveUpPursuitMs`（4000ms）失聯放棄機制（`behaviour.cpp:740-742`） |
| **自衛 AI** | 特工自衛行為陽春 | 可選的 Smart AI：自動拔出傷害最高的有彈武器（`selectBestDefensiveWeapon`，`behaviour.cpp:164-179`），由 `g_Ctx.isSmartAI()` 切換 |
| **群體協同** | 敵人各打各的 | 發現玩家會警報半徑內同夥一起上（`alertNearbyAllies`，`behaviour.cpp:838-851`） |
| **CPU 預算** | 每個小人都要省著算 | 保留了原版的省電思維：`PanicComponent` 預設停用、各元件用 `scoutTimer_` 節流掃描，而非每幀全掃 |

特別要講 **Smart AI 開關**這件事。FreeSynd 給了一個 `g_Ctx.isSmartAI()` 旗標（`behaviour.cpp:36`）：
關掉時是**忠實模式（faithful）** ── 特工絕不自動拔槍，只有手上已有武器才會還擊（`behaviour.cpp:208-211`）；
打開時才啟用上面那些「拔最猛的槍、用腎上腺素調反應頻率」的現代強化（`behaviour.cpp:200-221`）。
這種「忠於原作 vs 玩得更順」二選一的設計，正是開源重製專案最體面的做法 ── 不擅自改掉你記憶裡的那款遊戲，
但允許你選一條更聰明的路。

值得強調的是：**FreeSynd 沒有偷懶把 IPA 簡化掉**。
那套 amount/effect/dependency 三段流動、那條 0.5x～2.0x 的乘數、那個會上癮的 dependency 蠕動，
全部一比一還原（`ipastim.cpp` 整份）。它甚至在註解裡老老實實寫下哪些是「從原版觀察推得」、
哪些是「原版機制的近似」（如 `canPersuade` 上方那段對 `can_i_persuad_you @ 0x302a0` 的考據，`ped.cpp:1417-1419`）。
這是還原工程該有的誠實 ── **不確定的地方標出來，不假裝自己懂得比 1993 年的反組譯更多**。

---

<a name="appendix"></a>
## 附錄：給自己接手的人

如果你想動 FreeSynd 的 AI，記住這幾條真相之源：

- **IPA 數學**：`kernel/include/fs-kernel/model/ipastim.h` + `kernel/src/model/ipastim.cpp`。
  改 `getMultiplier()` 或那兩個 timer 之前，先讀懂 `processTicks` 的註解。
- **行為決策**：`kernel/src/ia/behaviour.cpp`（八個元件）+ `kernel/include/fs-kernel/ia/behaviour.h`（狀態列舉、事件列舉、各元件常數）。
- **動作執行**：`kernel/src/ia/actions.cpp` + `kernel/include/fs-kernel/ia/actions.h`。
  動作鏈的「2/3 射程」「melee 128」「警告 2000ms」這些手感數字都藏在這。
- **ped 主迴圈**：`kernel/src/model/ped.cpp` 的 `doUpdateState`（`ped.cpp:462-474`）──
  先跑 behaviour，再跑動作，最後跑武器；IPA 的 `processTicks` 由 `ped.h:390-392` 每幀帶動。

一句話收束：Syndicate 的 AI 不是一套聰明的演算法，而是一群**各自帶著一台小狀態機、
被同一套藥物數值驅動、靠事件互相觸發**的小人。三十年前我們以為自己在指揮一支軍隊，
其實我們是在替一座會自己運轉的城市調參數。FreeSynd 把這座城市的原始碼攤開給你看 ── 拿去讀，拿去改。

---

*本文所有程式碼引用對應 FreeSynd kernel 原始碼。譯名與機制考據以原始碼註解為準；
不確定處（如說服力的精確公式）已在文中標明為「近似」。致敬 Bullfrog 1993，與 FreeSynd 歷年貢獻者。*
