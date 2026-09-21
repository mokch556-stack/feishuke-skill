# feishuke-skill 飞书课堂手册制作技能

依据教案生成**飞书课堂手册**（师生共用课堂引导文档、可投屏替代授课 PPT），覆盖 DocxXML 源稿生成 → 思政图 file_token 嵌入 → 覆盖写入飞书 doc → 线上核验全流程。

## 定位

- 师生共用、学生活动视角、可投屏；不是备课专用、不是 8 区学生手册。
- 教案（docx）= 唯一内容权威：时间口径、平台、分值归属全部照教案，禁编造。
- 结构标杆：**v1.2 版式**＝芳姐 2026-09-21 手改的第3讲线上手册（`references/线上手改版_第3次课_20260921.xml`）；`templates/manual_lesson*_sample.xml` 为 v1.2 同结构成品样板。

## 使用

读 `SKILL.md`（含结构规范/时间口径铁律/DocxXML 标签与命令/工作流 A·B/核验清单）。

```bash
# 校验 XML 源稿结构（默认 v1.2 口径：h2=3、无总览表、末 h3=课堂总结、checkbox≤3）
python scripts/verify_manual.py --dir templates
python scripts/verify_manual.py manual_lessonN.xml
python scripts/verify_manual.py manual_lessonN.xml --profile v101   # 查历史旧版式稿
python scripts/verify_manual.py live_doc.xml --img-mode any          # 线上版含大量截图时
```

## 目录

```
SKILL.md                          ← 技能说明（唯一规范真身）
templates/manual_lessonN_sample.xml  ← v1.2 成品 XML 样板（真实内容，可作样例/夹具）
references/线上手改版_第3次课_20260921.xml  ← v1.2 版式来源（芳姐手改线上版整稿）
references/v101_old_templates/     ← v1.0.1 旧版式模板（含总览表，仅存档）
scripts/verify_manual.py          ← XML 结构校验器（默认 v1.2；--profile v101 查旧稿）
.cicd/config.json                 ← CI/CD 参数（gen_cicd.py 生成）
.github/workflows/ci.yml          ← 远端 QA（gen_cicd.py 生成）
```

## 版本

- v1.2（2026-09-21）：芳姐确认三项版式改动（取消总览表／不设后测／不列作业清单）→ 进正式规范，校验器默认口径同步；据此改造第 4–6 讲线上手册。
- v1.1（2026-09-21）：对齐芳姐手改第3讲线上版式（h4/blockquote/grid/sheet/pre/a、标题三行、互动 callout 化、文字精简）。
- v1.0.0（2026-09-06）：依据第2次课手册 v1→v7 全部迭代教训 + 第3–6次课批量线上验证沉淀。

## 技能包 CI/CD

统一框架见 skill-cicd（skills/skill-cicd）：本地 QA 门禁 + 30 分钟自动同步 + GitHub Actions 远端 CI。
仓库：github.com/mokch556-stack/feishuke-skill
