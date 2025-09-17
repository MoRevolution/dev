local home = os.getenv("USERPROFILE") -- Use "HOME" on Unix-like systems
load(io.popen('oh-my-posh init cmd --config ' .. home .. '\\zsh-ish.omp.json'):read("*a"))()
