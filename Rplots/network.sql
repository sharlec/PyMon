SELECT 
	  monitcollector_server.localhostname, 
	  monitcollector_network.*, 
	  monitcollector_service.name
FROM 
	  monitcollector_server, 
	  monitcollector_network, 
	  monitcollector_service
WHERE 
	  monitcollector_server.id = monitcollector_network.server_id AND
	  monitcollector_network.service_ptr_id = monitcollector_service.id;
