import struct, zlib

def load(path):
    d=open(path,'rb').read()
    pos=8; idat=b''
    while pos<len(d):
        ln=struct.unpack('>I',d[pos:pos+4])[0]; typ=d[pos+4:pos+8]
        data=d[pos+8:pos+8+ln]
        if typ==b'IHDR':
            w,h,bd,ct,comp,filt,inter=struct.unpack('>IIBBBBB',data)
        elif typ==b'IDAT': idat+=data
        pos+=12+ln
    raw=zlib.decompress(idat)
    assert bd==8 and ct==2 and inter==0
    bpp=3; stride=w*bpp
    out=bytearray(h*stride); prev=bytearray(stride)
    p=0
    for y in range(h):
        f=raw[p]; p+=1
        line=bytearray(raw[p:p+stride]); p+=stride
        if f==1:
            for i in range(bpp,stride): line[i]=(line[i]+line[i-bpp])&255
        elif f==2:
            for i in range(stride): line[i]=(line[i]+prev[i])&255
        elif f==3:
            for i in range(stride):
                a=line[i-bpp] if i>=bpp else 0
                line[i]=(line[i]+((a+prev[i])>>1))&255
        elif f==4:
            for i in range(stride):
                a=line[i-bpp] if i>=bpp else 0
                b=prev[i]; c=prev[i-bpp] if i>=bpp else 0
                pa=abs(b-c); pb=abs(a-c); pc=abs(a+b-2*c)
                pr=a if pa<=pb and pa<=pc else (b if pb<=pc else c)
                line[i]=(line[i]+pr)&255
        out[y*stride:(y+1)*stride]=line
        prev=line
    return w,h,out
