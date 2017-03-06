service := caddy postgres monit src

.PHONY: all $(service)

all: $(service)

$(service):
	$(MAKE) -C $@ all
