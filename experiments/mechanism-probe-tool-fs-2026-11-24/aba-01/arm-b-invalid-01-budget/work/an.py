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
rowp=[sum(r) for r in dark]
print('row bands:')
for a,b in runs(rowp):
    print(a,b,b-a+1, sum(rowp[a:b+1]))
