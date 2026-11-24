# Home Hunt Map

A private, password-protected map of homes we're looking at. The page is encrypted
(StatiCrypt), so this repo only holds scrambled data.

- `index.html`: the locked map page (rebuilt after each sheet refresh)
- `tools/`: builds the page from the map's satellite edition and locks it (`tools/deploy.sh`)
