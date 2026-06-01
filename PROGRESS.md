# 进度日志

> 我(Claude)在用户出门期间自动推进的工作记录。从上往下读。
> 每完成一个特性会在这里加一行 + 简短说明 + 改动文件 + 验证结果。

## 计划摘要
A. 考官稳定化 · B. 测试流程(设置/计时器/控制) · C. 历史/分析(详情/导出/走势)
D. 体验(移动端/Landing/骨架/toast/快捷键) · E. 硬化(限流/健康/日志/bug 巡检)

跳过(等回来):Stripe / OAuth / 邮箱+短信验证 / Docker / Postgres / 服务端 TTS / git push

---

## ✅ A · 考官稳定化(离线验证)
**做了什么**:`webapp.py` 已加 PART1_BANK / PART2_BANK / PART3_THEMES 服务端题库 + `_pick_part1/2/3` 按 session id 确定性抽取 + 反馈带 `_candidate_stats` 量化注入。`phase_hint(history, sid)` 已重写。
**验证**:python 离线跑过 — 同一 sid 永远抽到同一主题/cue/sub-themes。例如 `demo-sid-12345` → Part 1=photos / Part 2=play_film / Part 3=Theatres+Actors。链路正确。
**留给你**:实际模型行为(听话度)需要你点开试。如果发现模型仍然跑题/重复,告诉我哪一段,我针对性加防线。

---

## ✅ B1 · 测试前设置页 + 用户偏好
**后端**(`webapp.py`):
- `users` 加 `target_band` / `accent` / `preferred_topic` 列(additive migration)
- `sessions` 加 `target_band` / `accent` / `p1_topic` 列
- 新接口:`PATCH /api/me`(更新姓名/分数/口音/主题)、`GET /api/topics`(返回 PART1_BANK 主题列表)
- `POST /api/session` 接受 body `{target_band, accent, p1_topic}`,缺省回退到用户 prefs
- `phase_hint(history, sid, p1_topic, target_band)`:Part 1 用指定主题、反馈带目标分校准

**前端**(`index.html`):
- `#setupOverlay` 全屏屏(用户名 / 目标分 / 口音 / Part 1 主题)
- 第一次登录或上一场完成 / 点 Reset → 出 setup,而不再自动新建 session
- 字段用 `/api/me` 预填,Start 时 PATCH 更新 + POST 新 session(带 prefs)
- 主题下拉从 `/api/topics` 动态加载

**验证**(throwaway 8001 跑了 7 个 curl 场景):signup → /api/me 含新字段 → /api/topics 列出 13 个主题 → PATCH 设 prefs → POST 新 session 继承 prefs → 带 body POST 覆盖 → 错误值 400 全过。

---

## ⚠️ 结构纠错(用户反馈"10 题 Part 1 你疯了吗")
真实雅思:**Intro → Part 1 选 1 个主题 × 3-4 题 → Part 2 cue → Part 3 延伸**。
我之前把 Part 1 分成 2-3 frame 是过度设计。
回到:
- `PART1_QUESTIONS = 4`(单主题,4 题)
- 删 `_pick_part1_frames`,回到 `_pick_part1(sid, override)`
- `MANDATORY_P1_FRAMES` 留着(work_studies / hometown_home 仍是 bank 里两个有效主题,但不再强制必出)
- `phase_hint` Part 1 简化:同一主题 4 题,中段 / 终问都鼓励先 ack 再问
- Modelfile 同步,已 `ollama create` 重建

🔄 同时启动 **deep-research workflow**(扇出搜索 + 多源核查 + 合成)爬当下 2024-2026 真实 IELTS Speaking 题库,完成后会用真实题目重建 `PART1_BANK` / `PART2_BANK` / `PART3_THEMES`。Workflow id: `wf_1e72816b-710`,可在 `/workflows` 看进度。

**Workflow 已完成**:110 个 agents / 563 工具调用 / 27 源 / 95 断言 / 16 confirmed / 9 refuted。已整套替换 bank:
- `PART1_BANK` 15 个高频主题 × 4 verbatim Cambridge 风格题(work_study / hometown / home_accommodation / food / fruit / sleep / museums / walking / weather / music / weekends / shopping / photos / friends / technology)
- `PART2_BANK` 12 张 cue card(person_admire / memorable_journey / useful_skill / changed_plan / book_read / film_again / foreign_country / important_decision / place_to_spend_time / satisfying_work / food_prepared / good_law)
- `PART3_THEMES` 12 套对应延伸题,每套 2 sub-theme × 3 题
- 每张 cue card 的 p3_key 都跟 PART3_THEMES 字典 key 对齐(无悬挂)
- Cambridge 18 直接 verbatim:fruit / sleep / museums / international food / good_law / food_prepared
- 其余来自 IELTS Liz / Keith Speaking / Cambridge 19/20 二次源,canonical 格式

