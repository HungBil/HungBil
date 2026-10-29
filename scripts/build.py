"""Builds the animated profile SVGs from assets/src.  Run: python scripts/build.py"""
import base64, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets/src", ROOT / "assets"


def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode((SRC / name).read_bytes()).decode()


FONTS = f"""
@font-face{{font-family:HBDisplay;src:url({b64('inter900.woff2','font/woff2')}) format('woff2')}}
@font-face{{font-family:HBText;src:url({b64('inter600.woff2','font/woff2')}) format('woff2')}}
@font-face{{font-family:HBMono;src:url({b64('cascadia.woff2','font/woff2')}) format('woff2')}}
"""

# Shared fire palette
GOLD, AMBER, ORANGE, RED = "#FFD54A", "#FFA21F", "#FF5A1F", "#C81E0A"


def embers(rng, n, spawn, rise=(40, 110), drift=(-25, 25), size=(0.8, 2.6), dur=(1.6, 3.6)):
    """Rising ember particles. spawn(rng) -> (x, y)."""
    out = []
    for _ in range(n):
        x, y = spawn(rng)
        dy, dx = -rng.uniform(*rise), rng.uniform(*drift)
        cx1, cx2 = dx * rng.uniform(-1, 1.5), dx * rng.uniform(0, 1.2)
        d, b = rng.uniform(*dur), -rng.uniform(0, 4)
        r = rng.uniform(*size)
        c = rng.choice([GOLD, GOLD, AMBER, ORANGE, "#FFF1B8"])
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" opacity="0">'
            f'<animateMotion dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite" '
            f'path="M0 0 C{cx1:.1f} {dy*0.35:.1f} {cx2:.1f} {dy*0.7:.1f} {dx:.1f} {dy:.1f}"/>'
            f'<animate attributeName="opacity" values="0;1;.8;0" keyTimes="0;.15;.6;1" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="{r:.2f};{r*0.25:.2f}" dur="{d:.2f}s" begin="{b:.2f}s" repeatCount="indefinite"/>'
            "</circle>"
        )
    return "\n".join(out)


WYVERN = """
<g id="wyv">
  <path d="M0,0 C-12,-2 -25,2 -35,-2 C-25,5 -10,3 0,4 Z" fill="#1A0200" stroke="#FF5A1F" stroke-width=".6"/>
  <polygon points="-35,-2 -46,-6 -40,1" fill="#FF6A1F"/>
  <path d="M3,0 Q5,-15 -5,-20 Q-2,-10 3,2 Z" fill="#120100" stroke="#7A1A00" stroke-width=".5">
    <animate attributeName="d" values="M3,0 Q5,-15 -5,-20 Q-2,-10 3,2 Z;M3,0 Q15,-2 -5,3 Q-2,-2 3,2 Z;M3,0 Q5,-15 -5,-20 Q-2,-10 3,2 Z" dur=".42s" repeatCount="indefinite"/>
  </path>
  <path d="M-5,3 Q5,8 14,2 Q22,-4 25,-10 L32,-7 L27,1 Q14,8 5,6 Z" fill="#240300" stroke="#FF5A1F" stroke-width=".6"/>
  <polygon points="32,-7 38,-4 34,2 27,1" fill="#2E0400" stroke="#FF7A2A" stroke-width=".6"/>
  <polygon points="28,-8 15,-18 22,-5" fill="#FFB02E"/>
  <circle cx="31" cy="-3" r="1.6" fill="#FFF3B0"/>
  <path d="M4,2 Q15,-22 -10,-18 Q0,-8 4,4 Z" fill="#2A0300" stroke="#FF5A1F" stroke-width=".8">
    <animate attributeName="d" values="M4,2 Q15,-22 -10,-18 Q0,-8 4,4 Z;M4,2 Q25,12 -10,8 Q0,4 4,4 Z;M4,2 Q15,-22 -10,-18 Q0,-8 4,4 Z" dur=".42s" repeatCount="indefinite"/>
  </path>
</g>"""


