# feishuke-skill 飞书课堂手册制作技能

依据教案生成**飞书课堂手册**（师生共用课堂引导文档、可投屏替代授课 PPT），覆盖 DocxXML 源稿生成 → 思政图 file_token 嵌入 → 覆盖写入飞书 doc → 线上核验全流程。

## 定位

- 师生共用、学生活动视角、可投屏；不是备课专用、不是 8 区学生手册。
- 教案（docx）= 唯一内容权威：时间口径、平台、分值归属全部照教案，禁编造。
- 结构标杆：《人工智能通识》第2次课 v7 手册；`templates/manual_lesson3–6_sample.xml` 为同结构成品样板。

## 使用

读 `SKILL.md`（含结构规范/时间口径铁律/DocxXML 标签与命令/工作流 A·B/核验清单）。

```bash
# 校验 XML 源稿结构
python scripts/verify_manual.py --dir templates
python scripts/verify_manual.py manual_lessonN.xml
```

## 目录

```
SKILL.md                          ← 技能说明（唯一规范真身）
templates/manual_lessonN_sample.xml  ← 成品 XML 样板（真实内容，可作样例/夹具）
scripts/verify_manual.py          ← XML 结构校验器（h2/h3 编号/总览时间轴/img/游离&）
.cicd/config.json                 ← CI/CD 参数（gen_cicd.py 生成）
.github/workflows/ci.yml          ← 远端 QA（gen_cicd.py 生成）
```

## 版本

- v1.0.0（2026-09-06）：依据第2次课手册 v1→v7 全部迭代教训 + 第3–6次课批量线上验证沉淀。

## 技能包 CI/CD

统一框架见 skill-cicd（skills/skill-cicd）：本地 QA 门禁 + 30 分钟自动同步 + GitHub Actions 远端 CI。
仓库：github.com/mokch556-stack/feishuke-skill
