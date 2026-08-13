#!/usr/bin/env python3
"""TI2026 战报 -> 公众号文章 (跟网页同款数据, 表格版)
队标+英雄图标内联图片, 深色电竞风 table。"""
import sys, json, os, time, urllib.request, re
sys.path.insert(0, "/home/ubuntu/.wechat")
import wechat_mp as w

BASE = "/home/ubuntu/hermes_share/ti2026"
d = json.load(open(f"{BASE}/data.json"))

URL = "https://ti2026.knownothing.dpdns.org/"

# 配色
BG = "#0d1226"; CARD = "#131a33"; GOLD = "#d4a53c"; GOLD2 = "#f5c04a"
TXT = "#e2e8f0"; DIM = "#8a94ad"; GREEN = "#3ddc97"; RED = "#ff4d5e"
CYAN = "#38e0d0"; BORDER = "#26304d"

CN_TEAMS = {"Xtreme Gaming": "XG", "Vici Gaming": "VG", "Team Resilience": "TR"}
def cn(t): return CN_TEAMS.get(t, t)

def kda(s):
    dd = s["deaths"] or 1
    return (s["kills"] + s["assists"]) / dd

# ---------- 1. 下载英雄图标 ----------
def hero_short_list():
    hs = d.get("hero_stats", [])
    top_pick = sorted(hs, key=lambda x: -x["pick"])[:6]
    top_ban = sorted(hs, key=lambda x: -x["ban"])[:6]
    seen = {}
    for h in top_pick + top_ban:
        seen[h["short"]] = h
    return list(seen.values())

def dl_hero_icon(short, out):
    url = f"https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/{short}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        open(out, "wb").write(data)
        return True
    except Exception as e:
        print(f"  英雄图标下载失败 {short}: {e}")
        return False

hero_list = hero_short_list()
os.makedirs(f"{BASE}/hero_icons", exist_ok=True)
hero_icon_files = {}
for h in hero_list:
    fp = f"{BASE}/hero_icons/{h['short']}.png"
    if not os.path.exists(fp):
        dl_hero_icon(h["short"], fp)
    if os.path.exists(fp):
        hero_icon_files[h["short"]] = fp

print(f"英雄图标 {len(hero_icon_files)} 个")

# ---------- 2. 上传所有图片 ----------
def upload(path):
    try:
        return w.upload_content_image(path)
    except Exception as e:
        print(f"  上传失败 {path}: {e}")
        return ""

# 队标
logo_urls = {}
for fn in os.listdir(f"{BASE}/logos"):
    if fn.endswith(".png"):
        logo_urls[fn] = upload(f"{BASE}/logos/{fn}")
        time.sleep(0.5)
print(f"队标上传 {sum(1 for v in logo_urls.values() if v)} / {len(logo_urls)}")

# 英雄图标
hero_urls = {}
for short, fp in hero_icon_files.items():
    hero_urls[short] = upload(fp)
    time.sleep(0.5)
print(f"英雄图标上传 {sum(1 for v in hero_urls.values() if v)} / {len(hero_urls)}")

def logo_img(fn, size=28):
    u = logo_urls.get(fn, "")
    if u:
        return f'<img src="{u}" style="width:{size}px;height:{size}px;object-fit:contain;vertical-align:middle;border-radius:4px;" />'
    return ""

# ---------- 3. 渲染 HTML ----------
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md2html(md):
    """markdown -> 公众号允许的 HTML"""
    out = []
    for line in md.split("\n"):
        line = line.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            out.append(f'<h2 style="font-size:17px;color:{GOLD2};margin:18px 0 8px;border-left:3px solid {GOLD};padding-left:10px;">{esc(line[4:])}</h2>')
        elif line.startswith("## "):
            out.append(f'<h2 style="font-size:18px;color:{GOLD2};margin:18px 0 8px;border-left:3px solid {GOLD};padding-left:10px;">{esc(line[3:])}</h2>')
        elif line.startswith("- "):
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(line[2:]))
            out.append(f'<p style="margin:4px 0;color:{TXT};font-size:14px;line-height:1.7;">· {t}</p>')
        else:
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(line))
            out.append(f'<p style="margin:4px 0;color:{TXT};font-size:14px;line-height:1.7;">{t}</p>')
    return "".join(out)