def wyvern(path, dur, begin, scale, flip=False, opacity=1.0, blur=False):
    t = f"scale({scale})" + (" scale(1,-1)" if flip else "")
    f = ' filter="url(#far)"' if blur else ""
    return (f'<g opacity="{opacity}"{f}><animateMotion path="{path}" dur="{dur}s" begin="{begin}s" '
            f'repeatCount="indefinite" rotate="auto"/><use href="#wyv" transform="{t}"/></g>')


def sparkle(x, y, s, begin, dur=2.6):
    return (f'<g transform="translate({x} {y})"><path d="M0,-{s} L{s*.22},-{s*.22} L{s},0 L{s*.22},{s*.22} L0,{s} '
            f'L-{s*.22},{s*.22} L-{s},0 L-{s*.22},-{s*.22} Z" fill="#FFF7D6" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.12;.3;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="scale" values="0.2;1.2;0.2;0.2" keyTimes="0;.12;.3;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="rotate" values="0;90" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" additive="sum"/>'
            "</path></g>")


def header():
    rng = random.Random(7)
    W, H = 1000, 340
    # dragon image placement (1500x689 source)
    ix, iy, iw, ih = -34, -20, 810, 372
    mouth = (360, 142)

    def fire_spawn(r):  # along the fire stream, mouth -> lower right
        t = r.random() ** 0.8
        return (mouth[0] + 20 + t * 400 + r.uniform(-10, 10),
                mouth[1] + 10 + t * 120 + r.uniform(-28, 28))

    def floor_spawn(r):
        return (r.uniform(0, W), H + r.uniform(0, 10))

    def text_spawn(r):
        return (r.uniform(560, 990), r.uniform(150, 330))

    name_x, name_y = 772, 192
    sub = "FULL STACK · AI BUILDER"
    tag = "AI-ASSISTED DEVELOPMENT — POWERED BY FIRE"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="HungBil — Full Stack · AI Builder">
<title>HungBil — Full Stack · AI Builder</title>
<style>{FONTS}
.name{{font-family:HBDisplay,'Segoe UI Black','Arial Black',sans-serif;font-weight:900;font-size:92px;letter-spacing:-1px}}
.mono{{font-family:HBMono,Consolas,'Courier New',monospace;font-weight:600}}
</style>
<defs>
  <image id="dragon" href="{b64('dragon.webp','image/webp')}" x="{ix}" y="{iy}" width="{iw}" height="{ih}"/>
  {WYVERN}
  <radialGradient id="bg" cx="30%" cy="48%" r="75%">
    <stop offset="0" stop-color="#2A0600"/><stop offset=".45" stop-color="#0E0200"/><stop offset="1" stop-color="#030000"/>
  </radialGradient>
  <radialGradient id="mouthGlow"><stop offset="0" stop-color="#FFE08A" stop-opacity=".95"/><stop offset=".35" stop-color="#FF7A1F" stop-opacity=".45"/><stop offset="1" stop-color="#FF3300" stop-opacity="0"/></radialGradient>
  <radialGradient id="scrim" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#160200" stop-opacity=".78"/><stop offset=".7" stop-color="#1A0300" stop-opacity=".4"/><stop offset="1" stop-color="#1A0300" stop-opacity="0"/></radialGradient>
  <linearGradient id="nameFill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFF6C9"/><stop offset=".28" stop-color="{GOLD}"/><stop offset=".58" stop-color="{ORANGE}"/><stop offset="1" stop-color="#9A0E00"/>
  </linearGradient>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="160" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="420 0;1150 0;1150 0" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>
  <linearGradient id="bodyFade" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#fff"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="fireFade" x1="0" x2="1"><stop offset=".44" stop-color="#fff" stop-opacity="0"/><stop offset=".56" stop-color="#fff"/><stop offset=".75" stop-color="#fff" stop-opacity=".8"/><stop offset=".97" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="mBody" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect x="{ix}" y="0" width="{iw}" height="{H}" fill="url(#bodyFade)"/></mask>
  <mask id="mFire" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect x="{ix}" y="0" width="{iw}" height="{H}" fill="url(#fireFade)"/></mask>
  <filter id="haze" x="0" y="0" width="{W}" height="{H}" filterUnits="userSpaceOnUse">
    <feTurbulence type="fractalNoise" baseFrequency="0.011 0.04" numOctaves="2" seed="4" result="n">
      <animate attributeName="baseFrequency" values="0.011 0.040;0.014 0.055;0.010 0.047;0.011 0.040" dur="2.4s" repeatCount="indefinite"/>
    </feTurbulence>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="14" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="hot"><feColorMatrix type="matrix" values="1.35 .1 0 0 .03  .05 .9 0 0 0  0 0 .4 0 0  0 0 0 1 0"/></filter>
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="bigGlow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="far"><feGaussianBlur stdDeviation=".8"/></filter>
  <clipPath id="typeSub"><rect x="560" y="210" width="430" height="30"><animate attributeName="width" values="0;430;430" keyTimes="0;.35;1" dur="7s" repeatCount="indefinite"/></rect></clipPath>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#FF3300" opacity=".035"/></pattern>
