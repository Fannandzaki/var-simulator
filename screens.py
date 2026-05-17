"""screens.py — VAR Simulator (Retro Desk)"""
import os, random, math, pygame
from constants import *
from video_player import VideoPlayer
from renderer import bresenham

# ── helpers ──────────────────────────────────────────────────────────────────
def txt(s,t,f,c,cx,cy):
    r=f.render(t,True,c); s.blit(r,r.get_rect(center=(cx,cy)))

def box(s,r,fill,border=None,rad=6,bw=2):
    if fill is not None: pygame.draw.rect(s,fill,r,border_radius=rad)
    if border: pygame.draw.rect(s,border,r,bw,border_radius=rad)

def shadow_box(s,r,fill,border,rad=10):
    sh=r.move(5,6); pygame.draw.rect(s,(0,0,0,70),sh,border_radius=rad)
    box(s,r,fill,border,rad)

def scan(s,r):
    sl=pygame.Surface((r.w,r.h),pygame.SRCALPHA)
    for y in range(0,r.h,3): pygame.draw.line(sl,(0,0,0,25),(0,y),(r.w,y))
    s.blit(sl,r.topleft)

def crt(s,rect,sw,sh):
    """Draw CRT casing. Returns inner screen Rect."""
    shadow_box(s,rect,CRT_BEIGE,CRT_SHADOW,12)
    pygame.draw.line(s,WHITE,(rect.x+12,rect.y+5),(rect.right-12,rect.y+5),2)
    pygame.draw.line(s,CRT_SHADOW,(rect.x+12,rect.bottom-5),(rect.right-12,rect.bottom-5),3)
    ix,iy=rect.centerx-sw//2, rect.centery-sh//2-8
    inner=pygame.Rect(ix,iy,sw,sh)
    bz=inner.inflate(14,14)
    box(s,bz,CRT_BEZEL,(15,20,20),8,2)
    box(s,inner,(5,10,15),None,4)
    for i in range(5): pygame.draw.line(s,CRT_SHADOW,(rect.centerx-20+i*10,rect.bottom-14),(rect.centerx-20+i*10,rect.bottom-8),2)
    return inner

