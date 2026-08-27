# Evaluation Report

Tarih: 2026-08-27  
Platform: Apple M1, 8 GB RAM, macOS arm64  
Foundry Local SDK: 1.2.4  
Chat modeli: `qwen3.5-2b-text`  
Embedding modeli: `qwen3-embedding-0.6b`

## Sonuç özeti

- Unit suite: **24 PASS**, 2 gerçek-model testi normal koşuda bilinçli olarak SKIP
- Gerçek Foundry integration suite: **2/2 PASS**
- Gerçek evaluation matrisi: **12/12 PASS**
- Answerable: **5/5 PASS**
- Unanswerable: **3/3 PASS**
- Edge case: **4/4 PASS**
- Hallucination fallback: **PASS**
- Source doğruluğu: **PASS**

## Evaluation yöntemi

Kalıcı vakalar `tests/evaluation_cases.json` içindedir. `scripts/evaluate.py` iki Foundry modelini bir kez yükler; bütün vakaları aynı model yaşam döngüsünde çalıştırır; source, gerekli cevap terimi, fallback ve hata beklentilerini denetler; cold-load ile warm-query sürelerini ayrı ölçer.

Çalıştırılan komutlar:

```text
.venv/bin/python -m unittest discover -s tests -v
env RUN_REAL_FOUNDRY_TESTS=1 .venv/bin/python -m unittest discover -s tests -p 'test_real_foundry.py' -v
.venv/bin/python scripts/evaluate.py
```

## Son gerçek evaluation matrisi

| ID | Kategori | Beklenen/gerçek source | Top score | Süre | Sonuç |
|---|---|---|---:|---:|---|
| answerable_normalization | Answerable | `databases.md` | 0.777587 | 2.799 sn | PASS |
| answerable_tcp_udp | Answerable | `networking.md` | 0.755604 | 2.875 sn | PASS |
| answerable_polymorphism | Answerable | `oop.md` | 0.783113 | 2.213 sn | PASS |
| answerable_virtual_memory | Answerable | `operating-systems.md` | 0.710864 | 2.568 sn | PASS |
| answerable_integration_tests | Answerable | `software-testing.md` | 0.685905 | 2.338 sn | PASS |
| unanswerable_world_cup | Unanswerable | source yok/fallback | 0.197778 | 0.225 sn | PASS |
| unanswerable_tiramisu | Unanswerable | source yok/fallback | 0.254877 | 0.067 sn | PASS |
| unanswerable_photosynthesis | Unanswerable | source yok/fallback | 0.298080 | 0.064 sn | PASS |
| edge_empty | Edge | `ValueError` | n/a | <0.001 sn | PASS |
| edge_short | Edge | `networking.md` | 0.631758 | 2.188 sn | PASS |
| edge_general | Edge | source yok/fallback | 0.307663 | 0.065 sn | PASS |
| edge_cross_document | Edge | `git-basics.md`, `databases.md` | 0.616530 | 2.445 sn | PASS |

## Timing

- Cold model load: **14.844 sn**
- Warm query minimum: **0.064 sn**
- Warm query median: **2.213 sn**
- Warm query maximum: **2.875 sn**

Fallback sorguları LLM generation çalıştırmadığı için en hızlı gruptur. Gerçek answer-generation sorguları bu ölçümde yaklaşık 2.2–2.9 saniye sürmüştür. İlk model indirmeleri cold-load süresine dahil değildir; modeller önceden cache'lenmiştir.

## Grounding ve threshold gerekçesi

Threshold seçilmeden önce gerçek retrieval score dağılımı ölçüldü:

- 7 answerable top-1: **0.650893–0.783113**
- 5 unanswerable top-1: **0.197778–0.298080**

İki küme arasındaki boşluk nedeniyle `0.50` konservatif eşik olarak seçildi. Eşik altı sorgular chat completion'a gönderilmeden deterministik olarak şu yanıtı verir:

```text
The information is not available in the provided documents.
```

İlk 0.5B chat modeli strict prompt'a rağmen unsupported ayrıntılar ve bir TCP/UDP doğruluk hatası üretti. Bunun üzerine gerçek katalogdaki `qwen3.5-2b-text` modeline geçildi. Son evaluation yanıtları source içerikleriyle uyumlu, kısa ve doğru bulundu.

## Bilinen sınırlamalar

- Threshold mevcut yedi doküman ve değerlendirme sorularına göre kalibre edilmiştir; knowledge domain ciddi biçimde değişirse yeniden ölçülmelidir.
- Brute-force cosine retrieval küçük koleksiyon için uygundur; çok büyük koleksiyonlarda vector index gerekebilir.
- Local LLM çıktısı generatif olduğundan kelime seçimi çalıştırmalar arasında küçük farklılık gösterebilir; evaluation source ve anlamlı anahtar terim kontrollerini birlikte kullanır.
- 8 GB cihazda cold model load warm sorgudan belirgin biçimde uzundur.
