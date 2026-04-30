import paramiko
from typing import Optional, Tuple, Dict, Any
from app.models.host import Host
from app.models.system_user import SystemUser
from app.models.gateway import Gateway


class SSHService:
    """SSH连接服务（支持ProxyJump）"""

    @staticmethod
    def create_ssh_client(
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: int = 10,
    ) -> paramiko.SSHClient:
        """创建SSH客户端"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": host,
            "port": port,
            "username": username,
            "timeout": timeout,
        }

        if private_key:
            # Load private key from string
            from io import StringIO
            pkey = paramiko.RSAKey.from_private_key(StringIO(private_key))
            connect_kwargs["pkey"] = pkey
        elif password:
            connect_kwargs["password"] = password

        client.connect(**connect_kwargs)
        return client

    @staticmethod
    def create_connection_with_gateway(
        target_host: str,
        target_port: int,
        target_username: str,
        target_password: Optional[str] = None,
        target_private_key: Optional[str] = None,
        gateway_host: Optional[str] = None,
        gateway_port: int = 22,
        gateway_username: Optional[str] = None,
        gateway_password: Optional[str] = None,
        gateway_private_key: Optional[str] = None,
    ) -> paramiko.SSHClient:
        """创建带有ProxyJump的SSH连接"""
        if not gateway_host:
            # Direct connection
            return SSHService.create_ssh_client(
                target_host, target_port, target_username,
                target_password, target_private_key
            )

        # Create gateway connection first
        gateway_client = SSHService.create_ssh_client(
            gateway_host, gateway_port, gateway_username,
            gateway_password, gateway_private_key
        )

        # Create transport through gateway
        gateway_transport = gateway_client.get_transport()
        if not gateway_transport:
            raise Exception("Failed to get gateway transport")

        # Create direct-tcpip channel
        dest_addr = (target_host, target_port)
        local_addr = ("127.0.0.1", 0)
        channel = gateway_transport.open_channel(
            "direct-tcpip", dest_addr, local_addr
        )

        # Create target SSH client
        target_client = paramiko.SSHClient()
        target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect through the channel
        connect_kwargs = {
            "username": target_username,
            "sock": channel,
        }
        if target_private_key:
            from io import StringIO
            pkey = paramiko.RSAKey.from_private_key(StringIO(target_private_key))
            connect_kwargs["pkey"] = pkey
        elif target_password:
            connect_kwargs["password"] = target_password

        target_client.connect(hostname="", **connect_kwargs)

        return target_client

    @staticmethod
    async def test_connection(host: Host) -> Tuple[bool, Optional[str]]:
        """测试主机连接（内部使用）"""
        try:
            # Build connection parameters from host
            ip = host.ip_internal if host.ip_preference == "internal" else host.ip_external
            if not ip:
                ip = host.ip_internal or host.ip_external
                if not ip:
                    return False, "No IP address configured"

            port = host.ssh_port or 22

            if not host.system_user:
                return False, "No system user configured"

            system_user: SystemUser = host.system_user
            username = system_user.username

            target_private_key = None
            target_password = None
            if system_user.auth_type == "private_key":
                target_private_key = system_user.private_key
            else:
                target_password = system_user.password_cipher

            # Resolve gateway
            gateway_host = None
            gateway_port = 22
            gateway_username = None
            gateway_password = None
            gateway_private_key = None

            if host.gateway:
                gateway: Gateway = host.gateway
                gateway_host = gateway.ip
                gateway_port = gateway.port
                if gateway.system_user:
                    gateway_username = gateway.system_user.username
                    if gateway.system_user.auth_type == "private_key":
                        gateway_private_key = gateway.system_user.private_key
                    else:
                        gateway_password = gateway.system_user.password_cipher
            elif host.business_node and host.business_node.gateway:
                gateway: Gateway = host.business_node.gateway
                gateway_host = gateway.ip
                gateway_port = gateway.port
                if gateway.system_user:
                    gateway_username = gateway.system_user.username
                    if gateway.system_user.auth_type == "private_key":
                        gateway_private_key = gateway.system_user.private_key
                    else:
                        gateway_password = gateway.system_user.password_cipher

            # Create connection and test
            client = SSHService.create_connection_with_gateway(
                target_host=ip,
                target_port=port,
                target_username=username,
                target_password=target_password,
                target_private_key=target_private_key,
                gateway_host=gateway_host,
                gateway_port=gateway_port,
                gateway_username=gateway_username,
                gateway_password=gateway_password,
                gateway_private_key=gateway_private_key,
            )

            # Run simple test command
            stdin, stdout, stderr = client.exec_command("echo 'connection_test'")
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            client.close()

            if output == "connection_test":
                return True, None
            else:
                return False, error or "Connection test failed"

        except Exception as e:
            return False, str(e)
