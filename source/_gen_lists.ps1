$enc = New-Object System.Text.UTF8Encoding($false)

function Write-Md($path, $lines) {
    [System.IO.File]::WriteAllText($path, ($lines -join "`n"), $enc)
}

# ---------- LeetCode study plans (Hot 100 / Interview 150) ----------
function Build-StudyPlan($rawPath, $outPath, $heading, $sourceUrl) {
    $d = (Get-Content $rawPath -Raw | ConvertFrom-Json).data.studyPlanV2Detail
    $total = 0
    foreach ($g in $d.planSubGroups) { $total += $g.questions.Count }
    $L = [System.Collections.Generic.List[string]]::new()
    $L.Add("# $heading")
    $L.Add("")
    $L.Add("> Source: [$sourceUrl]($sourceUrl) - fetched via LeetCode GraphQL API on 2026-06-09.")
    $L.Add("> Total: **$total** problems across **$($d.planSubGroups.Count)** topic groups.")
    $L.Add("")
    $n = 0
    foreach ($g in $d.planSubGroups) {
        $L.Add("## $($g.name) ($($g.questions.Count))")
        $L.Add("")
        $L.Add("| # | ID | Problem | Difficulty | Link |")
        $L.Add("|---|----|---------|------------|------|")
        foreach ($q in $g.questions) {
            $n++
            $url = "https://leetcode.com/problems/$($q.titleSlug)/"
            $L.Add("| $n | $($q.questionFrontendId) | $($q.title) | $($q.difficulty) | [link]($url) |")
        }
        $L.Add("")
    }
    Write-Md $outPath $L
    Write-Output "Wrote $outPath  ($total problems)"
}

Build-StudyPlan ".\source\_hot100_raw.json" ".\source\Hot100.md" "LeetCode Hot 100 (Top 100 Liked)" "https://leetcode.com/studyplan/top-100-liked/"
Build-StudyPlan ".\source\_int150_raw.json" ".\source\Leetcode150.md" "LeetCode Top Interview 150" "https://leetcode.com/studyplan/top-interview-150/"

# ---------- NeetCode 250 ----------
$p = (Get-Content ".\source\_neetcode250_raw.json" -Raw | ConvertFrom-Json).problems
$L = [System.Collections.Generic.List[string]]::new()
$L.Add("# NeetCode 250")
$L.Add("")
$L.Add("> Source: [neetcode.io/practice](https://neetcode.io/practice) (list=neetcode250), via dataset [ascherj/neetcode-250-guide](https://github.com/ascherj/neetcode-250-guide) - fetched 2026-06-09.")
$L.Add("> Total: **$($p.Count)** problems. NeetCode 250 = NeetCode 150 + 100 additional problems.")
$L.Add("")
$cats = [System.Collections.Generic.List[string]]::new()
foreach ($x in $p) { if (-not $cats.Contains($x.category)) { $cats.Add($x.category) } }
$n = 0
foreach ($c in $cats) {
    $items = $p | Where-Object { $_.category -eq $c }
    $L.Add("## $c ($($items.Count))")
    $L.Add("")
    $L.Add("| # | Problem | Difficulty | LeetCode |")
    $L.Add("|---|---------|------------|----------|")
    foreach ($x in $items) {
        $n++
        $L.Add("| $n | $($x.name) | $($x.difficulty) | [link]($($x.leetcode_url)) |")
    }
    $L.Add("")
}
Write-Md ".\source\Neetcode250.md" $L
Write-Output "Wrote .\source\Neetcode250.md  ($($p.Count) problems)"
