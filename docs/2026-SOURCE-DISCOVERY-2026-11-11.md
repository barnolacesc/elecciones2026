# Official 2026 General Election Programme Discovery and Ingestion Audit — 2026-11-11

**Document version:** 1.0.0  
**Audit date:** 2026-11-11  
**Roadmap package:** E0.4 (Issue #3)  
**Election identifier:** `es-gen-2026` (Spanish General Election, 29 November 2026)  
**Governing decrees:** [BOE-A-2026-20742](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742) (Real Decreto 806/2026)

---

## 1. Executive Summary

On 11 November 2026, an offline discovery and retrieval pass for the 29 November 2026 general election was performed. Eight candidate programme documents were downloaded and subjected to structural PDF parsing and cryptographic verification.

All eight documents were imported into the private source archive outside Git (`$HOME/Library/Application Support/elecciones2026/private-sources/es-gen-2026/`) with restricted permissions (`0700` directories, `0600` files). In accordance with `AGENTS.md` and ADR-0002, original PDF files are strictly excluded from the Git repository.

---

## 2. Document Inventory and Cryptographic Signatures

| Party / Candidacy | File | Pages | Bytes | SHA-256 Checksum | Discovery / Official URL | Direct URL | Status |
|---|---|---|---|---|---|---|---|
| **PP** | `PP_2026_Reconstruccion_Nacional_ES.pdf` | 64 | 12,304,990 | `ae0c35d7ef3faf540acaa79d47abbe3ae2bf56a3a755c4e78a8f5bf3ea49789c` | [PP Documentos](https://www.pp.es/actualidad/documentos/) | [Direct PDF](https://www.pp.es/wp-content/uploads/2026/11/PROGRAMA-ELECTORAL-PP-2026-RECONSTRUCCION-NACIONAL.pdf) | `published-unverified` |
| **ERC** | `ERC_2026_Programa_Electoral_CA.pdf` | 48 | 300,308 | `61728d162a6e88d492d44a0b0994effb31f9e4abb85ebf8aea715d870a9b2e04` | [ERC Oficial](https://esquerrarepublicana.cat/) | [Direct PDF](https://esquerrarepublicana.cat/documents/e2026-programa.pdf) | `published-unverified` |
| **EAJ-PNV** | `EAJ_PNV_2026_Programa_Electoral_29N_ES.pdf` | 43 | 509,986 | `5af7a5b6f67c26bad87ef6c3ca01ae38aa1f1d7d9029efb32fc52482de0c1314` | [EAJ-PNV Documentos](https://www.eaj-pnv.eus/es/adjuntos-documentos/21765/pdf/programa-electoral-29n) | [Direct PDF](https://www.eaj-pnv.eus/es/adjuntos-documentos/21765/pdf/programa-electoral-29n) | `published-unverified` |
| **BNG** | `BNG_2026_Programa_Electoral_29N_GL.pdf` | 91 | 1,387,491 | `fd5aef260b9c66d030b57b7b0e18914c8ad79384e2c46b2346d9fb4f6514a97d` | [BNG Oficial](https://www.bng.gal/) | [Direct PDF](https://www.bng.gal/media/bnggaliza/files/2026/11/03/26_bng_xerais_documentos_programa_electoral.pdf) | `published-unverified` |
| **Coalición Canaria** | `Coalicion_Canaria_2026_Programa_Electoral_29N_ES.pdf` | 23 | 69,215,587 | `3c40c0a6e38d8dd80ae1061d94b614f4e3f1b6492ec8c801834fb497f337044e` | [Coalición Canaria](https://coalicioncanaria.org/) | [Direct PDF](https://coalicioncanaria.org/wp-content/uploads/2026/11/CCA-26-Programa_Electoral-29NOV.pdf) | `published-unverified` |
| **SALF** | `SALF_2026_Contrato_Electoral_29N_ES.pdf` | 40 | 19,063,086 | `073425b9522da77608a0399923c2e0d3b9153776e8a0436ac8f0aea794b7893b` | [Se Acabó La Fiesta](https://www.seacabolafiesta.com/) | [Direct PDF](https://www.seacabolafiesta.com/SALF_Contrato_Electoral_29N.pdf?v=073425b9522d) | `published-unverified` |
| **Partido Humanista** | `Partido_Humanista_2026_Programa_Generales_ES.pdf` | 31 | 461,126 | `c53ab576b0c57a091665795cb8676269b85cc6f9b7e22c9d65ce11d86502086f` | [Partido Humanista](https://partidohumanista.es/) | [Direct PDF](https://partidohumanista.es/Documentos/Programas/Programa%20Generales%202026.pdf) | `published-unverified` |
| **Frente Obrero** | `Frente_Obrero_Programa_Politico_FECHA_NO_CONFIRMADA_ES.pdf` | 64 | 1,202,338 | `7b9f423f2c1ada187b6f42ed8dbf4e025356254d7a6b81830e114b818ef2e282` | [Frente Obrero](https://frenteobrero.es/nuestro-programa-2/) | [Direct PDF](https://frenteobrero.es/wp-content/uploads/2026/10/Programa.pdf) | `published-unverified` |

---

## 3. Technical Verification & Boundary Findings

The offline verification CLI (`python3 -m elecciones2026.importer verify-file`) checked each document against size, structure, polyglot signatures, and active content rules:

1. **Standard passes (6 documents):**
   - BNG, EAJ-PNV, ERC, Frente Obrero, Partido Humanista, and PP passed all static inspection checks, magic byte validations, and SHA-256 verifications.
2. **Coalición Canaria (Size threshold exception):**
   - File size (69,215,587 bytes) exceeds the default 50 MB ceiling (`DEFAULT_MAX_FILE_SIZE_BYTES`).
   - Verified cleanly when inspected with `--max-size-mb 75`. Structure and content are legitimate PDF 1.5.
3. **SALF (Active content token trigger):**
   - Detected active dictionary token `/js` during byte scan of the 19 MB document (`ActiveContentDetectedError`).
   - Must remain strictly quarantined in the offline private archive; extraction requires sanitized isolation.
4. **ERC (Discovery path caveat):**
   - Direct link identified via secondary index (`coinciden.com`). Direct automated fetch returned HTTP 403.
   - Content and election cycle identity require human editorial verification.
5. **Frente Obrero (Edition uncertainty):**
   - 64-page political programme verified, but document lacks explicit date or decree confirmation tying it exclusively to the 29 November 2026 general election.

---

## 4. Pending Formations (Coverage Gaps)

The following candidacies remain actively monitored with status `missing` in `content/sources/register.json`:

* **PSOE / PSC:** Official programme for 29N 2026 not yet located on official transparency channels.
* **VOX:** Official 2026 general election programme not yet located.
* **Movimiento Sumar / Frente Amplio / Comuns:** Official 2026 programme not yet published on primary portals.
* **Junts per Catalunya:** Official 2026 programme pending retrieval.
* **Podemos:** Official 2026 programme pending retrieval.
* **EH Bildu:** Official 2026 programme pending retrieval.
* **PACMA:** Official 2026 programme pending retrieval.
* **Compromís-Front Valencià:** Official 2026 programme pending retrieval.
* **UPN:** Own programme pending retrieval.
* **Por un Mundo Más Justo:** 2026 campaign site lists programme PDFs, but links contain unresolved template variables.
* **Iustitia Europa:** Contract available only in HTML format; no PDF recovered.
* **Democracia 21 / Alhora:** Pending discovery.

---

## 5. Repository and Architecture Hygiene

* `.gitignore` updated to ignore `programas-29N-2026/` to prevent raw source files from being committed.
* `content/sources/download-policy.json` updated with permitted hosts for the new candidacies.
* `content/sources/register.json` updated to version 1.0.0 with 17 tracked sources (13 for 2026, 4 for 2023).
* All eight PDF documents safely archived with retrieval manifests in `$HOME/Library/Application Support/elecciones2026/private-sources/es-gen-2026/`.
