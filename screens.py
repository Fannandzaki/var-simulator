"""
screens.py — All game screens (Video Version with Randomization)
"""
import os
import random
import math
import pygame
from constants import *
from video_player import VideoPlayer
from renderer import bresenham

def draw_text(surf, text, font, color, cx, cy):
    s = font.render(text, True, color)
    surf.blit(s, s.get_rect(center=(cx, cy)))

def fill_rect(surf, rect, fill, border=None, radius=4, bw=1):
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surf, border, rect, bw, border_radius=radius)

def scanlines(surf):
    for y in range(0, surf.get_height(), 4):
        pygame.draw.line(surf, (14,14,22), (0,y), (surf.get_width(),y))

# ── INTRO ────────────────────────────────────────────────────────────────────
class IntroScreen:
    def __init__(self, fonts):
        self.F = fonts
        self.t = 0
        self.blink = True; self.blink_t = 0
        self.btn = pygame.Rect(WIN_W//2-140, 460, 280, 50)
        self.anim = pygame.Surface((340,200))

    def handle(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and self.btn.collidepoint(ev.pos):
            return "levels"
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
            return "levels"

    def update(self):
        self.t += 1
        self.blink_t += 1
        if self.blink_t > 28: self.blink = not self.blink; self.blink_t = 0

    def draw(self, surf):
        surf.fill(INK); scanlines(surf)
        cx = WIN_W//2; F = self.F
        draw_text(surf,"GRAFIKA KOMPUTER · FINAL PROJECT 2025",F["tiny"],GREY,cx,36)
        draw_text(surf,"VAR",F["big"],AMBER,cx,105)
        draw_text(surf,"VIDEO ASSISTANT REFEREE",F["mono"],GREEN,cx,155)

        self._draw_anim()
        fx = cx-170
        fill_rect(surf,pygame.Rect(fx-2,174,344,204),(14,30,14),(42,74,42),6)
        surf.blit(self.anim,(fx,176))

        draw_text(surf,"Jadilah wasit VAR di Video Operation Room.",F["body"],GREY,cx,400)
        draw_text(surf,"Analisis tayangan ulang & buat keputusan!",F["body"],GREY,cx,422)

        if self.blink:
            fill_rect(surf,self.btn,INK,AMBER,4)
            draw_text(surf,"► MULAI SEKARANG",F["press"],AMBER,cx,485)
        draw_text(surf,"Kelompok Grafkom · Simulator VAR · 2025",F["tiny"],GREY,cx,560)

    def _draw_anim(self):
        s = self.anim; t = self.t
        IW,IH = 340,200
        s.fill((20,84,20))
        for i in range(5):
            cl = pygame.Surface((68,IH),pygame.SRCALPHA)
            cl.fill((0,0,0,18) if i%2 else (255,255,255,5))
            s.blit(cl,(i*68,0))
        pygame.draw.line(s,(255,255,255,100),(IW//2,0),(IW//2,IH),1)
        pygame.draw.circle(s,(255,255,255,100),(IW//2,IH//2),30,1)
        pygame.draw.rect(s,(255,255,255,100),(6,6,IW-12,IH-12),1)
        bx=IW//2+int(math.sin(t*.04)*80); by=IH//2+int(math.cos(t*.06)*40)
        pygame.draw.circle(s,WHITE,(bx,by),5)
        p1x=bx-22+int(math.sin(t*.03)*4); p1y=by-2+int(math.cos(t*.05)*3)
        pygame.draw.rect(s,(204,34,0),(p1x-5,p1y-4,10,16),border_radius=2)
        pygame.draw.circle(s,(245,192,154),(p1x,p1y-7),4)
        p2x=bx+28+int(math.cos(t*.025)*4); p2y=by+3+int(math.sin(t*.04)*3)
        pygame.draw.rect(s,(0,68,187),(p2x-5,p2y-4,10,16),border_radius=2)
        pygame.draw.circle(s,(245,192,154),(p2x,p2y-7),4)

# ── LEVEL SELECT ─────────────────────────────────────────────────────────────
class LevelSelectScreen:
    def __init__(self, fonts):
        self.F = fonts; self.hover = -1
        cw,ch,gap = 280,190,18
        total = 3*cw+2*gap; sx=(WIN_W-total)//2; sy=175
        self.cards = [pygame.Rect(sx+i*(cw+gap),sy,cw,ch) for i in range(3)]
        self.back  = pygame.Rect(20,16,90,28)

    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = next((i for i,r in enumerate(self.cards) if r.collidepoint(ev.pos)),-1)
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if self.back.collidepoint(ev.pos): return "intro"
            for i,r in enumerate(self.cards):
                if r.collidepoint(ev.pos): return i+1

    def update(self): pass

    def draw(self, surf):
        surf.fill(INK); scanlines(surf)
        F=self.F; cx=WIN_W//2
        fill_rect(surf,self.back,(10,10,20),BORDER,3)
        draw_text(surf,"◄ BACK",F["tiny"],GREY,self.back.centerx,self.back.centery)
        draw_text(surf,"PILIH KATEGORI",F["press"],AMBER,cx,96)
        draw_text(surf,"Sistem akan memilih video acak dari folder kategori",F["body"],GREY,cx,130)

        cols=[GREEN,AMBER,RED]
        for i,(r,lid) in enumerate(zip(self.cards,[1,2,3])):
            lv=LEVELS[lid]; col=cols[i]
            off=-5 if self.hover==i else 0
            rr=r.move(0,off)
            if self.hover==i:
                gl=pygame.Surface((rr.w+12,rr.h+12),pygame.SRCALPHA)
                pygame.draw.rect(gl,(*col,36),(0,0,rr.w+12,rr.h+12),border_radius=8)
                surf.blit(gl,(rr.x-6,rr.y-6))
            fill_rect(surf,rr,(12,12,24),col,6)
            fy=rr.y+12
            draw_text(surf,lv["icon"],F["icon"],WHITE,rr.centerx,fy+16)
            draw_text(surf,f"0{lid}",F["num"],col,rr.centerx,fy+54)
            bb=F["tiny"].render(lv["badge"],True,col)
            bsx=rr.centerx-bb.get_width()//2
            bg=pygame.Surface((bb.get_width()+10,bb.get_height()+4),pygame.SRCALPHA)
            bg.fill((*col,36)); surf.blit(bg,(bsx-5,fy+72)); surf.blit(bb,(bsx,fy+74))
            draw_text(surf,lv["name"],F["body"],(200,200,200),rr.centerx,fy+104)
            # wrap case text
            words=lv["case"].split(); lines=[]; cur=""
            for w in words:
                test=cur+" "+w if cur else w
                if F["tiny"].size(test)[0]<rr.w-16: cur=test
                else: lines.append(cur); cur=w
            if cur: lines.append(cur)
            for li,ln in enumerate(lines[:3]):
                draw_text(surf,ln,F["tiny"],GREY,rr.centerx,fy+124+li*15)

# ── GAME ─────────────────────────────────────────────────────────────────────
MON_X, MON_Y, MON_W, MON_H = 268, 58, 592, 370

class GameScreen:
    def __init__(self, fonts):
        self.F = fonts
        self.video = None
        self.lv_id = 1
        self.score_ok = 0; self.score_tot = 0
        self._reset_state()
        self._build_rects()
        self.line_overlay = pygame.Surface((MON_W, MON_H), pygame.SRCALPHA)

    def _reset_state(self):
        self.zoom_idx  = 0
        self.zoom      = ZOOM_LEVELS[0]
        self.draw_mode = False
        self.user_line = None
        self.drag_start= None
        self.dragging  = False
        self.decided   = False
        self.result    = None
        self.cam_sel   = 1
        self._next_btn = None
        self._restart_btn = None
        self.current_video_file = "Belum Ada Video"

    def _build_rects(self):
        sx,sy = MON_X, MON_Y+MON_H+14
        self.slider_rect  = pygame.Rect(sx, sy, MON_W, 10)
        self.slider_drag  = False
        by = sy+28; bh = 34
        self.btns = {
            "back":   pygame.Rect(8,10,80,24),
            "m10":    pygame.Rect(sx,    by, 75,  bh),
            "play":   pygame.Rect(sx+82, by, 100, bh),
            "p10":    pygame.Rect(sx+189,by, 75,  bh),
            "zm":     pygame.Rect(sx+280,by, 54,  bh),
            "zp":     pygame.Rect(sx+341,by, 54,  bh),
            "line":   pygame.Rect(sx+410,by, 100, bh),
        }
        dbx = MON_X+MON_W+18; dby0 = MON_Y; dbw,dbh = 192,52
        self.dec_btns=[{**d,"rect":pygame.Rect(dbx,dby0+i*(dbh+10),dbw,dbh)} for i,d in enumerate(DECISIONS)]
        self.left_rect = pygame.Rect(8, MON_Y, 252, MON_H)

    def boot(self, lv_id):
        self.lv_id = lv_id
        self._reset_state()
        lv = LEVELS[lv_id]
        
        # --- LOGIKA MEMILIH VIDEO RANDOM DARI FOLDER ---
        v_dir = lv.get("video_dir", "")
        selected_path = "assets/placeholder.mp4"
        
        if os.path.exists(v_dir):
            videos = [f for f in os.listdir(v_dir) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
            if videos:
                chosen_file = random.choice(videos)
                selected_path = os.path.join(v_dir, chosen_file)
                self.current_video_file = chosen_file
            else:
                self.current_video_file = "[Folder Kosong]"
        else:
            self.current_video_file = "[Folder Tidak Ada]"

        self.video = VideoPlayer(selected_path)
        self.line_overlay.fill((0,0,0,0))

    def _mon_to_vid(self, sx, sy):
        return (sx - MON_X) / MON_W, (sy - MON_Y) / MON_H

    def handle(self, ev):
        mon  = pygame.Rect(MON_X, MON_Y, MON_W, MON_H)
        btns = self.btns
        if ev.type == pygame.MOUSEBUTTONDOWN:
            p = ev.pos
            if btns["back"].collidepoint(p): return "levels"
            if btns["m10"].collidepoint(p):   self._jump(-5)
            if btns["play"].collidepoint(p):  self.video.toggle_play_pause() if self.video else None
            if btns["p10"].collidepoint(p):   self._jump(5)
            if btns["zm"].collidepoint(p):    self._do_zoom(-1)
            if btns["zp"].collidepoint(p):    self._do_zoom(1)
            if LEVELS[self.lv_id]["show_line"] and btns["line"].collidepoint(p):
                self.draw_mode = not self.draw_mode
                if not self.draw_mode:
                    self.user_line = None
                    self.line_overlay.fill((0,0,0,0))
            if self.slider_rect.collidepoint(p):
                self.slider_drag = True
                self._seek_slider(p[0])
            if self.draw_mode and mon.collidepoint(p):
                vx,vy = self._mon_to_vid(*p)
                self.drag_start = (vx,vy)
                self.user_line  = (vx,vy,vx,vy)
                self.dragging   = True
            if not self.decided:
                for d in self.dec_btns:
                    if d["rect"].collidepoint(p): self._decide(d["key"])

        if ev.type == pygame.MOUSEMOTION:
            if self.slider_drag: self._seek_slider(ev.pos[0])
            if self.dragging and self.drag_start:
                vx,vy = self._mon_to_vid(*ev.pos)
                x1,y1 = self.drag_start
                self.user_line = (x1,y1,vx,vy)

        if ev.type == pygame.MOUSEBUTTONUP:
            self.slider_drag = False; self.dragging = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE and self.video: self.video.toggle_play_pause()
            if ev.key == pygame.K_LEFT:  self._jump(-3)
            if ev.key == pygame.K_RIGHT: self._jump(3)
            if ev.key == pygame.K_r and self.video: self.video.rewind()

    def _seek_slider(self, mx):
        if not self.video: return
        r = max(0.0,min(1.0,(mx-self.slider_rect.x)/self.slider_rect.w))
        self.video.seek(int(r*self.video.total_frames))
        self.video.is_playing = False

    def _jump(self, d):
        if self.video:
            self.video.seek(self.video.current_frame_index + d)
            self.video.is_playing = False

    def _do_zoom(self, d):
        self.zoom_idx = max(0,min(len(ZOOM_LEVELS)-1,self.zoom_idx+d))
        self.zoom = ZOOM_LEVELS[self.zoom_idx]

    def _decide(self, key):
        if not self.video: return
        self.decided = True
        self.video.is_playing = False
        lv = LEVELS[self.lv_id]; ok = key == lv["ans"]
        if ok: self.score_ok += 1
        self.score_tot += 1
        self.result = {"ok":ok,"key":key,"lv":lv,"next_lv":self.lv_id<3}

    def update(self, dt):
        if self.video and not self.decided:
            self.video.advance()

    def draw(self, surf):
        surf.fill(DESK); scanlines(surf)
        F=self.F; lv=LEVELS[self.lv_id]

        pygame.draw.rect(surf,(8,8,18),(0,0,WIN_W,52))
        pygame.draw.line(surf,BORDER,(0,52),(WIN_W,52))
        fill_rect(surf,self.btns["back"],(10,10,20),BORDER,3)
        draw_text(surf,"◄ BACK",F["tiny"],GREY,self.btns["back"].centerx,self.btns["back"].centery)
        draw_text(surf,"KATEGORI",F["tiny"],GREY,WIN_W//2-200,18)
        draw_text(surf,lv["name"],F["body"],AMBER,WIN_W//2-200,36)
        
        # Tampilkan nama file yang sedang dimainkan
        draw_text(surf,"FILE AKTIF:",F["tiny"],GREY,WIN_W//2+40,18)
        draw_text(surf,self.current_video_file,F["tiny"],BLUE,WIN_W//2+40,36)
        
        draw_text(surf,"SKOR",F["tiny"],GREY,WIN_W-65,18)
        draw_text(surf,f"{self.score_ok}/{self.score_tot}",F["body"],GREEN,WIN_W-65,36)

        lp=self.left_rect
        fill_rect(surf,lp,(0,8,22),BORDER,4)
        draw_text(surf,"LIVE FEED",F["tiny"],GREY,lp.centerx,lp.y+14)
        pygame.draw.rect(surf,(180,0,0),(lp.x+8,lp.y+28,38,14),border_radius=2)
        draw_text(surf,"LIVE",F["tiny"],WHITE,lp.x+27,lp.y+35)
        draw_text(surf,"1 — 1",F["mono"],WHITE,lp.centerx,lp.y+72)
        draw_text(surf,"⏱ 78'",F["body"],(120,170,187),lp.centerx,lp.y+102)
        draw_text(surf,"VAR Review Active",F["tiny"],(170,130,130),lp.centerx,lp.y+126)
        
        pygame.draw.line(surf,BORDER,(lp.x+6,lp.y+148),(lp.right-6,lp.y+148))
        draw_text(surf,"⚖ ATURAN VAR",F["body"],(180,120,255),lp.centerx,lp.y+164)
        for i,rule in enumerate(lv["rules"]):
            draw_text(surf,rule,F["tiny"],(140,90,200),lp.centerx,lp.y+186+i*26)

        mon_rect = pygame.Rect(MON_X,MON_Y,MON_W,MON_H)
        pygame.draw.rect(surf,(5,5,10),mon_rect,border_radius=4)

        if self.video:
            raw_surf = self.video.get_surface((MON_W, MON_H))
            if self.zoom > 1.0:
                cw=int(MON_W/self.zoom); ch=int(MON_H/self.zoom)
                cx2=MON_W//2-cw//2; cy2=MON_H//2-ch//2
                crop=pygame.Rect(cx2,cy2,cw,ch).clip(raw_surf.get_rect())
                if crop.w>0 and crop.h>0:
                    raw_surf=pygame.transform.scale(raw_surf.subsurface(crop),(MON_W,MON_H))

            surf.blit(raw_surf, (MON_X,MON_Y))
            sl=pygame.Surface((MON_W,MON_H),pygame.SRCALPHA)
            for y in range(0,MON_H,4): pygame.draw.line(sl,(0,0,0,36),(0,y),(MON_W,y))
            surf.blit(sl,(MON_X,MON_Y))

            if self.user_line:
                x1r,y1r,x2r,y2r = self.user_line
                p1=(int(MON_X+x1r*MON_W), int(MON_Y+y1r*MON_H))
                p2=(int(MON_X+x2r*MON_W), int(MON_Y+y2r*MON_H))
                bresenham(surf,p1,p2,AMBER,thickness=2)
                pygame.draw.circle(surf,AMBER,p1,6); pygame.draw.circle(surf,AMBER,p2,6)

            prog = self.video.current_frame_index; tot = max(self.video.total_frames,1)
            draw_text(surf,f"F {prog:04d}/{tot:04d}",F["tiny"],AMBER,MON_X+50,MON_Y+12)
        else:
            draw_text(surf,"Video tidak ditemukan",F["body"],GREY,MON_X+MON_W//2,MON_Y+MON_H//2)

        pygame.draw.rect(surf,BORDER,mon_rect,2,border_radius=4)
        draw_text(surf,f"ZOOM ×{self.zoom:.1f}",F["tiny"],BLUE,MON_X+MON_W-40,MON_Y+12)

        sr = self.slider_rect
        fill_rect(surf,sr,(22,22,44),None,3)
        prog_ratio = self.video.current_frame_index/self.video.total_frames if self.video and self.video.total_frames>0 else 0
        fw=int(sr.w*prog_ratio)
        if fw>0: pygame.draw.rect(surf,BLUE,(sr.x,sr.y,fw,sr.h),border_radius=3)
        pygame.draw.circle(surf,(200,220,255),(sr.x+fw,sr.centery),7)
        pygame.draw.circle(surf,BLUE,(sr.x+fw,sr.centery),7,2)

        playing = self.video.is_playing if self.video else False
        ctrl_defs = [
            ("m10","⏮ −5f",False),
            ("play","⏸ PAUSE" if playing else "▶ PUTAR",playing),
            ("p10","+5f ⏭",False),
            ("zm","🔍−",False),
            ("zp","🔍+",False),
        ]
        for key,label,act in ctrl_defs:
            r=self.btns[key]
            fill_rect(surf,r,(10,10,32) if not act else (10,30,70),BLUE if act else BORDER,3)
            draw_text(surf,label,F["body"],(200,200,255) if act else (136,136,160),r.centerx,r.centery)

        if lv["show_line"]:
            r=self.btns["line"]
            fill_rect(surf,r,(10,30,60) if self.draw_mode else (10,10,32),BLUE if self.draw_mode else BORDER,3)
            lbl="✏ SELESAI" if self.draw_mode else "✏ GARIS"
            draw_text(surf,lbl,F["body"],BLUE if self.draw_mode else GREY,r.centerx,r.centery)
            if self.draw_mode:
                draw_text(surf,"Klik & seret di monitor untuk garis offside",F["tiny"],AMBER,MON_X+MON_W//2,self.btns["play"].bottom+18)

        dx = self.dec_btns[0]["rect"].x
        draw_text(surf,"▶ KEPUTUSAN:",F["tiny"],GREY,dx+96,MON_Y-14)
        for d in self.dec_btns:
            r=d["rect"]; dim = self.decided and not(self.result and self.result["key"]==d["key"])
            s=pygame.Surface((r.w,r.h),pygame.SRCALPHA); a=80 if dim else 255
            pygame.draw.rect(s,(*d["bg"],a),(0,0,r.w,r.h),border_radius=6); surf.blit(s,r.topleft)
            t=F["body"].render(d["label"],True,(*d["fg"],a)); surf.blit(t,t.get_rect(center=r.center))

        draw_text(surf,"SPACE=Play  ←/→=Frame  R=Rewind  ESC=Keluar",F["tiny"],GREY,WIN_W//2,WIN_H-12)
        if self.result: self._draw_result(surf)

    def _draw_result(self, surf):
        F=self.F; res=self.result; ok=res["ok"]
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,220)); surf.blit(ov,(0,0))
        cx=WIN_W//2; bw,bh=440,310; bx,by=cx-bw//2,WIN_H//2-bh//2
        fill_rect(surf,pygame.Rect(bx,by,bw,bh),(7,7,15),AMBER,4,2)
        draw_text(surf,"✅" if ok else "❌",F["icon"],WHITE,cx,by+44)
        draw_text(surf,"BENAR!" if ok else "SALAH!",F["press"],GREEN if ok else RED,cx,by+90)
        draw_text(surf,res["lv"]["explain"],F["tiny"],GREY,cx,by+132)
        draw_text(surf,"Jawaban: "+res["lv"]["ans_label"],F["tiny"],(102,102,102),cx,by+160)
        draw_text(surf,f"Skor: {self.score_ok} / {self.score_tot}",F["mono"],GREEN,cx,by+194)
        nb=pygame.Rect(cx-100,by+234,200,44); fill_rect(surf,nb,DARK,AMBER,4)
        lbl="LEVEL BERIKUTNYA ►" if res["next_lv"] else "LIHAT HASIL ►"
        draw_text(surf,lbl,F["tiny"],AMBER,cx,nb.centery); self._next_btn=nb

    def handle_result_click(self, pos):
        if self.result and self._next_btn and self._next_btn.collidepoint(pos):
            return "next" if self.result["next_lv"] else "final"

    def draw_final(self, surf):
        F=self.F; c=self.score_ok; t=self.score_tot; cx=WIN_W//2
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,225)); surf.blit(ov,(0,0))
        bw,bh=460,340; bx,by=cx-bw//2,WIN_H//2-bh//2
        fill_rect(surf,pygame.Rect(bx,by,bw,bh),(7,7,15),GREEN,4,2)
        draw_text(surf,"⚽ GAME SELESAI!",F["press"],AMBER,cx,by+42)
        draw_text(surf,"⭐"*c if c>0 else "—",F["big"],(255,200,0),cx,by+96)
        draw_text(surf,f"{c}/{t}",F["big"],GREEN,cx,by+174)
        draw_text(surf,SCORE_MSGS[c],F["mono"],GREY,cx,by+238)
        rb=pygame.Rect(cx-100,by+274,200,44); fill_rect(surf,rb,DARK,GREEN,4)
        draw_text(surf,"↺ MAIN LAGI",F["tiny"],GREEN,cx,rb.centery); self._restart_btn=rb
