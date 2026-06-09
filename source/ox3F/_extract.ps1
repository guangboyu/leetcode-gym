param([string]$HtmlPath, [string]$OutPath)

# Read raw HTML as UTF-8 (curl saved server UTF-8 bytes)
$html = [System.IO.File]::ReadAllText($HtmlPath, [System.Text.Encoding]::UTF8)

# Isolate the __NEXT_DATA__ JSON blob
$tag = '<script id="__NEXT_DATA__" type="application/json">'
$start = $html.IndexOf($tag)
if ($start -lt 0) { Write-Error "no __NEXT_DATA__ in $HtmlPath"; exit 1 }
$start += $tag.Length
$end = $html.IndexOf('</script>', $start)
$json = $html.Substring($start, $end - $start)

# Find the post body: "content":"...."  (char-scan respecting JSON escapes)
$key = '"content":"'
$ci = $json.IndexOf($key)
if ($ci -lt 0) { Write-Error "no content field"; exit 1 }
$i = $ci + $key.Length
$sb = [System.Text.StringBuilder]::new()
while ($i -lt $json.Length) {
    $c = $json[$i]
    if ($c -eq '\') {
        $n = $json[$i+1]
        switch ($n) {
            '"'  { [void]$sb.Append('"'); $i += 2 }
            '\'  { [void]$sb.Append('\'); $i += 2 }
            '/'  { [void]$sb.Append('/'); $i += 2 }
            'n'  { [void]$sb.Append("`n"); $i += 2 }
            'r'  { $i += 2 }                      # drop CR
            't'  { [void]$sb.Append("`t"); $i += 2 }
            'b'  { $i += 2 }
            'f'  { $i += 2 }
            'u'  {
                $hex = $json.Substring($i+2, 4)
                [void]$sb.Append([char][Convert]::ToInt32($hex, 16))
                $i += 6
            }
            default { [void]$sb.Append($n); $i += 2 }
        }
    }
    elseif ($c -eq '"') { break }   # unescaped closing quote -> end of string
    else { [void]$sb.Append($c); $i++ }
}

$content = $sb.ToString()
[System.IO.File]::WriteAllText($OutPath, $content, (New-Object System.Text.UTF8Encoding($false)))
$probCount = ([regex]::Matches($content, '/problems/')).Count
Write-Output "OK $OutPath  chars=$($content.Length)  /problems/ links=$probCount"
