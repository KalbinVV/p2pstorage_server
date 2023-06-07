create table if not exists files(
    id integer primary key autoincrement,
    host_id integer not null
    name str not null,
    size integer not null,
    hash str not null,
    foreign key(host_id) references hosts(id)
)