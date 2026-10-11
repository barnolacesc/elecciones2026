#!/usr/bin/env python3
"""Rehearse real SSH and sudo in a disposable Ubuntu container, never a VPS."""
import os
from pathlib import Path
import shutil
import subprocess
import time


def run(*arguments, succeeds=True):
    result = subprocess.run(arguments, capture_output=True, text=True)
    if (result.returncode == 0) != succeeds:
        raise RuntimeError("Unexpected result for " + arguments[0] + ": " + result.stderr)
    return result


def main():
    if not Path("/.dockerenv").exists() or os.geteuid() != 0:
        raise RuntimeError("Run only as root in the disposable test container")
    source = Path("/work/ops")
    for directory, mode in (("/opt/elecciones2026", 0o755),
                            ("/var/lib/elecciones2026", 0o700),
                            ("/usr/local/libexec", 0o755),
                            ("/etc/ssh/authorized_keys", 0o755),
                            ("/run/sshd", 0o755)):
        Path(directory).mkdir(parents=True, exist_ok=True)
        Path(directory).chmod(mode)
    for name in ("restricted_release.py", "release.py", "compose.yaml"):
        shutil.copyfile(source / name, "/opt/elecciones2026/" + name)
        Path("/opt/elecciones2026/" + name).chmod(0o644)
    for name, target in (("elecciones-release", "/usr/local/sbin/elecciones-release"),
                         ("elecciones-ssh", "/usr/local/libexec/elecciones-ssh"),
                         ("deployer.sudoers", "/etc/sudoers.d/deployer"),
                         ("deployer-sshd.conf", "/etc/ssh/sshd_config.d/00-elecciones-deployer.conf")):
        shutil.copyfile(source / name, target)
        Path(target).chmod(0o440 if name.endswith("sudoers") else 0o755 if name.startswith("elecciones") else 0o644)
    run("useradd", "--create-home", "--shell", "/bin/sh", "deployer")
    run("visudo", "-c")
    run("ssh-keygen", "-A")
    run("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", "/tmp/test-key")
    shutil.copyfile("/tmp/test-key.pub", "/etc/ssh/authorized_keys/deployer")
    Path("/etc/ssh/authorized_keys/deployer").chmod(0o644)
    run("/usr/sbin/sshd", "-t")
    configuration = run("/usr/sbin/sshd", "-T", "-C", "user=deployer,host=localhost,addr=127.0.0.1").stdout
    for setting in ("forcecommand /usr/local/libexec/elecciones-ssh", "disableforwarding yes",
                    "permittty no", "permituserrc no", "passwordauthentication no",
                    "kbdinteractiveauthentication no", "authorizedkeysfile /etc/ssh/authorized_keys/deployer"):
        if setting not in configuration.splitlines():
            raise RuntimeError("Missing effective restriction: " + setting)
    ready = run("sudo", "-u", "deployer", "sudo", "-n", "--", "/usr/local/sbin/elecciones-release", "check")
    if "no deployment performed" not in ready.stdout:
        raise RuntimeError("Access check failed")
    run("sudo", "-u", "deployer", "sudo", "-n", "id", succeeds=False)
    for target in ("/opt/elecciones2026/compose.yaml", "/var/lib/elecciones2026/release.json",
                   "/etc/ssh/authorized_keys/deployer"):
        run("sudo", "-u", "deployer", "touch", target, succeeds=False)
    run("sudo", "-u", "deployer", "sudo", "-n", "--", "/usr/local/sbin/elecciones-release",
        "deploy ghcr.io/other/site@sha256:" + "a" * 64, succeeds=False)
    # Trust the locally generated host key directly, without network discovery.
    public = Path("/etc/ssh/ssh_host_ed25519_key.pub").read_text().split()
    Path("/tmp/test-known-hosts").write_text("[127.0.0.1]:2222 " + " ".join(public[:2]) + "\n")
    server = subprocess.Popen(["/usr/sbin/sshd", "-D", "-e", "-p", "2222"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ssh = ["ssh", "-T", "-p", "2222", "-i", "/tmp/test-key", "-o", "BatchMode=yes",
           "-o", "IdentitiesOnly=yes", "-o", "StrictHostKeyChecking=yes",
           "-o", "UserKnownHostsFile=/tmp/test-known-hosts", "-o", "ConnectTimeout=2",
           "deployer@127.0.0.1"]
    try:
        for attempt in range(20):
            result = subprocess.run([*ssh, "check"], capture_output=True, text=True)
            if result.returncode == 0:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("Restricted SSH check failed: " + result.stderr)
        run(*ssh, "id", succeeds=False)
        run(*ssh, "check; id", succeeds=False)
        run(*ssh, "check extra", succeeds=False)
        # A second key put in the user's home must not bypass the central key file.
        run("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", "/tmp/old-key")
        home_keys = Path("/home/deployer/.ssh")
        home_keys.mkdir(mode=0o700)
        shutil.copyfile("/tmp/old-key.pub", home_keys / "authorized_keys")
        run("chown", "-R", "deployer:deployer", str(home_keys))
        old_ssh = ssh.copy()
        old_ssh[old_ssh.index("/tmp/test-key")] = "/tmp/old-key"
        run(*old_ssh, "check", succeeds=False)
    finally:
        server.terminate()
        server.wait(timeout=10)
    print("Ubuntu SSH/sudo rehearsal passed: check allowed; arbitrary commands, foreign images, writable tooling and old home key denied.")


if __name__ == "__main__":
    main()