# --- 领跑队伍 ---
def leader_card(rank, s, medal):
    color = {1: GOLD2, 2: "#c0c8dc", 3: "#c98a4b"}[rank]
    return f'''
<td style="background:{CARD};border:1px solid {BORDER};border-radius:10px;padding:10px;width:33%;text-align:center;vertical-align:top;">
  <p style="margin:0;font-size:22px;">{medal}</p>
  <p style="margin:6px 0;">{logo_img(s["logo_file"], 40)}</p>
  <p style="margin:2px 0;color:{TXT};font-weight:bold;font-size:14px;">{esc(cn(s["team"]))}{" 🇨🇳" if s["team"] in CN_TEAMS else ""}</p>
  <p style="margin:2px 0;color:{GOLD};font-size:13px;">{esc(s["match"])} / {esc(s["game"])}</p>
</td>'''

# 领跑 = 排名前3 (按 rank 排序后取前3不同队)
st_sorted = sorted(d["standings"], key=lambda s: s["rank"])
leaders = st_sorted[:3]
medals = ["🥇", "🥈", "🥉"]
leaders_html = ""
if len(leaders) == 3:
    leaders_html = f'<table style="width:100%;border-collapse:separate;border-spacing:4px;margin:6px 0;"><tr>' + \
        "".join(leader_card(i+1, s, medals[i]) for i, s in enumerate(leaders)) + "</tr></table>"

# --- 积分榜 Swiss 对阵表 ---
rounds = d["cross"].get("rounds", [])
cross_table = d["cross"].get("table", {})

def cross_cell(team, rnd):
    cell = cross_table.get(team, {}).get(rnd)
    if not cell:
        return '<td style="padding:6px 8px;text-align:center;color:{DIM};font-size:12px;">—</td>'.format(DIM=DIM)
    opp = cell.get("opp", "")
    my = cell.get("my", 0); op = cell.get("op", 0)
    fin = cell.get("fin", False)
    if not fin:
        col = DIM
        txt = esc(cn(opp))
    elif my > op:
        col = GREEN
        txt = f"{esc(cn(opp))} {my}-{op}"
    elif my < op:
        col = RED
        txt = f"{esc(cn(opp))} {my}-{op}"
    else:
        col = GOLD
        txt = f"{esc(cn(opp))} {my}-{op}"
    return f'<td style="padding:6px 8px;text-align:center;color:{col};font-size:12px;">{txt}</td>'

def standings_rows():
    rows = ""
    for s in st_sorted:
        mw, ml = (s["match"].split("-") + ["0"])[:2]
        gw, gl = (s["game"].split("-") + ["0"])[:2]
        cn_flag = " 🇨🇳" if s["team"] in CN_TEAMS else ""
        teamcell = f'<span style="color:{TXT};font-weight:600;font-size:13px;">{logo_img(s["logo_file"], 22)} {esc(cn(s["team"]))}{cn_flag}</span>'
        row = f'<tr>'
        row += f'<td style="padding:5px 6px;text-align:center;color:{DIM};font-size:12px;width:26px;">{s["rank"]}</td>'
        row += f'<td style="padding:5px 6px;text-align:left;">{teamcell}</td>'
        row += f'<td style="padding:5px 6px;text-align:center;color:{GOLD};font-weight:bold;font-size:13px;">{esc(s["match"])}</td>'
        row += f'<td style="padding:5px 6px;text-align:center;color:{DIM};font-size:13px;">{esc(s["game"])}</td>'
        for rnd in rounds:
            row += cross_cell(s["team"], rnd)
        row += "</tr>"
        rows += row
    return rows

header_cols = f'<th style="padding:6px;color:{GOLD};font-size:12px;border-bottom:1px solid {BORDER};">#</th>'
header_cols += f'<th style="padding:6px;color:{GOLD};font-size:12px;border-bottom:1px solid {BORDER};text-align:left;">战队</th>'
header_cols += f'<th style="padding:6px;color:{GOLD};font-size:12px;border-bottom:1px solid {BORDER};">大分</th>'
header_cols += f'<th style="padding:6px;color:{GOLD};font-size:12px;border-bottom:1px solid {BORDER};">小分</th>'
for rnd in rounds:
    short_rnd = rnd.replace("Round ", "R")
    header_cols += f'<th style="padding:6px;color:{GOLD};font-size:12px;border-bottom:1px solid {BORDER};">{esc(short_rnd)}</th>'

standings_html = f'''
<table style="width:100%;border-collapse:collapse;background:{BG};margin:6px 0;">
<thead><tr>{header_cols}</tr></thead>
<tbody>{standings_rows()}</tbody>
</table>'''

