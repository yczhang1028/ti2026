#!/usr/bin/env python3
"""TI2026 战报公众号文章 v2 — 正文不放网址, 网址放「阅读原文」"""
import sys, json, urllib.request
sys.path.insert(0, "/home/ubuntu/.wechat")
import wechat_mp as w

URL = "https://ti2026.knownothing.dpdns.org/"
OLD_DRAFT = "_Tf6z4DGOPmab9XoA0cg1xWk0k4U9-m5g8M4fy3OycXY_O8OFwYYUToKeVif8Fff"
OLD_THUMB = "_Tf6z4DGOPmab9XoA0cg1wiXzeeaaour6KMcix6CjN62jEBXrNysbAbNg-O7VRhX"

# ---- 正文 (无网址, 结尾引导阅读原文) ----
body = f"""
<p>小组赛开打了，你大概也遇到了这个情况：想看积分榜，Liquipedia 半天刷不开；想知道中国队咋样了，还得一条条翻赛程；想看看谁是版本之子，英雄数据藏在一堆表格里。</p>

<p>折腾一圈，时间全花在找数据上了。</p>

<p>所以我做了个东西：一个页面，把 TI2026 上海小组赛的战报全装进去，每天自动更新。</p>

<h2 style="font-size:18px;color:#d97706;">积分榜一眼看穿</h2>

<p>不是那种「大分 - 小分」两列的干巴表格。是 Liquipedia 同款的横向对阵表——每支队一行，右边横着列出每一轮打了谁、比分多少，赢的绿色、输的红色。谁在连胜、谁快淘汰，扫一眼就知道。</p>

<p>首日打完，<strong>Iron Wing 和 BoomBoys 2-0 领跑</strong>，Nigma、OG 0-2 垫底，已经站在悬崖边。</p>

<h2 style="font-size:18px;color:#d97706;">中国队单独拎出来</h2>

<p>XG、VG、TR 三支中国战队，专门有个板块盯着。每个选手的 KDA、场均击杀、GPM、补刀、场均伤害，五个数字一张卡。首轮三队都没取大分，明天是抢分局——VG 碰 Liquid，XG 撞 Spirit，都是硬仗。</p>

<h2 style="font-size:18px;color:#d97706;">选手榜 + 英雄榜</h2>

<p>场均击杀 TOP3、KDA TOP3，谁在 C 谁在躺，队标名字写得清清楚楚。还加了个英雄 Ban/Pick 榜——这版本哪些英雄非 Ban 必选、哪些是版本陷阱，数据说话。</p>

<h2 style="font-size:18px;color:#d97706;">点一下，还有更多</h2>

<p>页面不是死的。点任意战队名，弹出它整套阵容的选手数据；点对阵卡片，弹出双方比分详情；每个板块标题都能折叠，想聚焦哪块就点开哪块。</p>

<p>每天上午八点半自动抓数据、自动更新，你只管打开看。</p>

<p>追比赛，别把时间花在找数据上。</p>

<p>想看完整战报，点左下角「阅读原文」。</p>
"""

article = {
    "title": "TI2026 战报，一个页面全看齐",
    "author": "KNOWNOTHING",
    "digest": "积分榜、中国队、选手英雄数据，每天自动更新，一个页面全装下。",
    "content": body,
    "content_source_url": URL,
    "thumb_media_id": OLD_THUMB,
    "need_open_comment": 0,
    "only_fans_can_comment": 0,
}

# 1. 删除旧草稿
tok = w.get_token()
del_url = f"https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={tok}"
try:
    req = urllib.request.Request(del_url, data=json.dumps({"media_id": OLD_DRAFT}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    print("删除旧草稿:", resp)
except Exception as ex:
    print("删除旧草稿失败(忽略):", ex)

# 2. 建新草稿 (正文无网址, 复用封面)
media_id = w.add_draft([article])
print("新草稿 media_id:", media_id)
print("DONE")
