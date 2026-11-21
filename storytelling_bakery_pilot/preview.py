from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).resolve().parent
D=Path('/mnt/data')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for shot,top,lines in (
    ('queue','08:47  •  TEXT FROM MY BOSS',['“WHY IS THE','DOOR LOCKED?”']),
    ('keys','I WAS ALREADY OUTSIDE',['I HAD','THE KEYS.']),
):
    im=Image.new('RGBA',(672,1194))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((46,125,585,180),20,fill='#182538')
    d.text((65,141),top,font=ImageFont.truetype(font,24),fill='#ffdf96')
    d.rounded_rectangle((38,795,581,1004),27,fill='#101b2b',outline='#67c8be',width=3)
    for i,line in enumerate(lines):
        d.text((62,820+73*i),line,font=ImageFont.truetype(font,52),fill='#fff5dc')
    im.save(p/(shot+'-type.png'))
graphs=[]
inputs=[]
for i,shot in enumerate(('queue','keys')):
    inputs+=['-i',str(p/(shot+'.png')),'-i',str(p/(shot+'-type.png'))]
    frames=[90,75][i]
    graphs+=[f'[{2*i}:v]scale=1344:2388,zoompan=z=1.04+on*0.001:x=iw/2-iw/zoom/2:y=ih/2-ih/zoom/2:d={frames}:s=672x1194:fps=30[z{i}]',
             f'[z{i}][{2*i+1}:v]overlay,scale=1080:1920,setsar=1[v{i}]']
graphs.append('[v0][v1]concat=n=2:v=1:a=0[out]')
subprocess.run(['ffmpeg','-hide_banner','-v','error','-y','-filter_complex_threads','2',*inputs,'-filter_complex',';'.join(graphs),'-map','[out]','-c:v','libx264','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',str(D/'Storytelling-Vibe-Bakery-Opening.mp4')],check=True)
