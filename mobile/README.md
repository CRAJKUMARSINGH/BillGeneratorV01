# Mobile companion guidance (React Native)

This folder is a guidance stub — we recommend creating a separate repo `billgenerator-mobile`.

Suggested stack:
- Expo + React Native
- Local SQLite for offline storage
- Sync via API `/generate` and `/sync` endpoints
- Use background sync / NetInfo to reconcile offline items

Minimum screens:
- Capture measurement (photo + text + quantity)
- Local drafts list
- Sync status & logs

Do not include mobile code in main repo; keep repo small and focused.