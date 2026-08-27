# Demo Rehberi — Yerel RAG Çalışma Asistanı

## Demo öncesi tek hazırlık

İlk model indirmeleri daha önce tamamlanmış olmalıdır. Demo öncesinde index'i yeniden kurup hızlı kontrol yap:

```bash
source .venv/bin/activate
python scripts/ingest.py
python app.py
```

## 1–2 dakikalık anlatım metni

“Bu proje, tamamen bilgisayarımda çalışan bir Local RAG Study Assistant. Knowledge base içinde yedi kısa yazılım mühendisliği belgesi var. RAG kullanmamın nedeni, modelin genel bilgisinden cevap vermesi yerine önce bu belgelerden kanıt bulmasını sağlamak.

Ingestion sırasında belgeleri başlık ve paragraf sınırlarına göre 21 parçaya ayırıyorum. Microsoft Foundry Local üzerindeki embedding modeli her parçayı 1024 sayılık bir anlam vektörüne dönüştürüyor ve içerik, source adı, chunk index ile birlikte SQLite'a kaydediyorum.

Kullanıcı soru sorunca aynı local embedding modeli soruyu vektöre dönüştürüyor. Cosine similarity en alakalı üç parçayı seçiyor. En yüksek skor 0.50'nin altındaysa sistem bilgi uydurmadan doğrudan belgelerde cevap olmadığını söylüyor. Yeterli kanıt varsa sadece bulunan context, Foundry Local üzerinde cihazda çalışan chat modeline veriliyor. Cevap ve source dosya adları terminalde gösteriliyor. Normal inference için OpenAI veya Azure API anahtarı gerekmiyor.”

## Canlı Demo 1 — Veritabanı belgesi

Sor:

```text
ACID transaction özellikleri nelerdir?
```

Beklenen davranış:

- ACID özelliklerini Türkçe olarak açıklar.
- Source: `databases.md`
- Mevcut örnek knowledge ile ölçülen top-1 skor: 0.667166

Kısa anlatım: “Türkçe soru embedding'i doğru veritabanı parçasını buldu ve model İngilizce bağlamı belgeye sadık Türkçe bir cevaba dönüştürdü.”

## Canlı Demo 2 — Ağ belgesi

Sor:

```text
TCP ile UDP arasındaki farklar nelerdir?
```

Beklenen davranış:

- TCP'nin bağlantılı ve güvenilir teslim; UDP'nin garanti vermeyen datagram davranışını Türkçe açıklar.
- Source: `networking.md`
- Mevcut örnek knowledge ile ölçülen top-1 skor: 0.620011

Kısa anlatım: “İkinci soru farklı bir belgeyi getiriyor; retrieval tek bir hard-coded konuya bağlı değil.”

## Canlı Demo 3 — Belgelerde olmayan bilgi

Sor:

```text
Tiramisu yapmak için hangi malzemeler gerekir?
```

Beklenen cevap:

```text
Bu bilgi sağlanan belgelerde bulunmuyor.
```

Beklenen davranış:

- Source göstermez.
- Mevcut örnek knowledge ile ölçülen top score: 0.204500; 0.50 threshold'un altında.
- Chat completion'a gitmeden deterministic fallback kullanır.

Kısa anlatım: “Bu, modelin genel yemek bilgisini kullanıp cevap uydurmadığını gösteriyor.”

## Kavramların çok basit açıklaması

- **RAG:** Önce belgede ilgili yeri bul, sonra o bilgiyle cevap üret.
- **Embedding:** Bir metnin anlamını sayılardan oluşan bir vektörle temsil eder.
- **Cosine similarity:** Soru vektörüyle belge vektörünün yönlerinin ne kadar benzer olduğunu ölçer.
- **SQLite:** Chunk metni, source ve embeddingleri bilgisayarda tek bir yerel dosyada saklar.
- **Retrieval:** En alakalı üç chunk'ı score sırasıyla seçer.
- **Foundry Local:** Embedding ve chat modellerini cloud yerine cihazda çalıştırır.
- **Grounding:** Cevabın yalnızca verilen belge context'ine dayanmasıdır.