# --- 今日赛程 ---
def match_rows():
    rows = ""
    for m in d.get("today", []):
        t = m.get("date_raw", "")
        hhmm = ""
        if " - " in t:
            hhmm = t.split(" - ")[1].split(" ")[0]
        fin = m.get("finished", False)
        if fin:
            center = f'<span style="color:{GOLD};font-weight:bold;font-size:15px;">{m["t1_score"]} : {m["t2_score"]}</span>'
        else:
            center = f'<span style="color:{DIM};font-size:13px;">VS · {esc(hhmm)}</span>'
        c1 = " 🇨🇳" if m["t1"] in CN_TEAMS else ""
        c2 = " 🇨🇳" if m["t2"] in CN_TEAMS else ""
        row = f'<tr>'
        row += f'<td style="padding:7px 6px;text-align:right;width:40%;color:{TXT};font-size:13px;">{esc(cn(m["t1"]))}{c1} {logo_img(m.get("logo1",""), 22)}</td>'
        row += f'<td style="padding:7px 6px;text-align:center;width:20%;">{center}</td>'
        row += f'<td style="padding:7px 6px;text-align:left;width:40%;color:{TXT};font-size:13px;">{logo_img(m.get("logo2",""), 22)} {esc(cn(m["t2"]))}{c2}</td>'
        row += "</tr>"
        rows += row
    return rows

schedule_html = f'''
<table style="width:100%;border-collapse:collapse;background:{BG};margin:6px 0;">
<tbody>{match_rows()}</tbody>
</table>'''

# --- 形势分析 ---
analysis_html = md2html(d.get("analysis", ""))

# --- 选手榜 TOP3 ---
def player_top(kind):
    ps = [s for s in d["player_stats"].values() if s["games"] >= 2]
    if kind == "kill":
        ps = sorted(ps, key=lambda s: -s["kills"]/s["games"])[:3]
        def val(s): return f'{s["kills"]/s["games"]:.1f}'
        unit = "K"
    else:
        ps = sorted(ps, key=lambda s: -kda(s))[:3]
        def val(s): return f'{kda(s):.1f}'
        unit = ""
    rows = ""
    for i, s in enumerate(ps):
        team = s["team"]
        lf = ""
        for st in st_sorted:
            if st["team"] == team:
                lf = st["logo_file"]; break
        rows += f'<tr><td style="padding:6px 8px;color:{DIM};font-size:12px;width:24px;">{i+1}</td>' \
                f'<td style="padding:6px 8px;color:{TXT};font-size:13px;">{logo_img(lf, 22)} {esc(s["name"])} <span style="color:{DIM};font-size:11px;">{esc(cn(team))}</span></td>' \
                f'<td style="padding:6px 8px;text-align:right;color:{GOLD};font-weight:bold;font-size:14px;">{val(s)}{unit}</td></tr>'
    return f'<table style="width:100%;border-collapse:collapse;background:{BG};margin:6px 0;"><tbody>{rows}</tbody></table>'

kill_top = player_top("kill")
kda_top = player_top("kda")

# --- 中国选手 ---
def cn_players():
    PLAYER_ALIAS = {"ysr-04e": "erika", "echozz": "echo"}
    def is_cn(name):
        k = name.lower().strip()
        k = PLAYER_ALIAS.get(k, k)
        CN_ROSTER = {"ame","nothingtosay","xxs","fy","xnova","shiro","xm","bach","xinq","y`","erika","echo","niu","planet","zzq"}
        return k in CN_ROSTER
    def team_of(name):
        k = name.lower().strip()
        k = PLAYER_ALIAS.get(k, k)
        for t, plist in CN_TEAMS.items():
            pass
        # 简化: 用 player_stats 里的 team 字段
        return None
    ps = [s for s in d["player_stats"].values() if is_cn(s["name"])]
    ps = sorted(ps, key=lambda s: -kda(s))
    rows = ""
    for s in ps:
        team = s["team"]
        lf = ""
        for st in st_sorted:
            if st["team"] == team:
                lf = st["logo_file"]; break
        tag = f'<span style="background:{GOLD};color:#1a1a1a;font-size:10px;padding:1px 5px;border-radius:3px;font-weight:bold;">[{cn(team)}]</span>'
        g = s["games"]
        rows += f'<tr>'
        rows += f'<td style="padding:7px 6px;color:{TXT};font-size:13px;">{tag} {logo_img(lf, 20)} <strong>{esc(s["name"])}</strong></td>'
        rows += f'<td style="padding:7px 6px;text-align:center;color:{GOLD};font-weight:bold;font-size:13px;">KDA {kda(s):.1f}</td>'
        rows += f'<td style="padding:7px 6px;text-align:center;color:{TXT};font-size:12px;">{s["kills"]}/{s["deaths"]}/{s["assists"]}</td>'
        rows += f'<td style="padding:7px 6px;text-align:center;color:{DIM};font-size:12px;">{g}局</td>'
        rows += "</tr>"
    return f'<table style="width:100%;border-collapse:collapse;background:{BG};margin:6px 0;"><tbody>{rows}</tbody></table>'

