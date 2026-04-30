"""Ansible Runner 封装模块"""
import os
import tempfile
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class AnsibleRunnerWrapper:
    """Ansible Runner 封装"""

    @staticmethod
    def _write_inventory(hosts_data: List[Dict[str, Any]], inventory_path: str):
        """生成 Ansible inventory 文件"""
        # Write INI format inventory
        with open(inventory_path, 'w') as f:
            f.write("[all]\n")
            for host_data in hosts_data:
                host_vars = []
                host_vars.append(f"ansible_host={host_data.get('ansible_host')}")
                host_vars.append(f"ansible_port={host_data.get('ansible_port', 22)}")
                host_vars.append(f"ansible_user={host_data.get('ansible_user')}")

                if host_data.get('ansible_ssh_private_key'):
                    key_path = os.path.join(os.path.dirname(inventory_path), f"{host_data.get('ansible_host')}_key")
                    with open(key_path, 'w') as key_f:
                        key_f.write(host_data['ansible_ssh_private_key'])
                    os.chmod(key_path, 0o600)
                    host_vars.append(f"ansible_ssh_private_key_file={key_path}")

                if host_data.get('ansible_ssh_pass'):
                    host_vars.append(f"ansible_ssh_pass={host_data['ansible_ssh_pass']}")

                if host_data.get('ansible_ssh_common_args'):
                    host_vars.append(f"ansible_ssh_common_args='{host_data['ansible_ssh_common_args']}'")

                f.write(f"{host_data.get('ansible_host')} {' '.join(host_vars)}\n")

    @staticmethod
    async def run_shell_command(
        command: str,
        hosts_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """运行 Shell 命令"""
        # Create temporary directory for this run
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = os.path.join(tmpdir, "inventory")
            AnsibleRunnerWrapper._write_inventory(hosts_data, inventory_path)

            # Write playbook
            playbook_content = f"""
---
- name: Run shell command
  hosts: all
  gather_facts: no
  tasks:
    - name: Execute command
      ansible.builtin.shell: {command}
      register: shell_output
    - name: Debug output
      debug:
        var: shell_output
"""
            playbook_path = os.path.join(tmpdir, "playbook.yml")
            with open(playbook_path, 'w') as f:
                f.write(playbook_content)

            # Run ansible-playbook
            result = AnsibleRunnerWrapper._run_playbook(playbook_path, inventory_path, tmpdir)
            return result

    @staticmethod
    async def run_module(
        module_name: str,
        module_args: Optional[str],
        hosts_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """运行 Ansible 模块"""
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory_path = os.path.join(tmpdir, "inventory")
            AnsibleRunnerWrapper._write_inventory(hosts_data, inventory_path)

            args_part = f"args: {module_args}" if module_args else ""
            playbook_content = f"""
---
- name: Run ansible module
  hosts: all
  gather_facts: no
  tasks:
    - name: Execute {module_name}
      ansible.builtin.{module_name}:
        {args_part}
      register: module_output
    - name: Debug output
      debug:
        var: module_output
"""
            playbook_path = os.path.join(tmpdir, "playbook.yml")
            with open(playbook_path, 'w') as f:
                f.write(playbook_content)

            result = AnsibleRunnerWrapper._run_playbook(playbook_path, inventory_path, tmpdir)
            return result

    @staticmethod
    def _run_playbook(playbook_path: str, inventory_path: str, work_dir: str) -> Dict[str, Any]:
        """运行 ansible-playbook"""
        import subprocess
        cmd = [
            "ansible-playbook",
            "-i", inventory_path,
            playbook_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -2,
            }