</defs>

<!-- background -->
<rect width="{W}" height="{H}" fill="#030000"/>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<g stroke="#2A0700" stroke-width=".6" opacity=".7">
  {''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W + 1, 100))}
  {''.join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(40, H, 100))}
</g>

<!-- far wyverns (behind the dragon) -->
{wyvern("M1050,70 C850,20 700,110 520,60 C380,25 200,90 -80,40", 11, -3, .45, True, .55, True)}
{wyvern("M-80,30 C150,90 300,10 480,40 C650,70 800,0 1080,30", 13, -8, .38, False, .45, True)}

<!-- dragon: body = animated WebP (Codex keyframes + optical-flow in-betweens), fire with heat-haze + flicker -->
<g style="mix-blend-mode:screen">
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
    <image href="{b64('dragon-body.webp','image/webp')}" x="{ix}" y="{iy}" width="{iw*0.6:.0f}" height="{ih}" mask="url(#mBody)"/>
    <g mask="url(#mFire)"><use href="#dragon" filter="url(#haze)"/></g>
    <g mask="url(#mFire)" opacity=".3"><use href="#dragon" filter="url(#hot)"/>
      <animate attributeName="opacity" values=".15;.5;.25;.6;.2;.45;.15" dur="1.9s" repeatCount="indefinite"/>
    </g>
    <circle cx="{mouth[0]}" cy="{mouth[1]}" r="46" fill="url(#mouthGlow)">
      <animate attributeName="r" values="38;58;44;62;38" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".55;1;.7;.95;.55" dur="2.2s" repeatCount="indefinite"/>
    </circle>
  </g>
</g>

<!-- embers -->
<g filter="url(#glow)">
{embers(rng, 46, fire_spawn)}
{embers(rng, 18, floor_spawn, rise=(90, 220), size=(.7, 2), dur=(3, 6))}
{embers(rng, 10, text_spawn, rise=(30, 70), size=(.5, 1.4), dur=(2.5, 4.5))}
</g>

<!-- near wyverns -->
{wyvern("M-120,300 C120,330 260,250 330,300 C420,360 520,250 640,320 C760,380 900,300 1120,330", 7.5, -2, .9)}
{wyvern("M1100,20 C900,120 820,-10 680,30 C560,60 520,0 440,-60", 6, -4.2, .7, True)}

<rect width="{W}" height="{H}" fill="url(#scan)"/>

