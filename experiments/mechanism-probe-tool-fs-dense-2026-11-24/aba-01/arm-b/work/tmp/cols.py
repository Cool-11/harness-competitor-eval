import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
def dark(p): return sum(p)/3 < 128
textrows=[(38,59),(129,150),(187,203),(227,243),(267,283),(307,323),(347,363),(387,403),(427,443),(467,483),(507,523),(547,563),(587,603),(627,643)]
cols=[0]*w
for (y0,y1) in textrows:
    for x in range(w):
        cols[x]+=sum(1 for y in range(y0,y1+1) if dark(img[y][x]))
cruns=[];inrun=False
for x,c in enumerate(cols):
    if c>0 and not inrun: start=x;inrun=True
    if c==0 and inrun: cruns.append((start,x-1));inrun=False
if inrun: cruns.append((start,w-1))
print(cruns)
