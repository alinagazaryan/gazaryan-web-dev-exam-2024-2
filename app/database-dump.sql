PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('537a7f00bdda');
CREATE TABLE genres (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	CONSTRAINT pk_genres PRIMARY KEY (id), 
	CONSTRAINT uq_genres_name UNIQUE (name)
);
INSERT INTO genres VALUES(1,'Роман');
INSERT INTO genres VALUES(2,'Рассказ');
INSERT INTO genres VALUES(3,'Повесть');
CREATE TABLE images (
	id VARCHAR(100) NOT NULL, 
	file_name VARCHAR(100) NOT NULL, 
	mime_type VARCHAR(100) NOT NULL, 
	md5_hash VARCHAR(256) NOT NULL, 
	CONSTRAINT pk_images PRIMARY KEY (id), 
	CONSTRAINT uq_images_md5_hash UNIQUE (md5_hash)
);
INSERT INTO images VALUES('8e8a3d92-bd0d-4fb6-9674-eee4ddf98ad2','8e8a3d92-bd0d-4fb6-9674-eee4ddf98ad2.webp','image/webp','59502844f69c1d62c90c2ab9c1ce1198');
INSERT INTO images VALUES('07b8bc3b-c6f3-406b-b560-61ca4d60242b','07b8bc3b-c6f3-406b-b560-61ca4d60242b.webp','image/webp','9eaf1666f28e3c638e3fdd149076949e');
INSERT INTO images VALUES('e0ff9e56-d497-4fb6-bb1e-204240777bcf','e0ff9e56-d497-4fb6-bb1e-204240777bcf.png','image/png','c1877718d6fbc80a5177f36ebb48e1cc');
INSERT INTO images VALUES('60f82c05-e125-41c5-bd80-d97a97a70992','60f82c05-e125-41c5-bd80-d97a97a70992.png','image/png','777fe2f8a69d7e579866c96c6d305aa9');
INSERT INTO images VALUES('32499f42-1a06-44e4-8ad7-bff17875f09a','32499f42-1a06-44e4-8ad7-bff17875f09a.png','image/png','ea028222d99e711d418f93edd0c519fa');
INSERT INTO images VALUES('8ea826bf-7e5b-43e1-af8c-58932e797cd8','8ea826bf-7e5b-43e1-af8c-58932e797cd8.png','image/png','568acf4212862e516e030425e27d5e53');
INSERT INTO images VALUES('1c208e39-0aca-423a-bad0-5120a446731a','1c208e39-0aca-423a-bad0-5120a446731a.png','image/png','83cf4d53ff11a934a5988cc9b7a21824');
INSERT INTO images VALUES('6e431b0e-4669-44ee-b83b-e249c923f2b3','6e431b0e-4669-44ee-b83b-e249c923f2b3.png','image/png','ff76686472f306c8653cba84bd575e1b');
INSERT INTO images VALUES('9fb9cab0-18cf-442f-af4f-d0aaf9dfa971','9fb9cab0-18cf-442f-af4f-d0aaf9dfa971.png','image/png','7eb1ceff616617db9bab9232c5b72589');
INSERT INTO images VALUES('15086d6c-1d14-444a-81db-00f80bbf0250','15086d6c-1d14-444a-81db-00f80bbf0250.png','image/png','50e94b38b7140c51d3d88725c4633829');
INSERT INTO images VALUES('15814590-0a41-491f-9356-2c92634b4107','15814590-0a41-491f-9356-2c92634b4107.png','image/png','7748aaf3e1a2cd492fcc7fbc1b017a60');
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	"desc" TEXT NOT NULL, 
	CONSTRAINT pk_roles PRIMARY KEY (id)
);
INSERT INTO roles VALUES(1,'Администратор','Администратор');
INSERT INTO roles VALUES(2,'Модератор','Модератор');
INSERT INTO roles VALUES(3,'Пользователь','Пользователь');
CREATE TABLE books (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	short_desc TEXT NOT NULL, 
	year VARCHAR(10) NOT NULL, 
	publisher VARCHAR(100) NOT NULL, 
	author VARCHAR(100) NOT NULL, 
	volume INTEGER NOT NULL, 
	cover_id VARCHAR(100) NOT NULL, 
	CONSTRAINT pk_books PRIMARY KEY (id), 
	CONSTRAINT fk_books_cover_id_images FOREIGN KEY(cover_id) REFERENCES images (id), 
	CONSTRAINT uq_books_name UNIQUE (name)
);
INSERT INTO books VALUES(1,'Записки о Шерлоке Холмсе','В книгу включены повесть «Знак четырех» и рассказы известного английского писателя Артура Конан Дойла, в которых описываются приключения популярного сыщика-любителя Шерлока Холмса.','1984','Высшая школа','Артур Конан Дойл',450,'8e8a3d92-bd0d-4fb6-9674-eee4ddf98ad2');
INSERT INTO books VALUES(2,'Мастер и Маргарита','«Мастер и Маргарита» — один из самых известных и значимых романов прошлого столетия. Книга легла в основу многочисленных опер, симфоний, рок-опер, фильмов и телесериалов. Так что же так привлекает людей к истории о визите дьявола и его свиты в советскую Москву тридцатых годов прошлого века, истории о нищем философе и обречённом прокураторе Иудеи, о талантливом и несчастном Мастере и его прекрасной и верной возлюбленной Маргарите?','1967','АСТ','Булгаков Михаил Афанасьевич ',512,'07b8bc3b-c6f3-406b-b560-61ca4d60242b');
INSERT INTO books VALUES(3,'Жизнь взаймы, или У неба любимчиков нет',replace('Аннотация: Клерфэ — автогонщик. Навещая в клинике своего знакомого, такого же гонщика, он встречается с неизлечимо больной Лилиан. Туберкулез не оставляет ей шанса на долгую жизнь, но она не желает покорно и обреченно дожидаться неизбежной смерти — Лилиан намерена последние месяцы пожить на полную катушку.\n','\n',char(10)),'1959','АСТ','Эрих Мария Ремарк',384,'e0ff9e56-d497-4fb6-bb1e-204240777bcf');
INSERT INTO books VALUES(4,'Театр','В романе "Театр" Сомерсет Моэм изображает актрису, чья жизнь полностью поглощена ее блестящим сценическим образом. Но одна встреча рушит этот безупречный мир, и мы видим те тонкие грани, которые отделяют реальность от театра и которые часто исчезают, смешивая два столь близких друг другу измерения.','1937','АСТ','Уильям Сомерсет Моэм',320,'60f82c05-e125-41c5-bd80-d97a97a70992');
INSERT INTO books VALUES(5,'Рождественские каникулы','Уезжая на Рождество в Париж, богатый наследник, аристократ и тонкий ценитель искусства Чарли Мейсон и не предполагал, что вернется другим человеком. Ведь именно здесь он встретил Лидию – русскую эмигрантку, вынужденную сделаться "ночной бабочкой".','1939','АСТ','Уильям Сомерсет Моэм',320,'32499f42-1a06-44e4-8ad7-bff17875f09a');
INSERT INTO books VALUES(6,'Старик и море','Сантьяго — старый кубинский рыбак. Раз за разом он выходит в море на своей лодке вместе с мальчиком Манолином — своим помощником, но уже целых сорок дней старику не удаётся поймать ни одной рыбины. Он лишается помощи мальчика, которому родители велят рыбачить с другими, но не его дружбы и участия.','1952','АСТ','Эрнест Миллер Хемингуей',107,'8ea826bf-7e5b-43e1-af8c-58932e797cd8');
INSERT INTO books VALUES(7,'Воскресение','"Воскресение" — шедевр позднего творчества Льва Толстого. История уставшего от светской жизни и развлечений аристократа, переживающего внезапное духовное прозрение при трагической встрече с циничной "жрицей любви", которую он сам некогда толкнул на этот печальный путь.','1889','Азбука','Лев Толстой',640,'1c208e39-0aca-423a-bad0-5120a446731a');
INSERT INTO books VALUES(8,'Дубровский','Владимир Дубровский - молодой и беспечный корнет. Он служит в гвардии и не заботится о будущем: играет в карты, "входит в долги" и устраивает шумные застолья. Но однажды он получает письмо от своей старой няни: отец Владимира при смерти, а их поместье отнимает богатый самодур Троекуров.','1841','Дрофа плюс','Александр Сергеевич Пушкин',112,'6e431b0e-4669-44ee-b83b-e249c923f2b3');
INSERT INTO books VALUES(9,'Грозовой перевал','Это история роковой любви Хитклифа, приемного сына владельца поместья "Грозовой Перевал", к дочери хозяина Кэтрин. Демоническая страсть двух сильных личностей, не желающих идти на уступки друг другу, из-за чего страдают и гибнут не только главные герои, но и окружающие их люди.','1847','АСТ','Эмили Джейн Бронте',384,'9fb9cab0-18cf-442f-af4f-d0aaf9dfa971');
INSERT INTO books VALUES(10,'Незнакомка из Уайлдфелл-Холла',replace('В заброшенной усадьбе Уайлдфелл-Холл неожиданно появляется молодая женщина в черном. Она красива, умна, образованна и держится независимо. Соседи умирают от любопытства, но загадочная незнакомка не спешит отрыть тайну своего прошлого...\nПодробнее: https://www.labirint.ru/books/724116/','\n',char(10)),'1848','АСТ','Энн Бронте',480,'15086d6c-1d14-444a-81db-00f80bbf0250');
INSERT INTO books VALUES(11,'Джейн Эйр',replace('Любовь, которая не подвластна ни времени, ни обстоятельствам, ни ударам судьбы. Если жизнь не балует, то можно ли ее ждать? Детство и юность воспитанницы пансионата для бедных девочек, Джейн Эйр, были безрадостными. Она вынуждена сама зарабатывать на хлеб, и кажется, что судьба к ней совсем не благосклонна. Все меняется, когда она устраивается гувернанткой в поместье загадочного мистера Рочестера. В ее жизнь приходит Большая Любовь. Но спасет она ее или погубит? Героине предстоит научиться принимать нелегкие решения и делать сложный выбор между чувством и долгом, сердцем и разумом, самопожертвованием и жизнью. Будет ли в конце этой пронзительной истории счастливый конец?\nЧто бы ни случилось, вера в любовь и сострадание, в людей и справедливость, в человеческое достоинство и силу духа помогут героине с честью выдержать все испытания.\nПодробнее: https://www.labirint.ru/books/849557/','\n',char(10)),'1847','АСТ','Шарлотта Бронте',504,'15814590-0a41-491f-9356-2c92634b4107');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	first_name VARCHAR(100) NOT NULL, 
	last_name VARCHAR(100) NOT NULL, 
	middle_name VARCHAR(100), 
	login VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(256) NOT NULL, 
	role_id INTEGER NOT NULL, 
	CONSTRAINT pk_users PRIMARY KEY (id), 
	CONSTRAINT fk_users_role_id_roles FOREIGN KEY(role_id) REFERENCES roles (id), 
	CONSTRAINT uq_users_login UNIQUE (login)
);
INSERT INTO users VALUES(1,'Алина','Газарян','Александровна','gazaryan_alina','scrypt:32768:8:1$jdu6wKcP9lTWWgMD$3c88ab5562e2eac7add19a03c68b172934b15b9379ea02c8e1ba5b385bd6f5c60842bdb6c077b4df01ca5d1351d352330bbd86d2ecefda8a8c3bd61e307527e1',1);
INSERT INTO users VALUES(2,'Иван','Иванов','Иванович','ivanov_ivan','scrypt:32768:8:1$uNxIWG5ZMsPWBrvh$32f843312dbf7682134690aa4df4625362ae5d7de21b2721ef0b25d569c5c12bcf949860f2bcf8f29831f66deff6de905ec3a3f2743a88e4b8e1c77f9ac8d709',3);
CREATE TABLE book_genres (
	id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	genre_id INTEGER NOT NULL, 
	CONSTRAINT pk_book_genres PRIMARY KEY (id), 
	CONSTRAINT fk_book_genres_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_book_genres_genre_id_genres FOREIGN KEY(genre_id) REFERENCES genres (id)
);
INSERT INTO book_genres VALUES(1,1,2);
INSERT INTO book_genres VALUES(3,3,1);
INSERT INTO book_genres VALUES(8,8,3);
INSERT INTO book_genres VALUES(9,2,1);
INSERT INTO book_genres VALUES(10,5,1);
INSERT INTO book_genres VALUES(11,4,1);
INSERT INTO book_genres VALUES(12,7,1);
INSERT INTO book_genres VALUES(13,6,3);
INSERT INTO book_genres VALUES(14,9,1);
INSERT INTO book_genres VALUES(15,10,1);
INSERT INTO book_genres VALUES(16,11,1);
CREATE TABLE reviews (
	id INTEGER NOT NULL, 
	mark INTEGER NOT NULL, 
	text TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	CONSTRAINT pk_reviews PRIMARY KEY (id), 
	CONSTRAINT fk_reviews_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_reviews_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO reviews VALUES(1,5,'Отличный рассказ, заставляет остановиться и задуматься над собой, и уяснить, для чего мы работаем, и для кого вообще живём. Я думаю, в рассказе не зря упоминается целая семья господина, но семья эта описана именно так, что она существует как бы отдельно от самого господина, предполагаю, что автор сделал это осознанно для того, чтобы подчеркнуть обособленность главного героя: его жизни прожитой и жизнью запланированной.','2024-06-04 00:34:22.938183',1,1);
INSERT INTO reviews VALUES(2,5,'Книга понравилась, но конец очень расстроил!','2024-06-14 20:37:38.692355',3,1);
CREATE TABLE histories (
	id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	CONSTRAINT pk_histories PRIMARY KEY (id), 
	CONSTRAINT fk_histories_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_histories_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO histories VALUES(1,'2024-06-10 02:39:45.312103',2,1);
INSERT INTO histories VALUES(2,'2024-06-10 02:40:29.054085',1,1);
INSERT INTO histories VALUES(3,'2024-06-10 02:40:44.889570',1,1);
INSERT INTO histories VALUES(5,'2024-06-10 02:41:10.987922',1,-1);
INSERT INTO histories VALUES(6,'2024-06-10 02:41:12.832311',2,-1);
INSERT INTO histories VALUES(7,'2024-06-10 16:26:47.352241',2,1);
INSERT INTO histories VALUES(8,'2024-06-12 13:39:14.126977',3,1);
INSERT INTO histories VALUES(9,'2024-06-12 13:40:58.269655',1,1);
INSERT INTO histories VALUES(10,'2024-06-12 13:44:09.096073',4,1);
INSERT INTO histories VALUES(11,'2024-06-12 13:47:58.668273',5,1);
INSERT INTO histories VALUES(12,'2024-06-12 13:54:58.397185',6,1);
INSERT INTO histories VALUES(13,'2024-06-12 14:00:05.632264',7,1);
INSERT INTO histories VALUES(14,'2024-06-12 14:03:14.713867',8,1);
INSERT INTO histories VALUES(15,'2024-06-12 14:03:21.131466',2,1);
INSERT INTO histories VALUES(16,'2024-06-12 14:03:47.760670',5,1);
INSERT INTO histories VALUES(17,'2024-06-12 14:06:59.566800',9,1);
INSERT INTO histories VALUES(18,'2024-06-12 14:08:59.994538',10,1);
INSERT INTO histories VALUES(19,'2024-06-12 14:11:55.944476',11,1);
INSERT INTO histories VALUES(20,'2024-06-12 14:15:28.495254',7,-1);
INSERT INTO histories VALUES(21,'2024-06-12 14:15:51.296151',6,-1);
INSERT INTO histories VALUES(22,'2024-06-13 17:34:53.352512',1,1);
INSERT INTO histories VALUES(23,'2024-06-13 18:04:46.439738',2,1);
INSERT INTO histories VALUES(24,'2024-06-13 18:04:51.504449',2,1);
INSERT INTO histories VALUES(25,'2024-06-14 11:21:04.924296',2,1);
INSERT INTO histories VALUES(26,'2024-06-14 20:37:17.751574',3,1);
INSERT INTO histories VALUES(27,'2024-06-14 20:37:38.742614',3,1);
INSERT INTO histories VALUES(28,'2024-06-14 20:37:55.485851',3,1);
INSERT INTO histories VALUES(29,'2024-06-14 20:37:58.195318',3,1);
COMMIT;