<!-- text block -->
<ellipse cx="{name_x}" cy="215" rx="250" ry="130" fill="url(#scrim)"/>
<g>
  <animateTransform attributeName="transform" type="translate" values="0 14;0 0" dur="1.1s" calcMode="spline" keySplines=".2 .8 .2 1"/>
  <animate attributeName="opacity" values="0;1" dur="1.1s"/>
  <text class="name" x="{name_x}" y="{name_y}" text-anchor="middle" fill="none" stroke="{ORANGE}" stroke-width="10" filter="url(#bigGlow)" opacity=".75">HungBil
    <animate attributeName="opacity" values=".45;.85;.55;.9;.45" dur="3s" repeatCount="indefinite"/></text>
  <text class="name" x="{name_x + 3}" y="{name_y + 4}" text-anchor="middle" fill="#2A0000">HungBil</text>
  <text class="name" x="{name_x}" y="{name_y}" text-anchor="middle" fill="url(#nameFill)" stroke="#FFE7B0" stroke-width="1.2">HungBil</text>
  <text class="name" x="{name_x}" y="{name_y}" text-anchor="middle" fill="url(#shine)" style="mix-blend-mode:overlay">HungBil</text>

  <!-- crown on the H -->
  <g transform="rotate(-16 612 96)">
    <image href="{b64('crown.webp','image/webp')}" x="578" y="54" width="82" height="82" style="mix-blend-mode:screen" filter="url(#glow)"/>
    {sparkle(613, 66, 7, 0.4)}{sparkle(589, 84, 5, 1.6)}{sparkle(637, 84, 5, 2.3)}
    <animateTransform attributeName="transform" type="rotate" values="-16 612 96;-13 612 96;-16 612 96" dur="4s" repeatCount="indefinite" additive="replace"/>
  </g>

  <line x1="560" y1="208" x2="985" y2="208" stroke="url(#rule)" stroke-width="1.6"/>
  <circle cy="208" r="2.6" fill="#FFF3B0" filter="url(#glow)"><animate attributeName="cx" values="560;985;560" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".5 0 .5 1;.5 0 .5 1"/></circle>

  <g clip-path="url(#typeSub)">
    <text class="mono" x="{name_x}" y="233" text-anchor="middle" font-size="17" letter-spacing="4" fill="#FFF1E0">{sub}</text>
  </g>
  <g fill="none" stroke="{GOLD}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)">
    <path d="M584,217 L576,227 L584,237"/>
    <path d="M960,217 L968,227 L960,237"><animate attributeName="opacity" values="1;.15;1" dur="1s" repeatCount="indefinite"/></path>
  </g>
  <text class="mono" x="{name_x}" y="266" text-anchor="middle" font-size="11.5" letter-spacing="2.4" fill="{AMBER}">{tag}</text>
</g>

<!-- frame -->
<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="10" fill="none" stroke="#5A1200" stroke-width="1.5"/>
<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="10" fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-dasharray="120 {2*(W+H)}" filter="url(#glow)" opacity=".9">
  <animate attributeName="stroke-dashoffset" values="0;-{2*(W+H)}" dur="9s" repeatCount="indefinite"/>
</rect>
<g stroke="{GOLD}" stroke-width="2.4" fill="none" filter="url(#glow)" stroke-linecap="round">
  <path d="M2,40 V2 H40"/><path d="M{W-40},2 H{W-2} V40"/><path d="M2,{H-40} V{H-2} H40"/><path d="M{W-40},{H-2} H{W-2} V{H-40}"/>
