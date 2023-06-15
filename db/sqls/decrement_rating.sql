update hosts
set rating = IIF(rating <= 0, 0, rating - ?)
where id = ?