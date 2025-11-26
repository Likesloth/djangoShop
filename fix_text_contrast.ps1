$rootPath = "e:\work\year 4 ss1\Python web\djangoShop\mywebsite\myapp\templates"
$files = Get-ChildItem -Path $rootPath -Recurse -Include *.html

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false
    
    # Fix text colors for better contrast
    
    # 1. Change gray-600 text to darker shades for readability
    if ($content -match 'text-gray-400') {
        $content = $content -replace 'placeholder-gray-400', 'placeholder-gray-500'
        $modified = $true
    }
    
    # 2. Ensure text on white cards/backgrounds is dark
    # Keep text-gray-600 as is (now maps to #404040 via CSS)
    # Keep text-gray-700 as is (now maps to #1a1a1a via CSS)
    # Keep text-gray-800 as is (now maps to #000000 via CSS)
    
    # 3. Fix text in dark hero sections - ensure it's white
    if ($content -match 'text-white/90') {
        # Already good - text-white/90 will be white with 90% opacity
        $modified = $false
    }
    
    # Fix any remaining low-contrast text colors
    if ($content -match 'text-gray-300(?![0-9])'  -and $content -notmatch 'bg-white') {
        # text-gray-300 is too light on dark backgrounds, change to white
        $content = $content -replace 'text-gray-300(?![0-9])', 'text-white'
        $modified = $true
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content
        Write-Host "Updated text colors in: $($file.FullName)"
    }
}

Write-Host "Text color contrast updates complete!"