</g>
</svg>"""


COMMON_DEFS = f"""
  <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#170401"/><stop offset="1" stop-color="#070100"/></linearGradient>
  <linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></linearGradient>"""

STYLE = f"""<style>{FONTS}
.t{{font-family:HBText,'Segoe UI',sans-serif;font-weight:600}}
.mono{{font-family:HBMono,Consolas,'Courier New',monospace;font-weight:600}}
</style>"""


def frame(w, h, dur=8, rx=12):
    per = 2 * (w + h)
    return f"""<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="url(#panel)" stroke="#4A1000" stroke-width="1.5"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="90 {per}" filter="url(#glow)">
  <animate attributeName="stroke-dashoffset" values="0;-{per}" dur="{dur}s" repeatCount="indefinite"/></rect>"""


def svg_doc(w, h, label, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
            f"<title>{label}</title>{STYLE}<defs>{COMMON_DEFS}{defs}</defs>{body}</svg>")


def about():
    rng = random.Random(11)
    W, H = 1000, 290
    cx, cy = 150, 145
    T = 16  # typing loop seconds
    P, C, O = ORANGE, "#FFF1E0", "#FFC58A"
    lines = [  # (is_command, text)
        (True, "whoami"),
        (False, "Henry Don — aka HungBil"),
        (True, "cat focus.txt"),
        (False, "AI Agents · AI Security · Full-Stack Web · AI Product"),
        (True, "ls ./building"),
        (False, "ai-log-hook/  scamgraph-agents/  di-san-viet-nam/  ai-test/"),
        (True, "echo $MOTTO"),
        (False, "AI-assisted development — powered by fire."),
    ]
    tx, ty0, step, cw = 318, 84, 22, 8.45  # cw: mono advance at 13px
    t, rows, clips = 0.04, [], []
    for i, (cmd, text) in enumerate(lines):
        y = ty0 + i * step
        x0 = tx + (20 if cmd else 0)
        full = x0 - tx + len(text) * cw + 12
        typ = len(text) * (0.09 if cmd else 0.012) / T
        s, e = t, t + typ
        t = e + (0.03 if cmd else 0.05)
        clips.append(
            f'<clipPath id="l{i}"><rect x="{tx}" y="{y-16}" height="22" width="{full:.0f}">'
            f'<animate attributeName="width" values="0;0;{full:.0f};{full:.0f};0" keyTimes="0;{s:.3f};{e:.3f};.97;1" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>')
        prompt = f'<text class="mono" x="{tx}" y="{y}" font-size="14" fill="{P}">❯</text>' if cmd else ""
        rows.append(f'<g clip-path="url(#l{i})">{prompt}<text class="mono" x="{x0}" y="{y}" font-size="14" fill="{C if cmd else O}">{text}</text></g>')
    last_y = ty0 + len(lines) * step

    ring_ticks = "".join(
        f'<line x1="{cx}" y1="{cy-124}" x2="{cx}" y2="{cy-(118 if k % 3 else 112)}" transform="rotate({k*10} {cx} {cy})"/>' for k in range(36))

    body = f"""{frame(W, H, 10)}
<!-- portrait -->
<circle cx="{cx}" cy="{cy}" r="112" fill="#FF5A1F" opacity=".25" filter="url(#soft)">
  <animate attributeName="opacity" values=".15;.4;.15" dur="3s" repeatCount="indefinite"/></circle>
<g clip-path="url(#portrait)">
  <rect x="{cx-106}" y="{cy-106}" width="212" height="212" fill="#000"/>
  <image href="{b64('dragon-head.webp','image/webp')}" x="{cx-112}" y="{cy-110}" width="224" height="224">
    <animateTransform attributeName="transform" type="scale" values="1;1.04;1" dur="6s" repeatCount="indefinite" additive="sum"/>
    <animateTransform attributeName="transform" type="translate" values="0 0;-6 -5;0 0" dur="6s" repeatCount="indefinite" additive="sum"/>
  </image>
</g>
<circle cx="{cx}" cy="{cy}" r="106" fill="none" stroke="{GOLD}" stroke-width="2" filter="url(#glow)"/>
<g stroke="{AMBER}" stroke-width="1.4" opacity=".8">{ring_ticks}
  <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></g>
<circle cx="{cx}" cy="{cy}" r="131" fill="none" stroke="{ORANGE}" stroke-width="1.2" stroke-dasharray="3 9 40 9" opacity=".7">
  <animateTransform attributeName="transform" type="rotate" values="360 {cx} {cy};0 {cx} {cy}" dur="24s" repeatCount="indefinite"/></circle>
