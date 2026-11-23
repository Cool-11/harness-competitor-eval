import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
def dark(p): return sum(p)/3 < 128
ys=[(38,59),(129,150),(187,203),(227,243),(267,283),(307,323),(347,363),(387,403),(427,443),(467,483),(507,523),(547,563),(587,603),(627,643)]
for (y0,y1) in ys:
    runs=[];inrun=False
    for x in range(w):
        c=sum(1 for y in range(y0,y1+1) if dark(img[y][x]))
        if c>0 and not inrun: start=x;inrun=True
        if c==0 and inrun: runs.append((start,x-1));inrun=False
    if inrun: runs.append((start,w-1))
    print(f'y={y0}:',runs)
