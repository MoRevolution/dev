FROM ubuntu:24.04

ARG NU_VERSION=0.103.0

RUN apt-get update && apt-get install -y curl wget git sudo build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for Homebrew
RUN useradd -m -s /bin/bash linuxbrew && \
    echo "linuxbrew ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/linuxbrew

# Switch to linuxbrew user and install Homebrew
USER linuxbrew
RUN NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN /home/linuxbrew/.linuxbrew/bin/brew update

# Switch back to root and set PATH
USER root
ENV PATH="/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"

# Install Nushell
RUN wget -q https://github.com/nushell/nushell/releases/download/${NU_VERSION}/nu-${NU_VERSION}-x86_64-unknown-linux-gnu.tar.gz -O /tmp/nu.tar.gz && \
    tar -xzf /tmp/nu.tar.gz -C /tmp && \
    cp /tmp/nu-*/nu /usr/local/bin/ && \
    rm -rf /tmp/nu*

# Install Starship
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y

# Copy nushell + starship configs
RUN mkdir -p /root/.config/nushell /root/.config
COPY files/env.nu /root/.config/nushell/env.nu
COPY files/config.nu /root/.config/nushell/config.nu
COPY files/starship.toml /root/.config/starship.toml

WORKDIR /setup
COPY . .

SHELL ["/usr/local/bin/nu", "-c"]
CMD ["nu", "setup.nu", "--dry-run"]
