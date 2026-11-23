import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
def dark(p): return sum(p)/3 < 128
y0,y1=int(sys.argv[1]),int(sys.argv[2])
xs=[int(v) for v in sys.argv[3:]]
# split by runs
runs=[];inrun=False
for x in range(w):
    c=sum(1 for y in range(y0,y1+1) if dark(img[y][x]))
    if c>0 and not inrun: start=x;inrun=True
    if c==0 and inrun: runs.append((start,x-1));inrun=False
if inrun: runs.append((start,w-1))
for i,(a,b) in enumerate(runs):
    print(f'--- glyph {i}: x{a}-{b} w{b-a+1} ---')
    for y in range(y0,y1+1):
        print(''.join('#' if dark(img[y][x]) else '.' for x in range(a,b+1)))
