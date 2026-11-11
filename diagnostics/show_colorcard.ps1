Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$imagePath = Join-Path $PSScriptRoot "colorcard.png"
$form = New-Object System.Windows.Forms.Form
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
$form.WindowState = [System.Windows.Forms.FormWindowState]::Maximized
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::Black

$picture = New-Object System.Windows.Forms.PictureBox
$picture.Image = [System.Drawing.Image]::FromFile($imagePath)
$picture.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
$picture.Dock = [System.Windows.Forms.DockStyle]::Fill
$form.Controls.Add($picture)

$form.Add_KeyDown({
    param($sender, $event)
    if ($event.KeyCode -eq [System.Windows.Forms.Keys]::Escape) {
        $form.Close()
    }
})

[void]$form.ShowDialog()
