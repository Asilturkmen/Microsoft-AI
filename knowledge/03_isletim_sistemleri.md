# İşletim Sistemleri

## İşletim Sisteminin Görevi

İşletim sistemi, kullanıcı uygulamaları ile bilgisayar donanımı arasında çalışan temel yazılımdır. İşlemci, bellek, disk, dosyalar ve giriş-çıkış cihazları gibi kaynakların yönetimini gerçekleştirir.

macOS, Windows ve Linux yaygın masaüstü işletim sistemlerine örnektir.

## Process ve Thread

Process, çalışmakta olan bir program örneğidir. Her process kendisine ayrılan bellek alanı ve sistem kaynaklarıyla çalışır.

Thread ise bir process içerisindeki yürütme birimidir. Aynı process içinde birden fazla thread bulunabilir ve bu threadler process'in kaynaklarını paylaşabilir.

## Bellek Yönetimi

RAM sınırlı bir kaynaktır ve işletim sistemi hangi process'in ne kadar bellek kullandığını takip eder. Uygulamalar doğrudan fiziksel belleğin her bölümüne erişmez; işletim sistemi sanal bellek mekanizmalarıyla süreçleri birbirinden izole eder.

Sanal bellek, programlara büyük ve düzenli bir adres alanı sunar. Gerektiğinde bazı veriler geçici olarak disk üzerindeki swap alanına taşınabilir. Disk RAM'den çok daha yavaş olduğu için yoğun swap kullanımı sistem performansını düşürebilir.

## CPU Scheduling

Aynı anda birçok process çalışmak istese de işlemci kaynakları sınırlıdır. Scheduler, hangi process veya thread'in ne zaman CPU kullanacağını belirler.

## Dosya Sistemi

Dosya sistemi, diskteki verilerin dosya ve klasör yapısı içinde düzenlenmesini sağlar. İşletim sistemi dosyaların isimlerini, konumlarını, boyutlarını, izinlerini ve diğer metadata bilgilerini yönetir.

## Deadlock

Deadlock, iki veya daha fazla process'in birbirlerinin tuttuğu kaynakları beklemesi ve hiçbirinin ilerleyememesi durumudur.

Basit bir örnekte Process A birinci kaynağı kilitleyip ikinci kaynağı beklerken, Process B ikinci kaynağı kilitleyip birinci kaynağı bekleyebilir.

## Context Switch

İşletim sistemi CPU'yu bir process'ten diğerine geçirirken mevcut process'in durumunu kaydedip yeni process'in durumunu yükler. Buna context switch denir.

Context switch çoklu görev için gereklidir fakat ücretsiz değildir. Çok fazla context switch oluşması işlemcinin gerçek uygulama işi yerine süreç değiştirmeye zaman harcamasına neden olabilir.
