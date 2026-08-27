# Yazılım Testi

## Yazılım Testinin Amacı

Yazılım testi, bir uygulamanın beklenen şekilde çalışıp çalışmadığını doğrulamak ve hataları kullanıcıya ulaşmadan önce bulmak için yapılan çalışmalardır.

Testlerin amacı bir programın hiçbir zaman hata vermeyeceğini kanıtlamak değildir. Amaç, önemli davranışların sistematik biçimde kontrol edilmesi ve değişikliklerin mevcut özellikleri bozma riskinin azaltılmasıdır.

## Unit Test

Unit test, sistemin küçük bir parçasını izole biçimde test eder. Genellikle tek bir fonksiyon, sınıf veya modül hedeflenir.

Örneğin bir fiyat hesaplama fonksiyonunun yüzde 20 indirim uyguladığında doğru sonucu döndürüp döndürmediği unit test ile kontrol edilebilir.

## Integration Test

Integration test, birden fazla bileşenin birlikte doğru çalışıp çalışmadığını kontrol eder.

Örneğin uygulama servisinin veritabanına kayıt ekleyip daha sonra aynı kaydı okuyabilmesi integration test kapsamına girebilir.

## End-to-End Test

End-to-end test, sistemi kullanıcının deneyimine yakın biçimde baştan sona test eder.

Bir e-ticaret uygulamasında kullanıcının giriş yapması, ürünü sepete eklemesi ve sipariş oluşturması tek bir end-to-end senaryosu olabilir.

## Regression

Regression, yeni bir değişikliğin daha önce çalışan özelliği bozmasıdır. Otomatik testler regression hatalarının erken fark edilmesine yardımcı olur.

## Test Case

İyi bir test case yalnızca başarılı senaryoyu kontrol etmez. Hatalı veya sınır durumlar da düşünülmelidir.

Bir yaş alanı için geçerli bir yaş, sıfır, negatif sayı, beklenenden çok büyük sayı, boş değer ve sayı yerine metin gibi durumlar ayrı testler olabilir.

## Mock

Mock, test sırasında gerçek bir bağımlılığın yerine kontrollü bir sahte nesne veya davranış kullanılmasıdır. Örneğin her unit testte gerçek ödeme servisine bağlanmak yerine ödeme servisi mock edilebilir.

Mock kullanımı testleri hızlı ve güvenilir yapabilir. Ancak bütün testlerin mock olması gerçek entegrasyon problemlerini gizleyebilir. Bu nedenle unit testlerin yanında gerçek bileşenlerle integration veya end-to-end testler de önemlidir.
