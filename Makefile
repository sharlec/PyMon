service := caddy postgres monit src
architecture := amd64 armhf aarch64

.PHONY: all $(service)

all: $(service)

$(service):
	$(MAKE) -j 1 -C $@ $(architecture)
