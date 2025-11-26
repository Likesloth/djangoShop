$file = "mywebsite/myapp/templates/myapp/layout/base.html"
$content = Get-Content $file -Raw

# Reapply all black and white theme CSS changes

# 1. Tailwind colors
$content = $content -replace "primary: '#1A374D'", "primary: '#000000'"
$content = $content -replace "secondary: '#406882'", "secondary: '#1a1a1a'"
$content = $content -replace "accent: '#6998AB'", "accent: '#404040'"
$content = $content -replace "muted: '#B1D0E0'", "muted: '#666666'"

# Add new light colors  
$content = $content -replace "muted: '#666666',", "muted: '#666666',     // medium gray`r`n" +
"              light: '#e5e5e5',     // light gray`r`n" +
"              lighter: '#f5f5f5',   // very light gray"

# 2. Color mappings
$content = $content -replace "indigo: '#1A374D'", "indigo: '#000000'"
$content = $content -replace "'indigo-500': '#1A374D'", "'indigo-500': '#000000'"
$content = $content -replace "purple: \{ '500': '#406882' \}", "purple: { '500': '#1a1a1a' }"
$content = $content -replace "pink: '#6998AB'", "pink: '#404040'"
$content = $content -replace "lavender: '#B1D0E0'", "lavender: '#666666'"
$content = $content -replace "peach: '#B1D0E0'", "peach: '#e5e5e5'"
$content = $content -replace "'peach-300': '#B1D0E0'", "'peach-300': '#e5e5e5'"
$content = $content -replace "'peach-400': '#B1D0E0'", "'peach-400': '#d4d4d4'"

# 3. Background gradient  
$content = $content -replace "background: linear-gradient\(135deg, #B1D0E0 0%, #6998AB 50%, #406882 100%\)", "background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #2d2d2d 100%)"

# 4. Surface colors
$content = $content -replace ".bg-white \{ background-color: #B1D0E0", ".bg-white { background-color: #ffffff"
$content = $content -replace "rgba\(177, 208, 224,", "rgba(255, 255, 255,"
$content = $content -replace "background-color: rgba\(245, 245, 245", "background-color: rgba(255, 255, 255"

# 5. Borders
$content = $content -replace "border-color: #1A374D", "border-color: #e5e5e5"
$content = $content -replace "border-color: rgba\(26, 55, 77", "border-color: rgba(229, 229, 229"

# 6. Add text contrast rules before closing style tag
$textContrastCSS = @"


    /* TEXT CONTRAST ENHANCEMENTS */
    body { color: #f5f5f5; }
    section { color: #f5f5f5; }
    .bg-white, .bg-white\/90, .bg-gray-50, .bg-gray-100 { color: #000000 !important; }
    .text-gray-100 { color: #f5f5f5 !important; }
    .text-gray-600 { color: #404040 !important; }
    .text-gray-700 { color: #1a1a1a !important; }
    .text-gray-800, .text-gray-900 { color: #000000 !important; }
    .bg-black, .bg-gray-800, .bg-gray-900 { color: #ffffff !important; }
    .text-indigo { color: #000000 !important; }
    nav.bg-white\/80 .text-gray-700 { color: #000000 !important; }
"@

$content = $content -replace "    </style>", "$textContrastCSS`r`n    </style>"

Set-Content -Path $file -Value $content
Write-Host "Applied black and white theme CSS changes successfully!"
