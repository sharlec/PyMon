services := caddy postgres monit src
architectures := amd64 armhf aarch64

.PHONY: all $(services)

all: $(services)

$(services):
	@$(MAKE) -j 1 -C $@ $(architectures)

clean_all:
	@$(foreach service,$(services),$(MAKE) -C $(service) clean;)

push_all:
	@$(foreach service,$(services),$(MAKE) -C $(service) push;)
