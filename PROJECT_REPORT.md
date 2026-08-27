# Proje Raporu — Yerel RAG Çalışma Asistanı

## Proje özeti

Bu proje, yedi yerel yazılım mühendisliği belgesinden bilgi bulan ve Microsoft Foundry Local üzerinde çalışan cihaz-içi bir modelle kaynaklara dayalı cevap üreten küçük bir RAG asistanıdır. Kullanıcıya cevapla birlikte kaynak dosya adları gösterilir; belgelerde yeterli bilgi yoksa sistem genel model bilgisini kullanmak yerine kontrollü biçimde reddeder.

## Neden bu çözüm?

Yerel ders notları genel bir modelin eğitim verisinde bulunmayabilir. Belgelerin tamamını her soruda modele vermek hem gereksiz hem de gerçek retrieval değildir. Bu nedenle sistem belgeleri küçük passage'lara ayırır, anlamlarını embeddinglerle temsil eder ve sadece en ilgili üç passage'ı modele gönderir. Foundry Local, chat ve embedding inference'ın cihazda kalmasını sağlar; SQLite ise basit, taşınabilir ve tamamen yerel persistence sağlar.

## Mimari kararlar

- **Python 3.12 ve basit modüller:** Gereksiz framework eklenmedi.
- **Foundry Local SDK 1.2.4:** Chat için `qwen3.5-2b-text`, embedding için `qwen3-embedding-0.6b` kullanıldı.
- **Heading-aware chunking:** Yedi belge 21 anlamlı chunk'a ayrıldı; source ve chunk index korundu.
- **SQLite:** Content, source, index ve 1024 boyutlu embedding JSON olarak saklandı. Metadata model alias/dimension consistency sağlar.
- **Brute-force cosine retrieval:** 21 chunk için anlaşılır ve yeterince hızlıdır; varsayılan top-k 3'tür.
- **0.50 unknown threshold:** Kör bir sabit yerine gerçek answerable/unanswerable score dağılımındaki boşluktan seçildi.
- **CLI:** Programın minimum arayüz gereksinimini düşük riskle karşılar ve aynı pipeline ile ardışık soru destekler.
- **Web ürünü:** React/TypeScript/Tailwind arayüzü, FastAPI üzerinden aynı çekirdek pipeline'ı kullanır; responsive chat, gerçek kaynaklar, runtime durumu ve PDF upload sağlar.
- **Gerçek PDF ingestion:** Metin katmanlı PDF, `pypdf` ile okunur; mevcut chunker, Foundry embedding modeli ve atomik SQLite rebuild akışına dahil edilir.
- **Model lifecycle:** İki model uygulama başlangıcında bir kez yüklenir ve kapanışta unload edilir.

## Doğrulanan sonuçlar

- 7 doküman → 21 chunk → 21 gerçek embedding → 21 benzersiz SQLite satırı
- Re-ingestion iki kez çalıştırıldı; row count 21 kaldı
- Birim testleri: 24 PASS
- Gerçek Foundry entegrasyon testleri: 2/2 PASS
- Türkçe değerlendirme: 5/5 cevaplanabilir, 3/3 cevaplanamaz, 4/4 sınır durumu; toplam 12/12 PASS
- Soğuk yükleme: 14.245 sn
- Sıcak sorgu: min 0.074, medyan 4.250, maks 12.964 sn
- Remote LLM key veya endpoint: yok
- Frontend component testleri: 4/4 PASS; production build PASS
- Chromium UI: masaüstü ve mobil PASS; ciddi console/page error yok
- Gerçek geçici PDF E2E: upload → 1 parça → embedding → SQLite → retrieval → doğru cevap/source PASS

Bu testler Türkçeleştirilmiş uygulama akışını doğrular. `knowledge/` dosyaları kullanıcının isteğiyle değiştirilmemiştir ve mevcut örnekler İngilizcedir. Dolayısıyla Türkçe cevapların nihai doğruluk ve akıcılık denetimi, kullanıcı güvenilir Türkçe belgeleri ekledikten sonra yeniden yapılacaktır.

## Gerçek teknik zorluklar ve lessons learned

İlk seçilen `qwen2.5-0.5b` modeli küçük ve hızlıydı, fakat strict prompt'a rağmen normalization yanıtına unsupported ayrıntılar ekledi ve bir denemede TCP/UDP davranışını ters anlattı. Yalnızca testin çalışması yeterli kabul edilmedi; katalogdaki daha güçlü `qwen3.5-2b-text` modeline geçildi, prompt sadeleştirildi ve temperature/seed sınırlandı. Son evaluation grounded ve doğru sonuç verdi.

İkinci önemli ders, bilinmeyen cevabı eşiğinin tahminle belirlenmemesiydi. Mevcut İngilizce örnek belgelerde güvenilir seçilen Türkçe cevaplanabilir sorgular 0.614069–0.683195, cevaplanamaz sorgular 0.158867–0.256008 aralığında kaldı. 0.50 eşik bu geçici veri kümesinde iki grup arasında güvenli bir ayrım sağladı ve cevaplanamaz sorgularda LLM çağrısını tamamen önledi. Türkçe belgeler eklendiğinde eşik yeniden ölçülmelidir.

## Offline ve privacy

İlk kurulum/model download internet gerektirebilir. Cache tamamlandıktan sonra uygulama OpenAI cloud, Azure OpenAI veya başka remote inference servisi kullanmaz. SDK'nın `openai` dependency'si yalnızca uyumlu veri tipleri içindir; gerçek request SDK'nın native `CoreInterop` katmanına gider. Knowledge base ve SQLite kullanıcı cihazında kalır.

## Sınırlamalar ve gelecek çalışma

Mevcut yükleyici Markdown/TXT ve metin katmanlı PDF destekler; taranmış PDF için OCR, DOCX desteği ve büyük koleksiyonlar için vektör indeksi henüz yoktur. Alan veya belge dili değişince eşik yeniden ölçülmelidir. Mevcut İngilizce örnek içerik küçük yerel modelde zaman zaman doğal olmayan Türkçe terimlere neden olmaktadır. Web upload işleri süreç içi izlenir; çok kullanıcılı dağıtımda kalıcı job kuyruğu eklenebilir.
