$rootPath = "e:\work\year 4 ss1\Python web\djangoShop\mywebsite\myapp\templates"
$files = Get-ChildItem -Path $rootPath -Recurse -Include *.html

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false
    
    # Replace gradient patterns
    if ($content -match 'from-indigo to-purple-500' -or 
        $content -match 'from-lavender via-pink to-peach' -or
        $content -match 'from-pink/30 to-lavender/30' -or
        $content -match 'from-lavender') {
        
        $content = $content -replace 'from-indigo to-purple-500', 'from-black to-gray-900'
        $content = $content -replace 'from-lavender via-pink to-peach', 'from-gray-200 via-gray-300 to-gray-400'
        $content = $content -replace 'bg-gradient-to-r from-pink/30 to-lavender/30', 'bg-gray-100'
        $content = $content -replace 'bg-gradient-to-br from-pink/30 to-lavender/30', 'bg-gray-100'
        $content = $content -replace 'hover:from-pink/50 hover:to-lavender/50', 'hover:bg-gray-200'
        $content = $content -replace 'from-lavender/20 to-pink/20', 'from-gray-100 to-gray-200'
        $content = $content -replace 'from-lavender to-pink', 'from-gray-700 to-gray-900'
        $content = $content -replace 'from-lavender/10 to-pink/10', 'from-gray-50 to-gray-100'
        
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content
        Write-Host "Updated: $($file.FullName)"
    }
}

Write-Host "Gradient replacement complete!"
