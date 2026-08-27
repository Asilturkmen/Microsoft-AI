# Değerlendirme Raporu

Tarih: 2026-08-27  
Platform: Apple M1, 8 GB RAM, macOS arm64  
Foundry Local SDK: 1.2.4  
Sohbet modeli: `qwen3.5-2b-text`
Embedding modeli: `qwen3-embedding-0.6b`

## Sonuç özeti

- Birim testleri: **24 PASS**, 2 gerçek-model testi normal koşuda bilinçli olarak SKIP
- Gerçek Foundry entegrasyon testleri: **2/2 PASS**
- Türkçe değerlendirme matrisi: **12/12 PASS**
- Cevaplanabilir: **5/5 PASS**
- Cevaplanamaz: **3/3 PASS**
- Sınır durumları: **4/4 PASS**
- Kontrollü bilinmeyen cevabı: **PASS**
- Kaynak doğruluğu: **PASS**

Bu sonuçlar Türkçeleştirilmiş uygulama, istem, hata mesajı ve test akışının teknik olarak çalıştığını doğrular. Ancak `knowledge/` dosyaları kullanıcının isteğiyle değiştirilmemiştir ve hâlâ İngilizcedir. Bu nedenle Türkçe cevapların dil kalitesi geçicidir; kullanıcı güvenilir Türkçe belgeleri ekledikten sonra nihai içerik denetimi ve eşik kalibrasyonu yeniden yapılmalıdır.

## Değerlendirme yöntemi

Kalıcı vakalar `tests/evaluation_cases.json` içindedir. `scripts/evaluate.py` iki Foundry modelini bir kez yükler; bütün vakaları aynı model yaşam döngüsünde çalıştırır; kaynak, gerekli cevap terimi, kontrollü bilinmeyen cevabı ve hata beklentilerini denetler; soğuk yükleme ile sıcak sorgu sürelerini ayrı ölçer.

Çalıştırılan komutlar:

```text
.venv/bin/python -m unittest discover -s tests -v
env RUN_REAL_FOUNDRY_TESTS=1 .venv/bin/python -m unittest discover -s tests -p 'test_real_foundry.py' -v
.venv/bin/python scripts/evaluate.py
```

## Son gerçek Türkçe değerlendirme matrisi

| ID | Kategori | Beklenen/gerçek kaynak | En yüksek skor | Süre | Sonuç |
|---|---|---|---:|---:|---|
| cevaplanabilir_acid | Cevaplanabilir | `databases.md` | 0.667166 | 4.771 sn | PASS |
| cevaplanabilir_tcp_udp | Cevaplanabilir | `networking.md` | 0.620011 | 5.766 sn | PASS |
| cevaplanabilir_web_api | Cevaplanabilir | `web-development.md` | 0.683195 | 8.305 sn | PASS |
| cevaplanabilir_git_dali | Cevaplanabilir | `git-basics.md` | 0.614069 | 12.964 sn | PASS |
| cevaplanabilir_test_seviyeleri | Cevaplanabilir | `software-testing.md` | 0.666048 | 7.671 sn | PASS |
| cevaplanamaz_dunya_kupasi | Cevaplanamaz | kaynak yok/kontrollü cevap | 0.158867 | 0.322 sn | PASS |
| cevaplanamaz_tiramisu | Cevaplanamaz | kaynak yok/kontrollü cevap | 0.204500 | 0.074 sn | PASS |
| cevaplanamaz_fotosentez | Cevaplanamaz | kaynak yok/kontrollü cevap | 0.248889 | 0.076 sn | PASS |
| sinir_bos | Sınır | `ValueError` | yok | 0.004 sn | PASS |
| sinir_kisa | Sınır | `networking.md` | 0.631758 | 4.250 sn | PASS |
| sinir_genel | Sınır | kaynak yok/kontrollü cevap | 0.283010 | 0.225 sn | PASS |
| sinir_coklu_belge | Sınır | kaynak yok/kontrollü cevap | 0.480033 | 0.096 sn | PASS |

## Süreler

- Soğuk model yükleme: **14.245 sn**
- Sıcak sorgu minimumu: **0.074 sn**
- Sıcak sorgu medyanı: **4.250 sn**
- Sıcak sorgu maksimumu: **12.964 sn**

Kontrollü cevap verilen sorgularda LLM üretimi çalışmadığı için bu grup daha hızlıdır. İlk model indirmeleri soğuk yükleme süresine dahil değildir; modeller önceden önbelleğe alınmıştır.

## Grounding ve eşik gerekçesi

Mevcut İngilizce örnek belgelerde güvenilir seçilen Türkçe sorgular için ölçülen dağılım:

- Cevaplanabilir en yüksek skorları: **0.614069–0.683195**
- Cevaplanamaz en yüksek skorları: **0.158867–0.256008**

`0.50` eşiği bu geçici veri kümesinde iki grup arasında kalır. Eşik altındaki sorgular sohbet modeline gönderilmeden deterministik olarak şu yanıtı verir:

```text
Bu bilgi sağlanan belgelerde bulunmuyor.
```

Bu değer nihai değildir. Türkçe belgeler, dosya adları ve konu dağılımı retrieval skorlarını değiştireceğinden, belge değişiminden sonra `scripts/ingest.py` ve `scripts/evaluate.py` yeniden çalıştırılmalıdır.

## Dil kalitesi incelemesi

Otomatik kontroller doğru kaynağın getirildiğini, beklenen teknik terimlerin bulunduğunu ve bilinmeyen soruların reddedildiğini doğruladı. Manuel incelemede İngilizce bağlamdan Türkçe üretim yapılırken bazı doğal olmayan ifadeler görüldü. Örneğin model bir çalıştırmada “consistency” terimini “konsantrasyon”, “commit” terimini ise “komite” olarak çevirdi; bazı cevaplar da hedeflenenden uzun oldu.

Bu kusurlar uygulama arayüzünden değil, geçici İngilizce kaynak metinlerin küçük yerel model tarafından anlık çevrilmesinden kaynaklanır. Kullanıcının ekleyeceği Türkçe belgeler üzerinde aynı sorularla manuel doğruluk ve akıcılık denetimi yapılmadan Türkçe içerik kalitesi nihai kabul edilmemelidir.

## Bilinen sınırlamalar

- `knowledge/` içeriği şu anda İngilizcedir ve bilerek değiştirilmemiştir.
- Eşik mevcut örnek belgeler ve seçilmiş Türkçe değerlendirme sorularına göre geçici olarak doğrulanmıştır.
- Brute-force cosine retrieval küçük koleksiyon için uygundur; çok büyük koleksiyonlarda vector index gerekebilir.
- Yerel model çıktısı generatif olduğundan kelime seçimi çalıştırmalar arasında küçük farklılık gösterebilir.
- 8 GB cihazda soğuk model yükleme sıcak sorgudan belirgin biçimde uzundur.

## Web UI ve PDF doğrulama eki

- Backend: 34 test; 32 PASS, 2 gerçek-model testi normal suite içinde opt-in SKIP
- Frontend: 4/4 component testi PASS
- TypeScript + Vite production build: PASS
- Chromium: masaüstü chat/source/fallback ve mobil responsive/overflow testleri PASS
- Console/page error: 0
- Gerçek PDF: upload → metin çıkarma → 1 parça → Foundry embedding → geçici SQLite → retrieval → `MAVI-47` cevabı ve PDF source PASS

PDF smoke testi geçici dizinde çalıştırıldığı için projenin gerçek `knowledge/` içeriğini veya `data/knowledge.db` indeksini değiştirmedi.