cn_html = cn_players()

# --- 英雄 Ban/Pick ---
def hero_section():
    hs = d.get("hero_stats", [])
    top_pick = sorted(hs, key=lambda x: -x["pick"])[:6]
    top_ban = sorted(hs, key=lambda x: -x["ban"])[:6]
    max_pick = top_pick[0]["pick"] if top_pick else 1
    max_ban = top_ban[0]["ban"] if top_ban else 1
    def hero_rows(list_, kind, mx):
        rows = ""
        for h in list_:
            icon = hero_urls.get(h["short"], "")
            ic = f'<img src="{icon}" style="width:26px;height:26px;border-radius:5px;vertical-align:middle;" />' if icon else ""
            if kind == "pick":
                wr = h["winrate"]
                col = GREEN if wr >= 60 else (GOLD if wr >= 45 else RED)
                right = f'<span style="color:{col};font-weight:bold;font-size:12px;">{wr}%</span>'
                num = f'<span style="color:{GOLD};font-weight:bold;font-size:12px;">{h["pick"]}次</span>'
            else:
                right = f'<span style="color:{CYAN};font-size:11px;">ban</span>'
                num = f'<span style="color:{RED};font-weight:bold;font-size:12px;">{h["ban"]}次</span>'
            bar_w = int((h["pick"] if kind=="pick" else h["ban"]) / mx * 100)
            bar = f'<span style="display:inline-block;height:3px;background:linear-gradient(90deg,{GOLD},{CYAN});width:{bar_w}px;border-radius:2px;vertical-align:middle;"></span>'
            rows += f'<tr><td style="padding:5px 6px;">{ic}</td>' \
                    f'<td style="padding:5px 6px;color:{TXT};font-size:13px;">{esc(h["name"])}</td>' \
                    f'<td style="padding:5px 6px;text-align:right;">{num}</td>' \
                    f'<td style="padding:5px 6px;text-align:right;width:52px;">{right}</td></tr>'
        return rows
    return f'''
<table style="width:100%;border-collapse:collapse;background:{BG};margin:6px 0;">
<tbody><tr>
<td style="width:50%;vertical-align:top;padding:4px;">
<p style="margin:4px 0;color:{CYAN};font-weight:bold;font-size:13px;">🔥 热门 Pick</p>
<table style="width:100%;border-collapse:collapse;"><tbody>{hero_rows(top_pick, "pick", max_pick)}</tbody></table>
</td>
<td style="width:50%;vertical-align:top;padding:4px;">
<p style="margin:4px 0;color:{CYAN};font-weight:bold;font-size:13px;">🚫 热门 Ban</p>
<table style="width:100%;border-collapse:collapse;"><tbody>{hero_rows(top_ban, "ban", max_ban)}</tbody></table>
</td>
</tr></tbody></table>'''

hero_html = hero_section()

# ---------- 4. 组装正文 ----------
def sec(title, num, inner):
    return f'''
<h2 style="font-size:17px;color:{GOLD2};margin:22px 0 8px;border-left:3px solid {GOLD};padding-left:10px;">{num} {title}</h2>
{inner}
'''

body = f'''
<p style="color:{DIM};font-size:13px;margin:0 0 12px;">TI2026 · 上海 · 小组赛 8/13-8/16 · 数据每日 8:30 自动更新</p>
{sec("积分榜 · Swiss 对阵", "01", leaders_html + standings_html)}
{sec("今日赛程", "02", schedule_html)}
{sec("形势分析", "03", analysis_html)}
{sec("英雄 Ban/Pick", "04", hero_html)}
{sec("场均击杀 TOP3", "05", kill_top)}
{sec("KDA TOP3", "06", kda_top)}
{sec("中国选手状态", "07", cn_html)}
<p style="color:{DIM};font-size:12px;margin-top:20px;text-align:center;">完整交互版（折叠/弹窗/选手详情）点「阅读原文」</p>
'''

article = {
    "title": "TI2026 小组赛战报",
    "author": "KNOWNOTHING",
    "digest": "积分榜 · 赛程 · 选手英雄数据，每日更新",
    "content": body,
    "content_source_url": URL,
    "thumb_media_id": "",
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

# ---------- 5. 封面 + 建草稿 ----------
thumb_id = w.upload_thumb(f"{BASE}/cover_ti2026.png")
print("封面:", thumb_id)
article["thumb_media_id"] = thumb_id

media_id = w.add_draft([article])
print("草稿 media_id:", media_id)
print("DONE")
