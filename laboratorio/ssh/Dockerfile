FROM ubuntu:24.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends openssh-server python3 iproute2 systemd && rm -rf /var/lib/apt/lists/*
# Somente para o laboratório local: autenticação por chave efêmera, sem senha.
RUN mkdir -p /run/sshd /root/.ssh && chmod 700 /root/.ssh && printf '%s\n' 'PasswordAuthentication no' 'KbdInteractiveAuthentication no' 'PermitRootLogin prohibit-password' > /etc/ssh/sshd_config.d/laboratorio.conf
EXPOSE 22
CMD ["sh", "-c", "ssh-keygen -A >/dev/null && exec /usr/sbin/sshd -D -e"]
