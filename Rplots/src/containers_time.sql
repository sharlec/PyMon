SELECT
  monitcollector_container.docker_id,
	monitcollector_container.name,
	monitcollector_container.date,
	monitcollector_container.cpu,
	monitcollector_container.memory
FROM
	public.monitcollector_system,
	public.monitcollector_server,
	public.monitcollector_process,
	public.monitcollector_service,
	public.monitcollector_container 
WHERE
	monitcollector_server.id = monitcollector_system.server_id AND
	monitcollector_server.id = monitcollector_process.server_id AND
	monitcollector_service.id = monitcollector_process.service_ptr_id AND
	monitcollector_container.process_id = monitcollector_process.service_ptr_id
ORDER BY
	monitcollector_server.localhostname ASC; 

