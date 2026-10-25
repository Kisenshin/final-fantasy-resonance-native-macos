"""Small unkeyed BLAKE3 reference for validating owned IoStore chunk metadata."""
import struct
IV = [0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
PERM = [2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
MASK = 0xffffffff

def rotr(x,n): return ((x >> n) | (x << (32-n))) & MASK

def compress(cv, block, counter, length, flags):
 s = cv[:] + IV[:4] + [counter & MASK, counter >> 32, length, flags]
 m = block[:]
 def g(a,b,c,d,x,y):
  s[a]=(s[a]+s[b]+x)&MASK; s[d]=rotr(s[d]^s[a],16)
  s[c]=(s[c]+s[d])&MASK; s[b]=rotr(s[b]^s[c],12)
  s[a]=(s[a]+s[b]+y)&MASK; s[d]=rotr(s[d]^s[a],8)
  s[c]=(s[c]+s[d])&MASK; s[b]=rotr(s[b]^s[c],7)
 for _ in range(7):
  g(0,4,8,12,m[0],m[1]);g(1,5,9,13,m[2],m[3]);g(2,6,10,14,m[4],m[5]);g(3,7,11,15,m[6],m[7])
  g(0,5,10,15,m[8],m[9]);g(1,6,11,12,m[10],m[11]);g(2,7,8,13,m[12],m[13]);g(3,4,9,14,m[14],m[15])
  m=[m[i] for i in PERM]
 return [s[i]^s[i+8] for i in range(8)] + [s[i+8]^cv[i] for i in range(8)]

def output_cv(o): return compress(*o)[:8]

def leaf(data,counter):
 cv=IV[:];blocks=[data[i:i+64] for i in range(0,len(data),64)] or [b'']
 for i,b in enumerate(blocks):
  flags=(1 if i==0 else 0)|(2 if i==len(blocks)-1 else 0)
  o=(cv,list(struct.unpack('<16I',b.ljust(64,b'\0'))),counter,len(b),flags)
  cv=output_cv(o)
 return o

def digest(data):
 chunks=[data[i:i+1024] for i in range(0,len(data),1024)] or [b'']
 def tree(start,count):
  if count==1:return leaf(chunks[start],start)
  left_count=1 << ((count-1).bit_length()-1)
  left=output_cv(tree(start,left_count));right=output_cv(tree(start+left_count,count-left_count))
  return (IV[:],left+right,0,64,4)
 cv,block,_,length,flags=tree(0,len(chunks))
 return struct.pack('<16I',*compress(cv,block,0,length,flags|8))[:32]

assert digest(b'').hex()=='af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'
assert digest(b'abc').hex()=='6437b3ac38465133ffb63b75273a8db548c558465d79db03fd359c6cd5bd9d85'
