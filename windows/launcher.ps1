
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