---

## ✅ A++ · 评分换 14B 模型 + 考官接得住考生话
**模型分流**:
- 拉了 `qwen2.5:14b-instruct-q3_K_M`(7.3 GB,装到 F:)
- `webapp.py` 加 `FEEDBACK_MODEL_NAME` 配置 + `_model_available()` 带 60s 缓存
- `/api/chat` 仅在 `label=="feedback"` 时用 14B(`num_ctx=12288`、`temperature=0.3`);7B 不可用时自动降级回 `ielts-examiner`
- 反馈 payload 改为聚焦 `[system+transcript, user("now produce report")]`,避免把整个 history 重发一遍

**反馈 hint 升级**:
- 新增 `_full_transcript(history)`:压缩成 `CANDIDATE: ... / EXAMINER: ...` 行,塞进 hint 顶端(尾部 6000 字符)
- 重写 `_band_anchored_feedback_hint(stats, history, target_band)`:把全转录 + 量化信号 + band 阈值表 + 严格输出模板全部一次性塞进去
- 强制每条"主要问题"必须是真实考生原句(verbatim),改写要语义贴近但 band 更高
- Overall 计算公式写死:`round((F&C+Lex+Gram+Pron)/4*2)/2`,避免随便加权

**考官接住考生话**(解决"不会根据考生的问题来变换思想"):
- Part 1 中段 / 终问 hint 现允许 `≤1 句简短 acknowledgment`(回引考生提到的具体细节,如 "You said you work in marketing —")
- Part 3 中段 hint 改为"应当"先呼应考生上一句再问下一个,或用一次 "Why do you think that is?" 反问

**环境**:`IELTS_FEEDBACK_MODEL` 环境变量可指向其他模型(如 `qwen2.5:14b` 默认 q4,或 `qwen2.5:32b` 如果以后有更大盘)

---

## ✅ A+ · 题量与评分校准(根据反馈"问题太少 + 评分不太对")
**问题量**:
- `PART1_QUESTIONS = 10`(3 frame:4+3+3)+ `PART3_QUESTIONS = 5`(2 子主题:3+2)
- 新增 `MANDATORY_P1_FRAMES = ("work_studies", "hometown_home")` — Frame 1 永远从这俩抽,匹配真题"Cambridge 开场必问 work 或 home"
- `_pick_part1_frames(sid, override)` 返回 3 个 frame 元组;hint 把 n=1-4 / 5-7 / 8-10 映射到对应 frame + focus
- Part 3 hint 把 n=1-3 / 4-5 映射到子主题 0 / 1,子主题各 3 / 2 个 focus

**评分校准**(关键):
- `_candidate_stats` 现在算 **vocab_diversity (TTR)** + **discourse_markers 数** + **avg_sentence_words** 加原有词数
- 新函数 `_band_anchored_feedback_hint(stats, target_band)`:把每个量化信号映射到具体 band 阈值,塞进 hint。例如:
  - `avg words/turn < 15 → F&C 5.0; 15-25 → 5.5-6.0; 25-40 → 6.5-7.0; ...`
  - `TTR < 0.40 → Lex 5.0-5.5; 0.40-0.50 → 6.0-6.5; ...`
  - `discourse markers 0-1 → F&C 5.0-5.5; 2-4 → 6.0-6.5; ...`
  - `avg sentence words < 7 → Gram 5.0; ...`
- 强制要求"主要问题"里必须引用真实考生句子(原句:"..." → 改写:"...")
- 反馈 hint 同时附最长 / 最短答案原文,模型直接抓素材

**Modelfile**:Part 1 段落 + Part 3 段落同步改为新节奏,已 `ollama create` 重建。

---

## ✅ B2 · Part 2 双计时器
**只前端**(`index.html`):
- cue card 检测到时(`isCueCardText` 触发)自动在 cue 气泡下方插一条计时条
- Phase 1:60 秒准备(进度条 + 数字倒计时,30s 黄、10s 红),按"开始说"立即跳转
- Phase 2:120 秒长答(进度条同样配色),按"完成"提前结束;到 0 显示"时间到"
- 多重防御:`streamExaminer` 开头、`restoreLog`、`resetBtn` 都会 `stopCueTimer()`
- i18n:中英 `cue_timer.*` 5 个 key

**验证**:HTML 现有 15 处 `cue_timer.*` key、46 处 `data-i18n`,服务端 compile 通过。

---

