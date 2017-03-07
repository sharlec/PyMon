service := caddy postgres monit src

.PHONY: all $(service)

all: $(service)

$(service):
	$(MAKE) -j 1 -C $@ all
