select h.addr, h.port from hosts h
join files f on f.host_id = h.id
where f.id = ?