CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE genres (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	CONSTRAINT pk_genres PRIMARY KEY (id), 
	CONSTRAINT uq_genres_name UNIQUE (name)
);
CREATE TABLE images (
	id VARCHAR(100) NOT NULL, 
	file_name VARCHAR(100) NOT NULL, 
	mime_type VARCHAR(100) NOT NULL, 
	md5_hash VARCHAR(256) NOT NULL, 
	CONSTRAINT pk_images PRIMARY KEY (id), 
	CONSTRAINT uq_images_md5_hash UNIQUE (md5_hash)
);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	"desc" TEXT NOT NULL, 
	CONSTRAINT pk_roles PRIMARY KEY (id)
);
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
CREATE TABLE book_genres (
	id INTEGER NOT NULL, 
	book_id INTEGER NOT NULL, 
	genre_id INTEGER NOT NULL, 
	CONSTRAINT pk_book_genres PRIMARY KEY (id), 
	CONSTRAINT fk_book_genres_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_book_genres_genre_id_genres FOREIGN KEY(genre_id) REFERENCES genres (id)
);
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
CREATE TABLE histories (
	id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	book_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	CONSTRAINT pk_histories PRIMARY KEY (id), 
	CONSTRAINT fk_histories_book_id_books FOREIGN KEY(book_id) REFERENCES books (id), 
	CONSTRAINT fk_histories_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
