# Nesne Yönelimli Programlama

## Genel Bakış

Nesne yönelimli programlama, yazılımı birbirleriyle etkileşime giren nesneler üzerinden tasarlayan bir programlama yaklaşımıdır. Bir nesne, belirli verileri ve bu veriler üzerinde çalışan davranışları birlikte taşır. Bu yaklaşım özellikle büyük yazılım projelerinde kodun daha düzenli, yeniden kullanılabilir ve sürdürülebilir olmasına yardımcı olur.

## Sınıf ve Nesne

Sınıf, nesnelerin nasıl oluşturulacağını tanımlayan bir şablondur. Bir sınıfın içinde özellikler ve metotlar bulunabilir. Nesne ise bu sınıftan oluşturulan gerçek örnektir.

Örneğin `Araba` isimli bir sınıfın marka, model ve hız gibi özellikleri olabilir. `hizlan()` veya `frenYap()` gibi metotlar da arabanın davranışlarını temsil eder. Aynı `Araba` sınıfından farklı marka ve modellere sahip birçok nesne üretilebilir.

## Kapsülleme

Kapsülleme, bir nesnenin iç durumunu doğrudan dışarı açmak yerine kontrollü bir arayüz üzerinden yönetme prensibidir. Amaç, nesnenin iç yapısını korumak ve başka kodların bu yapıyı yanlışlıkla bozmasını engellemektir.

Örneğin bir banka hesabının bakiyesi doğrudan değiştirilebilir bir değişken olarak sunulmak yerine `paraYatir()` ve `paraCek()` gibi metotlarla yönetilebilir. Böylece negatif para yatırma veya mevcut bakiyeden fazla para çekme gibi hatalar kontrol edilebilir.

## Kalıtım

Kalıtım, bir sınıfın başka bir sınıfın özelliklerini ve davranışlarını devralmasına olanak sağlar. Ortak özelliklerin tekrar tekrar yazılmasını azaltır.

Örneğin `Calisan` temel sınıfında ad, soyad ve maaş bilgileri bulunabilir. `Yazilimci` ve `Tasarimci` sınıfları `Calisan` sınıfından türeyerek bu ortak özellikleri kullanabilir ve kendi özel davranışlarını ekleyebilir.

## Polimorfizm

Polimorfizm, aynı arayüz veya metot çağrısının farklı nesnelerde farklı davranışlar gösterebilmesidir.

Örneğin `sesCikar()` isimli bir metot, `Kedi` nesnesinde miyavlama, `Kopek` nesnesinde havlama davranışı üretebilir. Kullanıcı kodu nesnenin tam türünü bilmeden ortak arayüz üzerinden çalışabilir.

## Soyutlama

Soyutlama, karmaşık bir sistemin gereksiz ayrıntılarını gizleyip kullanıcıya yalnızca ihtiyaç duyduğu kısmı göstermektir. Bir araba kullanırken motorun içindeki yanma sürecini bilmeden direksiyon, gaz ve fren üzerinden aracı kontrol etmek buna günlük hayattan bir örnektir.

Yazılımda soyutlama; sınıflar, arayüzler ve modüller aracılığıyla karmaşık uygulamaların daha anlaşılır parçalara ayrılmasını sağlar.

## Neden Kullanılır?

Nesne yönelimli programlama özellikle büyük projelerde kodun modüler tutulmasını, aynı yapıların tekrar kullanılmasını ve sorumlulukların daha net ayrılmasını kolaylaştırır. Ancak her problem için zorunlu değildir. Küçük ve basit uygulamalarda gereğinden fazla sınıf oluşturmak kodu gereksiz yere karmaşıklaştırabilir.
