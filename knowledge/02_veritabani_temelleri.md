# Veritabanı Temelleri

## Veritabanı Nedir?

Veritabanı, bilgilerin düzenli biçimde saklanmasını, aranmasını ve güncellenmesini sağlayan yapıdır. Bir e-ticaret uygulamasındaki kullanıcılar, ürünler, siparişler ve ödemeler veritabanında tutulabilecek verilere örnektir.

İlişkisel veritabanlarında bilgiler tablolar halinde saklanır. Bir tablo satır ve sütunlardan oluşur. Her satır bir kaydı, her sütun ise o kaydın belirli bir özelliğini temsil eder.

## Primary Key

Primary key, bir tablodaki her kaydı benzersiz olarak tanımlayan alandır. Aynı tabloda iki kaydın aynı primary key değerine sahip olmaması gerekir.

Örneğin `users` tablosundaki `id` alanı primary key olabilir. Kullanıcıların isimleri aynı olsa bile `id` değerleri farklı olduğu için kayıtlar birbirinden ayırt edilebilir.

## Foreign Key

Foreign key, iki tablo arasında ilişki kurulmasını sağlar. Bir tablodaki alan, başka bir tablodaki primary key değerine referans verebilir.

Örneğin `orders` tablosundaki `user_id`, `users` tablosundaki `id` alanına bağlanabilir. Böylece her siparişin hangi kullanıcıya ait olduğu belirlenebilir.

## Normalizasyon

Normalizasyon, veriyi gereksiz tekrarları azaltacak ve veri tutarlılığını artıracak şekilde tablolara ayırma sürecidir. Aynı müşteri bilgisini her sipariş kaydında tekrar saklamak yerine müşteri bilgileri ayrı bir kullanıcı tablosunda tutulabilir.

Normalizasyonun amacı veriyi olabildiğince çok tabloya bölmek değildir. Amaç, aynı bilginin birden fazla yerde gereksiz biçimde tutulmasını azaltmak ve güncelleme hatalarını önlemektir.

## SQL

SQL, ilişkisel veritabanlarıyla çalışmak için kullanılan sorgu dilidir.

Temel işlemler:
- `SELECT`: veri okumak için kullanılır.
- `INSERT`: yeni kayıt ekler.
- `UPDATE`: mevcut kaydı değiştirir.
- `DELETE`: kayıt siler.

## Index

Index, belirli alanlarda yapılan aramaları hızlandırmak için kullanılan veri yapısıdır. Kitabın sonundaki dizine benzer şekilde veritabanının ilgili kaydı daha hızlı bulmasına yardımcı olur.

Ancak her sütuna index eklemek doğru değildir. Indexler okuma işlemlerini hızlandırırken ekleme ve güncelleme işlemlerinde ek maliyet oluşturur ve disk alanı kullanır.

## Transaction

Transaction, birden fazla veritabanı işlemini tek bir mantıksal işlem olarak ele alır. İşlemlerin tamamı başarılı olursa değişiklikler kaydedilir; kritik bir hata oluşursa işlemler geri alınabilir.

Örneğin bir hesaptan para düşürülüp başka hesaba para eklenen para transferinde bu iki işlemin birlikte başarılı olması gerekir.

## SQLite

SQLite, ayrı bir veritabanı sunucusu gerektirmeyen hafif bir ilişkisel veritabanıdır. Veritabanının tamamı genellikle tek bir dosyada tutulur. Bu nedenle masaüstü uygulamaları, mobil uygulamalar, prototipler ve tamamen lokal çalışan sistemler için uygundur.
