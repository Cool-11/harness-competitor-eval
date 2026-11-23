import sys
sys.path.insert(0,'/work/tmp')
from pngread import read_png
w,h,img,ct,bd = read_png('/work/inventory.png')
def dark(p): return sum(p)/3 < 128
rows=[]
for y in range(h):
    c=sum(1 for x in range(w) if dark(img[y][x]))
    rows.append(c)
# print runs of nonzero
runs=[]
inrun=False
for y,c in enumerate(rows):
    if c>0 and not inrun: start=y; inrun=True
    if c==0 and inrun: runs.append((start,y-1,max(rows[start:y]))); inrun=False
if inrun: runs.append((start,h-1,max(rows[start:])))
print('row runs (y0,y1,maxcount):')
for r in runs: print(r)
cols=[]
for x in range(w):
    c=sum(1 for y in range(h) if dark(img[y][x]))
    cols.append(c)
cruns=[]; inrun=False
for x,c in enumerate(cols):
    if c>0 and not inrun: start=x; inrun=True
    if c==0 and inrun: cruns.append((start,x-1,max(cols[start:x]))); inrun=False
if inrun: cruns.append((start,w-1,max(cols[start:])))
print('col runs:', len(cruns))
print(cruns[:60])
