SELECT 
	monitcollector_server.localhostname, 
	monitcollector_service.name, 
	monitcollector_process.*
FROM 
	monitcollector_server, 
	monitcollector_process, 
	monitcollector_service
WHERE 
	monitcollector_server.id = monitcollector_process.server_id AND
	monitcollector_service.id = monitcollector_process.service_ptr_id AND
	monitcollector_process.date_last IS NOT NULL ;