# ── INTRO ─────────────────────────────────────────────────────────────────────
class IntroScreen:
    def __init__(self,F):
        self.F=F; self.t=0; self.blink=True; self.bt=0
        self.btn=pygame.Rect(WIN_W//2-130,520,260,48)
        self.anim=pygame.Surface((320,190))

    def handle(self,ev):
        if ev.type==pygame.MOUSEBUTTONDOWN and self.btn.collidepoint(ev.pos): return"levels"
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN: return"levels"

    def update(self):
        self.t+=1; self.bt+=1
        if self.bt>28: self.blink=not self.blink; self.bt=0

    def draw(self,s):
        s.fill(DESK)
        # Wall area (darker top band)
        pygame.draw.rect(s,(90,130,145),(0,0,WIN_W,200))
        pygame.draw.line(s,(70,110,125),(0,200),(WIN_W,200),4)

        cx=WIN_W//2; F=self.F
        txt(s,"GRAFIKA KOMPUTER  ·  FINAL PROJECT 2025",F["tiny"],(180,200,210),cx,28)
        txt(s,"VAR SIMULATOR",F["press"],WHITE,cx,80)
        txt(s,"VIDEO ASSISTANT REFEREE",F["mono"],(200,220,225),cx,120)

        # Mini CRT in center
        cr=pygame.Rect(cx-185,155,370,255)
        sc=crt(s,cr,330,195)
        self._anim(); s.blit(self.anim,sc.topleft)
        scan(s,sc)

        txt(s,"Jadilah wasit VAR di ruang VOR.",F["body"],(50,70,80),cx,440)
        txt(s,"Analisis tayangan ulang & buat keputusan!",F["body"],(50,70,80),cx,462)
        if self.blink:
            shadow_box(s,self.btn,CRT_BLUE,(20,50,110),8)
            txt(s,"► MULAI SEKARANG",F["press"],WHITE,cx,544)
        txt(s,"Kelompok Grafkom · 2025",F["tiny"],(100,130,140),cx,620)

    def _anim(self):
        a=self.anim; t=self.t; IW,IH=320,190; a.fill((22,88,22))
        for i in range(5):
            sl=pygame.Surface((64,IH),pygame.SRCALPHA)
            sl.fill((0,0,0,15) if i%2 else (255,255,255,5)); a.blit(sl,(i*64,0))
        pygame.draw.line(a,(255,255,255,80),(IW//2,0),(IW//2,IH),1)
        pygame.draw.circle(a,(255,255,255,80),(IW//2,IH//2),28,1)
        bx=IW//2+int(math.sin(t*.04)*75); by=IH//2+int(math.cos(t*.06)*35)
        pygame.draw.circle(a,WHITE,(bx,by),5)
        for col,ox in [((204,34,0),-22),((0,68,187),26)]:
            px=bx+ox+int(math.sin(t*.03)*4); py=by+int(math.cos(t*.05)*3)
            pygame.draw.rect(a,col,(px-5,py-4,10,16),border_radius=2)
            pygame.draw.circle(a,(245,192,154),(px,py-8),4)

# ── LEVEL SELECT ──────────────────────────────────────────────────────────────
class LevelSelectScreen:
    def __init__(self,F):
        self.F=F; self.hover=-1
        cw,gap=290,20; total=3*cw+2*gap; sx=(WIN_W-total)//2
        self.cards=[pygame.Rect(sx+i*(cw+gap),160,cw,230) for i in range(3)]
        self.back=pygame.Rect(18,14,88,30)

    def handle(self,ev):
        if ev.type==pygame.MOUSEMOTION:
            self.hover=next((i for i,r in enumerate(self.cards) if r.collidepoint(ev.pos)),-1)
        if ev.type==pygame.MOUSEBUTTONDOWN:
            if self.back.collidepoint(ev.pos): return"intro"
            for i,r in enumerate(self.cards):
                if r.collidepoint(ev.pos): return i+1

    def update(self): pass

    def draw(self,s):
        s.fill(DESK)
        pygame.draw.rect(s,(90,130,145),(0,0,WIN_W,120))
        pygame.draw.line(s,(70,110,125),(0,120),(WIN_W,120),4)
        F=self.F; cx=WIN_W//2
        shadow_box(s,self.back,CRT_BEIGE,CRT_SHADOW,4)
        txt(s,"◄ BACK",F["tiny"],CRT_BEZEL,self.back.centerx,self.back.centery)
        txt(s,"PILIH KATEGORI",F["press"],WHITE,cx,56)
        txt(s,"Program akan memilih video acak dari folder yang dipilih",F["body"],(180,200,210),cx,92)
        cols=[GREEN,AMBER,RED]
        for i,(r,lid) in enumerate(zip(self.cards,[1,2,3])):
            lv=LEVELS[lid]; col=cols[i]; rr=r.move(0,-6 if self.hover==i else 0)
            sc=crt(s,rr,250,155)
            fy=sc.y+8
            txt(s,lv["icon"],F["icon"],WHITE,sc.centerx,fy+14)
            txt(s,f"LEVEL 0{lid}",F["body"],col,sc.centerx,fy+44)
            bb=F["tiny"].render(lv["badge"],True,col); bx2=sc.centerx-bb.get_width()//2
            bg=pygame.Surface((bb.get_width()+10,bb.get_height()+4),pygame.SRCALPHA)
            bg.fill((*col,40)); s.blit(bg,(bx2-5,fy+56)); s.blit(bb,(bx2,fy+58))
            txt(s,lv["name"],F["body"],WHITE,sc.centerx,fy+84)
            words=lv["case"].split(); lines=[]; cur=""
            for w in words:
                test=cur+" "+w if cur else w
                cur=test if F["tiny"].size(test)[0]<sc.w-10 else (lines.append(cur) or w)
            if cur: lines.append(cur)
            for j,ln in enumerate(lines[:2]): txt(s,ln,F["tiny"],(160,170,170),sc.centerx,fy+106+j*16)
            scan(s,sc)

# ── GAME ──────────────────────────────────────────────────────────────────────
# Layout constants
C_MON  = pygame.Rect(270, 30, 560, 400)   # Center monitor casing
L_MON  = pygame.Rect(18,  90, 240, 220)   # Left monitor casing
R_MON  = pygame.Rect(842, 90, 240, 220)   # Right monitor casing
BOARD  = pygame.Rect(230, 448, 640, 118)  # Control board

class GameScreen:
    def __init__(self,F):
        self.F=F; self.video=None; self.lv_id=1
        self.score_ok=0; self.score_tot=0
        self._reset(); self._build()

    def _reset(self):
        self.zoom_idx=0; self.zoom=ZOOM_LEVELS[0]
        self.draw_mode=False; self.user_line=None
        self.drag_start=None; self.dragging=False
        self.decided=False; self.result=None; self.cam_sel=1
        self._next_btn=None; self._restart_btn=None
        self.vid_file="Belum Ada Video"
        self.inner_c=pygame.Rect(340,70,430,310)  # fallback
        self.dyn_dec=[]

    def _build(self):
        bx,by=BOARD.x,BOARD.y
        self.slider=pygame.Rect(bx+200,by+50,240,12)
        self.slider_drag=False
        self.btns={
            "back":  pygame.Rect(18,14,88,30),
            "play":  pygame.Rect(bx+28, by+28,68,44),
            "m5":    pygame.Rect(bx+106,by+28,68,44),
            "p5":    pygame.Rect(bx+180,by+28,68,44), # ← added forward button
            "zm":    pygame.Rect(bx+460,by+28,50,44),
            "zp":    pygame.Rect(bx+520,by+28,50,44),
            "line":  pygame.Rect(bx+580,by+28,46,44),
        }
        self.dec_meta=[{"key":d["key"],"label":d["label"],"bg":d["bg"],"fg":d["fg"]} for d in DECISIONS]
        self.cam_rects=[]

    def boot(self,lid):
        self.lv_id=lid; self._reset()
        vdir=LEVELS[lid].get("video_dir","")
        path="assets/placeholder.mp4"
        if os.path.exists(vdir):
            vids=[f for f in os.listdir(vdir) if f.lower().endswith(('.mp4','.avi','.mov'))]
            if vids:
                cf=random.choice(vids); path=os.path.join(vdir,cf); self.vid_file=cf
            else: self.vid_file="[Folder Kosong]"
        else: self.vid_file="[Folder Tidak Ada]"
        self.video=VideoPlayer(path)

    def _to_vid(self,sx,sy):
        ic=self.inner_c
        return (sx-ic.x)/ic.w,(sy-ic.y)/ic.h

    def handle(self,ev):
        B=self.btns
        if ev.type==pygame.MOUSEBUTTONDOWN:
            p=ev.pos
            if B["back"].collidepoint(p): return"levels"
            if B["m5"].collidepoint(p):  self._jump(-5)
            if B["p5"].collidepoint(p):  self._jump(5)
            if B["play"].collidepoint(p) and self.video: self.video.toggle_play_pause()
            if B["zm"].collidepoint(p):  self._zoom(-1)
            if B["zp"].collidepoint(p):  self._zoom(1)
            if LEVELS[self.lv_id]["show_line"] and B["line"].collidepoint(p):
                self.draw_mode=not self.draw_mode
                if not self.draw_mode: self.user_line=None
            if self.slider.collidepoint(p): self.slider_drag=True; self._seek(p[0])
            for i,r in enumerate(self.cam_rects):
                if r.collidepoint(p): self.cam_sel=i+1
            if self.draw_mode and self.inner_c.collidepoint(p):
                vx,vy=self._to_vid(*p); self.drag_start=(vx,vy)
                self.user_line=(vx,vy,vx,vy); self.dragging=True
            if not self.decided:
                for d in self.dyn_dec:
                    if d["rect"].collidepoint(p): self._decide(d["key"])
        if ev.type==pygame.MOUSEMOTION:
            if self.slider_drag: self._seek(ev.pos[0])
            if self.dragging and self.drag_start:
                vx,vy=self._to_vid(*ev.pos); x1,y1=self.drag_start
                self.user_line=(x1,y1,vx,vy)
        if ev.type==pygame.MOUSEBUTTONUP: self.slider_drag=False; self.dragging=False
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_SPACE and self.video: self.video.toggle_play_pause()
            if ev.key==pygame.K_LEFT:  self._jump(-3)
            if ev.key==pygame.K_RIGHT: self._jump(3)

    def _seek(self,mx):
        if not self.video: return
        r=max(0.,min(1.,(mx-self.slider.x)/self.slider.w))
        self.video.seek(int(r*self.video.total_frames)); self.video.is_playing=False

    def _jump(self,d):
        if self.video: self.video.seek(self.video.current_frame_index+d); self.video.is_playing=False

    def _zoom(self,d):
        self.zoom_idx=max(0,min(len(ZOOM_LEVELS)-1,self.zoom_idx+d))
        self.zoom=ZOOM_LEVELS[self.zoom_idx]

    def _decide(self,key):
        if not self.video: return
        self.decided=True; self.video.is_playing=False
        lv=LEVELS[self.lv_id]; ok=key==lv["ans"]
        if ok: self.score_ok+=1
        self.score_tot+=1; self.result={"ok":ok,"key":key,"lv":lv,"next_lv":self.lv_id<3}

    def update(self,dt):
        if self.video and not self.decided: self.video.advance()

    def draw(self,s):
        F=self.F; lv=LEVELS[self.lv_id]

        # ── Background: wall + desk ───────────────────────────────────────────
        s.fill(DESK)
        pygame.draw.rect(s,(88,128,142),(0,0,WIN_W,60))
        pygame.draw.line(s,(68,108,122),(0,60),(WIN_W,60),4)

        # ── Top bar ───────────────────────────────────────────────────────────
        shadow_box(s,self.btns["back"],CRT_BEIGE,CRT_SHADOW,4)
        txt(s,"◄ EXIT",F["tiny"],CRT_BEZEL,self.btns["back"].centerx,self.btns["back"].centery)
        txt(s,lv["name"],F["press"],WHITE,WIN_W//2,30)
        txt(s,f"SKOR  {self.score_ok} / {self.score_tot}",F["body"],WHITE,WIN_W-80,30)

        # ── LEFT Monitor: Live Feed ───────────────────────────────────────────
        il=crt(s,L_MON,200,158)
        pygame.draw.rect(s,(170,0,0),(il.x+6,il.y+8,36,14),border_radius=2)
        txt(s,"LIVE",F["tiny"],WHITE,il.x+24,il.y+15)
        txt(s,"LIVE FEED",F["tiny"],(150,220,150),il.centerx,il.y+36)
        txt(s,"1  —  1",F["mono"],WHITE,il.centerx,il.y+68)
        txt(s,"⏱ 78'",F["body"],(120,180,200),il.centerx,il.y+92)
        clbls=["CAM1","CAM2","GOAL"]; self.cam_rects=[]
        for i,lb in enumerate(clbls):
            r=pygame.Rect(il.x+4+(i*64),il.bottom-28,58,22)
            self.cam_rects.append(r)
            act=i+1==self.cam_sel
            box(s,r,(60,20,20) if act else (30,44,54),(120,40,40) if act else (50,70,80),3)
            txt(s,lb,F["tiny"],WHITE,r.centerx,r.centery)
        scan(s,il)

        # ── RIGHT Monitor: Decision System ────────────────────────────────────
        ir=crt(s,R_MON,200,158)
        txt(s,"DISCIPLINARY",F["tiny"],(140,255,140),ir.centerx,ir.y+16)
        txt(s,"ACTION SYSTEM",F["tiny"],(140,255,140),ir.centerx,ir.y+30)
        pygame.draw.line(s,(60,80,60),(ir.x+8,ir.y+42),(ir.right-8,ir.y+42),1)
        self.dyn_dec=[]
        for i,d in enumerate(self.dec_meta):
            r=pygame.Rect(ir.x+8,ir.y+50+i*26,ir.w-16,22)
            self.dyn_dec.append({"rect":r,"key":d["key"]})
            dim=self.decided and not(self.result and self.result["key"]==d["key"])
            a=70 if dim else 255
            ds=pygame.Surface((r.w,r.h),pygame.SRCALPHA)
            pygame.draw.rect(ds,(*d["bg"],a),(0,0,r.w,r.h),border_radius=3); s.blit(ds,r.topleft)
            ts=F["tiny"].render(d["label"],True,(*d["fg"],a)); s.blit(ts,ts.get_rect(center=r.center))
        scan(s,ir)

        # ── CENTER Monitor: Main Video ────────────────────────────────────────
        self.inner_c=crt(s,C_MON,490,318)
        ic=self.inner_c
        if self.video:
            raw=self.video.get_surface((ic.w,ic.h))
            if self.zoom>1.0:
                cw2=int(ic.w/self.zoom); ch2=int(ic.h/self.zoom)
                crop=pygame.Rect(ic.w//2-cw2//2,ic.h//2-ch2//2,cw2,ch2).clip(raw.get_rect())
                if crop.w>0 and crop.h>0: raw=pygame.transform.scale(raw.subsurface(crop),(ic.w,ic.h))
            s.blit(raw,ic.topleft)
            if self.user_line:
                x1r,y1r,x2r,y2r=self.user_line
                p1=(int(ic.x+x1r*ic.w),int(ic.y+y1r*ic.h))
                p2=(int(ic.x+x2r*ic.w),int(ic.y+y2r*ic.h))
                bresenham(s,p1,p2,AMBER,2)
                pygame.draw.circle(s,AMBER,p1,5); pygame.draw.circle(s,AMBER,p2,5)
        else:
            txt(s,"Tidak ada video",F["body"],GREY,ic.centerx,ic.centery)
        scan(s,ic)
        # HUD overlay on monitor
        prog=self.video.current_frame_index if self.video else 0
        tot=self.video.total_frames if self.video else 1
        pygame.draw.rect(s,(0,0,0,120),(ic.x,ic.y,ic.w,22))
        txt(s,f"FRAME {prog:04d}/{tot:04d}",F["tiny"],(180,220,255),ic.x+60,ic.y+11)
        txt(s,f"ZOOM ×{self.zoom:.1f}",F["tiny"],AMBER,ic.right-38,ic.y+11)
        pygame.draw.rect(s,(0,0,0,100),(ic.x,ic.bottom-20,ic.w,20))
        fname=self.vid_file if len(self.vid_file)<40 else self.vid_file[:38]+"…"
        txt(s,f"▶ {fname}",F["tiny"],(160,180,190),ic.centerx,ic.bottom-10)

        # ── CONTROL BOARD ─────────────────────────────────────────────────────
        shadow_box(s,BOARD,CRT_BEIGE,CRT_SHADOW,14)
        # Decorative line top of board
        pygame.draw.line(s,WHITE,(BOARD.x+16,BOARD.y+6),(BOARD.right-16,BOARD.y+6),2)

        # Slider track
        sr=self.slider
        pygame.draw.rect(s,(60,65,70),sr,border_radius=4)
        pygame.draw.line(s,(35,40,45),(sr.x+4,sr.centery),(sr.right-4,sr.centery),2)
        ratio=prog/tot if tot>0 else 0
        fw=int(sr.w*ratio)
        if fw>0: pygame.draw.rect(s,CRT_BLUE,(sr.x,sr.y,fw,sr.h),border_radius=4)
        kx=sr.x+fw; pygame.draw.rect(s,(180,210,255),(kx-8,sr.centery-13,16,26),border_radius=4)
        box(s,pygame.Rect(kx-8,sr.centery-13,16,26),None,(100,140,200),4,2)

        # Playback buttons
        playing=self.video.is_playing if self.video else False
        for key,lbl,act in [("m5","◄◄",False),("play","▐▐" if playing else "►",playing),("p5","►►",False)]:
            r=self.btns[key]
            shadow_box(s,r,CRT_BLUE if act else (72,110,152),(20,50,110) if act else (40,70,110),6)
            txt(s,lbl,F["body"],WHITE,r.centerx,r.centery)

        # Zoom & Line buttons
        for key,lbl,act in [("zm","−",False),("zp","+",False)]:
            r=self.btns[key]; shadow_box(s,r,(72,110,152),(40,70,110),6)
            txt(s,lbl,F["body"],WHITE,r.centerx,r.centery)

        if lv["show_line"]:
            r=self.btns["line"]; act=self.draw_mode
            shadow_box(s,r,(160,50,50) if act else (72,110,152),(80,20,20) if act else (40,70,110),6)
            txt(s,"✏",F["body"],WHITE,r.centerx,r.centery)

        # Labels under slider
        txt(s,"TIMELINE",F["tiny"],(100,130,140),sr.centerx,sr.bottom+14)
        txt(s,"ZOOM",F["tiny"],(100,130,140),self.btns["zm"].centerx+25,BOARD.y+82)

        # ── PROPS ─────────────────────────────────────────────────────────────
        # Red rule book
        bk=pygame.Rect(42,490,130,118)
        shadow_box(s,bk,(185,38,38),(110,18,18),4)
        pygame.draw.rect(s,(210,210,210),(bk.x,bk.bottom-10,bk.w,10),border_radius=2)
        txt(s,"RULES",F["tiny"],(255,180,180),bk.centerx,bk.centery-10)

        # Grey notepad
        np=pygame.Rect(920,510,130,55)
        shadow_box(s,np,(200,205,195),(140,145,135),4)
        for row in range(3): pygame.draw.line(s,(155,160,150),(np.x+10,np.y+14+row*14),(np.right-10,np.y+14+row*14),1)

        if self.result: self._result_overlay(s)

    def _result_overlay(self,s):
        F=self.F; res=self.result; ok=res["ok"]
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,210)); s.blit(ov,(0,0))
        cx=WIN_W//2; bw,bh=460,320; bx,by=cx-bw//2,WIN_H//2-bh//2
        shadow_box(s,pygame.Rect(bx,by,bw,bh),CRT_BEIGE,CRT_BEZEL,10)
        txt(s,"✅" if ok else "❌",F["icon"],CRT_BEZEL,cx,by+46)
        txt(s,"KEPUTUSAN BENAR!" if ok else "KEPUTUSAN SALAH!",F["press"],GREEN if ok else RED,cx,by+94)
        txt(s,res["lv"]["explain"],F["tiny"],CRT_BEZEL,cx,by+136)
        txt(s,"Jawaban: "+res["lv"]["ans_label"],F["tiny"],(90,90,90),cx,by+162)
        txt(s,f"Skor: {self.score_ok} / {self.score_tot}",F["mono"],CRT_BEZEL,cx,by+196)
        nb=pygame.Rect(cx-110,by+244,220,46)
        shadow_box(s,nb,CRT_BLUE,(20,50,110),8)
        lbl="LEVEL BERIKUTNYA ►" if res["next_lv"] else "LIHAT HASIL ►"
        txt(s,lbl,F["tiny"],WHITE,cx,nb.centery); self._next_btn=nb

    def handle_result_click(self,pos):
        if self.result and self._next_btn and self._next_btn.collidepoint(pos):
            return"next" if self.result["next_lv"] else"final"

    def draw_final(self,s):
        F=self.F; c=self.score_ok; t=self.score_tot; cx=WIN_W//2
        ov=pygame.Surface((WIN_W,WIN_H),pygame.SRCALPHA); ov.fill((0,0,0,220)); s.blit(ov,(0,0))
        bw,bh=480,360; bx,by=cx-bw//2,WIN_H//2-bh//2
        shadow_box(s,pygame.Rect(bx,by,bw,bh),CRT_BEIGE,CRT_BEZEL,10)
        txt(s,"⚽ GAME SELESAI!",F["press"],CRT_BEZEL,cx,by+44)
        txt(s,"⭐"*c if c>0 else "—",F["big"],AMBER,cx,by+100)
        txt(s,f"{c} / {t}",F["big"],CRT_BEZEL,cx,by+178)
        txt(s,SCORE_MSGS[c],F["mono"],(80,80,80),cx,by+244)
        rb=pygame.Rect(cx-110,by+284,220,46)
        shadow_box(s,rb,CRT_BLUE,(20,50,110),8)
        txt(s,"↺ MAIN LAGI",F["tiny"],WHITE,cx,rb.centery); self._restart_btn=rb
