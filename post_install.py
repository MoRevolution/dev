#!/usr/bin/env python3
"""Post-installation stuff - anything i can't do via a file copy"""
from utils import Platform, run_cmd


def main():
    platform = Platform.detect()
    print(f"Platform: {platform.value}")

    if platform == Platform.WINDOWS:
        commands = [
            ("clink autorun", "clink autorun install --allusers"),
            ("clink theme", r"clink set ohmyposh.theme ~\zsh-ish.omp.json"),
            (
                "media keys startup",
                r"powershell -Command \"$WshShell = New-Object -ComObject "
                r"WScript.Shell; $shortcut = $WshShell.CreateShortcut("
                r"\\\"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\"
                r"Startup\\Media Keys.lnk\\\"); $shortcut.TargetPath = "
                r"\\\"$env:USERPROFILE\\Documents\\AutoHotkey\\Media Keys.ahk"
                r"\\\"; $shortcut.Save()\"",
            ),
            ("fnm lts", "fnm install --lts"),
            ("gh auth", "gh auth login"),
        ]
    else:
        commands = [
            ("fnm lts", "fnm install --lts"),
            ("gh auth", "gh auth login"),
            ("zsh default", "chsh -s $(which zsh)"),
        ]

    print("\nRunning post-install commands...")
    for name, cmd in commands:
        print(f"  {name}...", end=" ")
        success, _, stderr = run_cmd(cmd)
        if success:
            print("OK")
        else:
            print(f"SKIP ({stderr[:30] if stderr else 'failed'})")

    print("\nDone!")


if __name__ == "__main__":
    main()
