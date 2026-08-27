# Gereksinim İzlenebilirlik Matrisi

Son doğrulama: 2026-08-27. Hiçbir zorunlu satır yalnızca kod varlığına dayanarak PASS yapılmadı; gerçek Foundry, SQLite ve uçtan uca kanıtları son denetim sırasında yeniden çalıştırıldı. Türkçe uygulama akışı doğrulandı; `knowledge/` içeriği kullanıcı tarafından değiştirileceği için nihai Türkçe içerik kalitesi ayrıca beklemededir.

| # | Requirement | Implementation evidence | Test/runtime evidence | Status |
|---:|---|---|---|---|
| 1 | Foundry Local cihazda çalışıyor | `rag/foundry_runtime.py` | CLI 0.10.3, SDK 1.2.4; gerçek katalog ve inference | PASS |
| 2 | Local chat modeli çağrılabiliyor | `rag/llm.py`, `qwen3.5-2b-text` | `scripts/smoke_chat.py`, real integration, final evaluation | PASS |
| 3 | Local embedding modeli çağrılabiliyor | `rag/embeddings.py`, `qwen3-embedding-0.6b` | `scripts/smoke_embeddings.py`: 3×1024 finite vector | PASS |
| 4 | Runtime cloud LLM gerektirmiyor | `rag/foundry_runtime.py`, SDK native clients | credential/endpoint scan; CoreInterop audit | PASS |
| 5 | 5–10 dokümanlık knowledge base | `knowledge/` altında 7 Markdown | `scripts/list_documents.py`: 7 documents | PASS |
| 6 | Doküman loader çalışıyor | `rag/document_loader.py` | 4 loader unit testi + gerçek loader smoke | PASS |
| 7 | Dokümanlar chunk'lara ayrılıyor | `rag/chunker.py` | 6 chunk unit testi; gerçek 21 chunk | PASS |
| 8 | Source metadata korunuyor | `Document.source`, `Chunk.source` | loader/chunker testleri; SQLite yedi source kontrolü | PASS |
| 9 | Her chunk için embedding üretiliyor | `FoundryEmbeddingModel.embed_texts` | final ingestion: 21 chunk embedded | PASS |
| 10 | SQLite kullanılıyor | `rag/database.py`, `data/knowledge.db` | `PRAGMA integrity_check=ok` | PASS |
| 11 | Chunk ve embedding SQLite'a kaydediliyor | `KnowledgeDatabase.replace_chunks` | 21 row, 21 decoded vectors, dimension 1024 | PASS |
| 12 | Kullanıcı sorusu embedding'i oluşturuluyor | `FoundryEmbeddingModel.embed_query` | real retrieval/evaluation sorguları | PASS |
| 13 | Semantic/cosine similarity çalışıyor | `rag/retrieval.py::cosine_similarity` | unit numeric tests + real score rankings | PASS |
| 14 | En alakalı 2–3 chunk seçiliyor | `TOP_K=3`, `SemanticRetriever.get_top_chunks` | final evaluation top-3 sources/scores | PASS |
| 15 | Retrieved context local LLM'e gönderiliyor | `build_messages`, `RAGPipeline.answer_query` | pipeline recording testi + real E2E | PASS |
| 16 | LLM bağlama dayanarak Türkçe cevap üretiyor | Türkçe ve katı `SYSTEM_PROMPT` | 5/5 cevaplanabilir otomatik değerlendirme; içerik akıcılığı Türkçe belgelerden sonra yeniden incelenecek | PASS* |
| 17 | Source filename gösteriliyor | `AnswerResult.sources`, `app._show_result` | real CLI dry-run, source assertions | PASS |
| 18 | Bilgi yoksa sistem açıkça söylüyor | eşik + `UNKNOWN_ANSWER` | 3/3 cevaplanamaz; tam yanıt: `Bu bilgi sağlanan belgelerde bulunmuyor.` | PASS |
| 19 | CLI kullanılabiliyor | `app.py` | PTY: empty, multiple questions, exit code 0 | PASS |
| 20 | Answerable testler başarılı | evaluation cases | 5/5 PASS | PASS |
| 21 | Unanswerable testler başarılı | evaluation cases | 3/3 PASS | PASS |
| 22 | Edge-case testleri mevcut | empty, short, general, cross-document | 4/4 PASS | PASS |
| 23 | README tamam | `README.md` | içerik checklist audit | PASS |
| 24 | README kurulum komutları doğrulandı | README install/run/test bölümleri | venv, pip, Foundry info, ingestion, app, tests çalıştırıldı | PASS |
| 25 | Demo guide hazır | `DEMO_GUIDE.md` | tek CLI oturumunda 3-soruluk dry-run | PASS |
| 26 | Project report hazır | `PROJECT_REPORT.md` | README/evaluation consistency audit | PASS |
| 27 | Evaluation report hazır | `EVALUATION_REPORT.md` | son 12/12 sonuç ve timing kaydı | PASS |
| 28 | Requirements traceability hazır | bu dosya | 38 mandatory satırın tamamı eşlendi | PASS |
| 29 | Kullanılmayan/debug kod temiz | app/config/rag/scripts/tests | compileall, source scan, pip check | PASS |
| 30 | Modeller her soruda yeniden yüklenmiyor | `RAGPipeline.load`, `_loaded` | tek process çoklu-sorgu evaluation; 2 loaded model | PASS |
| 31 | Re-ingestion duplicate oluşturmuyor | transactional rebuild + UNIQUE constraint | final iki rebuild: ikisi de 21; 21 unique | PASS |
| 32 | Embedding model consistency doğrulandı | DB metadata alias check | DB alias = config alias; retrieval mismatch unit testi | PASS |
| 33 | Gerçek Foundry embedding testi yapıldı | `scripts/smoke_embeddings.py` | dimension 1024, finite, semantic cosine gap | PASS |
| 34 | Gerçek Foundry chat inference yapıldı | `scripts/smoke_chat.py` | gerçek qwen3.5 hello + E2E answers | PASS |
| 35 | Remote OpenAI/Azure key gerekmiyor | projede credential lookup yok | üç env key NOT_SET iken full E2E PASS | PASS |
| 36 | Cache sonrası normal inference cloud istemiyor | SDK native CoreInterop + local cache | chat/embedding execute_command audit; no remote URL | PASS |
| 37 | Sıcak sorgu süresi raporlandı | `scripts/evaluate.py` | soğuk 14.245 sn; sıcak medyan 4.250 sn | PASS |
| 38 | Full end-to-end test başarılı | loader → chunk → embed → SQLite → retrieve → LLM → CLI | 12/12 real evaluation + demo dry-run | PASS |

## Kanıt komutları

```text
.venv/bin/python -m unittest discover -s tests -v
env RUN_REAL_FOUNDRY_TESTS=1 .venv/bin/python -m unittest discover -s tests -p 'test_real_foundry.py' -v
.venv/bin/python scripts/ingest.py
.venv/bin/python scripts/evaluate.py
.venv/bin/python app.py
sqlite3 data/knowledge.db 'PRAGMA integrity_check; ...'
```

Teknik sonuç: **38/38 zorunlu gereksinim PASS**. `PASS*`, çalışma akışının geçtiğini; Türkçe cevap kalitesinin kullanıcı belgeleri eklendikten sonra yeniden inceleneceğini belirtir.
