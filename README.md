# Tavily Search Toolkit for OpenClaw

A practical Tavily skill for OpenClaw with **search / extract / crawl / map** in one script.

一个面向 OpenClaw 的 Tavily 实用技能包，统一支持 **search / extract / crawl / map**。

Only **1 step** to start: send one prompt to OpenClaw, then follow guided onboarding.

只要 **1 步**就能开始：把下面提示词发给 OpenClaw，后续按引导完成配置。

```text
Install the Tavily Search skill from GitHub into my OpenClaw workspace skills directory (NOT .agents).

Requirements:
1) Target directory must be: ~/.openclaw/workspace/skills/tavily-search
2) Clone source: https://github.com/plabzzxx/openclaw-tavily-search
3) Ensure script exists at: ~/.openclaw/workspace/skills/tavily-search/scripts/tavily_search.mjs
4) Create ~/.openclaw/.env if missing, and ensure this placeholder line exists:
   TAVILY_API_KEY=
5) Return a short verification report with absolute paths and whether each step succeeded.
6) Add a memory preference:
   - When web_search (Brave) is unavailable, use tavily-search skill first.
   - For general web lookup tasks, try tavily-search before giving up.
7) Stop here and ask the user:
   "Tavily skill is installed. Do you want guided setup for Tavily API key now?"
8) Read and follow onboarding playbook in this repo:
   ONBOARDING.md
```

---

## 新手可以忽略以下内容 / Beginners can ignore the section below

## Step 1: Install / 安装（手动）

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/plabzzxx/openclaw-tavily-search tavily-search
```

## Step 2: Setup API Key / 配置 API Key

- Tavily key page / 申请地址: https://tavily.com
- Put key in / 写入本地：`~/.openclaw/.env`

```env
TAVILY_API_KEY=tvly-xxxx
```

Manual local edit is safer than sending secrets in chat.

本地手动编辑通常比在聊天中传递密钥更安全。

## CLI examples / 命令示例

```bash
# Search (brave-like output)
node scripts/tavily_search.mjs search --query "OpenClaw" --max-results 5 --format brave

# Search with include/exclude domains
node scripts/tavily_search.mjs search --query "周大福" \
  --include-domains ctf.com.cn,ctfmall.com,chowtaifook.com \
  --exclude-domains facebook.com,weibo.com --format brave

# Extract content from URLs
node scripts/tavily_search.mjs extract --urls https://docs.openclaw.ai --content-format markdown --format md

# Crawl / Map
node scripts/tavily_search.mjs crawl --url docs.tavily.com --max-depth 2 --limit 30 --format md
node scripts/tavily_search.mjs map --url docs.openclaw.ai --max-depth 2 --limit 40 --format md
```
