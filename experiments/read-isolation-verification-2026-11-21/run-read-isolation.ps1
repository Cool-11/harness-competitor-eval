$ErrorActionPreference = 'Continue'
$name = "hev-read-isolation-verify"
$image = "harness-p0-dsh:20261120"
$repo = "F:\for-project-new\harness-competitor-eval"
$outdir = Join-Path $repo "experiments\read-isolation-verification-2026-11-21"
New-Item -ItemType Directory -Force -Path $outdir | Out-Null

docker rm -f $name 2>$null | Out-Null

docker run -d --name $name --network none --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 2g --cpus 1 $image sleep infinity
if ($LASTEXITCODE -ne 0) { Write-Output "RUN_FAILED"; exit 1 }

docker inspect $name | Out-File -Encoding utf8 (Join-Path $outdir "container-inspect.json")

docker cp (Join-Path $repo "tmp\read-isolation-verify.py") "${name}:/verify.py"
if ($LASTEXITCODE -ne 0) { Write-Output "CP_FAILED"; docker rm -f $name 2>$null | Out-Null; exit 1 }

$result = docker exec $name python3 /verify.py
$result | Out-File -Encoding utf8 (Join-Path $outdir "read-isolation-result.json")

Write-Output "===RESULT_START==="
$result
Write-Output "===RESULT_END==="

docker rm -f $name 2>$null | Out-Null
