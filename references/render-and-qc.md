# Rendering, Export & Quality Control

## Capability check
Periksa FFmpeg/FFprobe, Python packages, Node/browser, font, TTS, audio tools, image/video generation, dan kemampuan inspeksi media. Jalankan hanya tool yang ditemukan.

## Pipeline
Pilih yang stabil: Python/Pillow/NumPy/OpenCV; HTML/CSS/SVG + browser; Remotion/Node; FFmpeg; atau editor native. Jangan memaksakan satu pipeline. Jika gagal, coba alternatif tanpa menurunkan kualitas diam-diam.

## Render reproducible
Simpan konfigurasi, timeline, seed, ukuran frame, fps, dan parameter encode. Pastikan jumlah frame/durasi sinkron. Gunakan CFR bila sesuai platform. Pertahankan source dan aset asli.

## Export
MP4 adalah target utama bila dapat dibuat. H.264/AAC dapat menjadi default kompatibilitas luas; sesuaikan resolusi, rasio, fps, dan bitrate/CRF dengan brief.

## QC teknis
Periksa durasi container/stream, resolusi, frame rate aktual, jumlah frame, codec video/audio, sample rate, channel, dan ukuran file menggunakan FFprobe atau alat setara.

## QC visual
Inspeksi awal–tengah–akhir dan setiap scene penting. Periksa teks, safe area, distorsi, transisi, black/frozen frames, artefak, dan kepatuhan larangan figur utuh.

## QC audio
Pastikan voiceover lengkap/jelas, tidak clipping, tidak ada musik, SFX/ambience relevan, dan tidak ada audio tail/silence yang tidak disengaja.

## QC isi
Periksa brief, fakta, sumber, ejaan, istilah, CTA, dan makna. Materi Islam melewati pemeriksaan syariah.

## Serah terima
Sertakan QC report berisi apa yang diperiksa, hasil nyata, temuan, perbaikan, dan batas yang belum dapat diverifikasi. Jangan klaim lulus penuh jika sebagian pemeriksaan tidak dilakukan.
