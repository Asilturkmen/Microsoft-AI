# Project Report — Local RAG Study Assistant

## Proje özeti

Bu proje, yedi yerel yazılım mühendisliği dokümanından bilgi bulan ve Microsoft Foundry Local üzerinde çalışan cihaz-içi bir modelle grounded cevap üreten küçük bir RAG asistanıdır. Kullanıcıya cevapla birlikte source dosya adları gösterilir; belgelerde yeterli bilgi yoksa sistem genel model bilgisini kullanmak yerine kontrollü biçimde reddeder.

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
- **Model lifecycle:** İki model uygulama başlangıcında bir kez yüklenir ve kapanışta unload edilir.

## Doğrulanan sonuçlar

- 7 doküman → 21 chunk → 21 gerçek embedding → 21 benzersiz SQLite satırı
- Re-ingestion iki kez çalıştırıldı; row count 21 kaldı
- Unit: 24 PASS
- Gerçek Foundry integration: 2/2 PASS
- Evaluation: 5/5 answerable, 3/3 unanswerable, 4/4 edge; toplam 12/12 PASS
- Cold load: 14.844 sn
- Warm sorgu: min 0.064, median 2.213, max 2.875 sn
- Remote LLM key veya endpoint: yok

## Gerçek teknik zorluklar ve lessons learned

İlk seçilen `qwen2.5-0.5b` modeli küçük ve hızlıydı, fakat strict prompt'a rağmen normalization yanıtına unsupported ayrıntılar ekledi ve bir denemede TCP/UDP davranışını ters anlattı. Yalnızca testin çalışması yeterli kabul edilmedi; katalogdaki daha güçlü `qwen3.5-2b-text` modeline geçildi, prompt sadeleştirildi ve temperature/seed sınırlandı. Son evaluation grounded ve doğru sonuç verdi.

İkinci önemli ders, unknown threshold'un tahminle belirlenmemesiydi. Gerçek answerable skorları 0.650893 üzerindeyken unanswerable skorları 0.298080 altında kaldı. 0.50 eşik iki grup arasında güvenli bir ayrım sağladı ve unanswerable sorgularda LLM çağrısını tamamen önledi.

## Offline ve privacy

İlk kurulum/model download internet gerektirebilir. Cache tamamlandıktan sonra uygulama OpenAI cloud, Azure OpenAI veya başka remote inference servisi kullanmaz. SDK'nın `openai` dependency'si yalnızca uyumlu veri tipleri içindir; gerçek request SDK'nın native `CoreInterop` katmanına gider. Knowledge base ve SQLite kullanıcı cihazında kalır.

## Sınırlamalar ve gelecek çalışma

Mevcut loader Markdown/TXT ile sınırlıdır; retrieval küçük veri setinde brute-force çalışır. Domain değişince threshold yeniden ölçülmelidir. Gelecekte PDF/DOCX, büyük koleksiyonlar için local vector index, chunk-level citation ve opsiyonel web UI eklenebilir. Bu geliştirmeler çekirdek local RAG akışını ve CLI'ı bozmadan yapılmalıdır.
