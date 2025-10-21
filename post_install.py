import subprocess


def run_command(command):
    try:
        print(f"Running: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")


def main():
    commands = [
        r"clink autorun install --allusers",
        r"clink set ohmyposh.theme ~\zsh-ish.omp.json",
        r"fnm install --lts",
        r"gh auth login",
        r"git config --global alias.fd '!f() { git ls-files --others "
        r"--exclude-standard | fzf --preview \"cat {}\"; }; f'",
        r"git config --global alias.l1 'log --oneline -7'",
    ]

    for command in commands:
        run_command(command)


if __name__ == "__main__":
    main()
