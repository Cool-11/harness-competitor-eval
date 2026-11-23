g=[list(map(int,l.split())) for l in open('/work/gray.txt')]
h=len(g); w=len(g[0])
dark=[[1 if v<128 else 0 for v in r] for r in g]
def runs(vals,thr=1):
    out=[]; s=None
    for i,v in enumerate(vals):
        if v>=thr and s is None: s=i
        if v<thr and s is not None: out.append((s,i-1)); s=None
    if s is not None: out.append((s,len(vals)-1))
    return out
bands=[(45,72),(149,151),(174,201),(225,227),(252,278),(310,336),(368,394),(426,452),(484,510),(542,568),(603,605)]
for a,b in bands:
    if b-a<10: continue
    colp=[sum(dark[y][x] for y in range(a,b+1)) for x in range(w)]
    rr=runs(colp)
    print('ROW',a,b,'segments',len(rr))
    print([(x,y) for x,y in rr])
