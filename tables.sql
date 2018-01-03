CREATE TABLE "urls"
(
    [urlid] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [title] NVARCHAR(160) NOT NULL,
    [url] nvarchar(250) NOT NULL
);

CREATE TABLE "raw_ingredients"
(
    [ingredientid] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    [ingredient] NVARCHAR(160) NOT NULL
);
