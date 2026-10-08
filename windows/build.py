import struct,base64,pathlib,json
root=pathlib.Path(__file__).resolve().parents[1]
ps=r'''
$ErrorActionPreference='Stop'
$Host.UI.RawUI.WindowTitle='Guess Song - Local Server'
$listener=$null
try {
 $exe=[IO.File]::ReadAllBytes($env:GUESS_SONG_EXE)
 $n=[BitConverter]::ToInt32($exe,$exe.Length-8)
 $html=New-Object byte[] $n
 [Array]::Copy($exe,$exe.Length-8-$n,$html,0,$n)
 $listener=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,8000)
 try {$listener.Start()} catch {Write-Host 'Port 8000 is already in use. Close the other server, then try again.';Read-Host 'Press Enter to exit';exit 1}
 Write-Host 'Guess Song is running: http://localhost:8000/guess-song.html'
 Write-Host 'Keep this window open. Close it to stop the server.'
 Write-Host 'Songs are saved in your browser. Internet is required for YouTube.'
 Start-Process 'http://localhost:8000/guess-song.html'
 while($true){
  $client=$listener.AcceptTcpClient()
  try {
   $client.ReceiveTimeout=3000
   $stream=$client.GetStream()
   $reader=[IO.StreamReader]::new($stream,[Text.Encoding]::ASCII,$false,1024,$true)
   $line=$reader.ReadLine()
   if(!$line){continue}
   $parts=$line.Split(' ')
   $bytesRead=0
   do {$header=$reader.ReadLine();$bytesRead+=$header.Length;if($bytesRead -gt 16384){throw 'Request too large'}} while($header)
   $path=$parts[1].Split('?')[0]
   $ok=$parts[0] -in @('GET','HEAD') -and $path -in @('/','/guess-song.html')
   if($ok){$body=$html;$status='200 OK';$type='text/html; charset=utf-8'} else {$body=[Text.Encoding]::UTF8.GetBytes('Not found');$status='404 Not Found';$type='text/plain'}
   $head=[Text.Encoding]::ASCII.GetBytes("HTTP/1.1 $status`r`nContent-Type: $type`r`nContent-Length: $($body.Length)`r`nConnection: close`r`nCache-Control: no-store`r`nReferrer-Policy: strict-origin-when-cross-origin`r`n`r`n")
   $stream.Write($head,0,$head.Length)
   if($parts[0] -ne 'HEAD'){$stream.Write($body,0,$body.Length)}
  } catch {} finally {$client.Dispose()}
 }
} catch {Write-Host $_.Exception.Message;Read-Host 'Press Enter to exit'} finally {if($listener){$listener.Stop()}}
'''
cmd=('powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode()).encode()+b'\0'
b=bytearray();labels={};fix=[]
def emit(x): b.extend(bytes.fromhex(x))
def label(x): labels[x]=len(b)
def addr(x): fix.append((len(b),x,'abs'));b.extend(b'\0'*4)
def push(x):emit('68');addr(x)
def call(x):emit('FF15');addr(x)
def jump(op,x):emit(op);fix.append((len(b),x,'rel'));b.append(0)
push('size');push('buffer');emit('6A00');call('GetModuleFileNameW')
push('buffer');push('env');call('SetEnvironmentVariableW')
emit('BE');addr('buffer');emit('89F7');label('scan');emit('66833F00');jump('74','back');emit('83C702');jump('EB','scan')
label('back');emit('83EF0266833F5C');jump('75','back');emit('66C707000056');call('SetCurrentDirectoryW')
emit('6A01');push('command');call('WinExec');emit('6A00');call('ExitProcess')
def align(n):b.extend(b'\0'*((-len(b))%n))
align(4);label('imports');importpos=len(b);b.extend(b'\0'*40)
funcs=['GetModuleFileNameW','SetEnvironmentVariableW','SetCurrentDirectoryW','WinExec','ExitProcess']
label('ilt');ilt=len(b);b.extend(b'\0'*24);label('iat');iat=len(b);b.extend(b'\0'*24)
label('dll');b.extend(b'KERNEL32.dll\0')
for i,f in enumerate(funcs):
 align(2);label('hint'+f);b.extend(b'\0\0'+f.encode()+b'\0');labels[f]=iat+i*4
label('env');b.extend('GUESS_SONG_EXE\0'.encode('utf-16le'));label('command');b.extend(cmd);align(4);label('buffer');b.extend(b'\0'*2048)
rva=lambda x:0x1000+labels[x]
struct.pack_into('<IIIII',b,importpos,rva('ilt'),0,0,rva('dll'),rva('iat'))
for i,f in enumerate(funcs):struct.pack_into('<I',b,ilt+i*4,rva('hint'+f));struct.pack_into('<I',b,iat+i*4,rva('hint'+f))
labels['size']=1024-0x401000
for pos,name,kind in fix:
 if kind=='abs':struct.pack_into('<I',b,pos,0x401000+labels[name])
 else:struct.pack_into('<b',b,pos,labels[name]-(pos+1))
vs=len(b);align(512);raw=len(b)
h=bytearray(512);h[:2]=b'MZ';struct.pack_into('<I',h,0x3c,0x80);h[0x80:0x84]=b'PE\0\0'
struct.pack_into('<HHIIIHH',h,0x84,0x14c,1,0,0,0,224,0x103)
o=0x98;struct.pack_into('<HBBIIIIII',h,o,0x10b,1,0,raw,0,0,0x1000,0x1000,0)
struct.pack_into('<III',h,o+28,0x400000,0x1000,0x200)
struct.pack_into('<HHHHHH',h,o+40,6,0,0,0,6,0)
struct.pack_into('<IIIIHHIIIIII',h,o+52,0,(0x1000+vs+0xfff)&~0xfff,512,0,3,0x100,0x100000,0x1000,0x100000,0x1000,0,16)
struct.pack_into('<II',h,o+96+8,rva('imports'),40)
struct.pack_into('<II',h,o+96+12*8,rva('iat'),24)
s=o+224;h[s:s+8]=b'.text\0\0\0';struct.pack_into('<IIIIIIHHI',h,s+8,vs,0x1000,raw,512,0,0,0,0,0xe0000060)
page=(root/'index.html').read_text(encoding='utf-8')
tracks=json.loads((root/'songs.json').read_text(encoding='utf-8'))
page=page.replace("fetch('./songs.json').then(r=>{if(!r.ok)throw Error();return r.json()})",'Promise.resolve('+json.dumps(tracks,ensure_ascii=False).replace('</','<\\/')+')')
html=page.encode('utf-8');out=root/'windows'/'GuessSong.exe';out.write_bytes(h+b+html+struct.pack('<I',len(html))+b'GSG1')
(root/'windows'/'launcher.ps1').write_text(ps,encoding='utf-8')
assert out.read_bytes()[-8:-4]==struct.pack('<I',len(html))
print('Built',out,'bytes',out.stat().st_size)
