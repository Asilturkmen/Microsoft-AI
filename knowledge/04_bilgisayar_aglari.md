# Bilgisayar Ağları

## Bilgisayar Ağı Nedir?

Bilgisayar ağı, cihazların veri alışverişi yapabilmesini sağlayan iletişim sistemidir. Evdeki telefonun Wi-Fi üzerinden internete bağlanması, bir web sitesine erişilmesi veya iki sunucunun veri paylaşması ağ iletişimine örnektir.

## IP Adresi

IP adresi, bir ağ üzerindeki cihazın iletişim için kullandığı mantıksal adrestir. IPv4 adresleri genellikle `192.168.1.10` gibi dört sayıdan oluşur. IPv6 ise çok daha geniş bir adres alanı sağlar.

## DNS

DNS, alan adlarını IP adreslerine dönüştüren sistemdir. Kullanıcının tarayıcıya bir alan adı yazması daha kolaydır; bilgisayarın ise bağlantı kurmak için hedef sunucunun IP adresini bilmesi gerekir.

## TCP

TCP bağlantı odaklı bir taşıma protokolüdür. Verinin doğru sırada ve güvenilir biçimde karşı tarafa ulaşmasını sağlamaya çalışır.

TCP; paket kaybını algılama, yeniden iletim ve sıralama gibi mekanizmalara sahiptir.

## UDP

UDP daha hafif ve bağlantısız bir protokoldür. Teslim garantisi veya paketlerin doğru sırada ulaşması gibi mekanizmaları TCP kadar güçlü biçimde sağlamaz.

Bunun karşılığında daha düşük ek yükle hızlı iletişim kurulabilir. Gerçek zamanlı oyunlar, canlı ses veya görüntü gibi gecikmenin önemli olduğu senaryolarda UDP tercih edilebilir.

## HTTP ve HTTPS

HTTP, web istemcileri ile sunucular arasında veri alışverişinde kullanılan uygulama katmanı protokolüdür.

HTTPS, HTTP iletişiminin TLS ile şifrelenmiş biçimidir. HTTPS kullanıldığında istemci ile sunucu arasındaki veri ağ üzerinde okunması zor bir biçimde iletilir.

## Port

Aynı cihaz üzerinde birden fazla ağ servisi çalışabilir. Port numaraları gelen trafiğin hangi uygulama veya servise yönlendirileceğini belirlemeye yardımcı olur.

HTTPS için varsayılan port 443'tür.

## Latency ve Bandwidth

Latency, verinin kaynaktan hedefe ulaşması için geçen süreyle ilgilidir. Bandwidth ise belirli bir süre içinde aktarılabilecek veri miktarını ifade eder.

Yüksek bandwidth tek başına düşük gecikme anlamına gelmez.