<g filter="url(#glow)">{embers(rng, 22, lambda r: (cx + r.uniform(-100, 100), cy + r.uniform(60, 120)), rise=(60, 140), dur=(2, 4))}</g>

<!-- terminal -->
<rect x="292" y="22" width="680" height="248" rx="10" fill="#0A0201" stroke="#5A1500"/>
<path d="M292,50 V32 a10,10 0 0 1 10,-10 H962 a10,10 0 0 1 10,10 V50 Z" fill="#1C0502"/>
<circle cx="312" cy="36" r="5" fill="#FF5F57"/><circle cx="330" cy="36" r="5" fill="#FEBC2E"/><circle cx="348" cy="36" r="5" fill="#28C840"/>
<text class="mono" x="632" y="40" text-anchor="middle" font-size="12" fill="#B07A5A">hungbil@forge: ~</text>
{''.join(rows)}
<text class="mono" x="{tx}" y="{last_y}" font-size="14" fill="{P}">❯</text>
<rect x="{tx+20}" y="{last_y-12}" width="8" height="15" fill="{GOLD}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>
"""
    defs = (f'<clipPath id="portrait"><circle cx="{cx}" cy="{cy}" r="105"/></clipPath>'
            '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>'
            + "".join(clips))
    return svg_doc(W, H, "About HungBil", body, defs)


LANG = {"Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Jupyter Notebook": "#DA5B0B"}
STAR = "M0,-7 L2.1,-2.2 L7,-2.2 L3,1 L4.4,6 L0,3.1 L-4.4,6 L-3,1 L-7,-2.2 L-2.1,-2.2 Z"
FLAME = "M0,-30 C10,-16 18,-8 14,6 C11,16 4,20 0,20 C-4,20 -11,16 -14,6 C-17,-4 -10,-10 -6,-18 C-4,-10 -2,-6 2,-4 C4,-12 2,-20 0,-30 Z"


def card(title, desc, lang, stars, seed):
    rng = random.Random(seed)
    W, H = 480, 150
    lines = "".join(f'<text class="mono" x="24" y="{76 + i*20}" font-size="12.5" fill="#E9C9B2">{d}</text>' for i, d in enumerate(desc))
    star = (f'<g transform="translate({W-92} 127)"><path d="{STAR}" fill="{GOLD}"/></g>'
            f'<text class="t" x="{W-80}" y="131" font-size="13" fill="#FFE2B0">{stars}</text>') if stars else ""
    body = f"""{frame(W, H, 7 + seed % 3)}
<g transform="translate(24 30)" fill="none" stroke="{AMBER}" stroke-width="1.6" stroke-linejoin="round">
  <path d="M0,0 H11 a3,3 0 0 1 3,3 V18 H3 a3,3 0 0 0 -3,3 Z"/><path d="M0,21 a3,3 0 0 1 3,-3"/></g>
<text class="t" x="48" y="47" font-size="19" fill="url(#title)">{title}</text>
<line x1="24" y1="58" x2="{W-80}" y2="58" stroke="url(#rule)" stroke-width="1"/>
{lines}
<circle cx="30" cy="127" r="6" fill="{LANG[lang]}"/>
<text class="t" x="44" y="131" font-size="13" fill="#E9C9B2">{lang}</text>
{star}
<g transform="translate({W-44} 48)" filter="url(#glow)">
  <path d="{FLAME}" fill="url(#flame)">
    <animateTransform attributeName="transform" type="scale" values="1 1;1.06 .92;.95 1.08;1 1" dur="1.3s" repeatCount="indefinite"/></path>
  <path d="{FLAME}" fill="#FFF1B8" transform="translate(0 8) scale(.45)" opacity=".9">
    <animate attributeName="opacity" values=".9;.5;1;.9" dur=".9s" repeatCount="indefinite"/></path>
