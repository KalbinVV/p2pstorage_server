create table if not exists files(
    id integer primary key autoincrement,
    name str not null,
    size integer not null,
    hash str not null
)