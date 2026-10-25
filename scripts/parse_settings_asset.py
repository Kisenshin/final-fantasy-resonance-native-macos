"""Focused checked reader for this game's Zen FPS options DataTable."""
import struct

def name_map(data):
 n, _ = struct.unpack_from('<II', data, 0x3c)
 at = 0x4c + n*8
 hs = [int.from_bytes(data[at+2*i:at+2*i+2], 'big') for i in range(n)]
 at += n*2
 names = []
 for h in hs:
  size = (h & 0x7fff)*(2 if h & 0x8000 else 1)
  names.append(data[at:at+size].decode('utf-16-le' if h & 0x8000 else 'utf-8'))
  at += size
 return names

def fstring(data, at):
 n = struct.unpack_from('<i', data, at)[0];at+=4
 size = -2*n if n < 0 else n
 raw = data[at:at+size]
 assert len(raw)==size
 value=raw.decode('utf-16-le' if n<0 else 'utf-8').rstrip('\0')
 return value,at+size

def fps_table(data):
 header = struct.unpack_from('<I',data,4)[0]
 export_map = struct.unpack_from('<I',data,0x20)[0]
 bundles = struct.unpack_from('<I',data,0x24)[0]
 assert bundles-export_map==72, 'Expected exactly one 72-byte export.'
 serial_offset,serial_size=struct.unpack_from('<QQ',data,export_map)
 assert serial_offset==0 and header+serial_size+4==len(data)
 assert data[-4:]==bytes.fromhex('c1832a9e')
 # DataTable UObject unversioned header, RowStruct package index, zero GUID.
 assert data[header:header+10]==bytes.fromhex('0003faffffff00000000')
 count_at=header+10;count=struct.unpack_from('<I',data,count_at)[0];at=count_at+4
 names=name_map(data);rows=[]
 for i in range(count):
  start=at;ni,number=struct.unpack_from('<II',data,at);at+=8
  assert names[ni]=='NewRow' and number==i
  assert data[at:at+3]==bytes.fromhex('800b0c');at+=3
  flags=struct.unpack_from('<I',data,at)[0];at+=4
  assert flags==0
  history=data[at];at+=1
  if history==0:
   ns,at=fstring(data,at);key,at=fstring(data,at);label,at=fstring(data,at)
  elif history==11:
   table_id,table_number=struct.unpack_from('<II',data,at);at+=8
   assert table_number==0
   ns=names[table_id];key,at=fstring(data,at);label=key
  else: raise ValueError(f'Unexpected FText history {history}')
  # Nested optional value struct uses its unchanged all-default serialization.
  assert data[at:at+7]==bytes.fromhex('800301ffffffff');at+=7
  rows.append({'row_number':number,'start':start,'end':at,'label':label,'history':history,'namespace':ns,'key':key})
 assert at==header+serial_size
 return {'header_size':header,'export_map_offset':export_map,'serial_size':serial_size,'count_offset':count_at,'row_count':count,'rows':rows}
