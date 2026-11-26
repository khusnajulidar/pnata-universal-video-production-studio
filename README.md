# P'Nata Universal Video Production Studio

**Status:** Skill v0.1.0 + Production Engine v0.1.0 (starter)  
**Mode kerja:** Otomatis  
**Target penyerahan:** MP4 final + aset + source/project + laporan QC bila runtime memungkinkan

Studio produksi video universal untuk motion graphics, cinematic, educational, documentary, promotional, social media, presentation, dan format hybrid.

## Aturan P'Nata yang tidak dapat dinegosiasikan
1. Tidak menggunakan musik dalam bentuk apa pun.
2. Tidak menggambarkan manusia atau hewan secara utuh.
3. Audio yang diperbolehkan hanya voiceover/ucapan, efek suara non-musikal, ambience lingkungan yang benar-benar non-musikal, dan silence.
4. Akurasi, manfaat, dan kepatuhan mengalahkan tren atau efek visual.
5. MP4 hanya boleh dinyatakan final setelah benar-benar diekspor dan diperiksa.

## Struktur
- `SKILL.md` — instruksi inti dan orkestrator.
- `references/` — modul riset, kreatif, visual, aset, audio, render/QC, dan supervisi syariah.
- `adapters/` — panduan integrasi agen/platform.
- `templates/` — format status proyek.
- `tests/` — checklist penerimaan skill.
- `engine/` — Production Engine Python + FFmpeg v0.1.0, project schema, contoh proyek, policy gates, capability check, dan FFprobe QC.

## Production Engine
Lihat [engine/README.md](engine/README.md). Versi awal dapat merender timeline scene berbasis tipografi/still image menjadi MP4 H.264, menggabungkan audio yang sudah ditinjau manusia, dan membuat laporan metadata QC.

Engine v0.1 masih berupa starter renderer dengan hard cuts. Animasi keyframe, transisi, subtitle, compositor multi-layer, deteksi musik semantik, dan sertifikasi visual otomatis belum tersedia. Human-review declarations adalah gerbang proses, bukan bukti otomatis.

## Mode penggunaan
Contoh brief:
> Buat video edukasi 45 detik tentang [topik] untuk Instagram Reels. Jalankan mode otomatis dan serahkan MP4 beserta source dan aset.

Untuk proyek lanjutan:
> Lanjutkan proyek [nama]. Audit status, keputusan yang disetujui, dan aset yang tersedia. Jangan mengulang pekerjaan yang sudah final.

Setiap runtime wajib memeriksa tool aktual. Jangan mengklaim kemampuan yang belum diuji.