</g>
<g filter="url(#glow)">{embers(rng, 7, lambda r: (W - 44 + r.uniform(-12, 12), 48 + r.uniform(-20, 0)), rise=(20, 45), drift=(-10, 10), size=(.6, 1.6), dur=(1.2, 2.4))}</g>
"""
    defs = (f'<linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="#FFF6C9"/><stop offset=".6" stop-color="{GOLD}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>'
            f'<linearGradient id="flame" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{RED}"/><stop offset=".5" stop-color="{ORANGE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>')
    return svg_doc(W, H, title, body, defs)


def footer():
    rng = random.Random(5)
    W, H = 1000, 130

    def tongues(n, color, hmin, hmax, wmin, wmax):
        out = []
        for k in range(n):
            x = (k + rng.uniform(-.3, .3)) * W / (n - 1)
            sx, sy = rng.uniform(wmin, wmax), rng.uniform(hmin, hmax)
            d = rng.uniform(.9, 1.8)
            out.append(
                f'<g transform="translate({x:.0f} {H})"><g><path d="{FLAME}" transform="translate(0 -20)" fill="{color}"/>'
                f'<animateTransform attributeName="transform" type="scale" values="{sx:.2f} {sy:.2f};{sx*.85:.2f} {sy*1.3:.2f};{sx*1.05:.2f} {sy*.8:.2f};{sx:.2f} {sy:.2f}" '
                f'dur="{d:.2f}s" begin="-{rng.uniform(0, 2):.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/></g></g>')
        return "".join(out)

    body = f"""<g mask="url(#edges)">
<rect y="{H-40}" width="{W}" height="40" fill="url(#base)"/>
<g filter="url(#soft)" opacity=".85">{tongues(26, RED, 1.3, 2.2, 1.6, 2.4)}</g>
<g filter="url(#soft2)">{tongues(34, "url(#fl)", 1.0, 1.9, 1.1, 1.6)}</g>
<g opacity=".6" filter="url(#soft2)">{tongues(40, "#FFE9A0", .35, .75, .5, .8)}</g>
<g filter="url(#glow)">{embers(rng, 34, lambda r: (r.uniform(0, W), H - r.uniform(20, 60)), rise=(30, 70), dur=(1.4, 3))}</g>
</g>
<text class="mono" x="{W/2}" y="26" text-anchor="middle" font-size="13" letter-spacing="3" fill="#F08A2C">THANKS FOR STOPPING BY — KEEP THE FIRE BURNING
  <animate attributeName="opacity" values=".6;1;.6" dur="3s" repeatCount="indefinite"/></text>"""
    defs = (f'<linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset=".6" stop-color="{AMBER}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
            f'<linearGradient id="base" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ORANGE}" stop-opacity="0"/><stop offset="1" stop-color="{GOLD}" stop-opacity=".8"/></linearGradient>'
            '<linearGradient id="edgeG" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="edges" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#edgeG)"/></mask>'
            '<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>'
            '<filter id="soft2" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="1.2"/></filter>')
    return svg_doc(W, H, "Footer", body, defs)


PROJECTS = {
    "ai-test": ("AI-TEST", ["Self-hosted quiz app for AI exam prep:", "600 questions, answers, explanations."], "JavaScript", 15),
    "ai-log-hook": ("AI-Log-Hook", ["Git pre-push gate that makes teams log", "their AI usage. Zero dependencies."], "Python", 10),
    "scamgraph": ("ScamGraph-Expert-Agents", ["Graph + LLM agents that flag risky", "transfers and assist fraud investigation."], "Jupyter Notebook", 0),
    "di-san": ("Di-San-Viet-Nam", ["Vietnamese heritage explorer: 3D models,", "interactive map, AI storytelling."], "TypeScript", 0),
}

if __name__ == "__main__":
    out = {"header.svg": header(), "about.svg": about(), "footer.svg": footer()}
    for i, (slug, p) in enumerate(PROJECTS.items()):
        out[f"card-{slug}.svg"] = card(*p, seed=i + 1)
    for name, svg in out.items():
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"{name:28} {len(svg.encode()) // 1024:>4} KB")
