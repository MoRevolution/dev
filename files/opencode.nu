# opencode.nu — opencode web lifecycle helpers for nushell
# Loaded via config.nu: source ($nu.default-config-dir | path join "opencode.nu")
# Manual control: opencode-web start | stop | restart | status | log
# Requires: opencode (brew: anomalyco/tap/opencode), bash, lsof
# Intended for macOS/WSL. Cache: ~/.cache/opencode/.

export const OPENCODE_PORT = 4096
export def _opencode-pidfile [] { $env.HOME | path join ".cache/opencode/opencode-web.pid" }
export def _opencode-log [] { $env.HOME | path join ".cache/opencode/opencode-web.log" }

def _opencode-pid-running [pid: string] {
    if ($pid !~ '^\d+$') { return false }
    let res = (^ps -p $pid | complete)
    $res.exit_code == 0
}

def _opencode-pid-is-server [pid: string] {
    if not (_opencode-pid-running $pid) { return false }
    let result = (^ps -p $pid -o command= | complete)
    $result.exit_code == 0 and ($result.stdout | str trim) =~ '(^|/)opencode web( |$)'
}

def _opencode-port-pid [port: int] {
    # Avoid matching established browser connections to this port.
    try { ^lsof -ti $":($port)" -sTCP:LISTEN | lines | first | str trim } catch { "" }
}

# Start opencode web in background (nohup daemon, survives shell exit)
export def "opencode-web start" [
] {
    let pidfile = (_opencode-pidfile)
    let log = (_opencode-log)
    let port = $OPENCODE_PORT
    let hostname = "127.0.0.1"

    if ($pidfile | path exists) {
        let pid_str = (open $pidfile | str trim)
        if (_opencode-pid-is-server $pid_str) {
            print ("opencode web already running - pid " + $pid_str + " port " + ($port | into string) + " log " + $log)
            return
        } else {
            print ("stale pidfile " + $pidfile + " pid " + $pid_str + " not running - cleaning")
            rm -f $pidfile
        }
    }

    let port_pid = (_opencode-port-pid $port)
    if ($port_pid | is-not-empty) {
        print ("port " + ($port | into string) + " already in use by pid " + $port_pid + " - run opencode-web status or opencode-web stop")
        return
    }

    mkdir ($log | path dirname)
    mkdir ($pidfile | path dirname)

    # daemonize via bash/nohup so it outlives the nushell session
    let cmd = $"nohup opencode web --port ($port) --hostname ($hostname) > '($log)' 2>&1 & echo $! > '($pidfile)'"
    ^bash -c $cmd
    sleep 0.6sec

    if ($pidfile | path exists) {
        let pid_str = (open $pidfile | str trim)
        if (_opencode-pid-is-server $pid_str) {
            print ("opencode web started - pid " + $pid_str + " on http://" + $hostname + ":" + ($port | into string) + " log " + $log)
        } else {
            print ("failed to start - check log: " + $log)
            if ($log | path exists) { ^tail -n 20 $log | print }
        }
    } else {
        print ("failed to write pidfile - check log: " + $log)
    }
}

# Stop opencode web daemon
export def "opencode-web stop" [] {
    let pidfile = (_opencode-pidfile)
    mut killed = false

    if ($pidfile | path exists) {
        let pid_str = (open $pidfile | str trim)
        if (_opencode-pid-is-server $pid_str) {
            print ("stopping opencode web pid " + $pid_str + "...")
            ^kill $pid_str
            sleep 0.5sec
            if not (_opencode-pid-running $pid_str) {
                print "stopped"
                $killed = true
            } else if (_opencode-pid-is-server $pid_str) {
                print ("pid " + $pid_str + " still running, trying kill -9...")
                ^kill -9 $pid_str
                sleep 0.3sec
                $killed = true
            } else {
                print "process exited before the stop check completed"
                $killed = true
            }
        } else {
            print ("pidfile had stale pid " + $pid_str)
        }
        rm -f $pidfile
    }

    let port_pid = (_opencode-port-pid $OPENCODE_PORT)
    if ($port_pid | is-not-empty) and not $killed and (_opencode-pid-is-server $port_pid) {
        print ("killing process on port " + ($OPENCODE_PORT | into string) + " pid " + $port_pid + "...")
        ^kill $port_pid
        sleep 0.3sec
        if ((_opencode-port-pid $OPENCODE_PORT) | is-not-empty) {
            ^kill -9 $port_pid
        }
        $killed = true
    }

    if not $killed {
        print "no opencode web process found"
    }
}

export def "opencode-web restart" [
] {
    opencode-web stop
    sleep 0.5sec
    opencode-web start
}

export def "opencode-web status" [] {
    let pidfile = (_opencode-pidfile)
    let log = (_opencode-log)
    let port = $OPENCODE_PORT

    print ("port: " + ($port | into string) + "  pidfile: " + $pidfile + "  log: " + $log + "\n")

    if ($pidfile | path exists) {
        let pid_str = (open $pidfile | str trim)
        let running = _opencode-pid-is-server $pid_str
        let status = if $running { "running" } else { "NOT running (stale)" }
        print ("pidfile pid: " + $pid_str + " - " + $status)
    } else {
        print "pidfile: not found"
    }

    let port_pid = (_opencode-port-pid $port)
    if ($port_pid | is-not-empty) {
        print ("port " + ($port | into string) + ": listening pid " + $port_pid + " - http://127.0.0.1:" + ($port | into string))
        try { ^ps -p $port_pid -o pid,command | print } catch { }
    } else {
        print ("port " + ($port | into string) + ": not listening")
    }

    if ($log | path exists) {
        print ("\nlog tail last 10 lines of " + $log + ":")
        try { ^tail -n 10 $log | print } catch { print "(empty)" }
    } else {
        print ("\nlog: not found " + $log)
    }
}

export def "opencode-web log" [
    --follow (-f)  # tail -f
    --lines (-n): int = 50
] {
    let log = (_opencode-log)
    if not ($log | path exists) {
        print ("log not found: " + $log)
        return
    }
    if $follow {
        ^tail -f $log
    } else {
        ^tail -n $lines $log | print
    }
}

export alias ocws = opencode-web start
export alias ocwk = opencode-web stop
export alias ocwr = opencode-web restart
export alias ocwst = opencode-web status
