# Demo Guide — Local RAG Study Assistant

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

## Live Demo 1 — Database belgesi

Sor:

```text
What is database normalization and why is it used?
```

Beklenen davranış:

- Normalization'ın duplicated data ve update anomalies'i azaltmak için tabloları organize ettiğini söyler.
- Source: `databases.md`
- Son gerçek top-3 skorları: 0.7776, 0.6069, 0.5106

Kısa anlatım: “Soru embedding'i database chunk'larını ilk üç sıraya getirdi ve model sadece bu context'i kullandı.”

## Live Demo 2 — Networking belgesi

Sor:

```text
How are TCP and UDP different?
```

Beklenen davranış:

- TCP'nin connection, ordered/reliable delivery; UDP'nin guarantee olmadan datagram davranışını açıklar.
- Source: `networking.md`
- Son gerçek top-3 skorları: 0.7556, 0.5052, 0.4760

Kısa anlatım: “İkinci soru farklı bir belgeyi getiriyor; retrieval tek bir hard-coded konuya bağlı değil.”

## Live Demo 3 — Belgelerde olmayan bilgi

Sor:

```text
What ingredients are needed for tiramisu?
```

Beklenen cevap:

```text
The information is not available in the provided documents.
```

Beklenen davranış:

- Source göstermez.
- Son gerçek top score: 0.254877; 0.50 threshold'un altında.
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
6. `app.py` üzerinden üç live demo sorusunu sırayla sor.
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
Gerçek answerable skorları 0.650893–0.783113, unanswerable skorları 0.197778–0.298080 çıktı. 0.50 bu iki kümenin arasındaki konservatif boşlukta.

**Re-ingestion duplicate üretir mi?**  
Hayır. SQLite index transaction içinde rebuild edilir. İki gerçek çalıştırmada da row count 21 kaldı ve 21 source/chunk anahtarının tamamı benzersizdi.

**En büyük teknik sorun neydi?**  
İlk 0.5B chat modeli strict prompt'a uymadı ve bir testte TCP/UDP'yi ters anlattı. Daha güçlü `qwen3.5-2b-text` modeline geçip prompt ve deterministic generation ayarlarını iyileştirdim.

**Performans nasıl?**  
Son ölçümde cache'lenmiş modellerin cold load süresi 14.844 sn, warm query medianı 2.213 sn, maksimumu 2.875 sn idi.

**Mevcut sınırlamalar?**  
Markdown/TXT desteği, küçük koleksiyon için brute-force retrieval ve domain değişince yeniden threshold calibration gereksinimi.

## Demo kapanış cümlesi

“Sonuç olarak proje gerçek local embedding, SQLite persistence, cosine retrieval ve Foundry Local chat generation'ı tek bir offline-ready RAG akışında birleştiriyor; bilgi belgelerde yoksa cevap uydurmuyor.”
