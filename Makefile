service := caddy postgres monitcollector

.PHONY: all $(service)

all: $(service)

$(service):
	$(MAKE) -C $@ all