## Mimariyi gösterme sırası

1. `knowledge/` içindeki yedi dokümanı göster.
2. `scripts/ingest.py` ile 7 → 21 → SQLite çıktısını göster.
3. `config.py` içindeki iki model alias'ını, top-k 3 ve threshold 0.50'yi göster.
4. `rag/retrieval.py` içindeki cosine sıralamasını göster.
5. `rag/pipeline.py` içindeki threshold ve grounded prompt'u göster.
6. `app.py` üzerinden üç canlı demo sorusunu sırayla sor.
7. `EVALUATION_REPORT.md` içindeki 12/12 PASS ve timing tablosunu göster.

## Muhtemel değerlendirici soruları

**Neden keyword search değil?**  
Gereksinim semantic retrieval'dı. Hem belgeler hem soru aynı local embedding modeliyle vektörleştiriliyor ve gerçek cosine similarity ile sıralanıyor.

**SQLite bir vector database mi?**  
Hayır. Bu küçük koleksiyonda SQLite persistence sağlıyor; 21 vektör Python tarafında brute-force karşılaştırılıyor. Daha büyük ölçekte local vector index eklenebilir.

**Cloud kullanılmadığını nasıl biliyorsun?**  
Kodda API key veya remote endpoint yok. Microsoft SDK client'ları request'i native `CoreInterop` üzerinden Foundry Local Core'a gönderiyor. Gerçek chat ve embedding testleri local modellerle çalıştı.

**Python `openai` paketi neden kurulu?**  
Bu, resmî Foundry Local SDK'nın transitive dependency'si ve uyumlu request/response tipleri için kullanılıyor. Proje doğrudan import etmiyor ve OpenAI endpoint'ine bağlanmıyor.

**Model neden her soruda yeniden yüklenmiyor?**  
Pipeline iki modeli CLI başlangıcında bir kez yüklüyor, bütün sorularda aynı client'ları kullanıyor ve çıkışta unload ediyor.

**Threshold neden 0.50?**  
Mevcut İngilizce örnek knowledge üzerinde güvenilir seçilen Türkçe answerable sorular 0.614069–0.683195, unanswerable sorular 0.158867–0.256008 aralığında kaldı. 0.50 iki kümenin arasındaki güvenli boşlukta. Türkçe belgeler eklendikten sonra bu ölçüm tekrarlanmalıdır.

**Re-ingestion duplicate üretir mi?**  
Hayır. SQLite index transaction içinde rebuild edilir. İki gerçek çalıştırmada da row count 21 kaldı ve 21 source/chunk anahtarının tamamı benzersizdi.

**En büyük teknik sorun neydi?**  
İlk 0.5B chat modeli strict prompt'a uymadı ve bir testte TCP/UDP'yi ters anlattı. Daha güçlü `qwen3.5-2b-text` modeline geçip prompt ve deterministic generation ayarlarını iyileştirdim.

**Performans nasıl?**  
Son Türkçe değerlendirmede önbellekteki modellerin soğuk yükleme süresi 14.245 sn, sıcak sorgu medyanı 4.250 sn, maksimumu 12.964 sn idi. Bu ölçümler mevcut İngilizce örnek belgelerle alınmıştır.

**Mevcut sınırlamalar?**  
Markdown/TXT desteği, küçük koleksiyon için brute-force retrieval ve alan değişince eşik kalibrasyonunun yenilenmesi gerekir. Ayrıca mevcut örnek belgeler İngilizcedir; güvenilir Türkçe belgeler eklendikten sonra cevap akıcılığı ve doğruluğu yeniden denetlenmelidir.

## Demo kapanış cümlesi

“Sonuç olarak proje gerçek local embedding, SQLite persistence, cosine retrieval ve Foundry Local chat generation'ı tek bir offline-ready RAG akışında birleştiriyor; bilgi belgelerde yoksa cevap uydurmuyor.”
