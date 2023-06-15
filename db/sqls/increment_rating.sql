update hosts
set rating = IIF(rating >= 100, 100, rating + ?)
where id = ?