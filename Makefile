.PHONY: install develop

-include .env

FORCE ?= 0
PORT ?= 80
VOLUME_SECRETS ?= /mnt/hidden-secrets

install:
	@if [ "$(FORCE)" != "1" ]; then \
		if ! mountpoint -q "$(VOLUME_SECRETS)" 2>/dev/null; then \
			echo "error: VOLUME_SECRETS is missing or not a mountpoint." >&2; \
			echo "Connect removable media at that path, then retry." >&2; \
			echo "To skip this check: make install FORCE=1" >&2; \
			exit 1; \
		fi; \
	fi
	docker build -t hidden .
	docker run -dit \
	--init \
	--restart unless-stopped \
	--cap-add SYS_ADMIN \
	--device /dev/fuse \
	--security-opt apparmor:unconfined \
	-p $(PORT):80 \
	-p $(VERSITY_PORT):$(VERSITY_PORT) \
	-v hidden-cipherdir:$(INSTALL_CIPHERDIR) \
	-v $(VOLUME_SECRETS):$(INSTALL_SECRETS) \
	--name hidden \
	hidden

develop:
	docker exec hidden sh -c "apt-get update && apt-get install -y --no-install-recommends git openssh-client"
	docker exec hidden mkdir -p /root/.ssh
	docker cp "$$HOME/.ssh/." hidden:/root/.ssh
	docker exec hidden sh -c "\
	chmod 700 /root/.ssh && \
	find /root/.ssh -type f -exec chmod 600 {} \; && \
	find /root/.ssh -name '*.pub' -type f -exec chmod 644 {} \; \
	"