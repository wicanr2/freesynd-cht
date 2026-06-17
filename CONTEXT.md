# CONTEXT — 詞彙表（Ubiquitous Language）

依 Eric Evans (DDD) 的 ubiquitous language 精神：本專案的人與 agent 共用下表這套術語。
寫程式、命名、寫文件、翻譯時優先採用 **Term** 欄的正式用語；`Avoid:` 標出禁用同義詞。
新概念請先進此表再用。

| Term | 定義（一行） | Avoid / 備註 |
|---|---|---|
| **極道梟雄** | 本專案譯名，即 Bullfrog／EA 1993 年作 *Syndicate* 的 1994 台灣發行名（見《軟體世界》第 61 期）。 | Avoid: 直接叫「Syndicate」指代本中文版 |
| **財團** | 統治崩潰後世界的巨型企業勢力（Syndicate）；玩家掌權其一，目標是消滅其他財團。 | Avoid: 辛迪加、組織、公會 |
| **幹員** | 玩家指揮的改造作戰人員（agent），一隊四名。 | Avoid: 特工（同義，但統一用「幹員」）、探員、員工 |
| **勸服器** | 招牌特殊裝置（Persuadertron）：不殺傷，而是「說服」平民乃至敵方幹員倒戈加入你的部隊。 | Avoid: 感化器、說服器；「感化器」為 1994《軟體世界》舊譯，僅在史料引用時保留 |
| **義體** | 幹員各部位（眼／腦／心臟／胸／手臂／腿）可替換升級的生化零件（cyborg-mod，v1→v3）。 | Avoid: 改裝件、cyborg-mod、單寫「MOD」（口語可稱 MOD，正式文件用「義體」） |
| **IPA** | 每名幹員的三條可調滑桿屬性：**智力 Intelligence／感知 Perception／腎上腺素 Adrenaline**。 | Avoid: 拆開各自亂譯；三字首固定為 I/P/A |
| **智力** | IPA 之 Intelligence：偵測門檻與命中微調；聰明模式下決定打得多準。 | — |
| **感知** | IPA 之 Perception：偵測／警戒範圍、說服力、平民逃跑距離。 | — |
| **腎上腺素** | IPA 之 Adrenaline：移動速度、反應頻率、開槍間隔（越高反應越快）。 | — |
| **領地** | 未來地球切成的約 50 塊可征服區域（territory），拿下後可課稅充軍費。 | Avoid: 地盤、區域、省份 |
| **任務簡報** | 每關開打前的情報敘事（briefing），主目標以 `< >` 標出；本中文化最費心的部分。 | Avoid: 任務說明、brief、簡報書 |
| **隊伍選擇** | 出擊前配置每名幹員義體與 IPA 的畫面（squad-select / equip）；裝備配裝亦在此。 | Avoid: 編隊、選兵、裝備（裝備是此畫面的子功能，不另立術語） |
| **AI 模式：正常** | 忠於 1993 原版的敵我 AI（Classic）：幹員不自動拔槍、敵人無限追擊。 | Avoid: 經典、Classic（UI 字串固定「正常」） |
| **AI 模式：聰明** | 2026 強化的可切換 AI（Smart）：幹員依 IPA 自衛、敵人失聯 4 秒放棄追擊、守衛守崗位。 | Avoid: 智慧、強化、Smart（UI 字串固定「聰明」） |

> 設定切換位置：「**公司設定**」內可在 **AI：正常** 與 **AI：聰明** 間切換（持久化於 `ai_smart`）。
> AI 行為與 IPA 的完整考據見 [`docs/syndicate-ai-logic.md`](docs/syndicate-ai-logic.md)；引擎踩雷見 [`docs/ENGINE-NOTES.md`](docs/ENGINE-NOTES.md)。
