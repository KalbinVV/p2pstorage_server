select h.name, h.addr, h.port from hosts h
join owners o on o.host_id = h.id
join files f on o.file_id = f.id
where f.id = ?
order by h.rating